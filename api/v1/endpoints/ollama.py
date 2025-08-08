"""
Ollama API Endpoints
Manage local Ollama models and LLM functionality
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from database import get_db
from services.ollama_service import ollama_service
from config.ollama_config import get_ollama_config, validate_model, get_model_info
import schemas.ollama as ollama_schemas

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=Dict[str, Any])
def check_ollama_health():
    """
    Check if Ollama server is running and healthy
    """
    try:
        is_healthy = ollama_service.check_server_health()
        server_info = ollama_service.get_server_info()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "server_info": server_info,
            "base_url": ollama_service.base_url
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama service unavailable: {str(e)}"
        )

@router.get("/models", response_model=List[ollama_schemas.ModelInfo])
def get_available_models():
    """
    Get list of available Ollama models
    """
    try:
        models = ollama_service.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )

@router.get("/models/{model_name}", response_model=ollama_schemas.ModelDetail)
def get_model_detail(model_name: str):
    """
    Get detailed information about a specific model
    """
    try:
        model_info = ollama_service.get_model_info(model_name)
        return model_info
    except Exception as e:
        logger.error(f"Failed to get model info for {model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )

@router.post("/models/pull", response_model=Dict[str, Any])
def pull_model(model_data: ollama_schemas.PullModelRequest):
    """
    Pull a model from Ollama library
    """
    try:
        if not validate_model(model_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model {model_data.name} is not supported"
            )
        
        result = ollama_service.pull_model(model_data.name)
        return {
            "message": f"Model {model_data.name} pulled successfully",
            "details": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pull model {model_data.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull model: {str(e)}"
        )

@router.delete("/models/{model_name}", response_model=Dict[str, str])
def delete_model(model_name: str):
    """
    Delete a model from Ollama
    """
    try:
        success = ollama_service.delete_model(model_name)
        if success:
            return {"message": f"Model {model_name} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete model {model_name}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model {model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete model: {str(e)}"
        )

@router.post("/models/create", response_model=Dict[str, str])
def create_custom_model(model_data: ollama_schemas.CreateModelRequest):
    """
    Create a custom model using a Modelfile
    """
    try:
        success = ollama_service.create_custom_model(
            model_data.name,
            model_data.base_model,
            model_data.modelfile_content
        )
        
        if success:
            return {"message": f"Custom model {model_data.name} created successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create custom model {model_data.name}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create custom model {model_data.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom model: {str(e)}"
        )

@router.post("/generate", response_model=ollama_schemas.GenerateResponse)
def generate_response(request: ollama_schemas.GenerateRequest):
    """
    Generate AI response using local Ollama model
    """
    try:
        # Check if Ollama is healthy
        if not ollama_service.check_server_health():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama server is not available"
            )
        
        # Generate response
        response = ollama_service.generate_response(
            message=request.message,
            model=request.model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        return ollama_schemas.GenerateResponse(
            response=response,
            model=request.model or ollama_service.config["default_model"],
            usage={
                "prompt_tokens": len(request.message.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(request.message.split()) + len(response.split())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

@router.post("/generate/context", response_model=ollama_schemas.GenerateResponse)
def generate_with_context(request: ollama_schemas.GenerateWithContextRequest):
    """
    Generate AI response with conversation history context
    """
    try:
        # Check if Ollama is healthy
        if not ollama_service.check_server_health():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama server is not available"
            )
        
        # Generate response with context
        response = ollama_service.generate_with_context(
            message=request.message,
            conversation_history=request.conversation_history,
            model=request.model,
            system_prompt=request.system_prompt
        )
        
        return ollama_schemas.GenerateResponse(
            response=response,
            model=request.model or ollama_service.config["default_model"],
            usage={
                "prompt_tokens": len(request.message.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(request.message.split()) + len(response.split())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate response with context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

@router.get("/config", response_model=Dict[str, Any])
def get_ollama_config():
    """
    Get current Ollama configuration
    """
    try:
        config = get_ollama_config()
        # Remove sensitive information
        if "api_key" in config:
            del config["api_key"]
        return config
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )

@router.get("/server-info", response_model=Dict[str, Any])
def get_server_info():
    """
    Get Ollama server information
    """
    try:
        server_info = ollama_service.get_server_info()
        return server_info
    except Exception as e:
        logger.error(f"Failed to get server info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get server info: {str(e)}"
        )
