import re
from typing import Dict, List

class ReadabilityChecker:
    """Calculate readability scores for text"""
    
    def __init__(self):
        self.syllable_cache = {}
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        if word in self.syllable_cache:
            return self.syllable_cache[word]
        
        word = word.lower().strip('.,!?;:')
        if not word:
            return 0
        
        count = 0
        vowels = 'aeiouy'
        
        # Handle common exceptions
        if word.endswith('es') or word.endswith('ed'):
            word = word[:-2]
        elif word.endswith('e'):
            word = word[:-1]
        
        # Count vowel groups
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        self.syllable_cache[word] = max(1, count)
        return self.syllable_cache[word]
    
    def calculate_flesch_kincaid(self, text: str) -> Dict:
        """Calculate Flesch-Kincaid Grade Level"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences)
        
        if num_sentences == 0:
            return {"score": 0, "grade": "No text", "interpretation": ""}
        
        # Count words and syllables
        total_words = 0
        total_syllables = 0
        
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence)
            total_words += len(words)
            for word in words:
                total_syllables += self._count_syllables(word)
        
        if total_words == 0:
            return {"score": 0, "grade": "No words", "interpretation": ""}
        
        # Calculate scores
        words_per_sentence = total_words / num_sentences
        syllables_per_word = total_syllables / total_words
        
        # Flesch Reading Ease (0-100, higher is easier)
        reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        
        # Flesch-Kincaid Grade Level
        grade_level = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59
        
        # Interpret scores
        interpretation = self._interpret_score(reading_ease)
        
        return {
            "reading_ease": round(reading_ease, 1),
            "grade_level": round(grade_level, 1),
            "words_per_sentence": round(words_per_sentence, 1),
            "syllables_per_word": round(syllables_per_word, 2),
            "interpretation": interpretation,
            "total_words": total_words,
            "total_sentences": num_sentences
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret the Flesch Reading Ease score"""
        if score >= 90:
            return "Very Easy (5th grade level)"
        elif score >= 80:
            return "Easy (6th grade level)"
        elif score >= 70:
            return "Fairly Easy (7th grade level)"
        elif score >= 60:
            return "Standard (8th-9th grade level)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade level)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (College graduate level)"
    
    def find_complex_sentences(self, text: str, max_words: int = 25) -> List[Dict]:
        """Find sentences that are too long or complex"""
        sentences = re.split(r'[.!?]+', text)
        complex_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            words = re.findall(r'\b\w+\b', sentence)
            word_count = len(words)
            
            if word_count > max_words:
                complex_sentences.append({
                    "index": i + 1,
                    "sentence": sentence,
                    "word_count": word_count,
                    "suggestion": f"Consider breaking this {word_count}-word sentence into shorter ones"
                })
        
        return complex_sentences