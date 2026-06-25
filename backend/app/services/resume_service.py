import re
import io
from typing import Dict, List
import openai
import os
from app.core.config import settings

# Try to import PDF parser
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not PDF_SUPPORT:
        return ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception:
        return ""


def extract_resume_info(resume_text: str, role: str) -> Dict:
    """Use OpenAI to extract structured info from resume."""
    if not settings.OPENAI_API_KEY:
        return _fallback_extraction(resume_text)

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""You are a resume parser. Extract key information from this resume for a {role} position.

Resume:
{resume_text[:3000]}

Return a JSON object with:
{{
  "candidate_name": "name or Unknown",
  "skills": ["skill1", "skill2", ...],
  "technologies": ["tech1", "tech2", ...],
  "experience_years": 0,
  "education": "highest degree",
  "domains": ["domain1", ...],
  "summary": "2-sentence professional summary"
}}

Return only valid JSON, no markdown."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600
        )
        import json
        text = response.choices[0].message.content.strip()
        return json.loads(text)
    except Exception:
        return _fallback_extraction(resume_text)


def _fallback_extraction(text: str) -> Dict:
    """Simple regex-based fallback extractor."""
    skill_keywords = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
        "React", "Node.js", "FastAPI", "Flask", "Django", "Spring",
        "TensorFlow", "PyTorch", "Keras", "scikit-learn", "pandas", "numpy",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
        "AWS", "GCP", "Azure", "Git", "REST", "GraphQL", "Machine Learning",
        "Deep Learning", "NLP", "Computer Vision", "Data Science",
    ]
    
    found_skills = [s for s in skill_keywords if s.lower() in text.lower()]
    
    # Try to extract name from first lines
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    candidate_name = lines[0] if lines else "Unknown"
    
    return {
        "candidate_name": candidate_name,
        "skills": found_skills[:10],
        "technologies": found_skills[:8],
        "experience_years": 0,
        "education": "Not extracted",
        "domains": [],
        "summary": f"Candidate with skills in {', '.join(found_skills[:3])}" if found_skills else "Resume parsed"
    }
