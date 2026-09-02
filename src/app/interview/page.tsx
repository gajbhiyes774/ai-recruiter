"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function InterviewPage() {
  const [jobRole, setJobRole] = useState("Frontend Developer");
  const [experienceLevel, setExperienceLevel] = useState("mid");
  const [numQuestions, setNumQuestions] = useState(5);
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState<"setup" | "interview" | "results">("setup");

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const resp = await axios.post(`${API_BASE}/api/interview/questions`, {
        job_role: jobRole,
        experience_level: experienceLevel,
        num_questions: numQuestions,
        categories: ["technical", "behavioral"],
      });
      if (resp.data.success) {
        setQuestions(resp.data.questions);
        setPhase("interview");
        setAnswers([]);
        setCurrentQ(0);
      }
    } catch (e: any) {
      alert(e.message || "Failed to fetch questions");
    }
    setLoading(false);
  };

  const submitAnswer = () => {
    if (!currentAnswer.trim()) return;
    const newAnswers = [...answers];
    newAnswers[currentQ] = currentAnswer;
    setAnswers(newAnswers);
    setCurrentAnswer("");

    if (currentQ + 1 < questions.length) {
      setCurrentQ(currentQ + 1);
    } else {
      conductInterview(newAnswers);
    }
  };

  const conductInterview = async (allAnswers: string[]) => {
    setLoading(true);
    try {
      const resp = await axios.post(`${API_BASE}/api/interview/conduct`, {
        config: {
          job_role: jobRole,
          experience_level: experienceLevel,
          num_questions: numQuestions,
        },
        answers: allAnswers,
      });
      if (resp.data.success) {
        setResult(resp.data.result);
        setPhase("results");
      }
    } catch (e: any) {
      alert(e.message || "Interview failed");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-900">
          AI Mock Interview
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Practice with an AI interviewer powered by Ollama
        </p>

        {phase === "setup" && (
          <div className="bg-white rounded-xl shadow p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Role
              </label>
              <input
                type="text"
                value={jobRole}
                onChange={(e) => setJobRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Experience Level
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="mid">Mid Level (2-5 years)</option>
                <option value="senior">Senior Level (5+ years)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Questions
              </label>
              <input
                type="range"
                min="3"
                max="10"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{numQuestions} questions</span>
            </div>

            <button
              onClick={fetchQuestions}
              disabled={loading || !jobRole}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? "Starting..." : "Start Interview"}
            </button>
          </div>
        )}

        {phase === "interview" && questions.length > 0 && (
          <div className="bg-white rounded-xl shadow p-6">
            <div className="mb-4">
              <span className="text-sm text-gray-500">
                Question {currentQ + 1} of {questions.length}
              </span>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${((currentQ + 1) / questions.length) * 100}%` }}
                />
              </div>
            </div>

            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {questions[currentQ]?.question}
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Category: {questions[currentQ]?.category} | Difficulty: {questions[currentQ]?.difficulty}
            </p>

            <textarea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Type your answer here..."
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none"
            />

            <div className="flex justify-between mt-4">
              <button
                onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
                disabled={currentQ === 0}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={submitAnswer}
                disabled={!currentAnswer.trim() || loading}
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
              >
                {currentQ + 1 === questions.length ? "Finish Interview" : "Next"}
              </button>
            </div>
          </div>
        )}

        {phase === "results" && result && (
          <div className="bg-white rounded-xl shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Interview Results</h2>

            <div className="text-center py-6">
              <div className="text-4xl font-bold text-blue-600">
                {result.overall_score}/10
              </div>
              <p className="text-gray-600 mt-2">
                Performance: {result.summary?.performance}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="font-bold text-lg">{result.evaluations?.length}</div>
                <div className="text-sm text-gray-600">Questions Answered</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="font-bold text-lg">
                  {result.summary?.hiring_recommendation === "yes" ? "✅ Yes" :
                   result.summary?.hiring_recommendation === "no" ? "❌ No" : "⚠️ Consider"}
                </div>
                <div className="text-sm text-gray-600">Hiring Recommendation</div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-3">Feedback per Question</h3>
              <div className="space-y-4">
                {result.evaluations?.map((e: any, i: number) => (
                  <div key={i} className="border-l-4 border-blue-500 pl-4 py-2">
                    <p className="font-medium text-gray-900">Q{i + 1}: {e.question?.substring(0, 60)}...</p>
                    <div className="flex gap-4 text-sm mt-2">
                      <span>Score: {e.score}/10</span>
                      <span>Relevance: {e.relevance}/10</span>
                      <span>Communication: {e.communication}/10</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{e.overall_feedback}</p>
                    {e.strengths && (
                      <div className="mt-1">
                        <span className="text-sm font-medium text-green-700">Strengths:</span>
                        {e.strengths.map((s: string, j: number) => (
                          <span key={j} className="text-sm text-gray-600"> • {s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => setPhase("setup")}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Take Another Interview
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
