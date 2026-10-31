from dotenv import load_dotenv
load_dotenv()

import os
import base64
import re
from groq import Groq
from typing import Dict

class OCRExtractor:
    """Extract text from images using Groq's Vision model"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found")
            self.available = False
            return
        
        self.client = Groq(api_key=api_key)
        # FIXED: Using the correct Groq Vision model
        self.model = "qwen/qwen3.6-27b"
        self.available = True
        print(f"Groq Vision initialized with model: {self.model}")
    
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text(self, image_path: str) -> Dict:
        """Extract text from image using Groq's Vision model"""
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image not found: {image_path}",
                "cleaned_text": "",
                "raw_text": ""
            }
        
        if not self.available:
            return {
                "success": False,
                "error": "Groq API not available. Check your GROQ_API_KEY.",
                "cleaned_text": "",
                "raw_text": ""
            }
        
        try:
            base64_image = self.encode_image(image_path)
            
            prompt = """You are an expert OCR system reading a graphic design file, brochure, poster, or branding material.

Extract ALL visible text from this image accurately.

CRITICAL RULES FOR DESIGN FILES:
1. Read the text exactly ONCE. Do NOT repeat sections, headings, or paragraphs.
2. Read the text in a logical reading order (Top to Bottom, Left to Right).
3. Keep related items together (e.g., "Date: 7th August" should be on the same line).
4. Handle stylized fonts. If a font is very decorative, use context to guess the correct letters.
5. Do NOT add commentary, explanations, or extra formatting.
6. If there is no visible text, return an empty string.

Extract the text now:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            extracted_text = response.choices[0].message.content.strip()
            cleaned_text = self.clean_text(extracted_text)
            
            return {
                "success": True,
                "raw_text": extracted_text,
                "cleaned_text": cleaned_text,
                "word_count": len(cleaned_text.split()),
                "char_count": len(cleaned_text)
            }
            
        except Exception as e:
            print(f"Groq Vision error: {e}")
            return {
                "success": False,
                "error": str(e),
                "cleaned_text": "",
                "raw_text": ""
            }
    
    def clean_text(self, text: str) -> str:
        """Clean up extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()