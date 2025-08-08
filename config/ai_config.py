"""
AI Model Configuration
Replace these values with your own model and API settings
"""

# AI Model Configuration
AI_CONFIG = {
    # API Settings
    "api_url": "https://openrouter.ai/api/v1/chat/completions",  # Replace with your API endpoint
    "api_key": "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",  # Replace with your API key
    "model_name": "qwen/qwen3-30b-a3b-instruct-2507",  # Replace with your model name
    
    # Request Settings
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    
    # System Prompt
    "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions.",
    
    # Timeout Settings
    "timeout": 60,  # seconds
    
    # Error Messages
    "timeout_message": "I apologize, but I'm experiencing a timeout. Please try again in a moment.",
    "api_error_message": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
    "general_error_message": "I apologize, but I encountered an error while processing your request.",
}

# Alternative AI Providers (uncomment and configure as needed)
# AI_CONFIG = {
#     "api_url": "https://api.anthropic.com/v1/messages",  # Claude API
#     "api_key": "your-anthropic-key-here",
#     "model_name": "claude-3-sonnet-20240229",
#     "temperature": 0.7,
#     "max_tokens": 1000,
#     "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions.",
#     "timeout": 60,
#     "timeout_message": "I apologize, but I'm experiencing a timeout. Please try again in a moment.",
#     "api_error_message": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
#     "general_error_message": "I apologize, but I encountered an error while processing your request.",
# }

# AI_CONFIG = {
#     "api_url": "https://api.deepseek.com/v1/chat/completions",  # DeepSeek API
#     "api_key": "your-deepseek-key-here",
#     "model_name": "deepseek-chat",
#     "temperature": 0.7,
#     "max_tokens": 1000,
#     "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions.",
#     "timeout": 60,
#     "timeout_message": "I apologize, but I'm experiencing a timeout. Please try again in a moment.",
#     "api_error_message": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
#     "general_error_message": "I apologize, but I encountered an error while processing your request.",
# }
