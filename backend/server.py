"""
AI Recruiter — Backend API Server

FastAPI server providing:
- Resume parsing & analysis
- AI mock interview simulation
- Candidate scoring & ranking
"""

import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from resume_parser import extract_text, extract_with_llm, extract_basic, score_resume
from interview_simulator import (
    generate_interview_questions,
    evaluate_answer,
    conduct_mock_interview,
)

UPLOAD_DIR = "/tmp/ai-recruiter-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="AI Recruiter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────

class JobDescription(BaseModel):
    title: str
    description: str
    requirements: List[str] = []
    experience_level: str = "mid"


class ResumeParseResult(BaseModel):
    resume_text: str
    parsed_data: dict
    confidence: str


class InterviewConfig(BaseModel):
    job_role: str
    experience_level: str = "mid"
    num_questions: int = 5
    categories: List[str] = ["technical", "behavioral"]


# ── Routes ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"service": "AI Recruiter API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "upload_dir": UPLOAD_DIR}


# ── Resume Parsing ───────────────────────────────────────────

@app.post("/api/resume/parse")
async def parse_resume(
    file: UploadFile = File(...),
    use_llm: bool = Form(True),
):
    """Parse a resume file (PDF, DOCX, TXT) and extract structured data."""
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Extract text
        text = extract_text(file_path)

        # Parse
        if use_llm:
            parsed = extract_with_llm(text)
        else:
            parsed = extract_basic(text)

        # Clean up
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        confidence = "CONFIRMED" if use_llm and "error" not in parsed else "ESTIMATED"

        return {
            "success": True,
            "file_id": file_id,
            "file_name": file.filename,
            "resume_text": text,
            "parsed_data": parsed,
            "confidence": confidence,
            "pages": len(text.split('\n')),
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/api/resume/score")
async def score_resume_endpoint(
    resume_data: dict,
    job: JobDescription,
):
    """Score a resume against a job description."""
    try:
        result = score_resume(resume_data, job.description)
        return {"success": True, "result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/api/resume/parse-and-score")
async def parse_and_score(
    file: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
):
    """Parse resume and score against job in one call."""
    try:
        # Parse resume
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        text = extract_text(file_path)
        parsed = extract_with_llm(text)

        # Score
        score = score_resume(parsed, job_description)

        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        return {
            "success": True,
            "parsed_data": parsed,
            "score": score,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ── Interview Simulation ───────────────────────────────────────

@app.post("/api/interview/questions")
async def get_interview_questions(config: InterviewConfig):
    """Generate interview questions for a role."""
    questions = await generate_interview_questions(
        config.job_role,
        config.experience_level,
        config.num_questions,
        config.categories,
    )
    return {"success": True, "questions": questions}


@app.post("/api/interview/evaluate")
async def evaluate_single_answer(
    question: str,
    answer: str,
    job_role: str,
    experience_level: str = "mid",
):
    """Evaluate a single interview answer."""
    result = await evaluate_answer(question, answer, job_role, experience_level)
    return {"success": True, "evaluation": result}


@app.post("/api/interview/conduct")
async def conduct_interview(
    config: InterviewConfig,
    answers: List[str],
):
    """Conduct a full mock interview with scoring."""
    result = await conduct_mock_interview(
        config.job_role,
        config.experience_level,
        answers,
        num_questions=config.num_questions,
    )
    return {"success": True, "result": result}


# ── Candidate Ranking ──────────────────────────────────────────

@app.post("/api/rank")
async def rank_candidates(
    resumes: List[dict],
    job: JobDescription,
):
    """Rank multiple candidates against a job description."""
    scored = []
    for resume in resumes:
        try:
            score = score_resume(resume, job.description)
            scored.append({
                "candidate": resume.get("name", "Unknown"),
                "score": score.get("match_score", 0),
                "email": resume.get("email", ""),
                "key_strengths": score.get("key_strengths", []),
                "missing_skills": score.get("missing_skills", []),
                "experience_match": score.get("experience_match", "unknown"),
            })
        except Exception as e:
            scored.append({
                "candidate": resume.get("name", "Unknown"),
                "score": 0,
                "error": str(e),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"success": True, "rankings": scored}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
