# Run this to benchmark all models for speed
# Usage: python util/compare_models.py
# Make sure ollama is running: ollama serve

"""
Model Comparison Tool - Benchmark different Ollama models for speed
Tests multiple fast models and provides recommendations
"""

import sys
import time
import subprocess
import requests
from datetime import datetime
from tabulate import tabulate

# Test configuration
MODELS_TO_TEST = [
    {"id": "1", "name": "llama3.2:3b",     "description": "Llama 3.2 - 3B"},
    {"id": "2", "name": "qwen2.5:7b",       "description": "Qwen 2.5 - 7B"},
    {"id": "3", "name": "deepseek-r1:7b",   "description": "DeepSeek R1 - 7B"},
    {"id": "4", "name": "phi3:mini",         "description": "Phi-3 Mini - 3.8B"},
    {"id": "5", "name": "gemma:2b",          "description": "Gemma - 2B"},
    {"id": "6", "name": "gemma3:1b",         "description": "Gemma 3 - 1B"},
]

TEST_QUESTION = "What is the main topic of the documents?"
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_installed_models():
    """Check which models are actually pulled in Ollama."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        installed = set()
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    installed.add(parts[0])
        
        return installed
    
    except Exception as e:
        print(f"❌ Error checking installed models: {e}")
        print("Make sure Ollama is running: ollama serve")
        return set()


def benchmark_model(model_name, question):
    """
    Benchmark a single model.
    Returns dict with timing and response info, or None if failed.
    """
    try:
        payload = {
            "model": model_name,
            "prompt": question,
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        total_time = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        
        response_text = result.get("response", "")
        response_length = len(response_text)
        
        return {
            "model": model_name,
            "total_time": total_time,
            "response_length": response_length,
            "response_text": response_text,
            "status": "✓ OK"
        }
    
    except requests.exceptions.Timeout:
        return {
            "model": model_name,
            "total_time": None,
            "response_length": 0,
            "response_text": "",
            "status": "✗ TIMEOUT"
        }
    except Exception as e:
        return {
            "model": model_name,
            "total_time": None,
            "response_length": 0,
            "response_text": "",
            "status": f"✗ ERROR: {str(e)[:30]}"
        }


def save_results(results, filename="logs/benchmark_results.txt"):
    """Save full benchmark results to file with timestamp."""
    import os
    os.makedirs("logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w') as f:
        f.write("="*80 + "\n")
        f.write(f"OLLAMA MODEL BENCHMARK RESULTS\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Test Question: {TEST_QUESTION}\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"\nModel: {result['model']}\n")
            f.write(f"Status: {result['status']}\n")
            if result['total_time']:
                f.write(f"Total Time: {result['total_time']:.2f}s\n")
                f.write(f"Response Length: {result['response_length']} chars\n")
                f.write(f"\nResponse:\n{result['response_text']}\n")
            f.write("-"*80 + "\n")
    
    print(f"\n✓ Full results saved to {filename}")


def main():
    """Main benchmark function."""
    print("\n" + "="*80)
    print("OLLAMA MODEL BENCHMARK - Speed Comparison")
    print("="*80)
    
    # Check installed models
    print("\nChecking installed models...")
    installed = get_installed_models()
    
    if not installed:
        print("\n❌ Could not detect installed models. Is Ollama running?")
        print("Start Ollama: ollama serve")
        return
    
    print(f"Found {len(installed)} installed models")
    
    # Filter models to test
    models_to_run = []
    skipped = []
    
    for model_info in MODELS_TO_TEST:
        model_name = model_info["name"]
        if model_name in installed:
            models_to_run.append(model_info)
        else:
            skipped.append(model_name)
            print(f"[SKIP] {model_name} not found — run: ollama pull {model_name}")
    
    if not models_to_run:
        print("\n❌ No models available to test!")
        print("\nInstall models with:")
        for model_info in MODELS_TO_TEST:
            print(f"  ollama pull {model_info['name']}")
        return
    
    print(f"\n✓ Will test {len(models_to_run)} models")
    print(f"Question: \"{TEST_QUESTION}\"\n")
    
    # Run benchmarks
    results = []
    for i, model_info in enumerate(models_to_run, 1):
        model_name = model_info["name"]
        print(f"[{i}/{len(models_to_run)}] Testing {model_name}...", end=" ", flush=True)
        
        result = benchmark_model(model_name, TEST_QUESTION)
        results.append(result)
        
        if result['total_time']:
            print(f"{result['total_time']:.1f}s ✓")
        else:
            print(f"{result['status']}")
    
    # Sort by speed (fastest first)
    successful_results = [r for r in results if r['total_time'] is not None]
    failed_results = [r for r in results if r['total_time'] is None]
    successful_results.sort(key=lambda x: x['total_time'])
    
    # Prepare table data
    table_data = []
    for result in successful_results + failed_results:
        if result['total_time']:
            table_data.append([
                result['model'],
                f"{result['total_time']:.1f}",
                f"{result['response_length']} chars",
                result['status']
            ])
        else:
            table_data.append([
                result['model'],
                "N/A",
                "N/A",
                result['status']
            ])
    
    # Print benchmark table
    print("\n" + "="*80)
    print("BENCHMARK RESULTS")
    print("="*80)
    print(tabulate(
        table_data,
        headers=["Model", "Total Time (s)", "Response Length", "Status"],
        tablefmt="fancy_grid"
    ))
    
    # Print recommendation
    if successful_results:
        fastest = successful_results[0]
        
        # Find best balance (prefer models under 5s with good response length)
        balanced = None
        for r in successful_results:
            if r['total_time'] < 5.0 and r['response_length'] > 100:
                balanced = r
                break
        
        if not balanced:
            balanced = successful_results[0] if len(successful_results) > 0 else None
        
        print("\n" + "="*80)
        print("  RECOMMENDATION")
        print("="*80)
        print(f"  Fastest model: {fastest['model']} ({fastest['total_time']:.1f}s)")
        if balanced and balanced != fastest:
            print(f"  Best balance of speed + quality: {balanced['model']} ({balanced['total_time']:.1f}s)")
        print()
        print("  To switch model update src/config.py:")
        print(f'  OLLAMA_MODEL = "{fastest["model"]}"')
        print("="*80)
    
    # Save full results
    save_results(results)


if __name__ == "__main__":
    main()
