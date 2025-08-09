from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Chat Message Schemas
class ChatMessageBase(BaseModel):
    message: str
    response: str

class ChatMessageCreate(BaseModel):
    user_id: int
    message: str
    response: Optional[str] = None
    
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

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessageListResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int
    skip: int
    limit: int

class ChatStatisticsResponse(BaseModel):
    total_messages: int
    first_message_date: Optional[datetime] = None
    last_message_date: Optional[datetime] = None 