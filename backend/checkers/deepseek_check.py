from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI
from typing import List, Dict

class DeepSeekChecker:
    """Check grammar, logic, and coherence using DeepSeek API"""
    
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("Warning: DEEPSEEK_API_KEY not found in .env file")
            self.available = False
            return
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"  # DeepSeek endpoint [citation:4]
        )
        self.model = "deepseek-chat"  # Will be deprecated 2026/07/24, use deepseek-v4-flash after [citation:4]
        self.available = True
        print("DeepSeek initialized successfully!")
    
    def check_full_text(self, text: str) -> Dict:
        """Check everything in one API call"""
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a British English grammar expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}  # DeepSeek supports JSON output [citation:2]
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            return result
                
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return {
                "corrected_text": text,
                "grammar_issues": [],
                "logic_issues": [],
                "coherence_score": 0.5,
                "coherence_warnings": []
            }
    
    def check_grammar(self, text: str) -> List[Dict]:
        result = self.check_full_text(text)
        return result.get("grammar_issues", [])
    
    def check_logic(self, text: str) -> List[Dict]:
        result = self.check_full_text(text)
        return result.get("logic_issues", [])
    
    def check_coherence(self, text: str) -> Dict:
        result = self.check_full_text(text)
        return {
            "score": result.get("coherence_score", 0.5),
            "warnings": result.get("coherence_warnings", [])
        }