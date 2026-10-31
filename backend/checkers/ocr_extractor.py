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
        self.model = "openai/gpt-oss-120b"
        self.available = True
        print(f"Groq initialized with model: {self.model}")
    
    def clean_punctuation(self, text: str) -> str:
        """Clean up double punctuation and spacing issues"""
        text = text.replace("??", "?")
        text = text.replace("?!", "?")
        text = text.replace("?.", "?")
        text = text.replace("!.", ".")
        text = text.replace("..", ".")
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'\s+([.!?])', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
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
        
        prompt = f"""You are a strict British English editor and spell-checker. Fix ALL punctuation, grammar, and SPELLING errors in this text.

Text: "{text}"

CRITICAL RULES:
1. SPELLING: Correct ALL misspelled words, even if they are in UPPERCASE (e.g., "TEKNOLOGY" → "TECHNOLOGY", "INTELIGENCE" → "INTELLIGENCE").
2. PUNCTUATION: Add missing commas, periods, colons, and question marks.
3. GRAMMAR: Fix subject-verb agreement, tense errors, and double negatives.
4. BRITISH ENGLISH: Use British spelling (e.g., colour, centre, organise).
5. LOGIC: Detect sentences that are logically impossible (e.g., "The dead man is breathing").
6. Do NOT assume all-caps words are brand names; fix them if they are misspelled.

For EACH issue, provide:
- type: "spelling", "grammar", "punctuation", or "logic"
- message: clear description of the error
- original: the exact wrong text
- correction: the exact corrected text

If the text is already correct, return empty arrays.

Return ONLY valid JSON. Do not use markdown code blocks.

{{
    "corrected_text": "the COMPLETE fixed version with ALL spelling and grammar corrections applied",
    "grammar_issues": [
        {{"type": "spelling", "message": "Misspelled word", "original": "TEKNOLOGY", "correction": "TECHNOLOGY"}},
        {{"type": "punctuation", "message": "Missing colon", "original": "TECHNOLOGY A Global", "correction": "TECHNOLOGY: A Global"}},
        {{"type": "grammar", "message": "Subject-verb agreement", "original": "speakers is", "correction": "speakers are"}}
    ],
    "logic_issues": [
        {{"sentence": "The dead man is breathing", "reason": "Dead people cannot breathe", "suggestion": "Change to 'The injured man is breathing'"}}
    ],
    "coherence_score": 0.9,
    "coherence_warnings": []
}}

Only output valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict British English editor. Fix ALL spelling errors, including all-caps words. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown if the AI adds it
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Extract JSON safely
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(0)

            result = json.loads(result_text)
            
            # Clean up punctuation in corrected_text
            if result.get("corrected_text"):
                result["corrected_text"] = self.clean_punctuation(result["corrected_text"])
            
            # Clean up punctuation in grammar_issues
            for issue in result.get("grammar_issues", []):
                if issue.get("correction"):
                    issue["correction"] = self.clean_punctuation(issue["correction"])
                if issue.get("original"):
                    issue["original"] = issue["original"].strip()
            
            # Remove duplicate issues
            if result.get("grammar_issues"):
                seen = set()
                unique_issues = []
                for issue in result["grammar_issues"]:
                    key = issue.get("original", "")
                    if key and key not in seen:
                        seen.add(key)
                        unique_issues.append(issue)
                result["grammar_issues"] = unique_issues
            
            # Ensure all fields exist
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