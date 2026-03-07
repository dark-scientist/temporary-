"""
DocTR (Document Text Recognition) engine implementation.
Best for: Invoices, forms, tables, and complex document layouts.
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
    Extract text from images using DocTR.
    
    Args:
        images: List of PIL Images to process
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        # Set environment to use PyTorch backend (more stable than TensorFlow)
        os.environ['USE_TORCH'] = '1'
        from doctr.models import ocr_predictor
    except ImportError:
        print("DocTR not installed. Run: pip install python-doctr[torch]")
        return None
    
    try:
        # Load OCR predictor with PyTorch backend (downloads model on first run)
        print("[DocTR] Loading OCR predictor with PyTorch backend (downloads on first run)...")
        model = ocr_predictor(pretrained=True, det_arch='db_resnet50', reco_arch='crnn_vgg16_bn')
        
        # Convert PIL images to numpy arrays
        from tqdm import tqdm
        print("[DocTR] Converting images...")
        numpy_images = [np.array(img.convert('RGB')) for img in tqdm(images, desc="[DocTR] Converting", unit="page")]
        
        # Process all images
        result = model(numpy_images)
        
        all_text = []
        
        # Extract text maintaining reading order
        # Structure: pages -> blocks -> lines -> words
        for page in result.pages:
            page_text = []
            
            for block in page.blocks:
                block_text = []
                
                for line in block.lines:
                    # Join words in line with space
                    line_text = ' '.join([word.value for word in line.words])
                    block_text.append(line_text)
                
                # Join lines in block with newline
                page_text.append('\n'.join(block_text))
            
            # Join blocks with double newline
            all_text.append('\n\n'.join(page_text))
        
        # Concatenate all pages
        result = '\n\n'.join(all_text)
        
        # Clean and return
        return helpers.clean_text(result)
        
    except Exception as e:
        print(f"[DocTR] Error: {e}")
        return None
