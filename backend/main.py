from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import re
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from checkers.british_spelling import BritishSpellingChecker
from checkers.groq_check import GroqChecker
from checkers.pdf_checker import PDFChecker

main = FastAPI(title="British English Checker API", version="1.0.0")

# ========== UPDATED CORS WITH YOUR VERCEL URL ==========
main.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.onrender.com",
        "https://quality-check-automation.vercel.app",  # Your Vercel URL
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

british_checker = BritishSpellingChecker()
groq_checker = GroqChecker()
pdf_checker = PDFChecker()

class TextCheckRequest(BaseModel):
    text: str

@main.get("/")
@main.get("/health")
async def health_check():
    return {"status": "healthy", "message": "British English Checker API is running", "version": "1.0.0"}

def apply_cleanup(text: str) -> str:
    """Clean up punctuation and spacing"""
    text = text.replace("??", "?")
    text = text.replace("?!", "?")
    text = text.replace("?.", "?")
    text = text.replace("!.", ".")
    text = text.replace("..", ".")
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@main.post("/api/check-text")
async def check_text(request: TextCheckRequest):
    text = request.text
    
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # British spelling check (local)
    spelling_issues = british_checker.check(text)
    text_with_british = british_checker.apply_corrections(text, spelling_issues)
    
    # Initialize results
    grammar_issues = []
    logic_issues = []
    coherence_result = {"score": 0.5, "warnings": []}
    final_corrected = text_with_british
    
    # Use Groq for ALL grammar, punctuation, logic, coherence
    if groq_checker.available:
        print("Using Groq API for full text analysis...")
        result = groq_checker.check_full_text(text_with_british)
        
        if result.get("corrected_text"):
            final_corrected = apply_cleanup(result.get("corrected_text"))
        
        grammar_issues = result.get("grammar_issues", [])
        logic_issues = result.get("logic_issues", [])
        coherence_result = {
            "score": result.get("coherence_score", 0.5),
            "warnings": result.get("coherence_warnings", [])
        }
        print(f"Groq found {len(grammar_issues)} grammar issues")
    else:
        print("Groq not available - check your API key")
    
    # ========== IMPROVED FILTERING ==========
    # Only show grammar issues that are NOT already fixed in the corrected text
    filtered_grammar_issues = []
    
    for issue in grammar_issues:
        original = issue.get("original", "")
        correction = issue.get("correction", "")
        
        # Skip if no original or correction
        if not original or not correction:
            filtered_grammar_issues.append(issue)
            continue
        
        # Check if the original error still exists in the corrected text
        # AND the correction is NOT already present
        original_exists = original in final_corrected
        correction_exists = correction in final_corrected
        
        # If the correction is already in the final text, don't show this issue
        if correction_exists:
            print(f"Skipping issue - already fixed: '{original}' → '{correction}'")
            continue
        
        # If the original still exists AND correction doesn't exist, show the issue
        if original_exists and not correction_exists:
            filtered_grammar_issues.append(issue)
        # If the original doesn't exist, the text is already correct
        elif not original_exists:
            print(f"Skipping issue - original not found: '{original}'")
            continue
        else:
            filtered_grammar_issues.append(issue)
    
    # Format spelling issues
    spelling_issues_formatted = []
    for issue in spelling_issues:
        spelling_issues_formatted.append({
            "message": "American spelling",
            "original": issue['original'],
            "correction": issue['suggestion'],
            "context": issue['context']
        })
    
    print(f"Final: {len(filtered_grammar_issues)} grammar issues shown (filtered from {len(grammar_issues)})")
    
    return {
        "original_text": text,
        "corrected_text": final_corrected,
        "british_spelling": spelling_issues_formatted[:15],
        "grammar_issues": filtered_grammar_issues[:15],
        "logic_issues": logic_issues[:10],
        "coherence": coherence_result
    }

@main.post("/api/check-image-alignment")
async def check_image_alignment(logo: UploadFile = File(...), background: UploadFile = File(...)):
    try:
        from utils.image_processor import ImageAlignmentChecker
        checker = ImageAlignmentChecker()
        result = checker.check_overlap(logo, background)
        return result
    except Exception as e:
        return {"error": str(e), "overlap_percent": 0}

# ========== PDF QC ENDPOINT ==========
@main.post("/api/check-pdf")
async def check_pdf(file: UploadFile = File(...)):
    """Check PDF document with page numbers and TOC validation"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        print(f"Processing PDF: {file.filename}")
        result = pdf_checker.check_pdf(temp_path)
        
        return JSONResponse(content={
            "filename": file.filename,
            "results": result
        })
        
    except Exception as e:
        print(f"PDF processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main, host="0.0.0.0", port=8000)