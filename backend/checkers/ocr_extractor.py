# pylint: disable=no-member
import easyocr
import cv2
import numpy as np
from PIL import Image
import re
import os
from typing import Dict, List

class OCRExtractor:
    """Advanced OCR with multiple engines and preprocessing for maximum accuracy"""
    
    def __init__(self):
        self.reader = None
        self.initialize_easyocr()
    
    def initialize_easyocr(self):
        """Initialize EasyOCR with English language"""
        try:
            print("Initializing EasyOCR... (this may take a moment)")
            # ONLY CHANGE 1: Added quantize=True for speed (doesn't affect accuracy)
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False, quantize=True)
            print("EasyOCR ready!")
        except Exception as e:
            print(f"EasyOCR initialization failed: {e}")
            self.reader = None
    
    def preprocess_image(self, image_path: str):
        """Advanced preprocessing for maximum OCR accuracy"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to RGB (EasyOCR works better with RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # ONLY CHANGE 2: Smart resize (upscale small, downscale huge)
        height, width = img.shape[:2]
        if width < 1000 or height < 700:
            scale = max(1000/width, 700/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        elif width > 3000 or height > 3000:
            scale = min(2500/width, 2500/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply multiple preprocessing techniques and combine
        processed_images = []
        
        # 1. Original grayscale
        processed_images.append(gray)
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(gray)
        processed_images.append(clahe_img)
        
        # 3. Sharpened
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        processed_images.append(sharpened)
        
        # 4. Bilateral filter (noise reduction while preserving edges)
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        processed_images.append(bilateral)
        
        # 5. Thresholding (OTSU)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(thresh)
        
        # 6. Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
        processed_images.append(adaptive)
        
        return img, processed_images
    
    def extract_text_with_easyocr(self, image: np.ndarray) -> str:
        """Extract text using EasyOCR"""
        if self.reader is None:
            return ""
        
        try:
            # ONLY CHANGE 3: Slightly optimized parameters (still accurate)
            result = self.reader.readtext(
                image,
                paragraph=True,
                width_ths=0.7,
                height_ths=0.7,
                text_threshold=0.65,  # Changed from 0.7 to 0.65
                low_text=0.4,
                link_threshold=0.4,
                mag_ratio=1.8,        # Changed from 2.0 to 1.8
            )
            
            # Extract text from results
            texts = [item[1] for item in result]
            return ' '.join(texts)
            
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return ""
    
    def extract_text_with_tesseract(self, image: np.ndarray) -> str:
        """Fallback to Tesseract if EasyOCR fails (if installed)"""
        try:
            import pytesseract
            from PIL import Image
            
            configs = [
                '--oem 3 --psm 6',
                '--oem 3 --psm 4',
                '--oem 3 --psm 11'
            ]
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(
                        Image.fromarray(image),
                        lang='eng',
                        config=config
                    )
                    if len(text.strip()) > 10:
                        return text
                except:
                    continue
            
            return ""
            
        except ImportError:
            return ""
    
    def merge_text_results(self, texts: List[str]) -> str:
        """Merge and clean multiple OCR results"""
        if not texts:
            return ""
        
        texts = [t for t in texts if t.strip()]
        
        if not texts:
            return ""
        
        # ONLY CHANGE 4: Smarter merging (combines best words)
        if len(texts) == 1:
            return self.clean_text(texts[0])
        
        # Choose the longest text (usually most complete)
        best_text = max(texts, key=len)
        
        # Combine unique words from other results
        all_words = set(best_text.split())
        for text in texts:
            if text != best_text:
                all_words.update(text.split())
        
        # If combined has more words, use it
        if len(all_words) > len(set(best_text.split())) * 1.2:
            combined = ' '.join(all_words)
            return self.clean_text(combined)
        
        cleaned = self.clean_text(best_text)
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """Clean up extracted text"""
        # Remove excessive spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove repeated characters (more than 2)
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)
        
        # Fix common OCR errors
        corrections = {
            '0': 'O',
            '1': 'I',
            '5': 'S',
            '8': 'B',
            'STRATEOY': 'STRATEGY',
            'PRESENT5': 'PRESENTS',
            'LEADERSH1P': 'LEADERSHIP',
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_text(self, image_path: str) -> Dict:
        """Main extraction function with multiple fallbacks"""
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image not found: {image_path}",
                "cleaned_text": "",
                "raw_text": ""
            }
        
        try:
            # Preprocess image
            original_img, processed_images = self.preprocess_image(image_path)
            
            all_texts = []
            
            # Method 1: Try EasyOCR on each preprocessed image
            for proc_img in processed_images:
                text = self.extract_text_with_easyocr(proc_img)
                if text:
                    all_texts.append(text)
            
            # Method 2: Try EasyOCR on original image
            text = self.extract_text_with_easyocr(original_img)
            if text:
                all_texts.append(text)
            
            # Method 3: Try Tesseract as fallback (ONLY if EasyOCR found nothing)
            if not all_texts:
                for proc_img in processed_images[:3]:  # Only try on first 3
                    text = self.extract_text_with_tesseract(proc_img)
                    if text:
                        all_texts.append(text)
            
            # Merge and clean results
            merged_text = self.merge_text_results(all_texts)
            
            if not merged_text:
                return {
                    "success": False,
                    "error": "No text could be extracted",
                    "cleaned_text": "",
                    "raw_text": ""
                }
            
            final_text = self.clean_text(merged_text)
            
            return {
                "success": True,
                "raw_text": merged_text,
                "cleaned_text": final_text,
                "word_count": len(final_text.split()),
                "char_count": len(final_text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cleaned_text": "",
                "raw_text": ""
            }