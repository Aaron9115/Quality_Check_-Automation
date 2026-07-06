import re
from typing import List, Dict
from collections import Counter

class RepetitionChecker:
    """Detect repeated words, phrases, and ideas"""
    
    def __init__(self):
        self.common_words = {
            'the', 'and', 'of', 'to', 'in', 'for', 'on', 'with', 
            'by', 'at', 'a', 'an', 'is', 'are', 'was', 'were'
        }
    
    def find_repeated_words(self, text: str, distance: int = 10) -> List[Dict]:
        """Find words repeated within a certain distance"""
        words = re.findall(r'\b\w+\b', text.lower())
        repeated = []
        
        for i, word in enumerate(words):
            if word in self.common_words:
                continue
            
            # Check forward within distance
            for j in range(i + 1, min(i + distance, len(words))):
                if words[j] == word:
                    context_start = max(0, i - 3)
                    context_end = min(len(words), j + 4)
                    repeated.append({
                        "type": "adjacent_word",
                        "word": word,
                        "position": i,
                        "next_position": j,
                        "context": ' '.join(words[context_start:context_end]),
                        "suggestion": f"Replace second '{word}' with a synonym"
                    })
                    break
        
        # Remove duplicates
        seen = set()
        unique_repeated = []
        for r in repeated:
            key = f"{r['word']}_{r['position']}"
            if key not in seen:
                seen.add(key)
                unique_repeated.append(r)
        
        return unique_repeated[:10]
    
    def find_repeated_phrases(self, text: str, min_length: int = 3) -> List[Dict]:
        """Find repeated phrases"""
        words = re.findall(r'\b\w+\b', text.lower())
        phrases = Counter()
        
        # Extract phrases of length min_length
        for i in range(len(words) - min_length + 1):
            phrase = ' '.join(words[i:i + min_length])
            skip = False
            for common in self.common_words:
                if common in phrase.split():
                    skip = True
                    break
            if not skip:
                phrases[phrase] += 1
        
        repeated_phrases = []
        for phrase, count in phrases.items():
            if count > 1:
                repeated_phrases.append({
                    "phrase": phrase,
                    "count": count,
                    "suggestion": f"Consider rephrasing to avoid repeating '{phrase}'"
                })
        
        return repeated_phrases[:5]
    
    def find_redundant_pairs(self, text: str) -> List[Dict]:
        """Find redundant word pairs (e.g., 'free gift', 'end result')"""
        redundant_pairs = [
            ("free gift", "gift"),
            ("end result", "result"),
            ("past history", "history"),
            ("future plans", "plans"),
            ("final outcome", "outcome"),
            ("added bonus", "bonus"),
            ("unexpected surprise", "surprise"),
            ("close proximity", "proximity"),
            ("exact same", "same"),
            ("completely eliminate", "eliminate"),
            ("each and every", "each"),
            ("first and foremost", "first"),
            ("in order to", "to"),
            ("whether or not", "whether"),
        ]
        
        text_lower = text.lower()
        found = []
        
        for redundant, better in redundant_pairs:
            if redundant in text_lower:
                found.append({
                    "redundant": redundant,
                    "better": better,
                    "suggestion": f"Replace '{redundant}' with '{better}'"
                })
        
        return found