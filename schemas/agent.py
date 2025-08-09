from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    personality: str
    feedback_style: str
    system_prompt: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Agent name cannot be empty')
        return v.strip()
    
    @validator('personality')
    def validate_personality(cls, v):
        if not v.strip():
            raise ValueError('Personality cannot be empty')
        return v.strip()
    
    @validator('feedback_style')
    def validate_feedback_style(cls, v):
        if not v.strip():
            raise ValueError('Feedback style cannot be empty')
        return v.strip()
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        if not v.strip():
            raise ValueError('System prompt cannot be empty')
        return v.strip()

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    feedback_style: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Agent name cannot be empty')
        return v.strip() if v else None
    
    @validator('personality')
    def validate_personality(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Personality cannot be empty')
        return v.strip() if v else None
    
    @validator('feedback_style')
    def validate_feedback_style(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Feedback style cannot be empty')
        return v.strip() if v else None
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        if v is not None and not v.strip():
            raise ValueError('System prompt cannot be empty')
        return v.strip() if v else None

class AgentResponse(AgentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total_count: int

# Updated Chat Message Schemas with Agent Context
class ChatMessageWithAgentCreate(BaseModel):
    user_id: int
    message: str
    response: Optional[str] = None
    agent_id: Optional[int] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @validator('response')
    def validate_response(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Response cannot be empty if provided')
        return v.strip() if v else None

class ChatMessageWithAgentResponse(BaseModel):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    message: str
    response: str
    context_used: Optional[str] = None
    created_at: datetime
    agent: Optional[AgentResponse] = None
    
    class Config:
        from_attributes = True

class ChatMessageWithAgentListResponse(BaseModel):
    messages: List[ChatMessageWithAgentResponse]
    total_count: int
    skip: int
    limit: int
