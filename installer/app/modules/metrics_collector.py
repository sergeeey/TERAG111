"""
Metrics Collector Module
Collects and aggregates system metrics with Prometheus integration
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
import logging

try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("prometheus_client not available, metrics will be limited")

if PROMETHEUS_AVAILABLE:
    logger = logging.getLogger(__name__)
    
    # Prometheus metrics
    request_counter = Counter('terag_requests_total', 'Total number of requests', ['endpoint', 'status'])
    error_counter = Counter('terag_errors_total', 'Total number of errors', ['endpoint', 'error_type'])
    request_duration = Histogram('terag_request_duration_seconds', 'Request duration in seconds', ['endpoint'])
    
    # LLM metrics
    llm_requests = Counter('terag_llm_requests_total', 'Total LLM requests', ['task_type', 'model', 'status'])
    llm_duration = Histogram('terag_llm_duration_seconds', 'LLM response duration in seconds', ['task_type', 'model'])
    llm_model_usage = Gauge('terag_llm_model_current', 'Current LLM model in use', ['model'])
    llm_model_switches = Counter('terag_llm_model_switches_total', 'Total model switches', ['from_model', 'to_model', 'task_type'])
    llm_encoding_errors = Counter('terag_llm_encoding_errors_total', 'Total LLM encoding errors fixed', ['model', 'provider'])
    
    # Signal Discovery metrics
    new_concepts_total = Counter('terag_new_concepts_total', 'Total new concepts discovered', ['domain', 'type'])
    weak_signals_total = Counter('terag_weak_signals_total', 'Total weak signals detected', ['domain'])
    signal_confidence_avg = Gauge('terag_signal_confidence_avg', 'Average confidence of signals', ['domain'])
    novelty_index_avg = Gauge('terag_novelty_index_avg', 'Average novelty index', ['domain'])
    discoveries_inserted = Counter('terag_discoveries_inserted_total', 'Total discoveries inserted into graph', ['domain'])
    
    # Feedback Loop metrics
    concept_confidence_trend = Gauge('terag_concept_confidence_trend', 'Trend of concept confidence over time', ['concept', 'domain'])
    signal_decay_rate = Gauge('terag_signal_decay_rate', 'Rate of signal decay (confidence decrease)', ['domain'])
    concept_validation_rate = Counter('terag_concept_validation_rate_total', 'Total concept validations', ['concept', 'status'])
    signal_strength_trend = Gauge('terag_signal_strength_trend', 'Signal strength trend over time', ['signal', 'domain'])
    
    # Task type metrics
    task_type_counter = Counter('terag_task_types_total', 'Total requests by task type', ['task_type'])
    
    # System metrics
    system_info = Info('terag_system', 'TERAG system information')
    uptime_gauge = Gauge('terag_uptime_seconds', 'System uptime in seconds')
    
    # Cognitive Load Index - комплексный показатель нагрузки системы
    cognitive_load_index = Gauge('terag_cognitive_load_index', 'Cognitive Load Index (0-100)', ['level'])
    cognitive_load_components = Gauge('terag_cognitive_load_components', 'Cognitive Load components', ['component'])
else:
    # Define dummy variables when Prometheus is not available
    llm_encoding_errors = None

def record_encoding_error_metric(model: str, provider: str):
    """Safely record encoding error metric"""
    if PROMETHEUS_AVAILABLE and llm_encoding_errors is not None:
        try:
            llm_encoding_errors.labels(model=model, provider=provider).inc()
        except Exception as e:
            logger.debug(f"Failed to record encoding error metric: {e}")

class MetricsCollector:
    """Collect system and application metrics with Prometheus support"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.llm_request_count = 0
        self.llm_error_count = 0
        self.llm_encoding_errors_count = 0  # Track encoding errors fixed
        self.task_type_counts = {"code": 0, "analysis": 0, "reasoning": 0, "general": 0}
        self.current_llm_model = None
        self.recent_response_times = []  # Store recent response times for load calculation
        self.max_response_times_history = 100  # Keep last 100 response times
        
        if PROMETHEUS_AVAILABLE:
            system_info.info({'version': '1.0.0', 'service': 'terag-api'})
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect current metrics
        
        Returns:
            Dictionary with collected metrics
        """
        uptime = time.time() - self.start_time
        
        if PROMETHEUS_AVAILABLE:
            uptime_gauge.set(int(uptime))
        
        return {
            "system": {
                "uptime_seconds": int(uptime),
                "uptime_formatted": self._format_uptime(uptime),
                "timestamp": datetime.now().isoformat()
            },
            "requests": {
                "total": self.request_count,
                "errors": self.error_count,
                "success_rate": self._calculate_success_rate()
            },
            "llm": {
                "requests": self.llm_request_count,
                "errors": self.llm_error_count,
                "encoding_errors_fixed": self.llm_encoding_errors_count,
                "success_rate": self._calculate_llm_success_rate(),
                "current_model": self.current_llm_model or "none"
            },
            "task_types": self.task_type_counts.copy(),
            "performance": {
                "avg_response_time_ms": 145,  # Placeholder
                "requests_per_second": self.request_count / uptime if uptime > 0 else 0
            }
        }
    
    def increment_request(self, endpoint: str = "unknown"):
        """Increment request counter"""
        self.request_count += 1
        if PROMETHEUS_AVAILABLE:
            request_counter.labels(endpoint=endpoint, status='success').inc()
    
    def increment_error(self, endpoint: str = "unknown", error_type: str = "unknown"):
        """Increment error counter"""
        self.error_count += 1
        if PROMETHEUS_AVAILABLE:
            error_counter.labels(endpoint=endpoint, error_type=error_type).inc()
    
    def record_llm_request(self, task_type: str, model: str, duration: float, success: bool = True):
        """Record LLM request metrics"""
        self.llm_request_count += 1
        if not success:
            self.llm_error_count += 1
        
        self.current_llm_model = model
        
        if PROMETHEUS_AVAILABLE:
            status = 'success' if success else 'error'
            llm_requests.labels(task_type=task_type, model=model, status=status).inc()
            llm_duration.labels(task_type=task_type, model=model).observe(duration)
            llm_model_usage.labels(model=model).set(1)
    
    def record_task_type(self, task_type: str):
        """Record task type usage"""
        if task_type in self.task_type_counts:
            self.task_type_counts[task_type] += 1
        
        if PROMETHEUS_AVAILABLE:
            task_type_counter.labels(task_type=task_type).inc()
    
    def record_model_switch(self, from_model: str, to_model: str, task_type: str):
        """Record model switch"""
        if PROMETHEUS_AVAILABLE:
            llm_model_switches.labels(from_model=from_model, to_model=to_model, task_type=task_type).inc()
    
    def record_encoding_error(self, model: str, provider: str):
        """Record encoding error fixed"""
        self.llm_encoding_errors_count += 1
        if PROMETHEUS_AVAILABLE:
            llm_encoding_errors.labels(model=model, provider=provider).inc()
    
    def record_new_concept(self, domain: str, concept_type: str):
        """Record new concept discovered"""
        if PROMETHEUS_AVAILABLE:
            new_concepts_total.labels(domain=domain, type=concept_type).inc()
    
    def record_weak_signal(self, domain: str, confidence: float):
        """Record weak signal detected"""
        if PROMETHEUS_AVAILABLE:
            weak_signals_total.labels(domain=domain).inc()
            # Обновить среднюю уверенность
            signal_confidence_avg.labels(domain=domain).set(confidence)
    
    def record_novelty_index(self, domain: str, novelty: float):
        """Record novelty index"""
        if PROMETHEUS_AVAILABLE:
            novelty_index_avg.labels(domain=domain).set(novelty)
    
    def record_discovery_inserted(self, domain: str):
        """Record discovery inserted into graph"""
        if PROMETHEUS_AVAILABLE:
            discoveries_inserted.labels(domain=domain).inc()
    
    def update_concept_confidence_trend(self, concept: str, domain: str, confidence: float):
        """Update concept confidence trend"""
        if PROMETHEUS_AVAILABLE:
            concept_confidence_trend.labels(concept=concept, domain=domain).set(confidence)
    
    def update_signal_decay_rate(self, domain: str, decay_rate: float):
        """Update signal decay rate"""
        if PROMETHEUS_AVAILABLE:
            signal_decay_rate.labels(domain=domain).set(decay_rate)
    
    def record_concept_validation(self, concept: str, status: str):
        """Record concept validation (confirmed/refuted/uncertain)"""
        if PROMETHEUS_AVAILABLE:
            concept_validation_rate.labels(concept=concept, status=status).inc()
    
    def update_signal_strength_trend(self, signal: str, domain: str, strength: float):
        """Update signal strength trend"""
        if PROMETHEUS_AVAILABLE:
            signal_strength_trend.labels(signal=signal, domain=domain).set(strength)
    
    def record_request_duration(self, endpoint: str, duration: float):
        """Record request duration"""
        # Store for cognitive load calculation
        self.recent_response_times.append(duration)
        if len(self.recent_response_times) > self.max_response_times_history:
            self.recent_response_times.pop(0)
        
        if PROMETHEUS_AVAILABLE:
            request_duration.labels(endpoint=endpoint).observe(duration)
            self._update_cognitive_load_index()
    
    def _update_cognitive_load_index(self):
        """Calculate and update Cognitive Load Index"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        try:
            uptime = time.time() - self.start_time
            
            # Component 1: Request rate (0-30 points)
            # Normal: < 1 req/s = 0, High: 1-5 req/s = 15, Very High: > 5 req/s = 30
            request_rate = self.request_count / uptime if uptime > 0 else 0
            request_rate_score = min(30, request_rate * 6) if request_rate > 0 else 0
            
            # Component 2: LLM usage intensity (0-25 points)
            # Based on LLM requests vs total requests
            llm_usage_ratio = (self.llm_request_count / self.request_count) if self.request_count > 0 else 0
            llm_intensity_score = llm_usage_ratio * 25
            
            # Component 3: Response time (0-25 points)
            # Based on average response time (normal: < 2s, high: 2-5s, very high: > 5s)
            avg_response_time = sum(self.recent_response_times) / len(self.recent_response_times) if self.recent_response_times else 0
            if avg_response_time > 0:
                response_time_score = min(25, (avg_response_time - 0.5) * 5) if avg_response_time > 0.5 else 0
            else:
                response_time_score = 0
            
            # Component 4: Error rate (0-20 points)
            # Normal: < 5% = 0, Medium: 5-10% = 10, High: > 10% = 20
            error_rate = (self.error_count / self.request_count) if self.request_count > 0 else 0
            error_rate_score = 0 if error_rate < 0.05 else (10 if error_rate < 0.10 else 20)
            
            # Total Cognitive Load Index (0-100)
            cognitive_load = request_rate_score + llm_intensity_score + response_time_score + error_rate_score
            
            # Determine level
            if cognitive_load < 25:
                level = "low"
            elif cognitive_load < 50:
                level = "medium"
            elif cognitive_load < 75:
                level = "high"
            else:
                level = "critical"
            
            # Update Prometheus metrics
            cognitive_load_index.labels(level=level).set(cognitive_load)
            cognitive_load_components.labels(component="request_rate").set(request_rate_score)
            cognitive_load_components.labels(component="llm_intensity").set(llm_intensity_score)
            cognitive_load_components.labels(component="response_time").set(response_time_score)
            cognitive_load_components.labels(component="error_rate").set(error_rate_score)
            
        except Exception as e:
            logger.warning(f"Error calculating cognitive load index: {e}")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        if self.request_count == 0:
            return 1.0
        return (self.request_count - self.error_count) / self.request_count
    
    def _calculate_llm_success_rate(self) -> float:
        """Calculate LLM success rate"""
        if self.llm_request_count == 0:
            return 1.0
        return (self.llm_request_count - self.llm_error_count) / self.llm_request_count



