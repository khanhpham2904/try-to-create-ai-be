from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import models
import schemas.user as user_schemas
from utils.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
        """Get user by ID"""
        try:
            return db.query(models.User).filter(models.User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        """Get user by email"""
        try:
            return db.query(models.User).filter(models.User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        """Get all users with pagination"""
        try:
            return db.query(models.User).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    @staticmethod
    def create_user(db: Session, user: user_schemas.UserCreate) -> Optional[models.User]:
        """Create a new user"""
        try:
            logger.info(f"Starting user creation for: {user.email}")
            
            # Check if user already exists
            logger.info("Checking if user already exists...")
            existing_user = UserCRUD.get_user_by_email(db, user.email)
            if existing_user:
                logger.warning(f"User with email {user.email} already exists")
                return None
            
            # Hash the password
            logger.info("Hashing password...")
            hashed_password = get_password_hash(user.password)
            logger.info("Password hashed successfully")
            
            # Create user object
            logger.info("Creating user object...")
            db_user = models.User(
                email=user.email,
                full_name=user.full_name,
                hashed_password=hashed_password
            )
            logger.info("User object created")
            
            # Add to database
            logger.info("Adding user to database...")
            db.add(db_user)
            logger.info("User added to session")
            
            # Commit transaction
            logger.info("Committing transaction...")
            db.commit()
            logger.info("Transaction committed")
            
            # Refresh object
            logger.info("Refreshing user object...")
            db.refresh(db_user)
            logger.info("User object refreshed")
            
            logger.info(f"User created successfully: {user.email}")
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating user: {e}")
            logger.error(f"Integrity error details: {str(e)}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: user_schemas.UserUpdate) -> Optional[models.User]:
        """Update user information"""
        try:
            db_user = UserCRUD.get_user_by_id(db, user_id)
            if not db_user:
                return None
            
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User updated successfully: {user_id}")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        try:
            db_user = UserCRUD.get_user_by_id(db, user_id)
            if not db_user:
                return False
            
            db.delete(db_user)
            db.commit()
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
        """Authenticate user with email and password"""
        try:
            user = UserCRUD.get_user_by_email(db, email)
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None 