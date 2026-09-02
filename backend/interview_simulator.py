"""
AI Recruiter — Interview Simulator

Generates and conducts mock interviews using LLM,
provides scoring and feedback.
"""

import os
import json
from typing import Dict, Any, List
from pydantic import BaseModel

try:
    import ollama
except ImportError:
    ollama = None

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:latest")


class InterviewQuestion(BaseModel):
    question: str
    category: str  # technical, behavioral, situational
    difficulty: str  # easy, medium, hard


class InterviewSession(BaseModel):
    id: str
    job_role: str
    experience_level: str
    questions: List[InterviewQuestion] = []
    answers: List[Dict[str, Any]] = []
    current_q: int = 0
    status: str = "pending"  # pending, active, completed


# ── Question Generation ──

async def generate_interview_questions(
    job_role: str,
    experience_level: str = "mid",
    num_questions: int = 5,
    categories: List[str] = None
) -> List[Dict[str, str]]:
    """Generate interview questions using Ollama LLM."""
    if categories is None:
        categories = ["technical", "behavioral"]

    prompt = f"""
Generate {num_questions} interview questions for a {experience_level}-level 
{job_role} position.

Categories to include: {', '.join(categories)}

For each question, include:
- The question text
- Category (technical, behavioral, or situational)
- Difficulty (easy, medium, or hard)

Return only a JSON array with objects having keys: question, category, difficulty.
"""
    if ollama:
        try:
            client = ollama.AsyncClient(host=OLLAMA_HOST)
            response = await client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 2048},
            )
            return json.loads(response["message"]["content"])
        except Exception as e:
            return [{"error": str(e)}]
    else:
        # Fallback: basic questions
        return generate_fallback_questions(job_role, num_questions, categories)


def generate_fallback_questions(
    job_role: str, num: int, categories: List[str]
) -> List[Dict[str, str]]:
    """Generate basic fallback questions."""
    technical = [
        f"What are the key technical challenges in {job_role} work?",
        f"How do you stay current with {job_role} technologies?",
        f"Describe a complex project you worked on related to {job_role}.",
    ]
    behavioral = [
        "Tell me about a time you had to solve a difficult problem at work.",
        "Describe a situation where you had to work with a difficult team member.",
        "Tell me about a time you had to learn something completely new quickly.",
    ]
    situational = [
        "How would you handle a tight deadline with changing requirements?",
        "What would you do if you disagreed with your manager?",
        "How do you handle conflicting priorities?",
    ]

    questions = []
    for i in range(num):
        if "technical" in categories and i < len(technical):
            questions.append({"question": technical[i], "category": "technical", "difficulty": "medium"})
        elif "behavioral" in categories and i < len(behavioral):
            questions.append({"question": behavioral[i], "category": "behavioral", "difficulty": "medium"})
        elif "situational" in categories and i < len(situational):
            questions.append({"question": situational[i], "category": "situational", "difficulty": "medium"})

    return questions


# ── Answer Evaluation ──

async def evaluate_answer(
    question: str,
    answer: str,
    job_role: str,
    experience_level: str
) -> Dict[str, Any]:
    """Evaluate an interview answer and provide feedback."""
    prompt = f"""
You are an experienced hiring manager conducting a {job_role} interview.

Question: {question}
Candidate's Answer: {answer}

Evaluate this answer and return JSON with:
- score: integer 0-10 (how well this answer addresses the question)
- relevance: 0-10 (how relevant the answer is to a {job_role} role)
- communication: 0-10 (clarity and conciseness of communication)
- strengths: list of 2-3 things the candidate did well
- areas_for_improvement: list of 2-3 areas to improve
- key_points: list of key points the candidate mentioned
- missed_points: list of important points the candidate missed
- overall_feedback: 2-3 sentence summary

Be constructive and helpful in your feedback.
"""
    if ollama:
        try:
            client = ollama.AsyncClient(host=OLLAMA_HOST)
            response = await client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.5, "num_predict": 2048},
            )
            result = json.loads(response["message"]["content"])
            return result
        except Exception as e:
            return {"error": str(e), "score": 0}
    else:
        return {
            "score": 5,
            "relevance": 5,
            "communication": 5,
            "strengths": ["Answer provided"],
            "areas_for_improvement": ["More detail needed"],
            "key_points": [],
            "missed_points": [],
            "overall_feedback": "Answer evaluated. More specific details would improve this response.",
        }


# ── Interview Flow ──

async def conduct_mock_interview(
    job_role: str,
    experience_level: str,
    candidate_answers: List[str],
    questions: List[Dict[str, str]] = None,
    num_questions: int = 5
) -> Dict[str, Any]:
    """
    Conduct a full mock interview given the candidate's answers.
    Returns overall score and detailed feedback.
    """
    if questions is None:
        questions = await generate_interview_questions(
            job_role, experience_level, num_questions
        )

    evaluations = []
    total_score = 0

    for i, q in enumerate(questions[:min(len(candidate_answers), num_questions)]):
        if i < len(candidate_answers):
            evaluation = await evaluate_answer(
                q.get("question", ""),
                candidate_answers[i],
                job_role,
                experience_level
            )
            evaluation["question"] = q.get("question", "")
            evaluation["category"] = q.get("category", "general")
            evaluations.append(evaluation)
            total_score += evaluation.get("score", 0)

    avg_score = round(total_score / max(len(evaluations), 1), 1)

    # Overall feedback
    prompt = f"""
An AI interview was conducted for a {job_role} position ({experience_level}-level).
The candidate scored {avg_score}/10 on average across {len(evaluations)} questions.

Individual scores: {[e.get('score', 0) for e in evaluations]}
Categories: {[e.get('category', 'general') for e in evaluations]}

Provide a 3-4 sentence summary of the candidate's interview performance,
highlighting their strengths and major areas for growth.
"""
    overall_feedback = f"The candidate scored {avg_score}/10 on average. "
    if avg_score >= 8:
        overall_feedback += "Strong performance overall. Ready for next round."
    elif avg_score >= 6:
        overall_feedback += "Good foundation. Some areas need improvement."
    else:
        overall_feedback += "Needs significant preparation before interviewing."

    return {
        "job_role": job_role,
        "experience_level": experience_level,
        "overall_score": avg_score,
        "num_questions": len(evaluations),
        "evaluations": evaluations,
        "summary": {
            "performance": "strong" if avg_score >= 7 else "moderate" if avg_score >= 5 else "needs_improvement",
            "hiring_recommendation": "yes" if avg_score >= 7 else "no" if avg_score < 5 else "consider",
            "overall_feedback": overall_feedback,
        },
    }
