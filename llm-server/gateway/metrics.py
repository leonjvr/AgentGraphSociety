"""
Metrics collection for monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time

class Metrics:
    """Prometheus metrics for the LLM Gateway."""
    
    def __init__(self):
        # Request metrics
        self.request_count = Counter(
            'llm_gateway_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'llm_gateway_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Model metrics
        self.model_usage = Counter(
            'llm_gateway_model_usage_total',
            'Model usage count',
            ['model']
        )
        
        self.token_usage = Counter(
            'llm_gateway_tokens_total',
            'Total tokens processed',
            ['model', 'type']  # type: prompt, completion
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'llm_gateway_cache_hits_total',
            'Cache hits'
        )
        
        self.cache_misses = Counter(
            'llm_gateway_cache_misses_total',
            'Cache misses'
        )
        
        # Error metrics
        self.error_count = Counter(
            'llm_gateway_errors_total',
            'Total errors',
            ['type']
        )
        
        # Performance metrics
        self.active_requests = Gauge(
            'llm_gateway_active_requests',
            'Currently active requests'
        )
        
        self.ollama_response_time = Histogram(
            'llm_gateway_ollama_response_seconds',
            'Ollama response time',
            ['model']
        )
        
        # Batch metrics
        self.batch_request_count = Counter(
            'llm_gateway_batch_requests_total',
            'Total batch requests'
        )
        
        self.batch_size = Histogram(
            'llm_gateway_batch_size',
            'Batch request sizes'
        )
        
        # System info
        self.info = Info(
            'llm_gateway_info',
            'LLM Gateway information'
        )
        self.info.info({
            'version': '1.0.0',
            'start_time': str(time.time())
        })