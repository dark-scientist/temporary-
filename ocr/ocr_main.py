"""
OCR Benchmarking Tool - Main Entry Point

Processes PDFs and images using 4 OCR engines:
- Tesseract: Best for clean printed documents
- EasyOCR: Best for photos and real-world text
- TrOCR: Best for handwritten documents
- DocTR: Best for complex layouts (invoices, forms, tables)

Usage:
    1. Drop files into ocr/input/
    2. Run: python ocr_main.py
    3. Check results in ocr/output/
"""

import os
import sys
import time
from typing import List, Tuple, Callable, Optional
from tabulate import tabulate

# Import OCR engines
from engines import tesseract_ocr, easyocr_ocr, trocr_ocr, doctr_ocr
from utils import helpers


def print_banner():
    """Print startup banner."""
    print("=" * 44)
    print("  OCR Benchmarking Tool")
    print("  Engines: Tesseract | EasyOCR | TrOCR | DocTR")
    print("=" * 44)


def scan_input_folder() -> List[str]:
    """
    Scan input/ folder for supported files.
    
    Returns:
        List of file paths to process
    """
    input_dir = "input"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        return []
    
    # Supported extensions
    supported_exts = {'.pdf', '.jpg', '.jpeg', '.png'}
    
    # Find all supported files
    files = []
    for filename in os.listdir(input_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_exts:
            files.append(os.path.join(input_dir, filename))
    
    return sorted(files)


def process_file(filepath: str):
    """
    Process a single file with all OCR engines and display benchmark.
    
    Args:
        filepath: Path to the input file
    """
    filename = os.path.basename(filepath)
    print(f"\n📄 Processing: {filename}")
    
    # Load input file as list of PIL images
    images = helpers.load_input_file(filepath)
    
    if images is None:
        print(f"❌ Failed to load {filename}")
        return
    
    print(f"   Loaded {len(images)} page(s)")
    
    # Define OCR tools to benchmark
    tools: List[Tuple[str, Callable]] = [
        ("Tesseract", tesseract_ocr.extract),
        ("EasyOCR", easyocr_ocr.extract),
        ("TrOCR", trocr_ocr.extract),
        ("DocTR", doctr_ocr.extract),
    ]
    
    # Store results for benchmarking
    results = []
    
    # Process with each tool
    for tool_name, extract_func in tools:
        print(f"\n[{tool_name}] Processing...")
        
        # Record start time
        start = time.time()
        
        # Run OCR extraction with error handling
        try:
            text = extract_func(images)
        except Exception as e:
            print(f"[{tool_name}] Unexpected error: {e}")
            text = None
        
        # Record end time
        end = time.time()
        time_taken = round(end - start, 2)
        
        # Process results
        if text is None:
            # Extraction failed
            results.append({
                'tool': tool_name,
                'time': time_taken,
                'chars': 0,
                'score': 0.0,
                'status': 'FAILED',
                'output_path': None
            })
            print(f"[{tool_name}] ❌ Failed")
        else:
            # Extraction succeeded
            chars = len(text)
            score = helpers.calculate_score(chars, time_taken)
            
            # Save output
            output_path = helpers.save_output(tool_name, filename, text)
            
            results.append({
                'tool': tool_name,
                'time': time_taken,
                'chars': chars,
                'score': score,
                'status': 'OK',
                'output_path': output_path
            })
            print(f"[{tool_name}] ✓ Extracted {chars} characters in {time_taken}s")
    
    # Display benchmark table
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    
    table_data = [
        [r['tool'], r['time'], r['chars'], r['score'], r['status']]
        for r in results
    ]
    
    headers = ['Tool', 'Time (s)', 'Characters Extracted', 'Score', 'Status']
    print(tabulate(table_data, headers=headers, tablefmt='pretty'))
    
    # Find best tool (highest score among successful runs)
    successful = [r for r in results if r['status'] == 'OK']
    
    if successful:
        best = max(successful, key=lambda x: x['score'])
        print("\n🏆 WINNER")
        print(f"Best tool for \"{filename}\": {best['tool']}")
        print(f"Score: {best['score']} | Time: {best['time']}s | Characters: {best['chars']}")
        print(f"Output saved to: {best['output_path']}")
    else:
        print("\n❌ All tools failed for this file")


def main():
    """Main entry point."""
    print_banner()
    
    # Scan for input files
    files = scan_input_folder()
    
    if not files:
        print("\n❌ No input files found.")
        print("Please drop your PDF or image files into the ocr/input/ folder and run again.")
        return
    
    print(f"\n✓ Found {len(files)} file(s) to process")
    
    # Process each file
    for filepath in files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"\n❌ Unexpected error processing {os.path.basename(filepath)}: {e}")
            continue
    
    # Final summary
    print("\n" + "=" * 44)
    print("  All Done!")
    print("  Extracted text files saved to: ocr/output/")
    print("  Copy the best output files to your RAG")
    print("  pipeline's data/documents/ folder")
    print("=" * 44)


if __name__ == "__main__":
    main()
