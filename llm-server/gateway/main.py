"""
LLM Gateway API for AgentGraphSociety
Provides a unified interface to Ollama with caching, monitoring, and rate limiting.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import redis.asyncio as redis
import json
import hashlib
import time
import asyncio
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from .config import settings
from .models import (
    GenerateRequest, GenerateResponse, ChatRequest, ChatResponse,
    ModelInfo, AgentProfile, BatchGenerateRequest
)
from .cache import CacheManager
from .metrics import Metrics

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentGraphSociety LLM Gateway",
    description="Unified LLM API for agent simulation",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize components
cache_manager = CacheManager(settings.redis_url) if settings.enable_cache else None
metrics = Metrics()

# HTTP client for Ollama
http_client = httpx.AsyncClient(timeout=settings.request_timeout)

# API key validation
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for authentication."""
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    if cache_manager:
        await cache_manager.connect()
    logger.info("LLM Gateway started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    if cache_manager:
        await cache_manager.disconnect()
    await http_client.aclose()
    logger.info("LLM Gateway shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ollama_healthy = await check_ollama_health()
    cache_healthy = await cache_manager.health_check() if cache_manager else True
    
    status = "healthy" if ollama_healthy and cache_healthy else "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ollama": "healthy" if ollama_healthy else "unhealthy",
            "cache": "healthy" if cache_healthy else "disabled",
        }
    }

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")

@app.get("/models")
async def list_models(api_key: bool = Depends(verify_api_key)):
    """List available models."""
    try:
        response = await http_client.get(f"{settings.ollama_base_url}/api/tags")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list models")

@app.post("/generate", response_model=GenerateResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def generate(
    request: Request,
    generate_request: GenerateRequest,
    api_key: bool = Depends(verify_api_key)
):
    """Generate text completion with caching and monitoring."""
    start_time = time.time()
    metrics.request_count.labels(method="POST", endpoint="/generate", status="processing").inc()
    metrics.active_requests.inc()
    
    try:
        # Check cache if enabled
        if cache_manager and not generate_request.no_cache:
            cache_key = cache_manager.generate_key(
                generate_request.model,
                generate_request.prompt,
                generate_request.temperature,
                generate_request.agent_profile
            )
            
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                metrics.cache_hits.inc()
                return GenerateResponse(**json.loads(cached_response))
        
        # Add agent profile to prompt if provided
        prompt = generate_request.prompt
        if generate_request.agent_profile:
            prompt = format_prompt_with_profile(prompt, generate_request.agent_profile)
        
        # Call Ollama
        ollama_request = {
            "model": generate_request.model,
            "prompt": prompt,
            "temperature": generate_request.temperature,
            "max_tokens": generate_request.max_tokens,
            "top_p": generate_request.top_p,
            "top_k": generate_request.top_k,
            "stream": False
        }
        
        response = await call_ollama_with_retry("/api/generate", ollama_request)
        
        # Prepare response
        result = GenerateResponse(
            response=response["response"],
            model=generate_request.model,
            created_at=datetime.utcnow().isoformat(),
            total_duration=response.get("total_duration", 0),
            load_duration=response.get("load_duration", 0),
            eval_duration=response.get("eval_duration", 0),
            eval_count=response.get("eval_count", 0)
        )
        
        # Cache the response
        if cache_manager and not generate_request.no_cache:
            await cache_manager.set(cache_key, result.json(), ttl=settings.cache_ttl)
            metrics.cache_misses.inc()
        
        return result
        
    except Exception as e:
        metrics.error_count.labels(type="generation_error").inc()
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.active_requests.dec()
        metrics.request_duration.labels(method="POST", endpoint="/generate").observe(time.time() - start_time)

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    api_key: bool = Depends(verify_api_key)
):
    """Chat completion endpoint with conversation context."""
    start_time = time.time()
    metrics.request_count.labels(method="POST", endpoint="/chat", status="processing").inc()
    metrics.active_requests.inc()
    
    try:
        # Format messages with agent profile if provided
        messages = chat_request.messages
        if chat_request.agent_profile:
            messages = add_agent_context_to_messages(messages, chat_request.agent_profile)
        
        # Call Ollama chat endpoint
        ollama_request = {
            "model": chat_request.model,
            "messages": messages,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "stream": False
        }
        
        response = await call_ollama_with_retry("/api/chat", ollama_request)
        
        return ChatResponse(
            message=response["message"],
            model=chat_request.model,
            created_at=datetime.utcnow().isoformat(),
            total_duration=response.get("total_duration", 0)
        )
        
    except Exception as e:
        metrics.error_count.labels(type="chat_error").inc()
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics.active_requests.dec()
        metrics.request_duration.labels(method="POST", endpoint="/chat").observe(time.time() - start_time)

