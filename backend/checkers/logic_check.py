import httpx
import json
from typing import List, Dict, Optional
import re

class LogicChecker:
    """Check logical consistency using free GLM-4.7-Flash API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Try to get API key from environment or use mock mode
        self.api_key = api_key or "FREE_TIER_DEMO"
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.use_mock = not api_key  # If no key, use mock logic
        
    def check(self, text: str) -> List[Dict]:
        """Detect illogical sentences"""
        if not text or len(text.strip()) == 0:
            return []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        issues = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:
                continue
                
            is_logical = self._check_sentence_logic(sentence, sentences, i)
            
            if not is_logical.get("logical", True):
                issues.append({
                    "sentence": sentence,
                    "reason": is_logical.get("reason", "Potentially illogical statement"),
                    "suggestion": is_logical.get("suggestion", "")
                })
        
        return issues
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple approach)"""
        # Handle common abbreviations
        text = re.sub(r'(Mr|Ms|Mrs|Dr|Prof)\.', r'\1<period>', text)
        # Split on . ! ?
        sentences = re.split(r'[.!?]+', text)
        # Restore abbreviations
        sentences = [s.replace('<period>', '.') for s in sentences]
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _check_sentence_logic(self, sentence: str, all_sentences: List[str], idx: int) -> Dict:
        """Check logic using either API or simple rules"""
        
        # First, run basic rule-based checks (faster, free)
        rule_check = self._rule_based_check(sentence, all_sentences, idx)
        if not rule_check.get("logical", True):
            return rule_check
        
        # If API key available, use GLM for deeper check
        if self.api_key and self.api_key != "FREE_TIER_DEMO":
            return self._api_based_check(sentence, all_sentences, idx)
        
        # Otherwise, rule-based is enough
        return {"logical": True}
    
    def _rule_based_check(self, sentence: str, all_sentences: List[str], idx: int) -> Dict:
        """Simple rule-based logic detection (free, no API needed)"""
        sentence_lower = sentence.lower()
        
        # Rule 1: Contradictory statements about time
        if "born in" in sentence_lower and idx > 0:
            # Check if previous sentence mentions voting or events before birth
            prev = all_sentences[idx-1].lower()
            if "voted" in prev or "elected" in prev:
                # Extract years
                import re
                birth_years = re.findall(r'(\d{4})', sentence)
                event_years = re.findall(r'(\d{4})', prev)
                
                for birth_year in birth_years:
                    for event_year in event_years:
                        if int(event_year) < int(birth_year):
                            return {
                                "logical": False,
                                "reason": f"Person born in {birth_year} cannot have experienced events from {event_year}",
                                "suggestion": "Check chronological order of events"
                            }
        
        # Rule 2: Dead/alive contradictions
        if "dead" in sentence_lower or "died" in sentence_lower:
            if "breathing" in sentence_lower or "walking" in sentence_lower or "talking" in sentence_lower:
                return {
                    "logical": False,
                    "reason": "A dead person cannot perform living actions",
                    "suggestion": "Remove contradiction"
                }
        
        # Rule 3: Impossible sensory combinations
        sensory_impossible = [
            ("colour", "taste", "colour cannot be tasted"),
            ("color", "taste", "color cannot be tasted"),
            ("sound", "smell", "sound cannot be smelled"),
            ("silence", "loud", "silence cannot be loud")
        ]
        
        for word1, word2, reason in sensory_impossible:
            if word1 in sentence_lower and word2 in sentence_lower:
                return {
                    "logical": False,
                    "reason": reason,
                    "suggestion": "Rewrite with logical sensory attribution"
                }
        
        # Rule 4: Self-contradictions
        contradictions = [
            ("always", "never"),
            ("all", "none"),
            ("everyone", "no one"),
            ("completely", "slightly")
        ]
        
        for word1, word2 in contradictions:
            if word1 in sentence_lower and word2 in sentence_lower:
                return {
                    "logical": False,
                    "reason": f"Contradiction: '{word1}' and '{word2}' in same sentence",
                    "suggestion": "Remove one of the contradictory terms"
                }
        
        return {"logical": True}
    
    def _api_based_check(self, sentence: str, all_sentences: List[str], idx: int) -> Dict:
        """Use GLM API for advanced logic checking"""
        try:
            # Prepare context (previous and next sentences)
            context = ""
            if idx > 0:
                context += f"Previous: {all_sentences[idx-1]}\n"
            context += f"Current: {sentence}\n"
            if idx < len(all_sentences) - 1:
                context += f"Next: {all_sentences[idx+1]}"
            
            prompt = f"""Analyze if the following statement makes logical sense in context. 
Consider real-world facts, chronology, and common sense.

{context}

Answer in JSON format:
{{"logical": true/false, "reason": "brief explanation", "suggestion": "how to fix it"}}"""

            response = httpx.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [
                        {"role": "system", "content": "You are a logic checker. Identify illogical statements."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                # Parse JSON from response
                import json as json_lib
                # Find JSON in content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json_lib.loads(json_match.group())
                    return result
            
            return {"logical": True}
            
        except Exception as e:
            print(f"API logic check failed: {e}")
            return {"logical": True}