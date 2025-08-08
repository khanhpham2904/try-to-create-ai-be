from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import requests
import logging
import traceback
from database import get_db
import models
import schemas.chat as chat_schemas
import schemas.agent as agent_schemas
from crud.chat import ChatCRUD
from crud.user import UserCRUD
from crud.agent import AgentCRUD
from config.settings import settings
from services.ollama_service import ollama_service
from config.ollama_config import get_ollama_config
from services.dataset_service import dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/send", response_model=agent_schemas.ChatMessageWithAgentResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: agent_schemas.ChatMessageWithAgentCreate, 
    db: Session = Depends(get_db)
):
    """
    Send a message and get AI response using local Ollama LLM with optional agent and dataset context
    """
    try:
        logger.info(f"Sending message for user {message_data.user_id}")
        
        # Verify user exists
        user = UserCRUD.get_user_by_id(db, message_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get agent context if provided
        agent = None
        context_parts: List[str] = []
        if message_data.agent_id:
            agent = AgentCRUD.get_agent_by_id(db, message_data.agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            context_parts.append(
                f"Agent: {agent.name} | Personality: {agent.personality} | Style: {agent.feedback_style}"
            )
            logger.info(f"Using agent context: {agent.name}")
        
        # Compute dataset context for this query (best-effort)
        dataset_context: str | None = None
        try:
            dataset_context = dataset_service.get_relevant_context(message_data.message)  # type: ignore[attr-defined]
            if dataset_context:
                logger.info("Dataset context found and will be injected into prompt")
                # Store a compact preview in the DB context
                preview = " | ".join(dataset_context.splitlines()[:2])
                context_parts.append(f"Dataset: {preview}")
            else:
                logger.info("No dataset context found for this message")
        except Exception as dse:
            logger.warning(f"Dataset context unavailable: {dse}")
        
        # Use provided response if available, otherwise generate AI response using Ollama
        if message_data.response:
            ai_response = message_data.response
            logger.info(f"Using provided response for user {message_data.user_id}")
        else:
            # Check if Ollama is available
            if not ollama_service.check_server_health():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Ollama server is not available. Please ensure Ollama is running locally."
                )
            
            # Generate AI response using local Ollama model with agent + dataset context
            ai_response = generate_ollama_response_with_context(
                message_data.message, 
                agent,
                dataset_context=dataset_context
            )
        
        # Compose context_used string (if any)
        context_used = "\n".join(context_parts) if context_parts else None
        
        # Create the chat message in database
        db_message = ChatCRUD.create_chat_message_with_agent(
            db=db,
            user_id=message_data.user_id,
            agent_id=message_data.agent_id,
            message=message_data.message,
            response=ai_response,
            context_used=context_used
        )
        
        logger.info(f"Message sent successfully: ID {db_message.id}")
        return db_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/messages", response_model=chat_schemas.ChatMessageListResponse)
def get_user_messages(
    user_id: int = Query(..., description="User ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a user
    """
    try:
        logger.info(f"Getting messages for user {user_id}")
        
        # Verify user exists
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        messages = ChatCRUD.get_user_messages(db, user_id, skip, limit)
        total_count = len(messages)  # In a real app, you'd get total count separately
        
        return chat_schemas.ChatMessageListResponse(
            messages=messages,
            total_count=total_count,
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    user_id: int = Query(..., description="User ID to verify ownership"),
    db: Session = Depends(get_db)
):
    """
    Delete a specific message
    """
    try:
        logger.info(f"Deleting message {message_id} for user {user_id}")
        
        success = ChatCRUD.delete_chat_message(db, message_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or you don't have permission to delete it"
            )
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/messages", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_user_messages(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Delete all messages for a user
    """
    try:
        logger.info(f"Deleting all messages for user {user_id}")
        
        ChatCRUD.delete_all_user_messages(db, user_id)
        
        return {"message": "All messages deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting all messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/statistics", response_model=chat_schemas.ChatStatisticsResponse)
def get_chat_statistics(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get chat statistics for a user
    """
    try:
        logger.info(f"Getting chat statistics for user {user_id}")
        
        # Verify user exists
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        stats = ChatCRUD.get_chat_statistics(db, user_id)
        
        return chat_schemas.ChatStatisticsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

def generate_ollama_response_with_context(user_message: str, agent: models.Agent = None, *, dataset_context: str | None = None) -> str:
    """
    Generate AI response using local Ollama model with optional agent and dataset context.
    The dataset context, when provided, is appended to the system prompt with explicit instructions to use it.
    """
    try:
        config = get_ollama_config()
        
        # Check if Ollama server is running
        if not ollama_service.check_server_health():
            logger.error("Ollama server is not running")
            return config["connection_error_message"]
        
        # Check available models
        available_models = ollama_service.get_available_models()
        logger.info(f"Available models: {[model.get('name', 'unknown') for model in available_models]}")
        
        # Check if default model is available
        default_model = config["default_model"]
        model_names = [model.get('name', '') for model in available_models]
        
        if not model_names:
            logger.error("No models available in Ollama")
            return "No models are available in Ollama. Please install a model first."
        
        if default_model not in model_names:
            logger.warning(f"Default model '{default_model}' not found, using first available model")
            # Use the first available model instead
            default_model = model_names[0]
        
        # Prepare system prompt with agent and dataset context
        if agent:
            system_prompt = f"""You are {agent.name}, an AI assistant with the following characteristics:

Personality: {agent.personality}
Feedback Style: {agent.feedback_style}

{agent.system_prompt}

Always respond in character as {agent.name} with the specified personality and feedback style."""
        else:
            system_prompt = config["system_prompt"]
            logger.info("Using default system prompt")
        
        if dataset_context:
            guidance = (
                "\n\nWhen answering, prioritize and reference the following dataset context if it is relevant to the user's question. "
                "If it is not relevant, answer normally. Do not fabricate entries.\n\n" + dataset_context
            )
            system_prompt = system_prompt + guidance
            logger.info("Dataset context appended to system prompt")
        
        # Generate response using Ollama
        ai_response = ollama_service.generate_response(
            message=user_message,
            model=default_model,
            system_prompt=system_prompt,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            stream=False
        )
        
        logger.info(f"Ollama response generated successfully using model: {default_model}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating Ollama response: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error: {str(e)}"

def generate_ollama_response(user_message: str) -> str:
    """
    Generate AI response using local Ollama model (legacy function)
    """
    return generate_ollama_response_with_context(user_message, None) 