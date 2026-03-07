"""
Model Comparison Tool - Benchmark different Ollama models

Run this to benchmark all models for speed
Usage: python util/compare_models.py
Make sure ollama is running: ollama serve
"""

import sys
import time
import subprocess
import json
import os
from datetime import datetime

sys.path.insert(0, './src')

# Models to test
MODELS_TO_TEST = [
    {"id": "1", "name": "gemma:2b",      "description": "Gemma 2B"},
    {"id": "2", "name": "gemma2:2b",     "description": "Gemma 2 - 2B"},
    {"id": "3", "name": "gemma3:4b",     "description": "Gemma 3 - 4B"},
    {"id": "4", "name": "phi3:mini",     "description": "Phi-3 Mini 3.8B"},
    {"id": "5", "name": "llama3.2:3b",   "description": "Llama 3.2 - 3B"},
]

TEST_QUESTION = "What is the main topic of the documents? Answer in exactly 2 sentences. No more than 50 words total."


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
        installed = []
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    installed.append(parts[0])
        
        return installed
    
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        print("Make sure Ollama is running: ollama serve")
        return []


def test_model(model_name, run_number=1, total_runs=3):
    """Test a single model and measure performance."""
    print(f"[Testing] {model_name} run {run_number}/{total_runs}...")
    
    try:
        # Prepare request
        payload = {
            "model": model_name,
            "prompt": TEST_QUESTION,
            "stream": False,
            "options": {
                "num_predict": 80,
                "temperature": 0.7,
                "stop": ["\n\n", "###"]
            }
        }
        
        # Measure time
        start_time = time.time()
        
        # Call Ollama API
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            check=True
        )
        
        total_time = time.time() - start_time
        
        # Parse response
        response_data = json.loads(result.stdout)
        response_text = response_data.get("response", "").strip()
        word_count = len(response_text.split())
        
        return {
            "model": model_name,
            "total_time": total_time,
            "word_count": word_count,
            "response_text": response_text,
            "status": "✓ OK"
        }
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def print_benchmark_table(results):
    """Print benchmark results in a clean table."""
    try:
        from tabulate import tabulate
        
        # Prepare table data
        table_data = []
        for r in results:
            table_data.append([
                r["model"],
                f"{r['avg_time']:.1f}",
                f"{r['min_time']:.1f}",
                f"{r['max_time']:.1f}",
                f"{r['word_count']} words",
                r["status"]
            ])
        
        # Print table
        print("\n" + "="*80)
        print(tabulate(
            table_data,
            headers=["Model", "Avg Time (s)", "Min (s)", "Max (s)", "Word Count", "Status"],
            tablefmt="fancy_grid"
        ))
        print("="*80)
    
    except ImportError:
        # Fallback if tabulate not installed
        print("\n" + "="*80)
        print(f"{'Model':<15} {'Avg Time (s)':<15} {'Min (s)':<10} {'Max (s)':<10} {'Word Count':<15} {'Status':<10}")
        print("-"*80)
        for r in results:
            print(f"{r['model']:<15} {r['avg_time']:<15.1f} {r['min_time']:<10.1f} {r['max_time']:<10.1f} {r['word_count']:<15} {r['status']:<10}")
        print("="*80)


def save_results(results):
    """Save full results to log file."""
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"logs/benchmark_results_{timestamp}.txt"
    
    with open(filepath, 'w') as f:
        f.write("="*80 + "\n")
        f.write(f"OLLAMA MODEL BENCHMARK RESULTS (3 runs averaged)\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Question: {TEST_QUESTION}\n")
        f.write("="*80 + "\n\n")
        
        for r in results:
            f.write(f"\nModel: {r['model']}\n")
            f.write(f"Status: {r['status']}\n")
            f.write(f"Average Time: {r['avg_time']:.2f}s\n")
            f.write(f"Min Time: {r['min_time']:.2f}s\n")
            f.write(f"Max Time: {r['max_time']:.2f}s\n")
            f.write(f"Word Count: {r['word_count']} words\n")
            f.write(f"\nSample Response:\n{r['response_text']}\n")
            f.write("-"*80 + "\n")
    
    print(f"\n✓ Full results saved to: {filepath}")


def main():
    """Main benchmark function."""
    print("\n" + "="*80)
    print("  OLLAMA MODEL BENCHMARK")
    print("="*80)
    
    # Check installed models
    print("\n[1/3] Checking installed models...")
    installed = get_installed_models()
    
    if not installed:
        print("\n❌ No Ollama models found or Ollama not running!")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        print("\nThen install models:")
        for model in MODELS_TO_TEST:
            print(f"  ollama pull {model['name']}")
        return
    
    print(f"✓ Found {len(installed)} installed models")
    
    # Filter models to test
    models_to_run = []
    for model in MODELS_TO_TEST:
        if model["name"] in installed:
            models_to_run.append(model["name"])
            print(f"  ✓ {model['name']}")
        else:
            print(f"  [SKIP] {model['name']} not found — run: ollama pull {model['name']}")
    
    if not models_to_run:
        print("\n❌ No models available to test!")
        return
    
    # Run benchmarks
    print(f"\n[2/3] Running benchmarks (3 runs per model)...")
    print(f"Test question: \"{TEST_QUESTION}\"\n")
    
    results = []
    for model_name in models_to_run:
        times = []
        word_count = 0
        response_text = ""
        
        # Run 3 times
        for run in range(1, 4):
            result = test_model(model_name, run, 3)
            if result:
                times.append(result["total_time"])
                word_count = result["word_count"]
                response_text = result["response_text"]
        
        if times:
            results.append({
                "model": model_name,
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "word_count": word_count,
                "response_text": response_text,
                "status": "✓ OK"
            })
        else:
            results.append({
                "model": model_name,
                "avg_time": 0,
                "min_time": 0,
                "max_time": 0,
                "word_count": 0,
                "response_text": "",
                "status": "✗ FAILED"
            })
    
    # Sort by fastest average time first
    results.sort(key=lambda x: x["avg_time"] if x["avg_time"] > 0 else float('inf'))
    
    # Print results
    print(f"\n[3/3] Results:")
    print_benchmark_table(results)
    
    # Print recommendation
    if results and results[0]["avg_time"] > 0:
        fastest = results[0]
        
        # Find best balance (prefer models under 8s average)
        best_balance = fastest
        for r in results:
            if r["avg_time"] > 0 and r["avg_time"] < 8.0:
                best_balance = r
                break
        
        print("\n" + "="*80)
        print("  RECOMMENDATION")
        print("="*80)
        print(f"  Fastest model: {fastest['model']} ({fastest['avg_time']:.1f}s avg)")
        print(f"  Best balance of speed + quality: {best_balance['model']} ({best_balance['avg_time']:.1f}s avg)")
        print()
        print("  To switch model, update src/config.py:")
        print(f"  OLLAMA_MODEL = \"{best_balance['model']}\"")
        print("="*80)
    
    # Save results
    save_results(results)


if __name__ == "__main__":
    main()
