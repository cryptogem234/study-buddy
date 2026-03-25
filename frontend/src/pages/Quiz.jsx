import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import QuizCard from "../components/QuizCard.jsx";
import ScoreBoard from "../components/ScoreBoard.jsx";
import {
  getAdaptiveQuiz, getQuestions, checkAnswer, startSession, completeSession,
  checkAchievements, getLesson,
} from "../api.js";

const MASTERY_COLOR = {
  mastered:    { bg: "#d1fae5", color: "#065f46", label: "Mastered" },
  proficient:  { bg: "#dbeafe", color: "#1e40af", label: "Proficient" },
  developing:  { bg: "#fef3c7", color: "#92400e", label: "Developing" },
  beginner:    { bg: "#f1f5f9", color: "#475569", label: "Beginner" },
  not_started: { bg: "#f1f5f9", color: "#475569", label: "New" },
};

function LessonScreen({ lesson, onStart }) {
  return (
    <div style={{ maxWidth: 640, margin: "0 auto" }}>
      <div
        style={{
          background: "#fff",
          borderRadius: 18,
          border: "1px solid #e2e8f0",
          overflow: "hidden",
          boxShadow: "0 4px 20px rgba(0,0,0,0.07)",
        }}
      >
        {/* header */}
        <div
          style={{
            background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            padding: "28px 32px",
            color: "#fff",
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 600, opacity: 0.8, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Quick Review
          </div>
          <h2 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>{lesson.title}</h2>
        </div>

        <div style={{ padding: "28px 32px" }}>
          <p style={{ fontSize: 15, color: "#475569", lineHeight: 1.65, marginBottom: 24 }}>
            {lesson.content}
          </p>

          {/* key points */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Key Points
            </div>
            <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
              {lesson.key_points.map((pt, i) => (
                <li key={i} style={{ display: "flex", gap: 10, fontSize: 14, color: "#334155", lineHeight: 1.5 }}>
                  <span style={{ color: "#6366f1", fontWeight: 700, flexShrink: 0 }}>•</span>
                  {pt}
                </li>
              ))}
            </ul>
          </div>

          {/* example */}
          {lesson.example && (
            <div
              style={{
                background: "#f8fafc",
                borderLeft: "3px solid #6366f1",
                borderRadius: "0 10px 10px 0",
                padding: "14px 18px",
                fontSize: 14,
                color: "#334155",
                lineHeight: 1.55,
                marginBottom: 28,
              }}
            >
              <span style={{ fontWeight: 700, color: "#6366f1" }}>Example: </span>
              {lesson.example}
            </div>
          )}

          <button
            onClick={onStart}
            style={{
              width: "100%",
              padding: "14px 0",
              borderRadius: 12,
              border: "none",
              background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
              color: "#fff",
              fontWeight: 700,
              fontSize: 16,
              cursor: "pointer",
              boxShadow: "0 4px 14px rgba(99,102,241,0.35)",
            }}
          >
            Got It — Start Quiz
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Quiz() {
  const { subject, topic: topicParam } = useParams();
  const decodedTopic = topicParam ? decodeURIComponent(topicParam) : null;
  const isPractice = !!decodedTopic;
  const navigate = useNavigate();

  const [phase, setPhase] = useState("loading"); // loading | lesson | quiz | results | error
  const [lesson, setLesson] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answered, setAnswered] = useState(null);
  const [result, setResult] = useState(null);
  const [score, setScore] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const loadQuiz = useCallback(async () => {
    setPhase("loading");
    setCurrentIndex(0);
    setAnswered(null);
    setResult(null);
    setScore(0);
    setError(null);

    try {
      const fetchQs = isPractice
        ? getQuestions(subject, decodedTopic, 5)
        : getAdaptiveQuiz(subject, 10);

      const [qs, session] = await Promise.all([fetchQs, startSession(subject)]);
      if (!qs || qs.length === 0) {
        setError("No questions found. Try the full adaptive quiz instead.");
        setPhase("error");
        return;
      }
      setQuestions(qs);
      setSessionId(session.id);

      // Show lesson card before quiz only for adaptive mode (not repeat practice)
      if (!isPractice) {
        try {
          const lsn = await getLesson(subject, qs[0].topic);
          if (lsn) { setLesson(lsn); setPhase("lesson"); return; }
        } catch (_) {}
      }

      setPhase("quiz");
    } catch (e) {
      setError("Failed to load quiz. Is the backend running?");
      setPhase("error");
    }
  }, [subject]);

  useEffect(() => { loadQuiz(); }, [loadQuiz]);

  const handleAnswer = async (letter) => {
    if (answered || submitting) return;
    setAnswered(letter);
    setSubmitting(true);
    try {
      const res = await checkAnswer(questions[currentIndex].id, letter, sessionId);
      setResult(res);
      if (res.correct) setScore((s) => s + 1);
    } catch (e) {
      console.error("checkAnswer failed", e);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = async () => {
    const next = currentIndex + 1;
    if (next >= questions.length) {
      try { await completeSession(sessionId, score, questions.length); } catch (_) {}
      try { await checkAchievements(); } catch (_) {}
      setPhase("results");
    } else {
      setCurrentIndex(next);
      setAnswered(null);
      setResult(null);
    }
  };

  // ── render ──────────────────────────────────────────────────────────────────
  if (phase === "loading") {
    return (
      <div style={{ textAlign: "center", paddingTop: 80, color: "#64748b" }}>
        <div style={{ fontSize: 36, marginBottom: 12 }}>⏳</div>
        <p style={{ fontSize: 16 }}>Building your personalised quiz...</p>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div style={{ textAlign: "center", paddingTop: 80 }}>
        <div style={{ fontSize: 36, marginBottom: 12 }}>⚠️</div>
        <p style={{ fontSize: 16, color: "#ef4444", marginBottom: 20 }}>{error}</p>
        <button onClick={() => navigate("/")}
          style={{ padding: "10px 24px", borderRadius: 10, border: "none", background: "#6366f1", color: "#fff", fontWeight: 600, cursor: "pointer" }}>
          Go Home
        </button>
      </div>
    );
  }

  if (phase === "lesson") {
    return (
      <div style={{ paddingTop: 12 }}>
        <div style={{ marginBottom: 20 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>{subject} — {lesson.title}</h1>
          <p style={{ fontSize: 14, color: "#64748b" }}>Read before your quiz starts — this will help!</p>
        </div>
        <LessonScreen lesson={lesson} onStart={() => setPhase("quiz")} />
      </div>
    );
  }

  if (phase === "results") {
    return (
      <div style={{ paddingTop: 24 }}>
        <ScoreBoard
          score={score}
          total={questions.length}
          subject={subject}
          topic={decodedTopic}
          isPractice={isPractice}
          onRetry={loadQuiz}
          onBackToLesson={isPractice ? () => navigate(`/lesson/${subject}/${encodeURIComponent(decodedTopic)}`) : null}
        />
      </div>
    );
  }

  // ── quiz phase ───────────────────────────────────────────────────────────────
  const question = questions[currentIndex];
  const mc = MASTERY_COLOR["beginner"]; // placeholder until we wire live mastery

  return (
    <div>
      {/* header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
            <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", margin: 0 }}>
              {isPractice ? `${decodedTopic} Practice` : `${subject} Adaptive Quiz`}
            </h1>
            {isPractice && (
              <span style={{ background: "#eef2ff", color: "#6366f1", borderRadius: 7, padding: "3px 9px", fontSize: 11, fontWeight: 700 }}>
                PRACTICE
              </span>
            )}
          </div>
          <p style={{ fontSize: 13, color: "#64748b", margin: 0 }}>
            Question {currentIndex + 1} of {questions.length}
          </p>
        </div>
        <div style={{ background: "#eef2ff", borderRadius: 10, padding: "8px 16px", fontSize: 14, fontWeight: 700, color: "#6366f1" }}>
          Score: {score}/{currentIndex + (answered ? 1 : 0)}
        </div>
      </div>

      {/* progress bar */}
      <div style={{ height: 6, background: "#e2e8f0", borderRadius: 99, marginBottom: 28, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${((currentIndex + (answered ? 1 : 0)) / questions.length) * 100}%`,
          background: "linear-gradient(90deg, #6366f1, #8b5cf6)",
          borderRadius: 99,
          transition: "width 0.3s ease",
        }} />
      </div>

      {/* topic + difficulty badges */}
      <div style={{ marginBottom: 14, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <span style={{ background: "#f1f5f9", borderRadius: 8, padding: "4px 12px", fontSize: 12, fontWeight: 600, color: "#64748b" }}>
          {question.topic}
        </span>
        <span style={{
          borderRadius: 8, padding: "4px 12px", fontSize: 12, fontWeight: 600,
          background: question.difficulty === "easy" ? "#d1fae5" : question.difficulty === "medium" ? "#fef3c7" : "#fee2e2",
          color: question.difficulty === "easy" ? "#065f46" : question.difficulty === "medium" ? "#92400e" : "#991b1b",
        }}>
          {question.difficulty}
        </span>
      </div>

      <QuizCard question={question} onAnswer={handleAnswer} answered={answered} result={result} />

      {answered && (
        <div style={{ textAlign: "right", marginTop: 20 }}>
          <button onClick={handleNext} style={{
            padding: "12px 32px", borderRadius: 10, border: "none",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            color: "#fff", fontWeight: 700, fontSize: 15, cursor: "pointer",
            boxShadow: "0 4px 12px rgba(99,102,241,0.3)",
          }}>
            {currentIndex + 1 === questions.length ? "See Results" : "Next Question"} →
          </button>
        </div>
      )}
    </div>
  );
}
