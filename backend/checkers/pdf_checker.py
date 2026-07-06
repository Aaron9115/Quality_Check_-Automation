import fitz  # PyMuPDF
import pdfplumber
import re
from typing import List, Dict, Tuple
from checkers.groq_check import GroqChecker
from checkers.british_spelling import BritishSpellingChecker

class PDFChecker:
    def __init__(self):
        self.groq_checker = GroqChecker()
        self.british_checker = BritishSpellingChecker()
    
    def extract_text_with_pages(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers"""
        pages = []
        
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                pages.append({
                    "page_number": page_num + 1,
                    "text": text.strip(),
                    "word_count": len(text.split())
                })
        doc.close()
        
        return pages
    
    def extract_toc(self, pdf_path: str) -> List[Dict]:
        """Extract Table of Contents from PDF"""
        toc_entries = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Look for TOC patterns: "Chapter 1 ........ 5"
                    # or "Introduction ......... 1"
                    lines = text.split('\n')
                    for line in lines:
                        # Match patterns like: "Chapter 1 ........ 5"
                        match = re.search(r'^(.*?)(\.+|\s+)(\d+)$', line.strip())
                        if match:
                            title = match.group(1).strip()
                            page_ref = int(match.group(3))
                            toc_entries.append({
                                "title": title,
                                "listed_page": page_ref,
                                "actual_page": page_num
                            })
                        # Also match: "Chapter 1 - 5"
                        match2 = re.search(r'^(.*?)\s*[-–]\s*(\d+)$', line.strip())
                        if match2:
                            title = match2.group(1).strip()
                            page_ref = int(match2.group(2))
                            toc_entries.append({
                                "title": title,
                                "listed_page": page_ref,
                                "actual_page": page_num
                            })
        except Exception as e:
            print(f"TOC extraction error: {e}")
        
        return toc_entries
    
    def validate_toc(self, toc_entries: List[Dict]) -> List[Dict]:
        """Validate TOC entries against actual pages"""
        validation_results = []
        
        for entry in toc_entries:
            is_match = entry["listed_page"] == entry["actual_page"]
            validation_results.append({
                **entry,
                "is_valid": is_match,
                "status": "✔" if is_match else "✖",
                "difference": entry["actual_page"] - entry["listed_page"]
            })
        
        return validation_results
    
    def check_page_text(self, page_text: str, page_num: int) -> Dict:
        """Run all checks on a single page"""
        issues = {
            "page_number": page_num,
            "grammar_issues": [],
            "logic_issues": [],
            "british_spelling": [],
            "coherence": {"score": 0.5, "warnings": []}
        }
        
        # British spelling check
        spelling_issues = self.british_checker.check(page_text)
        issues["british_spelling"] = spelling_issues
        
        # Grammar and logic using Groq
        if self.groq_checker.available:
            result = self.groq_checker.check_full_text(page_text)
            issues["grammar_issues"] = result.get("grammar_issues", [])
            issues["logic_issues"] = result.get("logic_issues", [])
            issues["coherence"] = {
                "score": result.get("coherence_score", 0.5),
                "warnings": result.get("coherence_warnings", [])
            }
        
        return issues
    
    def check_pdf(self, pdf_path: str) -> Dict:
        """Complete PDF check with page numbers and TOC validation"""
        
        # Extract text with page numbers
        pages = self.extract_text_with_pages(pdf_path)
        print(f"Extracted {len(pages)} pages from PDF")
        
        # Check each page
        page_results = []
        for page in pages:
            result = self.check_page_text(page["text"], page["page_number"])
            result["word_count"] = page["word_count"]
            page_results.append(result)
        
        # Extract and validate TOC
        toc_entries = self.extract_toc(pdf_path)
        toc_validation = self.validate_toc(toc_entries)
        
        # Overall summary
        total_issues = {
            "grammar": sum(len(p["grammar_issues"]) for p in page_results),
            "logic": sum(len(p["logic_issues"]) for p in page_results),
            "spelling": sum(len(p["british_spelling"]) for p in page_results),
            "toc_mismatches": sum(1 for t in toc_validation if not t["is_valid"])
        }
        
        # Format results for frontend
        formatted_results = {
            "total_pages": len(pages),
            "page_results": page_results,
            "toc_validation": toc_validation,
            "summary": total_issues,
            "overall_score": self._calculate_overall_score(page_results, toc_validation)
        }
        
        return formatted_results
    
    def _calculate_overall_score(self, page_results: List[Dict], toc_validation: List[Dict]) -> float:
        """Calculate overall document quality score"""
        if not page_results:
            return 0.0
        
        # Base score (grammar + logic issues)
        total_pages = len(page_results)
        grammar_issues = sum(len(p["grammar_issues"]) for p in page_results)
        logic_issues = sum(len(p["logic_issues"]) for p in page_results)
        total_issues = grammar_issues + logic_issues
        
        # Penalize issues
        issue_penalty = min(total_issues / 10, 0.5)
        
        # Penalize TOC mismatches
        toc_penalty = sum(1 for t in toc_validation if not t["is_valid"]) * 0.1
        
        score = 1.0 - issue_penalty - toc_penalty
        return max(0.0, min(1.0, score))