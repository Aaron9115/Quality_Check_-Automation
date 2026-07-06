import httpx
from typing import List, Dict, Optional

class GrammarChecker:
    """Check grammar using LanguageTool API (free)"""
    
    def __init__(self):
        self.api_url = "https://api.languagetool.org/v2/check"
        self.language = "en-GB"  # British English
    
    def check(self, text: str) -> List[Dict]:
        """Check grammar and return issues"""
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            # Call LanguageTool API
            response = httpx.post(
                self.api_url,
                data={
                    "text": text,
                    "language": self.language,
                    "enabledOnly": "false"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                # Format issues for frontend
                issues = []
                for match in matches:
                    replacements = [rep["value"] for rep in match.get("replacements", [])]
                    
                    issues.append({
                        "message": match.get("message", "Grammar issue detected"),
                        "replacements": replacements[:3],  # Top 3 suggestions
                        "offset": match.get("offset", 0),
                        "length": match.get("length", 0),
                        "rule_id": match.get("rule", {}).get("id", "unknown"),
                        "context": match.get("context", {}).get("text", "")
                    })
                
                return issues
            else:
                return []
                
        except httpx.TimeoutException:
            # API timeout - return empty (graceful degradation)
            return []
        except Exception as e:
            print(f"Grammar check error: {e}")
            return []
    
    def check_sentence(self, sentence: str) -> List[Dict]:
        """Check a single sentence (used internally)"""
        return self.check(sentence)