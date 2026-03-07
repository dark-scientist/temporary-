"""
TrOCR (Transformer OCR) engine implementation.
Best for: Handwritten documents (when using handwritten model variant).
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
    Extract text from images using TrOCR.
    
    Args:
        images: List of PIL Images to process
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    except ImportError:
        print("Transformers not installed. Run: pip install transformers")
        return None
    
    try:
        # Load model (downloads on first run)
        print("[TrOCR] Loading model microsoft/trocr-base-printed (downloads on first run)...")
        processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
        model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
        
        # For handwritten docs change both to 'microsoft/trocr-base-handwritten'
        
        all_text = []
        
        # Process each image (page)
        from tqdm import tqdm
        for i, image in enumerate(tqdm(images, desc="[TrOCR] Pages", unit="page"), 1):
            # Convert to RGB
            image = image.convert('RGB')
            
            # Process image
            pixel_values = processor(image, return_tensors='pt').pixel_values
            
            # Generate text
            generated_ids = model.generate(pixel_values)
            
            # Decode to text
            text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            all_text.append(text)
        
        # Concatenate all pages
        result = '\n'.join(all_text)
        
        # Clean and return
        return helpers.clean_text(result)
        
    except Exception as e:
        print(f"[TrOCR] Error: {e}")
        return None
