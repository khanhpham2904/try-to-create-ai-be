from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import models
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatCRUD:
    @staticmethod
    def create_chat_message(db: Session, user_id: int, message: str, response: str) -> Optional[models.ChatMessage]:
        """Create a new chat message"""
        try:
            logger.info(f"Creating chat message for user {user_id}")
            
            db_message = models.ChatMessage(
                user_id=user_id,
                message=message,
                response=response
            )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            logger.info(f"Chat message created successfully: ID {db_message.id}")
            return db_message
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating chat message: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating chat message: {e}")
            raise

    @staticmethod
    def create_chat_message_with_agent(db: Session, user_id: int, agent_id: int = None, message: str = None, response: str = None, context_used: str = None) -> Optional[models.ChatMessage]:
        """Create a new chat message with optional agent context"""
        try:
            logger.info(f"Creating chat message with agent for user {user_id}")
            
            db_message = models.ChatMessage(
                user_id=user_id,
                agent_id=agent_id,
                message=message,
                response=response,
                context_used=context_used
            )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            logger.info(f"Chat message with agent created successfully: ID {db_message.id}")
            return db_message
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating chat message with agent: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating chat message with agent: {e}")
            raise

    @staticmethod
    def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.ChatMessage]:
        """Get chat messages for a specific user with pagination"""
        try:
            messages = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.user_id == user_id)\
                .order_by(models.ChatMessage.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
            
            logger.info(f"Retrieved {len(messages)} chat messages for user {user_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting chat messages for user {user_id}: {e}")
            return []

    @staticmethod
    def get_chat_message_by_id(db: Session, message_id: int, user_id: int) -> Optional[models.ChatMessage]:
        """Get a specific chat message by ID (only if it belongs to the user)"""
        try:
            message = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.id == message_id, models.ChatMessage.user_id == user_id)\
                .first()
            
            return message
            
        except Exception as e:
            logger.error(f"Error getting chat message {message_id}: {e}")
            return None

    @staticmethod
    def delete_chat_message(db: Session, message_id: int, user_id: int) -> bool:
        """Delete a chat message (only if it belongs to the user)"""
        try:
            message = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.id == message_id, models.ChatMessage.user_id == user_id)\
                .first()
            
            if not message:
                return False
            
            db.delete(message)
            db.commit()
            
            logger.info(f"Chat message {message_id} deleted successfully for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting chat message {message_id}: {e}")
            raise

    @staticmethod
    def delete_all_user_messages(db: Session, user_id: int) -> bool:
        """Delete all chat messages for a specific user"""
        try:
            deleted_count = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.user_id == user_id)\
                .delete()
            
            db.commit()
            
            logger.info(f"Deleted {deleted_count} chat messages for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting all chat messages for user {user_id}: {e}")
            raise

    @staticmethod
    def get_chat_statistics(db: Session, user_id: int) -> dict:
        """Get chat statistics for a user"""
        try:
            total_messages = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.user_id == user_id)\
                .count()
            
            # Get the first and last message dates
            first_message = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.user_id == user_id)\
                .order_by(models.ChatMessage.created_at.asc())\
                .first()
            
            last_message = db.query(models.ChatMessage)\
                .filter(models.ChatMessage.user_id == user_id)\
                .order_by(models.ChatMessage.created_at.desc())\
                .first()
            
            stats = {
                "total_messages": total_messages,
                "first_message_date": first_message.created_at if first_message else None,
                "last_message_date": last_message.created_at if last_message else None
            }
            
            logger.info(f"Retrieved chat statistics for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting chat statistics for user {user_id}: {e}")
            return {
                "total_messages": 0,
                "first_message_date": None,
                "last_message_date": None
            } 