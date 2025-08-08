#!/usr/bin/env python3
"""
Ollama Setup Script
Helps configure and test Ollama integration
"""

import requests
import json
import sys
import os
from pathlib import Path

def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print("❌ Ollama server responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server is not running")
        print("   Please start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama server: {e}")
        return False

def get_available_models():
    """Get list of available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                print(f"✅ Found {len(models)} available models:")
                for model in models:
                    print(f"   - {model.get('name', 'Unknown')}")
                return models
            else:
                print("⚠️  No models found. You may need to pull a model:")
                print("   ollama pull llama3.2:3b")
                return []
        else:
            print("❌ Failed to get models")
            return []
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return []

def test_model_generation():
    """Test model generation"""
    try:
        payload = {
            "model": "llama3.2:3b",
            "messages": [
                {"role": "user", "content": "Hello! Can you say hi back?"}
            ],
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("message", {}).get("content", "")
            print("✅ Model generation test successful")
            print(f"   Response: {ai_response[:100]}...")
            return True
        else:
            print(f"❌ Model generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing model generation: {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/v1/ollama/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API health check successful")
        else:
            print("❌ Backend API health check failed")
            return False
        
        # Test models endpoint
        response = requests.get("http://localhost:8000/api/v1/ollama/models", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API models endpoint working")
        else:
            print("❌ Backend API models endpoint failed")
            return False
        
        # Test generation endpoint
        payload = {
            "message": "Hello! This is a test.",
            "model": "llama3.2:3b"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/ollama/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Backend API generation endpoint working")
            return True
        else:
            print(f"❌ Backend API generation failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Please start the backend with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend API: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:7b
OLLAMA_TIMEOUT=120

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost/chatapp

# Server Configuration
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=ChatApp with Ollama
VERSION=1.0.0
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
        print("   Please update the DATABASE_URL with your actual database credentials")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🦙 Ollama Setup Script")
    print("=" * 50)
    
    # Check if Ollama is running
    if not check_ollama_server():
        print("\n📋 Setup Instructions:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull llama3.2:3b")
        print("4. Run this script again")
        return
    
    # Get available models
    models = get_available_models()
    
    # Test model generation
    if models:
        test_model_generation()
    
    # Create .env file
    create_env_file()
    
    # Test backend API (if backend is running)
    print("\n🔧 Testing Backend API...")
    test_backend_api()
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Start the backend: python main.py")
    print("2. Test the frontend: cd ../ChatApp && npm start")
    print("3. Try different models: ollama pull llama3.2:7b")
    print("4. Customize configuration in config/ollama_config.py")

if __name__ == "__main__":
    main()
