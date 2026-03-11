"""
Logging module for Voice RAG Pipeline
Logs all searches, responses, and system events
"""

import os
import json
from datetime import datetime


class RAGLogger:
    """Handles logging of all RAG interactions."""
    
    def __init__(self, log_dir="./logs"):
        """Initialize logger."""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log files
        self.search_log = os.path.join(log_dir, "searches.log")
        self.session_log = os.path.join(log_dir, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Initialize session
        self._log_session_start()
    
    def _log_session_start(self):
        """Log session start."""
        with open(self.session_log, 'w') as f:
            f.write(f"=== Voice RAG Session Started ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"{'='*50}\n\n")
    
    def log_search(self, question, context, response, model, duration):
        """
        Log a search interaction.
        
        Args:
            question (str): User's question
            context (str): Retrieved context
            response (str): LLM response
            model (str): Model used
            duration (float): Response time in seconds
        """
        timestamp = datetime.now().isoformat()
        
        # Log to searches.log (append mode)
        log_entry = {
            "timestamp": timestamp,
            "question": question,
            "model": model,
            "response": response,
            "duration_seconds": round(duration, 2),
            "context_length": len(context)
        }
        
        with open(self.search_log, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Log to session log (detailed)
        with open(self.session_log, 'a') as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"Question: {question}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Duration: {duration:.2f}s\n")
            f.write(f"Context Length: {len(context)} chars\n")
            f.write(f"Response: {response}\n")
            f.write(f"{'-'*50}\n\n")
    
    def log_error(self, error_type, error_message):
        """Log an error."""
        timestamp = datetime.now().isoformat()
        
        with open(self.session_log, 'a') as f:
            f.write(f"[{timestamp}] ERROR\n")
            f.write(f"Type: {error_type}\n")
            f.write(f"Message: {error_message}\n")
            f.write(f"{'-'*50}\n\n")
    
    def log_event(self, event_type, message):
        """Log a system event."""
        timestamp = datetime.now().isoformat()
        
        with open(self.session_log, 'a') as f:
            f.write(f"[{timestamp}] {event_type}\n")
            f.write(f"{message}\n")
            f.write(f"{'-'*50}\n\n")
