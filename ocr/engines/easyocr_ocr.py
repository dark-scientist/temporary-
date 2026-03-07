"""
EasyOCR engine implementation.
Best for: Photos of signs, real-world text, and natural scenes.
"""

from typing import List, Optional
from PIL import Image
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import helpers


def extract(images: List[Image.Image]) -> Optional[str]:
    """
    Extract text from images using EasyOCR.
    
    Args:
        images: List of PIL Images to process
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        import easyocr
    except ImportError:
        print("EasyOCR not installed. Run: pip install easyocr")
        return None
    
    try:
        # Initialize reader (downloads model on first run)
        print("[EasyOCR] Initializing reader (first run may take time to download model)...")
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        all_text = []
        
        # Process each image (page)
        from tqdm import tqdm
        for i, image in enumerate(tqdm(images, desc="[EasyOCR] Pages", unit="page"), 1):
            # Convert PIL image to numpy array
            numpy_array = np.array(image)
            
            # Run OCR - detail=0 returns only text, paragraph=True groups text naturally
            result = reader.readtext(numpy_array, detail=0, paragraph=True)
            
            # Join results
            if isinstance(result, list):
                text = '\n'.join(result)
            else:
                text = str(result)
            
            all_text.append(text)
        
        # Concatenate all pages
        result = '\n'.join(all_text)
        
        # Clean and return
        return helpers.clean_text(result)
        
    except Exception as e:
        print(f"[EasyOCR] Error: {e}")
        return None
