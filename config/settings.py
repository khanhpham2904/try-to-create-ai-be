import os
from typing import List

class Settings:
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://ecommerce:ecommerce@127.0.0.1:3306/chatbotapp"
    )
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat App API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI backend for the Chat Application"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # For development - remove in production
    ]
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Password settings
    PASSWORD_MIN_LENGTH: int = 6
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Dataset settings
    DATASET_ENABLED: bool = os.getenv("DATASET_ENABLED", "true").lower() in ("1", "true", "yes")
    DATASET_CSV_PATH: str | None = os.getenv(
        "DATASET_CSV_PATH",
        # Default to the user's provided path; can be overridden by env
        r"C:\Users\khanh\Downloads\archive\spotify_history.csv"
    )

settings = Settings() 