"""
LLM module for Ollama integration
Generates responses using local Ollama models
"""

import requests
from config import OLLAMA_URL, ACTIVE_MODEL, OLLAMA_MODEL_FALLBACK


class OllamaLLM:
    """
    Handles interaction with Ollama API for text generation.
    Supports multiple models with easy switching via config.
    """
    
    def __init__(self):
        """Initialize Ollama LLM client."""
        self.base_url = OLLAMA_URL
        self.model = ACTIVE_MODEL
        self.fallback_model = OLLAMA_MODEL_FALLBACK
        self.generate_url = f"{self.base_url}/api/generate"
        self.session = requests.Session()
        
        print(
            f"✓ Ollama LLM initialized "
            f"(primary: {self.model}, fallback: {self.fallback_model})"
        )
    
    def check_ollama_running(self):
        """Check if Ollama server is running."""
        try:
            response = self.session.get(self.base_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _build_payload(self, model_name, user_prompt, system_prompt):
        """Build Ollama request payload for a model."""
        return {
            "model": model_name,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                # Shorter responses reduce latency for both text and voice flows.
                "num_predict": 180,
                "temperature": 0.7,
                "stop": ["\n\n", "###", "Note:", "Additionally"]
            }
        }

    def _try_generate(self, model_name, user_prompt, system_prompt):
        """Try one model once and return response text or raise."""
        response = self.session.post(
            self.generate_url,
            json=self._build_payload(model_name, user_prompt, system_prompt),
            timeout=(5, 120)
        )
        response.raise_for_status()
        result = response.json()
        text = result.get("response", "").strip()
        if not text:
            raise RuntimeError(f"Model '{model_name}' returned empty response")
        return text

    def generate(self, user_question, context):
        """Generate response using Ollama with RAG context."""
        system_prompt = """You are a helpful assistant answering questions about documents. Use the provided context to answer the question. If the context contains relevant information, use it to give a complete helpful answer. If the answer is directly in the context, answer confidently without saying "the context says". Keep your answer to 3-4 sentences since it will be spoken aloud. Be natural and conversational — answer as if you already know this information."""
        
        user_prompt = f"Context: {context}\n\nQuestion: {user_question}"

        models_to_try = [self.model]
        if self.fallback_model and self.fallback_model != self.model:
            models_to_try.append(self.fallback_model)

        last_error = None
        for idx, model_name in enumerate(models_to_try):
            try:
                if idx > 0:
                    print(f"[LLM] Primary failed, trying fallback model: {model_name}")
                return self._try_generate(model_name, user_prompt, system_prompt)
            except Exception as e:
                print(f"[LLM] Model '{model_name}' failed: {e}")
                last_error = e

        return f"Error communicating with Ollama (all models failed): {last_error}"