@app.post("/batch/generate")
@limiter.limit("10/minute")
async def batch_generate(
    request: Request,
    batch_request: BatchGenerateRequest,
    api_key: bool = Depends(verify_api_key)
):
    """Batch generation for multiple agents."""
    start_time = time.time()
    metrics.batch_request_count.inc()
    
    try:
        # Process requests in parallel with concurrency limit
        semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        
        async def process_single(req: GenerateRequest):
            async with semaphore:
                return await generate(request, req, api_key)
        
        tasks = [process_single(req) for req in batch_request.requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful responses from errors
        results = []
        errors = []
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                errors.append({
                    "index": i,
                    "error": str(response)
                })
            else:
                results.append({
                    "index": i,
                    "response": response
                })
        
        return {
            "results": results,
            "errors": errors,
            "total": len(batch_request.requests),
            "successful": len(results),
            "failed": len(errors),
            "duration": time.time() - start_time
        }
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_ollama_with_retry(endpoint: str, data: dict) -> dict:
    """Call Ollama with retry logic."""
    try:
        response = await http_client.post(
            f"{settings.ollama_base_url}{endpoint}",
            json=data,
            timeout=settings.request_timeout
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout calling Ollama {endpoint}")
        raise HTTPException(status_code=504, detail="LLM request timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Ollama: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama: {e}")
        raise

async def check_ollama_health() -> bool:
    """Check if Ollama is healthy."""
    try:
        response = await http_client.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0
        )
        return response.status_code == 200
    except:
        return False

def format_prompt_with_profile(prompt: str, profile: AgentProfile) -> str:
    """Format prompt with agent profile information."""
    profile_context = f"""You are {profile.name}, a {profile.age}-year-old {profile.occupation}.

Personality traits:
- Openness: {profile.personality.openness}
- Conscientiousness: {profile.personality.conscientiousness}
- Extraversion: {profile.personality.extraversion}
- Agreeableness: {profile.personality.agreeableness}
- Neuroticism: {profile.personality.neuroticism}

Current state:
- Stress level: {profile.mental_state.stress_level}
- Life satisfaction: {profile.mental_state.life_satisfaction}
- Current emotion: {profile.mental_state.current_emotion}

Context: {profile.context}

"""
    
    return profile_context + prompt

def add_agent_context_to_messages(messages: List[Dict], profile: AgentProfile) -> List[Dict]:
    """Add agent context to chat messages."""
    system_message = {
        "role": "system",
        "content": f"""You are {profile.name}, a {profile.age}-year-old {profile.occupation}.
Your personality: Openness={profile.personality.openness}, Conscientiousness={profile.personality.conscientiousness}, 
Extraversion={profile.personality.extraversion}, Agreeableness={profile.personality.agreeableness}, 
Neuroticism={profile.personality.neuroticism}.
Current stress: {profile.mental_state.stress_level}, Life satisfaction: {profile.mental_state.life_satisfaction}.
Respond naturally based on your personality and current state."""
    }
    
    return [system_message] + messages

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)