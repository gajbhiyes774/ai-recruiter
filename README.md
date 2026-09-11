# 🤖 AI Recruiter — Resume Analysis & Mock Interview Platform

![Next.js](https://img.shields.io/badge/Next.js-16.2.6-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![Ollama](https://img.shields.io/badge/Ollama-gemma3:latest-000000?style=for-the-badge&logo=ollama)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> ATS-grade resume parsing, LLM-powered candidate scoring, and AI mock interviews — Next.js frontend + FastAPI + Ollama backend.

**Live Stack:** Frontend `Next.js 16` (port `3002`) ↔ Backend `FastAPI` (port `8001`) ↔ `Ollama` (`gemma3:latest`) — with graceful regex fallbacks when LLM is offline.

---

## 📖 Overview

**AI Recruiter** streamlines hiring for recruiters and helps candidates prepare:

1. **Resume Analysis** — Upload PDF/DOCX/TXT, extract structured data (name, contact, skills, experience, education, certifications) via LLM, then score the candidate 0–100 against any job description with explainable strengths, missing skills and experience-match assessment.
2. **Mock Interview** — Generate role- and level-aware questions (technical / behavioral / situational) and conduct a full interview with per-answer scoring (score, relevance, communication), strengths, improvement areas and an overall hiring recommendation.

Both flows degrade gracefully: if `Ollama` is unavailable, the system falls back to regex/keyword extraction and heuristic scoring so the app never blocks.

---

## ✨ Features

### 📄 Resume Intelligence (`/`)

- **Multi-format ingestion**: PDF (`pdfplumber`), DOCX (`python-docx`), TXT — single `extract_text()` dispatcher
- **LLM extraction** (`extract_with_llm`): Prompts `gemma3:latest` to return strict JSON with 9 fields (`name`, `email`, `phone`, `location`, `summary`, `experience[]`, `education[]`, `skills[]`, `certifications[]`) — with a 5000-char context window
- **Fallback parser** (`extract_basic`): Regex for email/phone + keyword scan over 16 canonical skills (Python, React, AWS, etc.) — always returns usable data
- **Job-aware scoring** (`score_resume`): LLM prompt compares resume vs job description and returns `match_score` (0–100), `key_strengths[3–5]`, `missing_skills[]`, `experience_match` (`strong|moderate|weak`), `explanation` — fallback is keyword-overlap scoring (`score = min(100, matches*5+20)`)
- **Endpoints**: `/api/resume/parse`, `/api/resume/score`, `/api/resume/parse-and-score` (single-call convenience), `/api/rank` (batch ranking)
- **Frontend**: File input → `FormData` (`file` + `use_llm=true`) → `POST /api/resume/parse` → extracted text preview + parsed card; then job title/description → `POST /api/resume/score` → score card with strengths/missing skills

### 🎤 Mock Interview (`/interview`)

- **Question generation** (`generate_interview_questions`): Role + experience level (`entry|mid|senior`) + category filter → LLM generates `num_questions` (3–10, slider) with `question`, `category`, `difficulty`; fallback pools for technical/behavioral/situational
- **Interview flow**: Setup → Interview (progress bar, prev/next, answer textarea) → Results (overall `score/10`, `performance` tier, hiring recommendation `yes|consider|no`, per-question evaluations)
- **Answer evaluation** (`evaluate_answer`): Per-answer LLM rubric — `score` (0–10), `relevance` (0–10), `communication` (0–10), `strengths`, `areas_for_improvement`, `key_points`, `missed_points`, `overall_feedback`
- **Full conduct** (`conduct_mock_interview`): Orchestrates generation + sequential evaluation → `overall_score` (mean), `summary.overall_feedback` with tiered messaging (≥8 strong, ≥6 good, else needs prep)
- **Models**: `InterviewQuestion`, `InterviewSession` (Pydantic) for future session persistence

### 🔧 Platform

- Clean two-route Next.js app with top nav (`Resume Analyzer` | `Mock Interview`)
- Axios with 60s timeout for LLM calls, `NEXT_PUBLIC_API_URL` env-aware
- CORS wildcard for dev, structured `success/error` JSON envelopes
- Temp upload dir `/tmp/ai-recruiter-uploads` (auto-cleaned after parse)
- Async Ollama client (`ollama.AsyncClient`) for non-blocking interview generation

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 16.2.6, React 19.2, TypeScript 5.6 | App framework, routing, client components |
| **Styling** | Tailwind CSS 3.4, PostCSS, Autoprefixer | Responsive design |
| **HTTP** | Axios 1.7 | REST + multipart uploads |
| **Backend** | FastAPI 0.115, Uvicorn (standard), Pydantic 2.10 | Async REST API, validation, auto-docs |
| **LLM** | Ollama 0.4 + `gemma3:latest` | Resume extraction, scoring, interview Q&A |
| **Parsing** | pdfplumber 0.11, python-docx 1.2 | PDF/DOCX text extraction |
| **Infra** | python-multipart 0.0.9, requests 2.32 | File uploads, HTTP |

---

## 📁 Project Structure

```
ai-recruiter/
├── src/
│   └── app/
│       ├── layout.tsx              # Root layout + nav (Analyzer | Interview)
│       ├── page.tsx                # Resume upload → parse → score flow
│       ├── interview/
│       │   └── page.tsx            # Mock interview (setup → interview → results)
│       └── globals.css
├── backend/
│   ├── server.py                   # FastAPI: /api/resume/*, /api/interview/*, /api/rank, /health
│   ├── resume_parser.py            # extract_text, extract_with_llm, extract_basic, score_resume
│   ├── interview_simulator.py      # generate_interview_questions, evaluate_answer, conduct_mock_interview
│   └── requirements.txt
├── package.json                    # Next.js scripts (dev:3002, build, start)
├── tsconfig.json                   # @/* → ./src/*, bundler resolution
├── tailwind.config.js
├── postcss.config.mjs
├── next-env.d.ts
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** ≥ 18, **npm** ≥ 9
- **Python** ≥ 3.11, **pip**
- **Ollama** (optional but recommended) — [ollama.com/download](https://ollama.com/download)

### 1. Clone

```bash
git clone https://github.com/gajbhiyes774/ai-recruiter.git
cd ai-recruiter
```

### 2. Frontend (port 3002)

```bash
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local  # optional
npm run dev      # http://localhost:3002
npm run build
npm start
```

### 3. Backend (port 8001)

```bash
cd backend
pip install -r requirements.txt

# optional: configure Ollama
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=gemma3:latest

python server.py
# or
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Ollama (for LLM features)

```bash
ollama serve &
ollama pull gemma3:latest
# verify
curl http://localhost:11434/api/tags
```

> Without Ollama the app still works — resume parsing and scoring fall back to regex/keyword heuristics, and interviews use canned question pools.

Verify backend:

```bash
curl http://localhost:8001/health
curl http://localhost:8001/
```

---

## 🔌 API Reference

Base URL: `http://localhost:8001` — Docs: `http://localhost:8001/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health + upload dir |
| `POST` | `/api/resume/parse` | Parse resume file → structured JSON |
| `POST` | `/api/resume/score` | Score parsed resume vs job description |
| `POST` | `/api/resume/parse-and-score` | Parse + score in one call |
| `POST` | `/api/interview/questions` | Generate interview questions |
| `POST` | `/api/interview/evaluate` | Evaluate single answer |
| `POST` | `/api/interview/conduct` | Full mock interview + summary |
| `POST` | `/api/rank` | Rank multiple candidates |

### `POST /api/resume/parse`

```bash
curl -X POST http://localhost:8001/api/resume/parse \
  -F "file=@resume.pdf" \
  -F "use_llm=true"
```

Response:

```json
{
  "success": true,
  "file_id": "uuid",
  "file_name": "resume.pdf",
  "resume_text": "John Doe ...",
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "skills": ["Python", "React", "AWS"],
    "experience": [{"company": "Acme", "role": "SDE", "duration": "2021-2024"}],
    "education": [], "certifications": []
  },
  "confidence": "CONFIRMED",
  "pages": 42
}
```

### `POST /api/resume/score`

```bash
curl -X POST http://localhost:8001/api/resume/score \
  -H "Content-Type: application/json" \
  -d '{
    "resume_data": {"name":"John Doe","skills":["Python","React"]},
    "job": {"title":"Frontend Developer","description":"Need React, TypeScript..."}
  }'
