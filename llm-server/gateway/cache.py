"""
Cache management for LLM responses.
"""

import redis.asyncio as redis
import hashlib
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of LLM responses."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            
    async def health_check(self) -> bool:
        """Check if cache is healthy."""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
    
    def generate_key(self, model: str, prompt: str, temperature: float, 
                    agent_profile: Optional[Any] = None) -> str:
        """Generate cache key from request parameters."""
        key_parts = [
            model,
            prompt,
            str(temperature),
        ]
        
        if agent_profile:
            # Include relevant agent characteristics in cache key
            key_parts.extend([
                str(agent_profile.agent_id),
                str(agent_profile.personality.openness),
                str(agent_profile.personality.conscientiousness),
                str(agent_profile.personality.extraversion),
                str(agent_profile.personality.agreeableness),
                str(agent_profile.personality.neuroticism),
                str(agent_profile.mental_state.stress_level),
                str(agent_profile.mental_state.life_satisfaction),
            ])
        
        key_string = "|".join(key_parts)
        return f"llm:cache:{hashlib.sha256(key_string.encode()).hexdigest()}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return value.decode()
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL."""
        if not self.redis_client:
            return
            
        try:
            await self.redis_client.setex(key, ttl, value)
            logger.debug(f"Cached response for key: {key}")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache."""
        if not self.redis_client:
            return
            
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if not self.redis_client:
            return
            
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.error(f"Cache clear error: {e}")