from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
import schemas.user as user_schemas
from crud.user import UserCRUD
from crud.chat import ChatCRUD
from database import get_db
from utils.security import create_access_token, verify_token
from datetime import timedelta
import logging
import traceback
import redis
import pickle

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory blacklist for demonstration
blacklisted_tokens = set()

# Redis configuration (same as in chat.py)
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False,  # Keep as bytes for pickle
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test Redis connection
    redis_client.ping()
    logger.info("✅ Redis connection established in users.py")
except Exception as e:
    logger.warning(f"❌ Redis connection failed in users.py: {e}")
    redis_client = None

def get_redis_key(user_id: int, message_id: int = None) -> str:
    """Generate Redis key for chat messages"""
    if message_id:
        return f"chat:user:{user_id}:message:{message_id}"
    return f"chat:user:{user_id}:messages"

def cache_chat_message(user_id: int, message) -> bool:
    """Cache a chat message in Redis"""
    if not redis_client:
        return False
    
    try:
        # Cache individual message
        message_key = get_redis_key(user_id, message.id)
        message_data = {
            'id': message.id,
            'user_id': message.user_id,
            'message': message.message,
            'response': message.response,
            'created_at': message.created_at.isoformat()
        }
        redis_client.setex(message_key, 3600, pickle.dumps(message_data))  # 1 hour TTL
        
        # Add to sorted set for chronological ordering
        sorted_set_key = get_redis_key(user_id)
        redis_client.zadd(sorted_set_key, {pickle.dumps(message_data): message.created_at.timestamp()})
        redis_client.expire(sorted_set_key, 3600)  # 1 hour TTL
        
        logger.info(f"✅ Cached message {message.id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to cache message: {e}")
        return False

def cache_user_messages_on_login(user_id: int, db: Session) -> dict:
    """Cache user's messages in Redis when they log in"""
    try:
        logger.info(f"🔄 Caching messages for user {user_id} on login")
        
        if not redis_client:
            logger.warning("❌ Redis not available, skipping message caching")
            return {"cached": False, "reason": "Redis not available"}
        
        # Get user's recent messages (last 100 messages)
        messages = ChatCRUD.get_chat_messages_by_user(db, user_id, skip=0, limit=100)
        
        if not messages:
            logger.info(f"📭 No messages found for user {user_id}")
            return {"cached": True, "messages_count": 0, "reason": "No messages to cache"}
        
        # Cache each message
        cached_count = 0
        for message in messages:
            if cache_chat_message(user_id, message):
                cached_count += 1
        
        logger.info(f"✅ Successfully cached {cached_count}/{len(messages)} messages for user {user_id}")
        
        return {
            "cached": True,
            "messages_count": cached_count,
            "total_messages": len(messages),
            "cache_status": "warmed"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to cache messages for user {user_id}: {e}")
        return {"cached": False, "reason": str(e)}

@router.post("/", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    """
    try:
        logger.info(f"Attempting to create user: {user.email}")
        db_user = UserCRUD.create_user(db, user)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logger.info(f"User created successfully: {user.email}")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=List[user_schemas.UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with pagination
    """
    try:
        users = UserCRUD.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{user_id}", response_model=user_schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID
    """
    try:
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{user_id}", response_model=user_schemas.UserResponse)
def update_user(user_id: int, user_update: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    Update user information
    """
    try:
        user = UserCRUD.update_user(db, user_id, user_update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user
    """
    try:
        success = UserCRUD.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=user_schemas.LoginResponse)
def login(user_credentials: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token with user data
    """
    try:
        user = UserCRUD.authenticate_user(db, user_credentials.email, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Cache user's messages on successful login
        cache_result = cache_user_messages_on_login(user.id, db)
        logger.info(f"User {user.id} logged in. Cache result: {cache_result}")

        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": user,
            "cache_info": cache_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 

@router.post("/logout")
def logout(Authorization: str = Header(...)):
    """
    Logout user by blacklisting the JWT token
    """
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = Authorization.split(" ", 1)[1]
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    blacklisted_tokens.add(token)
    return {"detail": "Successfully logged out"}

@router.post("/{user_id}/warm-cache", response_model=dict)
def warm_user_cache_on_demand(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually warm up Redis cache for a user by loading their recent messages
    This can be called after login or when cache needs to be refreshed
    """
    try:
        logger.info(f"🔄 Manually warming cache for user {user_id}")
        
        # Verify user exists
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cache user's messages
        cache_result = cache_user_messages_on_login(user_id, db)
        
        logger.info(f"✅ Cache warming completed for user {user_id}: {cache_result}")
        
        return {
            "success": cache_result["cached"],
            "user_id": user_id,
            "cache_info": cache_result,
            "message": "Cache warming completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error warming cache for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 