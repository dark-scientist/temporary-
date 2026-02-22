"""
LLM module for Ollama integration
Generates responses using local Ollama models
"""

import requests
from config import OLLAMA_URL, OLLAMA_MODEL


class OllamaLLM:
    """
    Handles interaction with Ollama API for text generation.
    Supports multiple models with easy switching via config.
    """
    
    def __init__(self):
        """Initialize Ollama LLM client."""
        self.base_url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.generate_url = f"{self.base_url}/api/generate"
        
        print(f"✓ Ollama LLM initialized (model: {self.model})")
    
    def check_ollama_running(self):
        """Check if Ollama server is running."""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, user_question, context):
        """Generate response using Ollama with RAG context."""
        system_prompt = (
            "You are a helpful assistant. Answer only using the provided context. "
            "Keep your answer to 2-3 sentences since it will be spoken aloud. "
            "Be natural and conversational."
        )
        
        user_prompt = f"Context: {context}\n\nQuestion: {user_question}"
        
        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=180
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.Timeout:
            return "Sorry, the response took too long. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
