from fastapi import APIRouter
from api.v1.endpoints import users, chat, ollama, agents

api_router = APIRouter()

# Include user endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include chat endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Include Ollama endpoints
api_router.include_router(ollama.router, prefix="/ollama", tags=["ollama"])

# Include agent endpoints
api_router.include_router(agents.router, prefix="/agents", tags=["agents"]) 