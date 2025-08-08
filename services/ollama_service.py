"""
Ollama Service for Local LLM Integration
Handles communication with local Ollama server
"""

import requests
import logging
import json
import time
from typing import Dict, Any, List, Optional, Generator
from config.ollama_config import get_ollama_config, validate_model, get_model_info

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.config = get_ollama_config()
        self.base_url = self.config["base_url"]
        self.session = requests.Session()
        self.session.timeout = self.config["request_timeout"]
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make HTTP request to Ollama API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama server")
            raise ConnectionError("Unable to connect to Ollama. Please ensure Ollama is running.")
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            raise TimeoutError("Request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def check_server_health(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self._make_request("/api/tags")
            return True
        except Exception as e:
            logger.error(f"Ollama server health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = self._make_request("/api/tags")
            models = response.get("models", [])
            
            # Add additional model information
            for model in models:
                model_name = model.get("name", "")
                model["info"] = get_model_info(model_name)
                model["valid"] = validate_model(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama library"""
        try:
            data = {"name": model_name}
            response = self._make_request("/api/pull", method="POST", data=data)
            return response
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise
    
    def generate_response(
        self, 
        message: str, 
        model: str = None,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> str:
        """
        Generate AI response using Ollama
        
        Args:
            message: User message
            model: Model name (uses default if None)
            system_prompt: System prompt (uses default if None)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        if not model:
            model = self.config["default_model"]
        
        if not system_prompt:
            system_prompt = self.config["system_prompt"]
        
        if temperature is None:
            temperature = self.config["temperature"]
        
        if max_tokens is None:
            max_tokens = self.config["max_tokens"]
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": self.config["top_p"],
                "top_k": self.config["top_k"],
                "repeat_penalty": self.config["repeat_penalty"],
                "num_predict": max_tokens
            }
        }
        
        try:
            if stream:
                return self._generate_streaming_response(payload)
            else:
                return self._generate_single_response(payload)
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return self.config["general_error_message"]
    
    def _generate_single_response(self, payload: Dict[str, Any]) -> str:
        """Generate single response (non-streaming)"""
        try:
            response = self._make_request("/api/chat", method="POST", data=payload)
            
            if "message" in response:
                return response["message"]["content"]
            else:
                logger.error(f"Unexpected response format: {response}")
                return self.config["general_error_message"]
                
        except Exception as e:
            logger.error(f"Single response generation failed: {e}")
            return self.config["general_error_message"]
    
    def _generate_streaming_response(self, payload: Dict[str, Any]) -> str:
        """Generate streaming response"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=self.config["timeout"]
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if "message" in data:
                            content = data["message"]["content"]
                            full_response += content
                    except json.JSONDecodeError:
                        continue
            
            return full_response
            
        except Exception as e:
            logger.error(f"Streaming response generation failed: {e}")
            return self.config["general_error_message"]
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        try:
            # Get model details from Ollama
            response = self._make_request(f"/api/show", method="POST", data={"name": model_name})
            
            # Add our custom info
            custom_info = get_model_info(model_name)
            response.update(custom_info)
            
            return response
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return get_model_info(model_name)
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model from Ollama"""
        try:
            self._make_request("/api/delete", method="POST", data={"name": model_name})
            return True
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False
    
    def create_custom_model(self, model_name: str, base_model: str, modelfile_content: str) -> bool:
        """Create a custom model using a Modelfile"""
        try:
            data = {
                "name": model_name,
                "modelfile": modelfile_content
            }
            self._make_request("/api/create", method="POST", data=data)
            return True
        except Exception as e:
            logger.error(f"Failed to create custom model {model_name}: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get Ollama server information"""
        try:
            return self._make_request("/api/version")
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return {}
    
    def generate_with_context(
        self, 
        message: str, 
        conversation_history: List[Dict[str, str]],
        model: str = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate response with conversation history context
        
        Args:
            message: Current user message
            conversation_history: List of previous messages [{"role": "user", "content": "..."}, ...]
            model: Model name
            system_prompt: System prompt
            
        Returns:
            Generated response
        """
        if not model:
            model = self.config["default_model"]
        
        if not system_prompt:
            system_prompt = self.config["system_prompt"]
        
        # Prepare messages with history
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config["temperature"],
                "top_p": self.config["top_p"],
                "top_k": self.config["top_k"],
                "repeat_penalty": self.config["repeat_penalty"],
                "num_predict": self.config["max_tokens"]
            }
        }
        
        try:
            response = self._make_request("/api/chat", method="POST", data=payload)
            
            if "message" in response:
                return response["message"]["content"]
            else:
                return self.config["general_error_message"]
                
        except Exception as e:
            logger.error(f"Context generation failed: {e}")
            return self.config["general_error_message"]

# Global Ollama service instance
ollama_service = OllamaService()