```

Response:

```json
{
  "success": true,
  "result": {
    "match_score": 82,
    "key_strengths": ["Strong React experience", "Matches 3/4 required skills"],
    "missing_skills": ["TypeScript"],
    "experience_match": "strong",
    "explanation": "Candidate matches core frontend stack with 3 years relevant experience."
  }
}
```

### `POST /api/interview/questions`

```json
{
  "job_role": "Frontend Developer",
  "experience_level": "mid",
  "num_questions": 5,
  "categories": ["technical", "behavioral"]
}
```

### `POST /api/interview/conduct`

```json
{
  "config": {"job_role":"Frontend Developer","experience_level":"mid","num_questions":5},
  "answers": ["Answer 1...", "Answer 2...", "Answer 3..."]
}
```

Response includes `overall_score` (0–10), `evaluations[]` per question, and `summary` with `performance` + `hiring_recommendation`.

---

## 🧠 Model Details

### Resume Parsing & Scoring

- **Text extraction**: `pdfplumber` (per-page `extract_text`), `python-docx` (paragraph join), plain `open().read()` for TXT — dispatched by file extension in `extract_text()`.
- **LLM extraction** (`OLLAMA_HOST`, `OLLAMA_MODEL=gemma3:latest`): Prompt asks for 9-field JSON, `temperature=0.3`, `num_predict=2048` to keep output deterministic and bounded. Response is `json.loads`-parsed directly — prompt explicitly says "Return JSON only".
- **Fallback** (`extract_basic`): First line as `name`, regex for `email` (`\b[\w.-]+@...`) and 10-digit `phone`, skill scan against 16 canonical keywords (case-insensitive), capped at 15 skills.
- **Scoring — LLM path**: Prompt includes full job description (truncated 3000 chars) + resume fields, asks for `match_score`, `key_strengths[3–5]`, `missing_skills`, `experience_match`, `explanation`.
- **Scoring — fallback**: Keyword overlap — `score = min(100, found*5+20)` where `found` counts job-description words (>3 chars) present in skills text.
- **Ranking** (`/api/rank`): Iterates candidates, calls `score_resume` per candidate, sorts descending by `match_score`, returns `rankings[]` with `candidate`, `score`, `email`, `key_strengths`, `missing_skills`.

### Interview Simulation

- **Question generation**: Prompt = `Generate {n} questions for {level}-level {role}, categories: {cats}, return JSON array {question, category, difficulty}` — `temperature=0.7` for variety, parsed as JSON array. Fallback pools: 3 technical + 3 behavioral + 3 situational templates interpolated with `job_role`.
- **Evaluation**: Prompt frames the LLM as a hiring manager, asks for `score`/`relevance`/`communication` (0–10 each) + `strengths`, `areas_for_improvement`, `key_points`, `missed_points`, `overall_feedback`. Fallback returns neutral 5/10 with generic feedback.
- **Conduct**: Generates questions if not supplied, loops over `min(len(answers), num_questions)`, calls `evaluate_answer` per Q&A (async), aggregates `total_score → avg_score (round 1 dec)`. Overall feedback tier: `≥8 strong → "Ready for next round"`, `≥6 good → "Some areas need improvement"`, else `"Needs significant preparation"`. Returns `performance` (`strong|moderate|needs_improvement`) and `hiring_recommendation` (`yes|consider|no`).

**Tunable env vars**:

| Variable | Default | Effect |
|----------|---------|--------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:latest` | Model for all LLM calls |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8001` | Frontend → backend URL |

Swap models without code changes: `OLLAMA_MODEL=llama3.1:8b` or `mistral:latest` — prompts are model-agnostic.

---

## ⚙️ Configuration & Deployment

- **CORS**: `allow_origins=["*"]` for dev — restrict in production:
  ```python
  allow_origins=["https://your-frontend.vercel.app"]
  ```
- **Uploads**: Ephemeral `/tmp/ai-recruiter-uploads` per request, `shutil.rmtree` after parse — no persistence, no PII at rest.
- **Frontend env**: `NEXT_PUBLIC_API_URL` is baked at build time — set before `npm run build` for production.
- **Suggested deploy**: Frontend on Vercel (`NEXT_PUBLIC_API_URL` → backend URL), Backend on Render/Fly/Railway with Ollama sidecar or hosted LLM proxy.

---

## 🛣️ Roadmap

- [ ] Persistent interview sessions + history (DB: Postgres/Supabase)
- [ ] Resume → JD skill-gap learning path suggestions
- [ ] Voice interview mode (Whisper STT + TTS)
- [ ] Bulk CSV ranking + PDF report export
- [ ] Auth & role-based dashboards (recruiter vs candidate)

---

## 🤝 Contributing

1. Fork → `git checkout -b feature/your-feature`
2. Ensure `npm run build` and `python -m py_compile backend/*.py` pass
3. PR with description + screenshots for UI changes

---

## 📄 License

MIT — see `LICENSE` (add one if missing). Built by [@gajbhiyes774](https://github.com/gajbhiyes774).

---

<p align="center">
  <sub>⚡ Helping recruiters find the right fit — and candidates ace the interview.</sub>
</p>
