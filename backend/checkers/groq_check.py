from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from groq import Groq
from typing import List, Dict

class GroqChecker:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found")
            self.available = False
            return
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.available = True
        print("Groq initialized!")
    
    def clean_punctuation(self, text: str) -> str:
        """Clean up double punctuation and spacing issues"""
        # Fix double question marks
        text = text.replace("??", "?")
        text = text.replace("?!", "?")
        text = text.replace("?.", "?")
        text = text.replace("!.", ".")
        text = text.replace("..", ".")
        
        # Fix space after punctuation (add space if missing)
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Fix space before punctuation (remove space if present)
        text = re.sub(r'\s+([.!?])', r'\1', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix space after comma
        text = re.sub(r',([A-Za-z])', r', \1', text)
        
        return text.strip()
    
    def check_full_text(self, text: str) -> Dict:
        if not self.available:
            return {
                "corrected_text": text,
                "grammar_issues": [],
                "logic_issues": [],
                "coherence_score": 0.5,
                "coherence_warnings": []
            }
        
        prompt = f"""You are a British English grammar expert. Fix ALL punctuation and grammar errors in this text.

Text: "{text}"

CRITICAL RULES - APPLY TO EVERY SENTENCE:
1. ANY sentence that asks a question MUST end with "?" not "."
2. "Hello how are you" → "Hello, how are you?"
3. "What is your name" → "What is your name?"
4. "How are you" → "How are you?"
5. "Good morning how can I help you" → "Good morning, how can I help you?"
6. "Good afternoon what would you like to order" → "Good afternoon, what would you like to order?"
7. "Good evening how was your day" → "Good evening, how was your day?"
8. "Where are you going" → "Where are you going?"
9. "Why is the sky blue" → "Why is the sky blue?"
10. "Can you help me" → "Can you help me?"

For EACH grammar issue, provide:
- type: "punctuation" for punctuation errors
- message: clear description of the error
- original: the exact wrong text
- correction: the exact corrected text with BOTH comma AND question mark if needed

If the text is already correct, return empty arrays for grammar_issues and logic_issues.

Return ONLY valid JSON.

{{
    "corrected_text": "the COMPLETE fixed version with ALL question marks and commas added",
    "grammar_issues": [
        {{"type": "punctuation", "message": "Missing comma after greeting and missing question mark", "original": "Hello how are you", "correction": "Hello, how are you?"}},
        {{"type": "punctuation", "message": "Missing question mark", "original": "What is your name", "correction": "What is your name?"}},
        {{"type": "punctuation", "message": "Missing comma after greeting and missing question mark", "original": "Good morning how can I help you", "correction": "Good morning, how can I help you?"}}
    ],
    "logic_issues": [
        {{"sentence": "The dead man is breathing", "reason": "Dead people cannot breathe", "suggestion": "Change to 'The injured man is breathing'"}},
        {{"sentence": "She was born in 2015. She graduated in 2010", "reason": "Cannot graduate before birth", "suggestion": "Change graduation year to after 2015"}}
    ],
    "coherence_score": 0.9,
    "coherence_warnings": []
}}

IMPORTANT RULES:
- If the text is ALREADY CORRECT, return empty arrays: "grammar_issues": [], "logic_issues": []
- For ANY question, add "?" at the end (ONE question mark only, not two)
- For greetings like "Good morning how", add comma AFTER the greeting
- DO NOT add double question marks "??" - only ONE "?"
- DO NOT suggest changes that are already applied
- The corrected_text MUST include ALL fixes
- Only output valid JSON, no other text"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a British English grammar expert. For ANY sentence that is a question, you MUST add ONE '?' at the end (not two). If the text is already correct, return empty arrays. Never suggest changes that are already applied."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Clean up punctuation in corrected_text
            if result.get("corrected_text"):
                result["corrected_text"] = self.clean_punctuation(result["corrected_text"])
            
            # Clean up punctuation in grammar_issues corrections
            for issue in result.get("grammar_issues", []):
                if issue.get("correction"):
                    issue["correction"] = self.clean_punctuation(issue["correction"])
                if issue.get("original"):
                    issue["original"] = issue["original"].strip()
            
            # Remove duplicate grammar issues (same original text)
            if result.get("grammar_issues"):
                seen = set()
                unique_issues = []
                for issue in result["grammar_issues"]:
                    key = issue.get("original", "")
                    if key and key not in seen:
                        seen.add(key)
                        unique_issues.append(issue)
                result["grammar_issues"] = unique_issues
            
            # Ensure all required fields exist
            if "grammar_issues" not in result:
                result["grammar_issues"] = []
            if "logic_issues" not in result:
                result["logic_issues"] = []
            if "coherence_warnings" not in result:
                result["coherence_warnings"] = []
            if "coherence_score" not in result:
                result["coherence_score"] = 0.8
            
            return result
                
        except Exception as e:
            print(f"Groq error: {e}")
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