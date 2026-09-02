"use client";

import { useState } from "react";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function HomePage() {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [parsedData, setParsedData] = useState<any>(null);
  const [scoreResult, setScoreResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleParseResume = async () => {
    if (!resumeFile) {
      setError("Please upload a resume file");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", resumeFile);
    formData.append("use_llm", "true");

    try {
      const resp = await axios.post(`${API_BASE}/api/resume/parse`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      });

      if (resp.data.success) {
        setResumeText(resp.data.resume_text);
        setParsedData(resp.data.parsed_data);
      } else {
        setError(resp.data.error || "Parse failed");
      }
    } catch (e: any) {
      setError(e.message || "Failed to parse resume");
    }
    setLoading(false);
  };

  const handleScoreResume = async () => {
    if (!parsedData || !jobTitle || !jobDesc) {
      setError("Please parse a resume and fill job details first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const resp = await axios.post(`${API_BASE}/api/resume/score`, {
        resume_data: parsedData,
        job: { title: jobTitle, description: jobDesc },
      });

      if (resp.data.success) {
        setScoreResult(resp.data.result);
      }
    } catch (e: any) {
      setError(e.message || "Scoring failed");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-900">
          AI Recruiter
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Resume Analysis & Mock Interview Platform
        </p>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left: Resume Upload */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Upload Resume</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Resume File (PDF/DOCX/TXT)
              </label>
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <button
              onClick={handleParseResume}
              disabled={loading || !resumeFile}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? "Parsing..." : "Parse Resume"}
            </button>

            {resumeText && (
              <div className="mt-4">
                <h3 className="font-medium text-gray-900 mb-2">Extracted Text</h3>
                <div className="p-3 bg-gray-100 rounded-lg text-sm max-h-40 overflow-y-auto">
                  {resumeText.substring(0, 500)}...
                </div>
              </div>
            )}

            {parsedData && (
              <div className="mt-4">
                <h3 className="font-medium text-gray-900 mb-2">Parsed Data</h3>
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="font-bold">{parsedData?.name || "Name not found"}</p>
                  <p className="text-sm">{parsedData?.email}</p>
                  {parsedData?.skills && (
                    <p className="text-sm mt-1">
                      Skills: {parsedData.skills.join(", ")}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right: Job + Scoring */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Job Description</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Frontend Developer"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description
              </label>
              <textarea
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                placeholder="Paste the full job description here..."
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none"
              />
            </div>

            <button
              onClick={handleScoreResume}
              disabled={loading || !parsedData || !jobTitle}
              className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              {loading ? "Scoring..." : "Score Resume"}
            </button>

            {scoreResult && (
              <div className="mt-4">
                <h3 className="font-medium text-gray-900 mb-2">Match Score</h3>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {scoreResult.match_score}/100
                  </div>
                  <p className="text-sm text-gray-700 mt-2">
                    {scoreResult.explanation}
                  </p>
                  <div className="mt-3">
                    <h4 className="font-medium text-gray-900">Strengths</h4>
                    <ul className="text-sm text-gray-700 mt-1">
                      {scoreResult.key_strengths?.map((s: string, i: number) => (
                        <li key={i}>• {s}</li>
                      ))}
                    </ul>
                  </div>
                  {scoreResult.missing_skills && scoreResult.missing_skills.length > 0 && (
                    <div className="mt-3">
                      <h4 className="font-medium text-gray-900">Missing Skills</h4>
                      <ul className="text-sm text-gray-700 mt-1">
                        {scoreResult.missing_skills.map((s: string, i: number) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="fixed bottom-4 right-4 bg-red-100 border border-red-300 text-red-800 px-4 py-2 rounded-lg">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
