"""
Tesseract OCR engine implementation.
Best for: Clean printed PDFs and documents.
"""

from typing import List, Optional
from PIL import Image
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import helpers


def extract(images: List[Image.Image]) -> Optional[str]:
    """
    Extract text from images using Tesseract OCR.
    
    Args:
        images: List of PIL Images to process
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        import pytesseract
    except ImportError:
        print("Tesseract not installed. Run: pip install pytesseract")
        return None
    
    # Check if tesseract binary is available
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        print("Tesseract binary missing. Run: sudo apt install tesseract-ocr")
        return None
    
    try:
        all_text = []
        
        # Process each image (page)
        from tqdm import tqdm
        for i, image in enumerate(tqdm(images, desc="[Tesseract] Pages", unit="page"), 1):
            # Run OCR with English language and PSM 3 (automatic page segmentation)
            text = pytesseract.image_to_string(image, lang='eng', config='--psm 3')
            all_text.append(text)
        
        # Concatenate all pages with newline separator
        result = '\n'.join(all_text)
        
        # Clean and return
        return helpers.clean_text(result)
        
    except Exception as e:
        print(f"[Tesseract] Error: {e}")
        return None
