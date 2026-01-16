"""
LLM Client Module
Integration with local LLM providers (Ollama, LM Studio)
"""

import requests
from typing import Dict, Any, Optional, List
import logging
import os
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import metrics collector for encoding error tracking
try:
    from modules.metrics_collector import record_encoding_error_metric
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    def record_encoding_error_metric(model: str, provider: str):
        pass  # No-op if metrics not available
    logger.debug("Metrics collector not available, encoding errors won't be tracked")


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"  # For compatibility with OpenAI-compatible APIs


class TaskType(str, Enum):
    """Types of tasks for model selection"""
    CODE = "code"  # Code generation, analysis, debugging
    ANALYSIS = "analysis"  # Data analysis, research, extraction
    REASONING = "reasoning"  # Complex reasoning, problem solving
    GENERAL = "general"  # General Q&A, conversation


class LLMClient:
    """Unified client for local LLM providers"""
    
    def __init__(self, provider: str = "ollama", base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider ("ollama", "lm_studio", "openai")
            base_url: Base URL for LLM API (defaults to provider defaults)
            model: Model name to use
        """
        self.provider = LLMProvider(provider.lower())
        self.model = model or self._get_default_model()
        self.base_url = base_url or self._get_default_url()
        self.timeout = 120  # 2 minutes timeout for LLM requests
        self._available_models_cache = None  # Cache for available models
        self.force_utf8_fix = os.getenv("LLM_FORCE_UTF8_FIX", "true").lower() == "true"
        
    def _get_default_url(self) -> str:
        """Get default URL for provider"""
        defaults = {
            LLMProvider.OLLAMA: "http://host.docker.internal:11434",
            LLMProvider.LM_STUDIO: "http://host.docker.internal:1234",
            LLMProvider.OPENAI: "http://host.docker.internal:1234"
        }
        return defaults.get(self.provider, defaults[LLMProvider.OLLAMA])
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            LLMProvider.OLLAMA: "llama3",
            LLMProvider.LM_STUDIO: "local-model",
            LLMProvider.OPENAI: "gpt-3.5-turbo"
        }
        return defaults.get(self.provider, defaults[LLMProvider.OLLAMA])
    
    def _fix_utf8_encoding(self, text: str) -> str:
        """
        Fix UTF-8 encoding issues from Ollama responses
        Some models return UTF-8 text marked as Latin-1, causing encoding issues
        
        This fixes cases where UTF-8 bytes were incorrectly decoded as Latin-1,
        which is common with qwen3-coder and deepseek models in Ollama.
        
        Args:
            text: Text that may have encoding issues
            
        Returns:
            Correctly decoded UTF-8 text
        """
        if not self.force_utf8_fix or not text:
            return text
        
        try:
            if isinstance(text, str):
                # Detect if text looks like misencoded UTF-8 (contains garbled Cyrillic/Unicode)
                # Common pattern: sequences like "⨬" or "ÐÑÐ¾ÑÐ¸Ð¼Ð¸Ð·Ð°ÑÐ¸Ñ"
                has_garbled_unicode = any(
                    ord(c) > 127 and (0x80 <= ord(c) <= 0xFF) 
                    for c in text[:100]  # Check first 100 chars for performance
                )
                
                if has_garbled_unicode:
                    try:
                        # Re-encode as latin-1 and decode as utf-8
                        # This fixes: UTF-8 bytes → incorrectly decoded as Latin-1 → re-encode → decode as UTF-8
                        fixed_text = text.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
                        
                        # Verify the fix improved the text
                        if fixed_text and fixed_text != text:
                            # Check if fixed text has more readable characters
                            # (contains Cyrillic, Chinese, or other non-Latin Unicode)
                            readable_chars = sum(1 for c in fixed_text if ord(c) > 127 and ord(c) < 0x10000)
                            garbled_chars = sum(1 for c in text[:min(100, len(text))] if 0x80 <= ord(c) <= 0xFF)
                            
                            if readable_chars > garbled_chars or len(fixed_text) > len(text) * 0.8:
                                logger.debug(f"Fixed UTF-8 encoding: {len(text)} → {len(fixed_text)} chars")
                                # Record encoding error in metrics
                                if METRICS_AVAILABLE:
                                    record_encoding_error_metric(self.model, self.provider.value)
                                return fixed_text
                    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
                        pass
        except Exception as e:
            logger.warning(f"Error fixing UTF-8 encoding: {e}")
        
        return text
    
    def generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            context: Additional context to include
            system_prompt: System prompt/instructions
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            if self.provider == LLMProvider.OLLAMA:
                return self._generate_ollama(prompt, context, system_prompt, **kwargs)
            elif self.provider == LLMProvider.LM_STUDIO:
                return self._generate_lm_studio(prompt, context, system_prompt, **kwargs)
            elif self.provider == LLMProvider.OPENAI:
                return self._generate_openai_compatible(prompt, context, system_prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": f"Error: {str(e)}",
                "error": True,
                "provider": self.provider.value
            }
    
    def _generate_ollama(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate using Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        # Build full prompt
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{full_prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": kwargs.get("stream", False),
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_tokens", 512)
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        raw_response = data.get("response", "")
        
        # Fix UTF-8 encoding issues (latin-1 → utf-8 misencoding)
        fixed_response = self._fix_utf8_encoding(raw_response)
        
        return {
            "response": fixed_response,
            "model": self.model,
            "provider": "ollama",
            "done": data.get("done", False),
            "context": data.get("context", []),
            "total_duration": data.get("total_duration", 0),
            "load_duration": data.get("load_duration", 0),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "eval_count": data.get("eval_count", 0)
        }
    
    def _generate_lm_studio(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate using LM Studio API (OpenAI-compatible)"""
        url = f"{self.base_url}/v1/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stream": kwargs.get("stream", False)
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        raw_response = data["choices"][0]["message"]["content"]
        
        # Fix UTF-8 encoding issues (latin-1 → utf-8 misencoding)
        fixed_response = self._fix_utf8_encoding(raw_response)
        
        return {
            "response": fixed_response,
            "model": self.model,
            "provider": "lm_studio",
            "usage": data.get("usage", {}),
            "finish_reason": data["choices"][0].get("finish_reason", "stop")
        }
    
    def _generate_openai_compatible(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate using OpenAI-compatible API"""
        return self._generate_lm_studio(prompt, context, system_prompt, **kwargs)
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            if self.provider == LLMProvider.OLLAMA:
                url = f"{self.base_url}/api/tags"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            elif self.provider in [LLMProvider.LM_STUDIO, LLMProvider.OPENAI]:
                url = f"{self.base_url}/v1/models"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
            else:
                return []
        except Exception as e:
            logger.warning(f"Error listing models: {e}")
            return []
    
    def health_check(self) -> bool:
        """Check if LLM service is available"""
        try:
            if self.provider == LLMProvider.OLLAMA:
                url = f"{self.base_url}/api/tags"
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            elif self.provider in [LLMProvider.LM_STUDIO, LLMProvider.OPENAI]:
                url = f"{self.base_url}/v1/models"
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            else:
                return False
        except:
            return False
    
    def select_model_for_task(self, task_type: TaskType, prompt: Optional[str] = None) -> Optional[str]:
        """
        Select best model for a specific task type
        
        Args:
            task_type: Type of task (code, analysis, reasoning, general)
            prompt: Optional prompt to analyze for better selection
            
        Returns:
            Best model name for the task, or None if not available
        """
        if self.provider != LLMProvider.OLLAMA:
            # For other providers, use current model
            return self.model
        
        # Get available models
        available_models = self.list_models()
        if not available_models:
            return self.model
        
        # Task-specific model priorities
        task_priorities = {
            TaskType.CODE: [
                "qwen3-coder", "qwen3coder",
                "deepseek-coder", "deepseekcoder",
                "codellama",
                "qwen2.5-coder", "qwen2.5coder",
                "llama3", "phi3"
            ],
            TaskType.ANALYSIS: [
                "qwen3", "qwen2.5",
                "llama3", "mistral",
                "phi3", "gemma"
            ],
            TaskType.REASONING: [
                "qwen3", "qwen2.5",
                "llama3", "mistral",
                "phi3"
            ],
            TaskType.GENERAL: [
                "llama3", "qwen3", "qwen2.5",
                "mistral", "phi3", "gemma"
            ]
        }
        
        priorities = task_priorities.get(task_type, task_priorities[TaskType.GENERAL])
        normalized_available = [m.lower().split(':')[0] for m in available_models]
        
        # Find best matching model
        for priority in priorities:
            for i, normalized in enumerate(normalized_available):
                if priority in normalized:
                    selected_model = available_models[i]
                    logger.info(f"Selected model {selected_model} for task type: {task_type.value}")
                    return selected_model
        
        # Fallback to current model or first available
        return self.model or available_models[0]
    
    def generate_with_task_detection(self, prompt: str, context: Optional[str] = None, 
                                    system_prompt: Optional[str] = None, 
                                    task_type: Optional[TaskType] = None,
                                    **kwargs) -> Dict[str, Any]:
        """
        Generate response with automatic model selection based on task type
        
        Args:
            prompt: User prompt
            context: Additional context
            system_prompt: System prompt
            task_type: Explicit task type, or None for auto-detection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        # Auto-detect task type if not provided
        if task_type is None:
            task_type = self._detect_task_type(prompt)
        
        # Select best model for task
        original_model = self.model
        selected_model = self.select_model_for_task(task_type, prompt)
        
        # Temporarily switch model if different
        model_switched = False
        if selected_model and selected_model != self.model:
            model_switched = True
            original_model = self.model
            self.model = selected_model
        
        try:
            # Generate response
            result = self.generate(prompt, context, system_prompt, **kwargs)
            
            # Add task type and model selection info
            result["task_type"] = task_type.value
            result["model_selected"] = selected_model
            result["model_switched"] = model_switched
            
            return result
        finally:
            # Restore original model
            if model_switched:
                self.model = original_model
    
    def _detect_task_type(self, prompt: str) -> TaskType:
        """
        Detect task type from prompt
        
        Args:
            prompt: User prompt text
            
        Returns:
            Detected task type
        """
        prompt_lower = prompt.lower()
        
        # Code-related keywords
        code_keywords = [
            "code", "function", "class", "method", "variable", "import",
            "debug", "error", "bug", "fix", "implement", "programming",
            "algorithm", "syntax", "compile", "test", "refactor",
            "python", "javascript", "typescript", "java", "c++", "go", "rust"
        ]
        
        # Analysis keywords
        analysis_keywords = [
            "analyze", "analysis", "extract", "parse", "data",
            "research", "study", "examine", "evaluate", "compare",
            "summary", "summarize", "findings", "trends"
        ]
        
        # Reasoning keywords
        reasoning_keywords = [
            "why", "how", "explain", "reasoning", "logic", "think",
            "solve", "problem", "strategy", "approach", "decision",
            "conclusion", "inference", "deduce"
        ]
        
        # Count matches
        code_score = sum(1 for keyword in code_keywords if keyword in prompt_lower)
        analysis_score = sum(1 for keyword in analysis_keywords if keyword in prompt_lower)
        reasoning_score = sum(1 for keyword in reasoning_keywords if keyword in prompt_lower)
        
        # Determine task type
        if code_score > analysis_score and code_score > reasoning_score and code_score > 0:
            return TaskType.CODE
        elif reasoning_score > analysis_score and reasoning_score > 0:
            return TaskType.REASONING
        elif analysis_score > 0:
            return TaskType.ANALYSIS
        else:
            return TaskType.GENERAL


def _detect_best_model(available_models: List[str], preferred_model: Optional[str] = None) -> Optional[str]:
    """
    Detect best available model with priority order
    
    Priority (for coding/analysis tasks):
    1. qwen3-coder (best for code)
    2. qwen2.5-coder
    3. deepseek-coder
    4. llama3 (general purpose)
    5. phi3 (lightweight)
    6. mistral (general purpose)
    7. Any other model if preferred is specified
    
    Args:
        available_models: List of available model names
        preferred_model: Preferred model from config
        
    Returns:
        Best available model name or None
    """
    if not available_models:
        return None
    
    # Normalize model names (remove tags, versions)
    normalized_available = [m.lower().split(':')[0] for m in available_models]
    
    # Priority order for coding/analysis tasks
    priority_models = [
        "qwen3-coder",
        "qwen3coder",
        "qwen2.5-coder",
        "qwen2.5coder",
        "deepseek-coder",
        "deepseekcoder",
        "llama3",
        "phi3",
        "mistral",
        "gemma",
        "codellama"
    ]
    
    # If preferred model is specified and available, use it
    if preferred_model:
        preferred_normalized = preferred_model.lower().split(':')[0]
        if preferred_normalized in normalized_available:
            # Find full name match
            for model in available_models:
                if model.lower().startswith(preferred_normalized):
                    return model
        # If preferred not found, try to match by partial name
        for model in available_models:
            if preferred_normalized in model.lower():
                return model
    
    # Otherwise, use priority order
    for priority in priority_models:
        for i, normalized in enumerate(normalized_available):
            if priority in normalized:
                return available_models[i]
    
    # Fallback to first available model
    return available_models[0]


def create_llm_client() -> Optional[LLMClient]:
    """
    Create LLM client from environment variables
    Automatically detects best available model if not specified
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    base_url = os.getenv("LLM_URL")
    preferred_model = os.getenv("LLM_MODEL")
    
    if not base_url:
        # Try to detect provider default
        if provider == "ollama":
            base_url = "http://host.docker.internal:11434"
        elif provider in ["lm_studio", "lmstudio"]:
            base_url = "http://host.docker.internal:1234"
        else:
            return None
    
    try:
        # Create temporary client to check health and list models
        temp_client = LLMClient(provider=provider, base_url=base_url, model=preferred_model or "dummy")
        
        if not temp_client.health_check():
            logger.warning(f"LLM service not available at {base_url}")
            return None
        
        # Auto-detect best model if Ollama provider
        detected_model = preferred_model
        if provider == "ollama":
            try:
                available_models = temp_client.list_models()
                if available_models:
                    detected_model = _detect_best_model(available_models, preferred_model)
                    if detected_model and detected_model != preferred_model:
                        logger.info(f"Auto-detected model: {detected_model} (preferred: {preferred_model or 'none'})")
                    elif detected_model:
                        logger.info(f"Using specified model: {detected_model}")
                else:
                    logger.warning("No models available in Ollama")
                    return None
            except Exception as e:
                logger.warning(f"Could not auto-detect models: {e}, using preferred: {preferred_model}")
                detected_model = preferred_model or temp_client.model
        
        # Create final client with detected/selected model
        client = LLMClient(provider=provider, base_url=base_url, model=detected_model)
        
        # Verify the model works (only for Ollama)
        if provider == "ollama" and detected_model:
            try:
                available = client.list_models()
                if detected_model not in available:
                    # Try to find similar model
                    found = False
                    for model in available:
                        if detected_model.lower() in model.lower() or model.lower() in detected_model.lower():
                            logger.info(f"Using similar model: {model} (requested: {detected_model})")
                            client.model = model
                            found = True
                            break
                    if not found:
                        logger.warning(f"Model {detected_model} not found, using: {available[0] if available else 'unknown'}")
                        if available:
                            client.model = available[0]
            except Exception as e:
                logger.warning(f"Could not verify model: {e}")
        
        logger.info(f"LLM client initialized: {provider} at {base_url} with model {client.model}")
        return client
        
    except Exception as e:
        logger.warning(f"Failed to initialize LLM client: {e}")
        return None



