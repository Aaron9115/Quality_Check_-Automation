import json
import os
import re
from typing import List, Dict, Tuple

class BritishSpellingChecker:
    """Convert US English to British English spellings"""
    
    def __init__(self, mapping_file=None):
        # Default US to UK mappings
        self.us_to_uk = {
            # -or to -our
            "color": "colour",
            "favor": "favour",
            "honor": "honour",
            "neighbor": "neighbour",
            "behavior": "behaviour",
            "labor": "labour",
            "rumor": "rumour",
            "savor": "savour",
            "flavor": "flavour",
            "harbor": "harbour",
            "ardor": "ardour",
            "armor": "armour",
            "candor": "candour",
            "clamor": "clamour",
            "endeavor": "endeavour",
            "glamor": "glamour",
            "humor": "humour",
            "pallor": "pallour",
            "rancor": "rancour",
            "rigor": "rigour",
            "splendor": "splendour",
            "tumor": "tumour",
            "valor": "valour",
            "vapor": "vapour",
            "vigor": "vigour",
            
            # -ize to -ise
            "organize": "organise",
            "realize": "realise",
            "recognize": "recognise",
            "analyze": "analyse",
            "criticize": "criticise",
            "emphasize": "emphasise",
            "summarize": "summarise",
            "standardize": "standardise",
            "visualize": "visualise",
            "specialize": "specialise",
            "authorize": "authorise",
            "characterize": "characterise",
            "civilize": "civilise",
            "colonize": "colonise",
            "dramatize": "dramatise",
            "fertilize": "fertilise",
            "formalize": "formalise",
            "globalize": "globalise",
            "harmonize": "harmonise",
            "immortalize": "immortalise",
            "legalize": "legalise",
            "localize": "localise",
            "mobilize": "mobilise",
            "modernize": "modernise",
            "moralize": "moralise",
            "naturalize": "naturalise",
            "normalize": "normalise",
            "organize": "organise",
            "popularize": "popularise",
            "rationalize": "rationalise",
            "socialize": "socialise",
            "standardize": "standardise",
            "sympathize": "sympathise",
            "systematize": "systematise",
            "theorize": "theorise",
            "visualize": "visualise",
            
            # -se vs -ze (nouns)
            "analyze": "analyse",
            
            # Single L vs Double L
            "panelist": "panellist",
            "traveled": "travelled",
            "traveling": "travelling",
            "traveler": "traveller",
            "canceled": "cancelled",
            "canceling": "cancelling",
            "counseled": "counselled",
            "counseling": "counselling",
            "fueled": "fuelled",
            "fueling": "fuelling",
            "labeled": "labelled",
            "labeling": "labelling",
            "marveled": "marvelled",
            "marveling": "marvelling",
            "modeled": "modelled",
            "modeling": "modelling",
            "quarreled": "quarrelled",
            "quarreling": "quarrelling",
            "signaled": "signalled",
            "signaling": "signalling",
            "worshiped": "worshipped",
            "worshiping": "worshipping",
            
            # -eable vs -able
            "likeable": "likable",
            
            # Other common differences
            "aluminum": "aluminium",
            "apologize": "apologise",
            "appetizer": "appetiser",
            "archaeology": "archeology",
            "catalog": "catalogue",
            "dialog": "dialogue",
            "check": "cheque",  # financial context
            "defense": "defence",
            "draft": "draught",
            "gray": "grey",
            "jail": "gaol",
            "jewelry": "jewellery",
            "judgment": "judgement",
            "license": "licence",  # noun
            "offense": "offence",
            "plow": "plough",
            "practice": "practise",  # verb
            "program": "programme",
            "skeptical": "sceptical",
            "tire": "tyre",  # wheel
            "zeal": "zeal"
        }
        
        # Load custom mappings if file exists
        if mapping_file and os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                custom = json.load(f)
                self.us_to_uk.update(custom)
    
    def check(self, text: str) -> List[Dict]:
        """Find US spellings that should be British"""
        issues = []
        text_lower = text.lower()
        
        for us, uk in self.us_to_uk.items():
            # Find all occurrences (case insensitive)
            pattern = re.compile(r'\b' + re.escape(us) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                # Get position in original text (not lowercased)
                start = match.start()
                end = match.end()
                
                issues.append({
                    "original": text[start:end],  # Preserve original case
                    "suggestion": self._preserve_case(text[start:end], uk),
                    "position": [start, end],
                    "context": text[max(0, start-20):min(len(text), end+20)]
                })
        
        return issues
    
    def apply_corrections(self, text: str, issues: List[Dict]) -> str:
        """Apply British spelling corrections to text"""
        corrected = text
        # Apply from end to start to preserve positions
        for issue in sorted(issues, key=lambda x: x["position"][0], reverse=True):
            start, end = issue["position"]
            corrected = corrected[:start] + issue["suggestion"] + corrected[end:]
        return corrected
    
    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve the case pattern from original word"""
        if original.isupper():
            return replacement.upper()
        elif original[0].isupper() and original[1:].islower():
            return replacement.capitalize()
        elif original[0].isupper() and original[1:].isupper():
            return replacement.upper()
        else:
            return replacement.lower()