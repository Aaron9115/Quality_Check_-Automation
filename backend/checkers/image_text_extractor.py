import pytesseract
from PIL import Image, ImageEnhance
import os
import re
from typing import Dict

class ImageTextExtractor:
    """Extract text from images using OCR with preprocessing"""
    
    def __init__(self):
        # Set Tesseract path for Windows
        if os.name == 'nt':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
            print(f"Tesseract path set to: {pytesseract.pytesseract.tesseract_cmd}")
    
    def preprocess_image(self, image_path: str) -> Image:
        """Preprocess image for better OCR results"""
        image = Image.open(image_path)
        
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def extract_text(self, image_path: str) -> Dict:
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Simple extraction - NO custom config (this was causing the error)
            extracted_text = pytesseract.image_to_string(
                processed_image, 
                lang='eng'
            )
            
            # Clean up extracted text
            cleaned_text = self.clean_text(extracted_text)
            
            return {
                "success": True,
                "raw_text": extracted_text,
                "cleaned_text": cleaned_text,
                "word_count": len(cleaned_text.split()),
                "char_count": len(cleaned_text)
            }
            
        except pytesseract.pytesseract.TesseractNotFoundError as e:
            return {
                "success": False,
                "error": f"Tesseract not found: {e}",
                "cleaned_text": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cleaned_text": ""
            }
    
    def clean_text(self, text: str) -> str:
        """Clean up extracted text"""
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text