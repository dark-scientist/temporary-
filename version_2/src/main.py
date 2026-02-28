"""
Voice RAG Pipeline - Main Entry Point with Model Selection
"""

import sys
import requests
from config import OLLAMA_URL


class ModelManager:
    """Manages Ollama model selection."""
    
    def __init__(self):
        self.ollama_url = OLLAMA_URL
        self.available_models = self.get_available_models()
    
    def get_available_models(self):
        """Get list of available models from Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            print(f"⚠️ Could not fetch models: {e}")
            return []
    
    def list_models(self):
        """Display all available models."""
        print("\n" + "="*60)
        print("AVAILABLE OLLAMA MODELS")
        print("="*60)
        
        if not self.available_models:
            print("No models found. Pull models using: ollama pull <model>")
            return
        
        for i, model in enumerate(self.available_models, 1):
            desc = ""
            if "llama3.2:3b" in model:
                desc = " (Fastest - ~30-40s)"
            elif "qwen2.5:7b" in model:
                desc = " (Balanced - ~70-80s)"
            elif "deepseek-r1:7b" in model:
                desc = " (Best Quality - ~150-160s)"
            
            print(f"{i}. {model}{desc}")
        
        print("="*60 + "\n")
    
    def select_model_interactive(self):
        """Interactive model selection."""
        if not self.available_models:
            return None
        
        while True:
            try:
                choice = input("Select model number (or 'q' to quit): ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(self.available_models):
                    return self.available_models[idx]
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a number.")


def update_config(model_name):
    """Update config.py with selected model."""
    config_path = './src/config.py'
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('OLLAMA_MODEL = '):
                lines[i] = f'OLLAMA_MODEL = "{model_name}"  # Selected model'
                break
        
        with open(config_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return True
    except Exception as e:
        print(f"⚠️ Could not update config: {e}")
        return False


def main():
    """Main application entry point."""
    print("\n" + "="*60)
    print("VOICE RAG PIPELINE - MODEL SELECTOR")
    print("="*60)
    
    manager = ModelManager()
    manager.list_models()
    
    if not manager.available_models:
        print("❌ No models found!")
        print("\nPull models using: ollama pull <model>")
        print("\nRecommended models:")
        print("  - ollama pull llama3.2:3b    (fastest)")
        print("  - ollama pull qwen2.5:7b     (balanced)")
        print("  - ollama pull deepseek-r1:7b (best quality)")
        return
    
    print("Select a model to use:")
    selected_model = manager.select_model_interactive()
    
    if not selected_model:
        print("\n⚠️ No model selected. Exiting.")
        return
    
    print(f"\n✓ Updating configuration to use: {selected_model}")
    update_config(selected_model)
    
    print("\n" + "="*60)
    run = input("Start Voice RAG application now? (y/n): ").strip().lower()
    
    if run == 'y':
        print("\n" + "="*60)
        print(f"Starting Voice RAG with {selected_model}...")
        print("="*60 + "\n")
        
        from voice_rag import main as run_voice_rag
        run_voice_rag()
    else:
        print(f"\n✓ Configuration saved.")
        print(f"Current model: {selected_model}")
        print("\nRun 'python app.py' to start the application.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Exited")
        sys.exit(0)
