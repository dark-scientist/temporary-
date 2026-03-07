"""
Helper utilities for OCR processing.
Handles PDF conversion, file loading, text cleaning, and output saving.
"""

import os
from typing import List, Optional
from PIL import Image


def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """
    Convert every page of a PDF to a PIL Image.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of PIL Images, one per page
        
    Raises:
        Exception: If poppler is not installed or PDF conversion fails
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise Exception("pdf2image not installed. Run: pip install pdf2image")
    
    try:
        # Convert at 300 DPI for high quality OCR
        images = convert_from_path(pdf_path, dpi=300)
        return images
    except Exception as e:
        if "poppler" in str(e).lower():
            raise Exception("Poppler not installed. Run: sudo apt install poppler-utils -y")
        raise Exception(f"Failed to convert PDF: {e}")


def load_input_file(filepath: str) -> Optional[List[Image.Image]]:
    """
    Load a file and return as list of PIL Images.
    
    Supports PDF (multi-page) and image files (single page).
    
    Args:
        filepath: Path to the input file
        
    Returns:
        List of PIL Images, or None if unsupported file type
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    # Handle PDF files
    if ext == '.pdf':
        try:
            return pdf_to_images(filepath)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return None
    
    # Handle image files
    elif ext in ['.jpg', '.jpeg', '.png']:
        try:
            image = Image.open(filepath)
            return [image]
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    # Unsupported file type
    else:
        print(f"Unsupported file type: {ext}")
        return None


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace.
    
    - Removes leading/trailing whitespace from each line
    - Removes lines that are only whitespace
    - Limits consecutive blank lines to maximum of 1
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Split into lines and strip each line
    lines = [line.strip() for line in text.split('\n')]
    
    # Remove lines that are only whitespace
    lines = [line for line in lines if line]
    
    # Join with single newline and limit consecutive blank lines
    cleaned = '\n'.join(lines)
    
    # Replace multiple consecutive newlines with max 2 (1 blank line)
    while '\n\n\n' in cleaned:
        cleaned = cleaned.replace('\n\n\n', '\n\n')
    
    return cleaned


def save_output(tool_name: str, original_filename: str, text: str) -> str:
    """
    Save extracted text to output directory.
    
    Creates output/ directory if it doesn't exist.
    If file exists, appends timestamp to avoid overwriting.
    
    Args:
        tool_name: Name of the OCR tool (e.g., "tesseract")
        original_filename: Original input filename
        text: Extracted text to save
        
    Returns:
        Path to the saved output file
    """
    # Create output directory if needed
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Remove extension from original filename
    base_name = os.path.splitext(original_filename)[0]
    
    # Create output filename
    output_filename = f"{tool_name.lower()}_{base_name}.txt"
    output_path = os.path.join(output_dir, output_filename)
    
    # If file exists, append timestamp
    if os.path.exists(output_path):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{tool_name.lower()}_{base_name}_{timestamp}.txt"
        output_path = os.path.join(output_dir, output_filename)
    
    # Save the text
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return output_path


def calculate_score(characters: int, time_seconds: float) -> float:
    """
    Calculate performance score for OCR tool.
    
    Simple scoring: characters extracted per second.
    Higher is better.
    
    Args:
        characters: Number of characters extracted
        time_seconds: Time taken in seconds
        
    Returns:
        Score as float (characters/second), or 0 if time is 0
    """
    if time_seconds == 0:
        return 0.0
    return round(characters / time_seconds, 1)
