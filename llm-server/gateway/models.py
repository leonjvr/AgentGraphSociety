"""
Data models for the LLM Gateway API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PersonalityTraits(BaseModel):
    """Big Five personality traits."""
    openness: float = Field(..., ge=0, le=1)
    conscientiousness: float = Field(..., ge=0, le=1)
    extraversion: float = Field(..., ge=0, le=1)
    agreeableness: float = Field(..., ge=0, le=1)
    neuroticism: float = Field(..., ge=0, le=1)

class MentalState(BaseModel):
    """Agent's current mental state."""
    stress_level: float = Field(..., ge=0, le=1)
    life_satisfaction: float = Field(..., ge=0, le=1)
    current_emotion: str = "neutral"
    energy_level: float = Field(0.7, ge=0, le=1)

class AgentProfile(BaseModel):
    """Complete agent profile for context."""
    agent_id: int
    name: str
    age: int
    occupation: str
    personality: PersonalityTraits
    mental_state: MentalState
    context: Optional[str] = None
    relationship_context: Optional[Dict[str, Any]] = None

class GenerateRequest(BaseModel):
    """Text generation request."""
    model: str = Field(..., description="Model name (e.g., 'mistral:7b')")
    prompt: str = Field(..., description="Text prompt")
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(200, ge=1, le=2000)
    top_p: float = Field(0.9, ge=0, le=1)
    top_k: int = Field(40, ge=1, le=100)
    agent_profile: Optional[AgentProfile] = None
    no_cache: bool = Field(False, description="Bypass cache")
    metadata: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    """Text generation response."""
    response: str
    model: str
    created_at: str
    total_duration: int = 0
    load_duration: int = 0
    eval_duration: int = 0
    eval_count: int = 0
    cached: bool = False

class ChatMessage(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Chat completion request."""
    model: str = Field(..., description="Model name")
    messages: List[ChatMessage]
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(200, ge=1, le=2000)
    agent_profile: Optional[AgentProfile] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Chat completion response."""
    message: ChatMessage
    model: str
    created_at: str
    total_duration: int = 0
    cached: bool = False

class BatchGenerateRequest(BaseModel):
    """Batch generation request for multiple agents."""
    requests: List[GenerateRequest]
    parallel: bool = Field(True, description="Process in parallel")
    
class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    size: int
    parameter_count: str
    quantization: str
    family: str
    
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())