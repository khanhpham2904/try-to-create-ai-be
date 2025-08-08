"""
Ollama Local LLM Configuration
Configure your local Ollama models and settings
"""

import os
from typing import Dict, Any

# Ollama Configuration
OLLAMA_CONFIG = {
    # Ollama Server Settings
    "base_url": "http://localhost:11434",  # Default Ollama server URL
    "api_endpoint": "/api/chat",  # Ollama chat API endpoint
    "generate_endpoint": "/api/generate",  # Ollama generate API endpoint
    
    # Model Settings
    "default_model": "llama3.2:3b",  # Default model to use (based on available model)
    "available_models": [
        "llama3.2",
        "llama3.2:3b",
        "llama3.2:7b", 
        "llama3.2:13b",
        "llama3.2:70b",
        "mistral",
        "mistral:7b",
        "mistral:instruct",
        "codellama",
        "codellama:7b",
        "codellama:13b",
        "codellama:34b",
        "qwen2",
        "qwen2:0.5b",
        "qwen2:1.5b",
        "qwen2:7b",
        "qwen2:72b",
        "phi3",
        "phi3:mini",
        "phi3:medium",
        "phi3:large",
        "gemma2",
        "gemma2:2b",
        "gemma2:9b",
        "neural-chat",
        "orca-mini",
        "llama2",
        "llama2:7b",
        "llama2:13b",
        "llama2:70b",
    ],
    
    # Generation Parameters
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "max_tokens": 2048,
    "stop": [],  # Stop sequences
    
    # System Prompt
    "system_prompt": """You are a helpful AI assistant. You provide clear, accurate, and helpful responses to user questions. 
    You are running locally on Ollama and can help with various tasks including:
    - Answering questions
    - Writing and editing text
    - Code generation and debugging
    - Analysis and explanations
    - Creative writing
    - Problem solving
    
    Always be helpful, accurate, and friendly in your responses.""",
    
    # Timeout Settings
    "timeout": 120,  # seconds (longer for local models)
    "request_timeout": 60,  # seconds for individual requests
    
    # Error Messages
    "timeout_message": "I apologize, but the response is taking longer than expected. Please try again.",
    "model_not_found_message": "The requested model is not available. Please check if it's installed in Ollama.",
    "connection_error_message": "Unable to connect to Ollama. Please ensure Ollama is running locally.",
    "general_error_message": "I apologize, but I encountered an error while processing your request.",
    
    # Model Information
    "model_info": {
        "llama3.2": {
            "description": "Meta's latest Llama model with improved performance",
            "parameters": "3B-70B",
            "recommended": True
        },
        "mistral": {
            "description": "Mistral AI's powerful open model",
            "parameters": "7B",
            "recommended": True
        },
        "codellama": {
            "description": "Specialized model for code generation",
            "parameters": "7B-34B",
            "recommended": True
        },
        "qwen2": {
            "description": "Alibaba's Qwen2 model series",
            "parameters": "0.5B-72B",
            "recommended": True
        },
        "phi3": {
            "description": "Microsoft's Phi-3 model family",
            "parameters": "Mini-Large",
            "recommended": True
        },
        "gemma2": {
            "description": "Google's Gemma2 model",
            "parameters": "2B-9B",
            "recommended": True
        }
    }
}

# Environment-specific overrides
def get_ollama_config() -> Dict[str, Any]:
    """Get Ollama configuration with environment overrides"""
    config = OLLAMA_CONFIG.copy()
    
    # Override with environment variables if present
    if os.getenv("OLLAMA_BASE_URL"):
        config["base_url"] = os.getenv("OLLAMA_BASE_URL")
    
    if os.getenv("OLLAMA_DEFAULT_MODEL"):
        config["default_model"] = os.getenv("OLLAMA_DEFAULT_MODEL")
    
    if os.getenv("OLLAMA_TIMEOUT"):
        config["timeout"] = int(os.getenv("OLLAMA_TIMEOUT"))
    
    return config

# Model validation
def validate_model(model_name: str) -> bool:
    """Validate if a model name is supported"""
    return model_name in OLLAMA_CONFIG["available_models"]

def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about a specific model"""
    return OLLAMA_CONFIG["model_info"].get(model_name, {
        "description": "Custom model",
        "parameters": "Unknown",
        "recommended": False
    })
