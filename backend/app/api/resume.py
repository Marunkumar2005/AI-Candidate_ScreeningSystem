from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.resume_service import extract_text_from_pdf, extract_resume_info

router = APIRouter()


class ResumeTextRequest(BaseModel):
    text: str
    role: str


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...)
):
    """Upload and parse a resume PDF."""
    content = await file.read()
    
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(content)
    else:
        try:
            resume_text = content.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")
    
    info = extract_resume_info(resume_text, role)
    return {
        "resume_text": resume_text,
        "extracted_info": info
    }


@router.post("/parse-text")
async def parse_resume_text(request: ResumeTextRequest):
    """Parse resume from plain text."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty")
    info = extract_resume_info(request.text, request.role)
    return {
        "resume_text": request.text,
        "extracted_info": info
    }
