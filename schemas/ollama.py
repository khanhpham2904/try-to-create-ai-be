"""
Ollama API Schemas
Pydantic models for Ollama API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ModelInfo(BaseModel):
    """Model information"""
    name: str
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None
    info: Optional[Dict[str, Any]] = None
    valid: bool = True

class ModelDetail(BaseModel):
    """Detailed model information"""
    name: str
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    info: Optional[Dict[str, Any]] = None
    valid: bool = True

class PullModelRequest(BaseModel):
    """Request to pull a model"""
    name: str = Field(..., description="Name of the model to pull")

class CreateModelRequest(BaseModel):
    """Request to create a custom model"""
    name: str = Field(..., description="Name of the custom model")
    base_model: str = Field(..., description="Base model to use")
    modelfile_content: str = Field(..., description="Modelfile content")

class GenerateRequest(BaseModel):
    """Request to generate AI response"""
    message: str = Field(..., description="User message")
    model: Optional[str] = Field(None, description="Model to use (uses default if not specified)")
    system_prompt: Optional[str] = Field(None, description="System prompt (uses default if not specified)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=8192, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream the response")

class ConversationMessage(BaseModel):
    """Conversation message"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")

class GenerateWithContextRequest(BaseModel):
    """Request to generate AI response with conversation history"""
    message: str = Field(..., description="Current user message")
    conversation_history: List[ConversationMessage] = Field(..., description="Previous conversation messages")
    model: Optional[str] = Field(None, description="Model to use (uses default if not specified)")
    system_prompt: Optional[str] = Field(None, description="System prompt (uses default if not specified)")

class GenerateResponse(BaseModel):
    """AI response"""
    response: str = Field(..., description="Generated AI response")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(..., description="Token usage information")

class OllamaHealthResponse(BaseModel):
    """Ollama health check response"""
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    server_info: Dict[str, Any] = Field(..., description="Server information")
    base_url: str = Field(..., description="Ollama server base URL")

class OllamaConfigResponse(BaseModel):
    """Ollama configuration response"""
    base_url: str = Field(..., description="Ollama server base URL")
    default_model: str = Field(..., description="Default model name")
    available_models: List[str] = Field(..., description="List of available models")
    temperature: float = Field(..., description="Default temperature")
    max_tokens: int = Field(..., description="Default max tokens")
    timeout: int = Field(..., description="Request timeout in seconds")
