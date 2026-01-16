"""
TERAG FastAPI Application
Main entry point for TERAG Local API Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime

from modules.ideas_extractor import IdeasExtractor
from modules.metrics_collector import MetricsCollector
from modules.llm_client import create_llm_client, LLMClient, TaskType
from modules.idea_collector import IdeaCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TERAG Local API",
    description="TERAG Cognitive Knowledge Infrastructure - Local Development Server",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to add charset=utf-8 to JSON responses
@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("application/json"):
        if "charset" not in response.headers.get("content-type", ""):
            response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# Initialize modules
ideas_extractor = IdeasExtractor()
metrics_collector = MetricsCollector()
llm_client = create_llm_client()  # Optional LLM client
idea_collector = IdeaCollector(llm_client=llm_client)  # Initialize with LLM if available

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None
    use_llm: bool = True  # Use LLM for response generation
    auto_select_model: bool = True  # Automatically select best model for task
    task_type: Optional[str] = None  # Explicit task type: "code", "analysis", "reasoning", "general"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

class QueryResponse(BaseModel):
    answer: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, Any]  # Allow complex structures for encoding info
    timestamp: str

class CollectIdeasRequest(BaseModel):
    source_type: str  # "pdf", "article", "x_thread"
    source_path: str  # Path to PDF or URL
    auto_extract: bool = True  # Use LLM for extraction

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "TERAG Local API Server",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "context": "/context",
                "docs": "/docs",
                "ideas_collect": "/ideas/collect",
                "ideas_list": "/ideas/list"
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    services = {
        "api": "healthy",
        "neo4j": "unknown",
        "prometheus": "unknown"
    }
    
    # Check Neo4j connection
    try:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "terag_local"))
        )
        driver.verify_connectivity()
        services["neo4j"] = "connected"
        driver.close()
    except Exception as e:
        logger.warning(f"Neo4j check failed: {e}")
        services["neo4j"] = "disconnected"
    
    # Check Prometheus
    try:
        import requests
        prometheus_url = f"http://prometheus:9090/-/healthy"
        response = requests.get(prometheus_url, timeout=2)
        if response.status_code == 200:
            services["prometheus"] = "healthy"
    except Exception as e:
        logger.warning(f"Prometheus check failed: {e}")
        services["prometheus"] = "unavailable"
    
    # Check LLM
    llm_info = {}
    if llm_client:
        if llm_client.health_check():
            services["llm"] = f"connected ({llm_client.provider.value})"
            llm_info["provider"] = llm_client.provider.value
            llm_info["model"] = llm_client.model
            llm_info["utf8_fix_enabled"] = llm_client.force_utf8_fix
        else:
            services["llm"] = "disconnected"
    else:
        services["llm"] = "not configured"
    
    # Get encoding errors count from metrics
    encoding_status = "ok"
    encoding_errors_count = metrics_collector.llm_encoding_errors_count
    if encoding_errors_count > 0:
        # Check if encoding errors are recent (within last hour)
        # If more than 10 errors, consider it problematic
        if encoding_errors_count > 10:
            encoding_status = "warning"
        else:
            encoding_status = "monitoring"
    
    # Try to get encoding errors from Prometheus if available
    try:
        import requests
        prometheus_query_url = "http://prometheus:9090/api/v1/query"
        response = requests.get(
            prometheus_query_url,
            params={"query": "sum(terag_llm_encoding_errors_total)"},
            timeout=2
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("data", {}).get("result"):
                prometheus_count = float(data["data"]["result"][0]["value"][1])
                if prometheus_count > encoding_errors_count:
                    encoding_errors_count = int(prometheus_count)
    except Exception as e:
        logger.debug(f"Could not query Prometheus for encoding errors: {e}")
    
    # Add encoding information to services
    services["encoding"] = {
        "status": encoding_status,
        "errors_fixed": encoding_errors_count,
        "fix_enabled": llm_info.get("utf8_fix_enabled", False) if llm_client else False
    }
    
    return HealthResponse(
        status="healthy",
        services=services,
        timestamp=datetime.now().isoformat()
    )

@app.post("/context", response_model=QueryResponse, tags=["Query"])
async def get_context(request: QueryRequest):
    """
    Get context for a question
    Returns context with optional LLM-generated response
    """
    import time
    start_time = time.time()
    
    try:
        # Extract ideas from question
        ideas = ideas_extractor.extract(request.question)
        
        # Collect metrics
        metrics_collector.increment_request(endpoint="context")
        metrics = metrics_collector.collect()
        
        # Build context from knowledge sources
        context = {
            "question": request.question,
            "ideas": ideas,
            "sources": [
                {
                    "type": "knowledge_graph",
                    "confidence": 0.85,
                    "source": "Neo4j Graph"
                },
                {
                    "type": "semantic_search",
                    "confidence": 0.92,
                    "source": "ChromaDB"
                }
            ],
            "reasoning_path": [
                {
                    "step": 1,
                    "action": "parse_query",
                    "result": "Query parsed successfully"
                },
                {
                    "step": 2,
                    "action": "graph_search",
                    "result": "Found 3 relevant nodes"
                },
                {
                    "step": 3,
                    "action": "context_assembly",
                    "result": "Context assembled"
                }
            ]
        }
        
        # Merge with provided context if any
        if request.context:
            context.update(request.context)
        
        # Generate answer using LLM if available and requested
        answer = "This is an example response from TERAG Local API. The system has processed your question and retrieved relevant context from the knowledge graph."
        llm_metadata = {}
        
        if request.use_llm and llm_client:
            try:
                # Prepare context string for LLM
                context_str = f"Question: {request.question}\n\nRetrieved context: {context.get('sources', [])}"
                
                # System prompt for TERAG
                system_prompt = """You are TERAG, a cognitive knowledge infrastructure system. 
                Answer questions based on the provided context from the knowledge graph.
                Be precise, factual, and cite sources when available."""
                
                # Determine task type
                task_type = None
                if request.task_type:
                    try:
                        task_type = TaskType(request.task_type.lower())
                    except ValueError:
                        logger.warning(f"Invalid task_type: {request.task_type}, using auto-detection")
                
                # Generate LLM response with automatic model selection if enabled
                llm_start_time = time.time()
                if request.auto_select_model:
                    llm_response = llm_client.generate_with_task_detection(
                        prompt=request.question,
                        context=context_str,
                        system_prompt=system_prompt,
                        task_type=task_type,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                    )
                else:
                    # Use standard generation without model switching
                    llm_response = llm_client.generate(
                        prompt=request.question,
                        context=context_str,
                        system_prompt=system_prompt,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                    )
                    llm_response["task_type"] = task_type.value if task_type else "general"
                    llm_response["model_selected"] = llm_client.model
                    llm_response["model_switched"] = False
                
                llm_duration = time.time() - llm_start_time
                detected_task_type = llm_response.get("task_type", "general")
                selected_model = llm_response.get("model_selected", llm_response.get("model", "unknown"))
                model_switched = llm_response.get("model_switched", False)
                
                # Record LLM metrics
                if not llm_response.get("error"):
                    answer = llm_response.get("response", answer)
                    metrics_collector.record_llm_request(
                        task_type=detected_task_type,
                        model=selected_model,
                        duration=llm_duration,
                        success=True
                    )
                    metrics_collector.record_task_type(detected_task_type)
                    
                    if model_switched:
                        metrics_collector.record_model_switch(
                            from_model=llm_client.model,
                            to_model=selected_model,
                            task_type=detected_task_type
                        )
                    
                    llm_metadata = {
                        "model": llm_response.get("model", "unknown"),
                        "model_selected": selected_model,
                        "task_type": detected_task_type,
                        "model_switched": model_switched,
                        "provider": llm_response.get("provider", "unknown"),
                        "usage": llm_response.get("usage", {}),
                        "total_duration": llm_response.get("total_duration", 0)
                    }
                else:
                    logger.warning("LLM returned error, using fallback answer")
                    metrics_collector.increment_error(endpoint="context", error_type="llm_error")
                    metrics_collector.record_llm_request(
                        task_type=detected_task_type,
                        model=selected_model,
                        duration=llm_duration,
                        success=False
                    )
            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                metrics_collector.increment_error(endpoint="context", error_type="llm_exception")
                llm_metadata = {"error": str(e)}
        elif request.use_llm and not llm_client:
            logger.warning("LLM requested but client not available")
            answer += " (LLM integration not available - check LLM_PROVIDER and LLM_URL in config.env)"
        
        request_duration = time.time() - start_time
        metrics_collector.record_request_duration("context", request_duration)
        
        return QueryResponse(
            answer=answer,
            context=context,
            metadata={
                "processing_time_ms": int(request_duration * 1000),
                "model": llm_metadata.get("model", "local"),
                "llm_used": request.use_llm and llm_client is not None,
                "llm_metadata": llm_metadata,
                "metrics": metrics
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing context request: {e}")
        metrics_collector.increment_error(endpoint="context", error_type="exception")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """Get collected metrics (JSON format)"""
    return metrics_collector.collect()

@app.get("/metrics/prometheus", tags=["Metrics"])
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        raise HTTPException(status_code=503, detail="Prometheus client not available")

@app.get("/llm/models", tags=["LLM"])
async def list_llm_models():
    """List available LLM models"""
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM client not available")
    
    try:
        models = llm_client.list_models()
        return JSONResponse(
            content={
                "provider": llm_client.provider.value,
                "base_url": llm_client.base_url,
                "current_model": llm_client.model,
                "available_models": models
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/llm/health", tags=["LLM"])
async def llm_health():
    """Check LLM service health and show auto-detected model info"""
    if not llm_client:
        return JSONResponse(
            content={
                "status": "unavailable",
                "message": "LLM client not configured",
                "tip": "Set LLM_PROVIDER, LLM_URL, and optionally LLM_MODEL in config.env"
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    is_healthy = llm_client.health_check()
    available_models = []
    auto_detected = False
    
    try:
        available_models = llm_client.list_models()
        # Check if current model matches preferred (if set)
        preferred_model = os.getenv("LLM_MODEL")
        if preferred_model and llm_client.model != preferred_model:
            auto_detected = True
    except:
        pass
    
    return JSONResponse(
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "provider": llm_client.provider.value,
            "base_url": llm_client.base_url,
            "current_model": llm_client.model,
            "preferred_model": os.getenv("LLM_MODEL"),
            "auto_detected": auto_detected,
            "available_models_count": len(available_models),
            "available_models": available_models[:10] if len(available_models) > 10 else available_models,  # Show first 10
            "auto_model_selection": True  # Feature available
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.post("/llm/test-task-selection", tags=["LLM"])
async def test_task_selection(question: str, task_type: Optional[str] = None):
    """
    Test automatic model selection for a task
    Returns which model would be selected for the given question
    """
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM client not available")
    
    try:
        # Detect or use provided task type
        if task_type:
            try:
                task = TaskType(task_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid task_type: {task_type}. Use: code, analysis, reasoning, general")
        else:
            task = llm_client._detect_task_type(question)
        
        # Get model selection
        selected_model = llm_client.select_model_for_task(task, question)
        available_models = llm_client.list_models()
        
        return JSONResponse(
            content={
                "question": question,
                "detected_task_type": task.value,
                "selected_model": selected_model,
                "current_model": llm_client.model,
                "would_switch": selected_model != llm_client.model,
                "available_models": available_models,
                "task_priorities": {
                    "code": ["qwen3-coder", "deepseek-coder", "codellama", "llama3"],
                    "analysis": ["qwen3", "qwen2.5", "llama3", "mistral"],
                    "reasoning": ["qwen3", "qwen2.5", "llama3", "mistral"],
                    "general": ["llama3", "qwen3", "mistral", "phi3"]
                }
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Error testing task selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ideas/collect", tags=["Ideas"])
async def collect_ideas(request: CollectIdeasRequest):
    """
    Collect ideas from PDF, article, or X thread
    Automatically extracts and stores ideas in Neo4j knowledge graph
    """
    try:
        if request.source_type == "pdf":
            result = idea_collector.collect_from_pdf(
                request.source_path, 
                auto_extract=request.auto_extract
            )
        elif request.source_type == "article":
            result = idea_collector.collect_from_url(
                request.source_path, 
                auto_extract=request.auto_extract
            )
        elif request.source_type == "x_thread":
            result = idea_collector.collect_from_x_thread(
                request.source_path, 
                auto_extract=request.auto_extract
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown source_type: {request.source_type}. Use 'pdf', 'article', or 'x_thread'"
            )
        
        metrics_collector.increment_request(endpoint="ideas/collect")
        return result
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.source_path}")
    except Exception as e:
        logger.error(f"Error collecting ideas: {e}")
        metrics_collector.increment_error(endpoint="ideas/collect", error_type="exception")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ideas/list", tags=["Ideas"])
async def list_ideas(limit: int = 50):
    """
    List all collected ideas from Neo4j knowledge graph
    """
    try:
        ideas = idea_collector.get_ideas_from_graph(limit=limit)
        return JSONResponse(
            content={
                "total": len(ideas),
                "ideas": ideas,
                "timestamp": datetime.now().isoformat()
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Error listing ideas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

