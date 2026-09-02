"""
AI Recruiter — Resume Parser & Analyzer

Extracts structured data from resumes (PDF, DOCX, TXT) and analyzes
them against job requirements using LLM-based scoring.
"""

import os
import io
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    import ollama
except ImportError:
    ollama = None

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:latest")


class ResumeData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    certifications: List[str] = []


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    if pdfplumber is None:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    if docx is None:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text(file_path: str) -> str:
    """Extract text from any supported file type."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_with_llm(text: str) -> Dict[str, Any]:
    """Use Ollama to extract structured data from resume text."""
    prompt = f"""
Extract the following information from this resume text. Return JSON only.

Resume Text:
{text[:5000]}

Extract:
- name: Full name
- email: Email address
- phone: Phone number
- location: City, State
- summary: Professional summary (max 100 words)
- experience: List of {{company, role, duration, description}} objects
- education: List of {{institution, degree, duration}} objects
- skills: List of technical/soft skills
- certifications: List of certifications

Return as JSON with these exact keys. If a field is not found, use empty/null.
"""
    if ollama:
        try:
            client = ollama.Client(host=OLLAMA_HOST)
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3, "num_predict": 2048},
            )
            import json
            return json.loads(response["message"]["content"])
        except Exception as e:
            return {"error": str(e)}
    # Fallback: basic regex extraction
    return extract_basic(text)


def extract_basic(text: str) -> Dict[str, Any]:
    """Basic regex-based extraction as fallback."""
    email = re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
    phone = re.search(r'\b\d{10}\b', text)
    name = text.split('\n')[0].strip() if text else ""

    # Extract skills from common patterns
    skills = []
    skill_keywords = ["python", "javascript", "react", "node.js", "typescript",
                      "aws", "docker", "kubernetes", "sql", "mongodb", "git",
                      "java", "c++", "machine learning", "data analysis"]
    text_lower = text.lower()
    for kw in skill_keywords:
        if kw in text_lower:
            skills.append(kw.title())

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else None,
        "location": None,
        "summary": None,
        "experience": [],
        "education": [],
        "skills": skills[:15],
        "certifications": [],
    }


def score_resume(resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Score a resume against a job description.
    Returns match score, key skills found, missing skills, and explanation.
    """
    prompt = f"""
You are an AI recruiter. Score the candidate's resume against the job description.

Job Description:
{job_description[:3000]}

Candidate Resume:
Name: {resume.get('name', '')}
Summary: {resume.get('summary', '')}
Experience: {resume.get('experience', [])}
Education: {resume.get('education', [])}
Skills: {resume.get('skills', [])}
Certifications: {resume.get('certifications', [])}

Score 0-100 and return JSON with:
- match_score: integer 0-100
- key_strengths: list of 3-5 strings matching candidate to job
- missing_skills: list of skills the candidate lacks for this role
- experience_match: string describing experience relevance ("strong", "moderate", "weak")
- explanation: string (2-3 sentences) explaining the score
"""

    if ollama:
        try:
            client = ollama.Client(host=OLLAMA_HOST)
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3, "num_predict": 2048},
            )
            import json
            result = json.loads(response["message"]["content"])
            return result
        except Exception as e:
            return {"error": str(e), "match_score": 0}

    # Fallback scoring
    skills = resume.get("skills", [])
    skills_text = " ".join(skills).lower()
    job_text_lower = job_description.lower()

    # Simple keyword matching
    job_skills_found = []
    for word in re.findall(r'\b\w+\b', job_text_lower):
        if len(word) > 3 and word in skills_text:
            job_skills_found.append(word)

    score = min(100, len(job_skills_found) * 5 + 20)

    return {
        "match_score": score,
        "key_strengths": job_skills_found[:5],
        "missing_skills": [],
        "experience_match": "moderate",
        "explanation": f"Basic keyword matching found {len(job_skills_found)} skill matches.",
    }
