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
            "keep_alive": "5m",
            "options": {
                # Keep responses concise while preserving enough context for RAG.
                "num_predict": 80,
                "temperature": 0.1,     # More deterministic
                "num_thread": 8,        # Max threads
                "num_ctx": 2048,
                "top_k": 1,             # Greedy decoding
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "stop": ["###"]
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

    def _is_refusal_like(self, text: str) -> bool:
        """Detect common 'insufficient context' style replies from the model."""
        low = (text or "").lower()
        patterns = [
            "cannot answer",
            "can't answer",
            "not enough information",
            "insufficient information",
            "context does not provide",
            "not specified in the context",
            "provided context"
        ]
        return any(p in low for p in patterns)

    def _fallback_summary_from_context(self, context: str) -> str:
        """
        Deterministic summary fallback for generic document questions when
        model drifts into refusal despite available context.
        """
        text = " ".join((context or "").split())
        if not text:
            return "I could not find relevant content in the knowledge base."
        # Keep short for voice and chat UI.
        return f"The document discusses: {text[:220].rstrip(' ,;:.')}."

    def generate(self, user_question, context):
        """Generate response using Ollama with RAG context."""
        if not context or not context.strip():
            return "I could not find relevant content in the knowledge base."
        if context.strip() == "No documents available in the knowledge base.":
            return "No documents are currently indexed in the knowledge base."

        system_prompt = (
            "Use only the provided context to answer in one short sentence. "
            "Start directly with the answer; do not add prefixes like 'Sure' or 'Here is'. "
            "If asked 'what is this document about', summarize the document topic from context. "
            "Do not claim the document is unspecified when context is present."
        )
        
        user_prompt = f"Context: {context}\n\nQuestion: {user_question}"

        models_to_try = [self.model]
        if self.fallback_model and self.fallback_model != self.model:
            models_to_try.append(self.fallback_model)

        last_error = None
        for idx, model_name in enumerate(models_to_try):
            try:
                if idx > 0:
                    print(f"[LLM] Primary failed, trying fallback model: {model_name}")
                answer = self._try_generate(model_name, user_prompt, system_prompt)
                if self._is_refusal_like(answer):
                    return self._fallback_summary_from_context(context)
                return answer
            except Exception as e:
                print(f"[LLM] Model '{model_name}' failed: {e}")
                last_error = e

        return f"Error communicating with Ollama (all models failed): {last_error}"
