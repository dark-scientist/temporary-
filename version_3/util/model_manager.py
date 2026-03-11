"""
Model Manager - Interactive Ollama model selection
"""

import subprocess
import json


class ModelManager:
    """Manages Ollama model selection."""
    
    def __init__(self):
        """Initialize model manager."""
        self.models = self.list_models()
    
    def list_models(self):
        """List all available Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append(model_name)
            
            return models
        
        except subprocess.CalledProcessError:
            print("❌ Error: Could not list Ollama models")
            print("Make sure Ollama is installed and running")
            return []
        except FileNotFoundError:
            print("❌ Error: Ollama not found")
            print("Please install Ollama from https://ollama.ai")
            return []
    
    def select_model(self):
        """Interactive model selection."""
        if not self.models:
            print("\n⚠️  No Ollama models found!")
            print("\nTo install models, run:")
            print("  ollama pull llama3.2:3b")
            print("  ollama pull qwen2.5:7b")
            print("  ollama pull deepseek-r1:7b")
            return None
        
        print("\n" + "="*60)
        print("SELECT OLLAMA MODEL")
        print("="*60)
        
        for i, model in enumerate(self.models, 1):
            print(f"{i}. {model}")
        
        print("="*60)
        
        while True:
            try:
                choice = input("\nEnter model number (or 'q' to quit): ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.models):
                    selected = self.models[choice_num - 1]
                    print(f"\n✓ Selected: {selected}\n")
                    return selected
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(self.models)}")
            
            except ValueError:
                print("⚠️  Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return None
    
    def update_config(self, model_name):
        """Update config.py with selected model."""
        config_path = "./src/config.py"
        
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            with open(config_path, 'w') as f:
                for line in lines:
                    if line.startswith('OLLAMA_MODEL ='):
                        f.write(f'OLLAMA_MODEL = "{model_name}"  # Selected model\n')
                    else:
                        f.write(line)
            
            print(f"✓ Updated config.py with model: {model_name}")
            return True
        
        except Exception as e:
            print(f"❌ Error updating config: {e}")
            return False


if __name__ == "__main__":
    manager = ModelManager()
    selected = manager.select_model()
    
    if selected:
        manager.update_config(selected)
