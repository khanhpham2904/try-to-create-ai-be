#!/usr/bin/env python3
"""
Startup script for the Chat App Backend
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pymysql',
        'pydantic',
        'passlib',
        'python-jose',
        'email-validator'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_imports():
    """Check if all imports work"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from config.settings import settings
        from database import get_db, init_db
        import models
        import schemas.user
        from utils.security import get_password_hash, verify_password
        from crud.user import UserCRUD
        from middleware.logging import LoggingMiddleware
        from api.v1.api import api_router
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        from main import app
        
        print("🚀 Starting Chat App Backend...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Chat App Backend Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check imports
    if not check_imports():
        print("\n❌ Import check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("=" * 40)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 