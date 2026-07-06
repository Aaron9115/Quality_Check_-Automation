from typing import List, Dict, Tuple
import re
import math

class CoherenceChecker:
    """Check document coherence and flow between sentences/paragraphs"""
    
    def __init__(self):
        # Common transition words that improve coherence
        self.transition_words = {
            "addition": ["and", "also", "furthermore", "moreover", "in addition"],
            "contrast": ["but", "however", "nevertheless", "on the other hand", "although"],
            "cause": ["because", "since", "therefore", "thus", "consequently"],
            "sequence": ["first", "second", "next", "then", "finally"],
            "example": ["for example", "for instance", "specifically", "such as"]
        }
    
    def check(self, text: str) -> Dict:
        """Check coherence and return score with warnings"""
        if not text or len(text.strip()) == 0:
            return {
                "score": 1.0,
                "warnings": [],
                "transitions": []
            }
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if len(sentences) < 2:
            return {
                "score": 1.0,
                "warnings": [],
                "transitions": []
            }
        
        # Calculate coherence metrics
        transitions = []
        warnings = []
        
        for i in range(len(sentences) - 1):
            current = sentences[i]
            next_sent = sentences[i + 1]
            
            # Check for transition words
            has_transition = self._has_transition_word(next_sent)
            
            # Check pronoun references
            pronoun_issue = self._check_pronoun_reference(current, next_sent)
            
            # Check topic similarity (simple word overlap)
            similarity = self._word_overlap_similarity(current, next_sent)
            
            transitions.append({
                "from": current[:50] + ("..." if len(current) > 50 else ""),
                "to": next_sent[:50] + ("..." if len(next_sent) > 50 else ""),
                "similarity": round(similarity, 2),
                "has_transition_word": has_transition
            })
            
            # Generate warnings for poor transitions
            if similarity < 0.2 and not has_transition:
                warnings.append(f"Abrupt topic shift between sentence {i+1} and {i+2}")
            
            if pronoun_issue:
                warnings.append(pronoun_issue)
        
        # Calculate overall coherence score (0-1, higher is better)
        if len(transitions) == 0:
            score = 1.0
        else:
            # Average similarity plus bonus for transition words
            avg_similarity = sum(t["similarity"] for t in transitions) / len(transitions)
            transition_bonus = sum(0.05 for t in transitions if t["has_transition_word"]) / len(transitions)
            score = min(1.0, avg_similarity + transition_bonus)
        
        return {
            "score": round(score, 2),
            "warnings": warnings[:5],  # Limit to 5 warnings
            "transitions": transitions
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle common abbreviations
        text = re.sub(r'(Mr|Ms|Mrs|Dr|Prof|Inc|etc)\.', r'\1<period>', text)
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        # Restore abbreviations
        sentences = [s.replace('<period>', '.') for s in sentences]
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _has_transition_word(self, sentence: str) -> bool:
        """Check if sentence starts with a transition word"""
        sentence_lower = sentence.lower().strip()
        
        for category, words in self.transition_words.items():
            for word in words:
                if sentence_lower.startswith(word):
                    return True
                # Also check if word appears early in sentence (first 10 chars)
                if sentence_lower[:15].find(word) != -1:
                    return True
        return False
    
    def _check_pronoun_reference(self, current: str, next_sent: str) -> str:
        """Check for unclear pronoun references"""
        pronouns = ["it", "they", "them", "he", "she", "we", "you"]
        
        next_lower = next_sent.lower()
        current_lower = current.lower()
        
        for pronoun in pronouns:
            if next_lower.startswith(pronoun) or next_lower.find(f" {pronoun} ") != -1:
                # Check if pronoun has clear antecedent in previous sentence
                # Simple check: look for nouns in previous sentence
                words = re.findall(r'\b[a-z]{3,}\b', current_lower)
                nouns = [w for w in words if w not in ["the", "and", "for", "but", "or", "so"]]
                
                if len(nouns) == 0 and len(current) > 10:
                    return f"Unclear pronoun '{pronoun}' at start of sentence - what does it refer to?"
        return ""
    
    def _word_overlap_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity based on word overlap (simplified)"""
        # Clean and tokenize
        words1 = set(re.findall(r'\b[a-z]{3,}\b', sent1.lower()))
        words2 = set(re.findall(r'\b[a-z]{3,}\b', sent2.lower()))
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        # Boost for shared key terms (nouns/verbs, not stopwords)
        stopwords = {"the", "and", "for", "but", "or", "so", "this", "that", "these", "those"}
        content_words1 = {w for w in words1 if w not in stopwords}
        content_words2 = {w for w in words2 if w not in stopwords}
        
        if len(content_words1) > 0 and len(content_words2) > 0:
            content_intersection = len(content_words1 & content_words2)
            content_union = len(content_words1 | content_words2)
            content_similarity = content_intersection / content_union if content_union > 0 else 0
            # Weight content similarity higher
            return (intersection / union) * 0.4 + content_similarity * 0.6
        else:
            return intersection / union