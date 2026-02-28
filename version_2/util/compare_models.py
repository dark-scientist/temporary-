"""
Model Comparison Tool - Benchmark different Ollama models
"""

import sys
import time
sys.path.insert(0, './src')

from rag import RAGSystem
from llm import OllamaLLM
from config import OLLAMA_MODEL
import subprocess


def get_available_models():
    """Get list of available Ollama models."""
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
                    models.append(parts[0])
        
        return models
    
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []


def test_model(model_name, question, rag):
    """Test a single model."""
    print("\n" + "="*60)
    print(f"Testing: {model_name}")
    print("="*60)
    
    # Update config temporarily
    import config
    original_model = config.OLLAMA_MODEL
    config.OLLAMA_MODEL = model_name
    
    try:
        # Initialize LLM with new model
        llm = OllamaLLM()
        
        # Get context
        context = rag.retrieve(question, top_k=3)
        
        # Generate response
        print("Generating response...")
        start_time = time.time()
        response = llm.generate(question, context)
        duration = time.time() - start_time
        
        print(f"⏱️  Response Time: {duration:.1f} seconds")
        print(f"📝 Answer: {response}")
        
        # Restore original model
        config.OLLAMA_MODEL = original_model
        
        return {
            "model": model_name,
            "duration": duration,
            "response": response,
            "response_length": len(response)
        }
    
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        config.OLLAMA_MODEL = original_model
        return None


def main():
    """Main comparison function."""
    print("\n" + "="*60)
    print("OLLAMA MODEL COMPARISON TOOL")
    print("="*60)
    
    # Get available models
    available_models = get_available_models()
    
    if not available_models:
        print("\n❌ No Ollama models found!")
        print("\nInstall models with:")
        print("  ollama pull llama3.2:3b")
        print("  ollama pull qwen2.5:7b")
        print("  ollama pull deepseek-r1:7b")
        return
    
    print(f"\nFound {len(available_models)} models:")
    for model in available_models:
        print(f"  - {model}")
    
    # Get question
    question = input("\n❓ Enter your question (or press Enter for default): ").strip()
    if not question:
        question = "What does the text say about dealing with difficulties?"
    
    print(f"\n❓ Question: {question}")
    
    # Initialize RAG
    print("\nInitializing RAG system...")
    rag = RAGSystem()
    
    # Test each model
    results = []
    for model in available_models:
        result = test_model(model, question, rag)
        if result:
            results.append(result)
    
    # Show comparison
    if results:
        print("\n" + "="*60)
        print("COMPARISON SUMMARY")
        print("="*60)
        
        for result in results:
            print(f"\n{result['model']}:")
            print(f"⏱️  Time: {result['duration']:.1f}s")
            print(f"📝 Length: {result['response_length']} characters")
        
        # Find fastest
        fastest = min(results, key=lambda x: x['duration'])
        print(f"\n🏆 Fastest: {fastest['model']} ({fastest['duration']:.1f}s)")
        print("="*60)


if __name__ == "__main__":
    main()
