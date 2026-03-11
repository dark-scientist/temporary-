"""
Run Voice RAG with a specific model (bypasses selector)
Usage: python util/run_with_model.py <model-name>
Example: python util/run_with_model.py qwen2.5:7b
"""

import sys
import os

sys.path.insert(0, './src')


def update_config(model_name):
    """Update config.py with specified model."""
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


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("\n❌ Error: Model name required")
        print("\nUsage:")
        print("  python util/run_with_model.py <model-name>")
        print("\nExamples:")
        print("  python util/run_with_model.py llama3.2:3b")
        print("  python util/run_with_model.py qwen2.5:7b")
        print("  python util/run_with_model.py deepseek-r1:7b")
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    print(f"\n🔧 Setting model to: {model_name}")
    
    if not update_config(model_name):
        sys.exit(1)
    
    print("\n🚀 Starting Voice RAG Pipeline...\n")
    
    # Import and run voice_rag
    from voice_rag import main as voice_rag_main
    voice_rag_main()


if __name__ == "__main__":
    main()
