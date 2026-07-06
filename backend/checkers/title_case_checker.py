import re
from typing import List, Dict

class TitleCaseChecker:
    """Check headings against Chicago Title Case rules"""
    
    def __init__(self):
        self.lowercase_words = {
            'a', 'an', 'the',
            'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
            'at', 'by', 'for', 'in', 'of', 'on', 'to', 'up', 'off', 'out', 'per',
            'via', 'with', 'without', 'under', 'over', 'through', 'across', 'along',
            'into', 'onto', 'upon', 'within', 'outside', 'against', 'between', 'among',
            'throughout', 'beyond', 'during', 'without'
        }
        
        self.uppercase_words = {
            'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
            'API', 'CEO', 'CFO', 'CTO', 'COVID', 'AI', 'ML', 'UK', 'USA', 'EU'
        }
    
    def check_title(self, title: str) -> Dict:
        """Check if a title follows Chicago Title Case"""
        original = title.strip()
        words = original.split()
        
        if len(words) <= 1:
            return {
                "is_correct": True,
                "original": original,
                "corrected": original,
                "issues": []
            }
        
        corrected_words = []
        issues = []
        
        for i, word in enumerate(words):
            # Check if word is all caps acronym
            if word.isupper() and len(word) > 1:
                corrected_words.append(word)
                continue
            
            # Check if word should be uppercase (custom list)
            if word in self.uppercase_words:
                corrected_words.append(word)
                continue
            
            # First and last words always capitalize
            if i == 0 or i == len(words) - 1:
                if word:
                    corrected = word[0].upper() + word[1:].lower()
                else:
                    corrected = word
                if corrected != word:
                    issues.append({
                        "position": i,
                        "original": word,
                        "corrected": corrected,
                        "rule": "First/last word must be capitalized"
                    })
                corrected_words.append(corrected)
                continue
            
            # Words with hyphens
            if '-' in word:
                parts = word.split('-')
                hyphenated_parts = []
                for part in parts:
                    if part.lower() in self.lowercase_words:
                        hyphenated_parts.append(part.lower())
                    else:
                        if part:
                            hyphenated_parts.append(part[0].upper() + part[1:].lower())
                        else:
                            hyphenated_parts.append(part)
                corrected = '-'.join(hyphenated_parts)
                if corrected != word:
                    issues.append({
                        "position": i,
                        "original": word,
                        "corrected": corrected,
                        "rule": "Hyphenated word case"
                    })
                corrected_words.append(corrected)
                continue
            
            # Check if word should be lowercase
            word_lower = word.lower()
            if word_lower in self.lowercase_words:
                corrected = word_lower
                if corrected != word:
                    issues.append({
                        "position": i,
                        "original": word,
                        "corrected": corrected,
                        "rule": f"'{word}' should be lowercase (preposition/conjunction)"
                    })
                corrected_words.append(corrected)
            else:
                # Capitalize normal words
                if word:
                    corrected = word[0].upper() + word[1:].lower()
                else:
                    corrected = word
                if corrected != word:
                    issues.append({
                        "position": i,
                        "original": word,
                        "corrected": corrected,
                        "rule": "Capitalize major words"
                    })
                corrected_words.append(corrected)
        
        corrected_title = ' '.join(corrected_words)
        
        return {
            "is_correct": original == corrected_title,
            "original": original,
            "corrected": corrected_title,
            "issues": issues
        }
    
    def extract_headings(self, text: str) -> List[Dict]:
        """Extract headings from markdown or plain text"""
        headings = []
        
        # Markdown headings (# Heading)
        md_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(md_pattern, text, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2)
            headings.append({
                "type": "markdown",
                "level": level,
                "original": title,
                "full_line": match.group(0)
            })
        
        # Plain text headings (lines ending with : or lines in all caps)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 100:
                if line.endswith(':') or (line.isupper() and len(line) > 3):
                    already_exists = False
                    for h in headings:
                        if h["original"] == line.rstrip(':'):
                            already_exists = True
                            break
                    if not already_exists:
                        headings.append({
                            "type": "plain",
                            "level": 1,
                            "original": line.rstrip(':'),
                            "full_line": line
                        })
        
        return headings
    
    def check_all_headings(self, text: str) -> List[Dict]:
        """Check all headings in the text"""
        headings = self.extract_headings(text)
        results = []
        for heading in headings:
            title_result = self.check_title(heading["original"])
            results.append({
                "heading": heading,
                "check": title_result
            })
        return results