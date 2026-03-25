import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getLesson, getMastery } from "../api.js";

const MASTERY = {
  mastered:    { bg: "#d1fae5", color: "#065f46", label: "Mastered",    bar: "#10b981", icon: "🏆", desc: "Excellent! You've mastered this topic." },
  proficient:  { bg: "#dbeafe", color: "#1e40af", label: "Proficient",  bar: "#6366f1", icon: "⭐", desc: "Great work! Keep pushing to mastery." },
  developing:  { bg: "#fef3c7", color: "#92400e", label: "Developing",  bar: "#f59e0b", icon: "📈", desc: "Good progress — keep practicing!" },
  beginner:    { bg: "#f1f5f9", color: "#475569", label: "Beginner",    bar: "#94a3b8", icon: "🌱", desc: "Just getting started. You've got this!" },
  not_started: { bg: "#f8fafc", color: "#94a3b8", label: "Not Started", bar: "#e2e8f0", icon: "📖", desc: "Start practicing to build your mastery." },
};

const SUBJECT_GRADIENT = {
  English: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
  Science: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
};

const SUBJECT_COLOR = { English: "#6366f1", Science: "#10b981" };

export default function Lesson() {
  const { subject, topic } = useParams();
  const decodedTopic = decodeURIComponent(topic);
  const navigate = useNavigate();

  const [lesson, setLesson]   = useState(null);
  const [mastery, setMastery] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    Promise.all([
      getLesson(subject, decodedTopic),
      getMastery(subject),
    ])
      .then(([lsn, masteries]) => {
        setLesson(lsn);
        setMastery(masteries.find(m => m.topic === decodedTopic) || null);
        if (!lsn) setNotFound(true);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [subject, decodedTopic]);

  const color    = SUBJECT_COLOR[subject] || "#6366f1";
  const gradient = SUBJECT_GRADIENT[subject] || SUBJECT_GRADIENT.English;
  const ms       = MASTERY[mastery?.mastery_level || "not_started"];

  // ── loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ textAlign: "center", paddingTop: 80, color: "#64748b" }}>
        <div style={{ fontSize: 36, marginBottom: 12 }}>📖</div>
        <p>Loading lesson...</p>
      </div>
    );
  }

  // ── no lesson card ─────────────────────────────────────────────────────────
  if (notFound) {
    return (
      <div style={{ maxWidth: 540, margin: "60px auto", textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", marginBottom: 8 }}>
          No lesson for "{decodedTopic}" yet
        </h2>
        <p style={{ color: "#64748b", marginBottom: 28 }}>
          Jump straight into practice questions — the explanations after each answer will teach you as you go.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button
            onClick={() => navigate(`/quiz/${subject}/${encodeURIComponent(decodedTopic)}`)}
            style={{ padding: "12px 24px", background: color, color: "#fff", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer" }}
          >
            Practice This Topic
          </button>
          <button
            onClick={() => navigate("/topics")}
            style={{ padding: "12px 24px", background: "#f1f5f9", color: "#0f172a", border: "none", borderRadius: 10, fontWeight: 600, cursor: "pointer" }}
          >
            Back to Topics
          </button>
        </div>
      </div>
    );
  }

  // ── lesson ─────────────────────────────────────────────────────────────────
  return (
    <div style={{ maxWidth: 720 }}>

      {/* breadcrumb */}
      <button
        onClick={() => navigate("/topics")}
        style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", fontSize: 14, fontWeight: 500, marginBottom: 20, padding: 0, display: "flex", alignItems: "center", gap: 6 }}
      >
        ← Topics
      </button>

      {/* hero header */}
      <div style={{ background: gradient, borderRadius: 20, padding: "32px 36px", color: "#fff", marginBottom: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", opacity: 0.75, marginBottom: 8 }}>
          {subject}
        </div>
        <h1 style={{ fontSize: 26, fontWeight: 900, margin: 0, lineHeight: 1.2 }}>
          {lesson.title}
        </h1>
        {mastery && (
          <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ background: "rgba(255,255,255,0.2)", borderRadius: 8, padding: "4px 12px", fontSize: 12, fontWeight: 700 }}>
              {ms.icon} {ms.label}
            </span>
            {mastery.total_attempts > 0 && (
              <span style={{ fontSize: 12, opacity: 0.8 }}>
                {mastery.accuracy}% accuracy · {mastery.total_attempts} questions answered
              </span>
            )}
          </div>
        )}
      </div>

      {/* lesson overview */}
      <div style={{ marginBottom: 32 }}>
        <p style={{ fontSize: 16, color: "#334155", lineHeight: 1.75, margin: 0 }}>
          {lesson.content}
        </p>
      </div>

      {/* key concepts */}
      <div style={{
        background: "#fff", borderRadius: 16, border: "1px solid #e2e8f0",
        overflow: "hidden", marginBottom: 24,
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
      }}>
        <div style={{
          padding: "16px 24px",
          background: "#f8fafc",
          borderBottom: "1px solid #e2e8f0",
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <span style={{ fontSize: 18 }}>🔑</span>
          <span style={{ fontSize: 15, fontWeight: 700, color: "#0f172a" }}>Key Concepts</span>
        </div>
        <div style={{ padding: "20px 24px", display: "flex", flexDirection: "column", gap: 14 }}>
          {lesson.key_points.map((pt, i) => (
            <div key={i} style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
              <div style={{
                width: 24, height: 24, borderRadius: "50%",
                background: color + "18",
                color: color,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12, fontWeight: 800, flexShrink: 0, marginTop: 1,
              }}>
                {i + 1}
              </div>
              <p style={{ fontSize: 14, color: "#334155", lineHeight: 1.6, margin: 0 }}>{pt}</p>
            </div>
          ))}
        </div>
      </div>

      {/* example */}
      {lesson.example && (
        <div style={{
          background: "#fff", borderRadius: 16, border: "1px solid #e2e8f0",
          overflow: "hidden", marginBottom: 32,
          boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        }}>
          <div style={{
            padding: "16px 24px", background: "#f8fafc",
            borderBottom: "1px solid #e2e8f0",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{ fontSize: 18 }}>💡</span>
            <span style={{ fontSize: 15, fontWeight: 700, color: "#0f172a" }}>Example</span>
          </div>
          <div style={{
            padding: "20px 24px",
            borderLeft: `4px solid ${color}`,
            fontSize: 14, color: "#334155", lineHeight: 1.7,
          }}>
            {lesson.example}
          </div>
        </div>
      )}

      {/* your progress card */}
      <div style={{
        background: "#fff", borderRadius: 16, border: "1px solid #e2e8f0",
        padding: "24px 28px", marginBottom: 28,
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
      }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
          <span>📊</span> Your Progress on This Topic
        </div>

        {mastery && mastery.total_attempts > 0 ? (
          <div>
            {/* mastery level */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
              <span style={{ fontSize: 28 }}>{ms.icon}</span>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#0f172a" }}>{ms.label}</div>
                <div style={{ fontSize: 13, color: "#64748b" }}>{ms.desc}</div>
              </div>
            </div>

            {/* stats row */}
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 16 }}>
              {[
                { label: "Accuracy",  value: `${mastery.accuracy}%`,        color: mastery.accuracy >= 70 ? "#10b981" : "#f59e0b" },
                { label: "Answered",  value: mastery.total_attempts,         color: "#6366f1" },
                { label: "Correct",   value: mastery.correct_count,          color: "#10b981" },
                { label: "Streak",    value: `${mastery.streak} in a row`,   color: "#f59e0b" },
              ].map(s => (
                <div key={s.label} style={{ background: "#f8fafc", borderRadius: 10, padding: "10px 16px", minWidth: 90 }}>
                  <div style={{ fontSize: 18, fontWeight: 800, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: "#94a3b8", fontWeight: 600 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* accuracy bar */}
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ flex: 1, height: 8, background: "#f1f5f9", borderRadius: 99, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${mastery.accuracy}%`, background: ms.bar, borderRadius: 99, transition: "width 0.5s ease" }} />
              </div>
              <span style={{ fontSize: 13, fontWeight: 700, color: ms.color, minWidth: 40 }}>{mastery.accuracy}%</span>
            </div>

            {mastery.needs_review && (
              <div style={{ marginTop: 12, background: "#fef2f2", borderRadius: 8, padding: "8px 14px", fontSize: 13, color: "#991b1b", display: "flex", gap: 6 }}>
                <span>⚠️</span> Your accuracy has dropped below 65%. Review this lesson and practice more!
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 14, color: "#64748b", fontSize: 14 }}>
            <span style={{ fontSize: 32 }}>🚀</span>
            <div>
              <div style={{ fontWeight: 600, color: "#0f172a", marginBottom: 2 }}>You haven't practiced this topic yet</div>
              <div>Click "Practice Questions" below to start building your mastery!</div>
            </div>
          </div>
        )}
      </div>

      {/* action buttons */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <button
          onClick={() => navigate(`/quiz/${subject}/${encodeURIComponent(decodedTopic)}`)}
          style={{
            flex: 1, minWidth: 200, padding: "15px 24px",
            background: gradient,
            color: "#fff", border: "none", borderRadius: 12,
            fontWeight: 700, fontSize: 15, cursor: "pointer",
            boxShadow: `0 4px 14px ${color}40`,
          }}
        >
          Practice This Topic →
        </button>
        <button
          onClick={() => navigate(`/quiz/${subject}`)}
          style={{
            flex: 1, minWidth: 200, padding: "15px 24px",
            background: "#f1f5f9",
            color: "#0f172a", border: "none", borderRadius: 12,
            fontWeight: 600, fontSize: 15, cursor: "pointer",
          }}
        >
          Full Adaptive Quiz
        </button>
      </div>

      {/* topic navigation */}
      <div style={{ marginTop: 32, paddingTop: 24, borderTop: "1px solid #f1f5f9" }}>
        <button
          onClick={() => navigate("/topics")}
          style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", fontSize: 14, fontWeight: 500, padding: 0, display: "flex", alignItems: "center", gap: 6 }}
        >
          ← Back to all {subject} topics
        </button>
      </div>
    </div>
  );
}
