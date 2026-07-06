from dotenv import load_dotenv
load_dotenv()

import os
import json
import requests
from typing import List, Dict

class GeminiChecker:
    """Check grammar, logic, and coherence using Google Gemini (free)"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in .env file")
            self.available = False
            return
        
        self.model = "gemini-2.0-flash-001"
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"
        self.available = True
        print(f"Gemini initialized with model: {self.model}")
    
    def check_full_text(self, text: str) -> Dict:
        if not self.available:
            return {
                "corrected_text": text,
                "grammar_issues": [],
                "logic_issues": [],
                "coherence_score": 0.5,
                "coherence_warnings": []
            }
        
        prompt = f"""Analyze this text and return ONLY valid JSON.

Text: "{text}"

Return this exact JSON structure:
{{
    "corrected_text": "full corrected version with fixed grammar and punctuation",
    "grammar_issues": [
        {{"message": "describe the error", "suggestion": "how to fix it", "context": "the problematic part"}}
    ],
    "logic_issues": [
        {{"sentence": "illogical sentence", "reason": "why it's wrong", "suggestion": "how to fix"}}
    ],
    "coherence_score": 0.85,
    "coherence_warnings": ["warning about topic shifts"]
}}

For "Hello how are you", corrected_text must be "Hello, how are you?"
Only output valid JSON. No other text."""

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean the response
                result_text = result_text.strip()
                if result_text.startswith('```json'):
                    result_text = result_text[7:]
                if result_text.startswith('```'):
                    result_text = result_text[3:]
                if result_text.endswith('```'):
                    result_text = result_text[:-3]
                result_text = result_text.strip()
                
                result = json.loads(result_text)
                return result
            else:
                print(f"Gemini API error: {response.status_code}")
                return {
                    "corrected_text": text,
                    "grammar_issues": [],
                    "logic_issues": [],
                    "coherence_score": 0.5,
                    "coherence_warnings": []
                }
                
        except Exception as e:
            print(f"Gemini error: {e}")
            return {
                "corrected_text": text,
                "grammar_issues": [],
                "logic_issues": [],
                "coherence_score": 0.5,
                "coherence_warnings": []
            }