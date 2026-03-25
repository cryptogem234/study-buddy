import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getSessions, getProgressSummary, getTopics } from "../api.js";

const STUDENT_NAME = "Aashi";

const SUBJECTS = [
  { key: "English", emoji: "📚", color: "#6366f1", bg: "#eef2ff",
    description: "Grammar, vocabulary, literary devices, text structure, and more" },
  { key: "Science", emoji: "🔬", color: "#10b981", bg: "#d1fae5",
    description: "Cells, genetics, ecosystems, forces, energy, geology, and more" },
];

const MASTERY_STYLES = {
  mastered:    { bg: "#d1fae5", color: "#065f46", label: "Mastered",   bar: "#10b981" },
  proficient:  { bg: "#dbeafe", color: "#1e40af", label: "Proficient", bar: "#6366f1" },
  developing:  { bg: "#fef3c7", color: "#92400e", label: "Developing", bar: "#f59e0b" },
  beginner:    { bg: "#f1f5f9", color: "#475569", label: "Beginner",   bar: "#94a3b8" },
  not_started: { bg: "#f8fafc", color: "#94a3b8", label: "Not Started",bar: "#e2e8f0" },
};

function StatCard({ label, value, sub }) {
  return (
    <div style={{ background: "#fff", borderRadius: 14, padding: "18px 22px", border: "1px solid #e2e8f0", minWidth: 120, flex: 1 }}>
      <div style={{ fontSize: 26, fontWeight: 800, color: "#0f172a" }}>{value}</div>
      <div style={{ fontSize: 13, color: "#64748b", marginTop: 2 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 1 }}>{sub}</div>}
    </div>
  );
}

function TopicCard({ topic, mastery_level, accuracy, needs_review, total_attempts, subject, onClick }) {
  const s = MASTERY_STYLES[mastery_level] || MASTERY_STYLES.not_started;
  return (
    <div
      onClick={onClick}
      style={{
        background: "#fff",
        borderRadius: 12,
        border: `1px solid ${needs_review ? "#fca5a5" : "#e2e8f0"}`,
        padding: "14px 16px",
        cursor: "pointer",
        transition: "box-shadow 0.15s",
        position: "relative",
        overflow: "hidden",
      }}
      onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 14px rgba(0,0,0,0.08)"}
      onMouseLeave={e => e.currentTarget.style.boxShadow = "none"}
    >
      {needs_review && (
        <div style={{
          position: "absolute", top: 8, right: 8,
          background: "#fef2f2", color: "#ef4444",
          borderRadius: 6, padding: "2px 7px",
          fontSize: 10, fontWeight: 700,
        }}>
          REVIEW
        </div>
      )}
      <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 6, paddingRight: needs_review ? 54 : 0 }}>
        {topic}
      </div>
      {/* progress bar */}
      <div style={{ height: 4, background: "#f1f5f9", borderRadius: 99, marginBottom: 8, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${accuracy}%`, background: s.bar, borderRadius: 99, transition: "width 0.4s ease" }} />
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 11, fontWeight: 600, background: s.bg, color: s.color, borderRadius: 6, padding: "2px 7px" }}>
          {s.label}
        </span>
        <span style={{ fontSize: 11, color: "#94a3b8" }}>
          {total_attempts > 0 ? `${accuracy}%` : "—"}
        </span>
      </div>
    </div>
  );
}

export default function Home() {
  const navigate = useNavigate();
  const [recentSessions, setRecentSessions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getSessions(), getProgressSummary(), getTopics()])
      .then(([sessions, sum, topicList]) => {
        setRecentSessions(sessions.slice(0, 3));
        setSummary(sum);
        setTopics(topicList);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  const topicsFor = (subj) => topics.filter((t) => t.subject.toLowerCase() === subj.toLowerCase());
  const needsReviewCount = topics.filter((t) => t.needs_review).length;

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>
          {greeting}, {STUDENT_NAME}! 👋
        </h1>
        <p style={{ fontSize: 16, color: "#64748b" }}>
          {needsReviewCount > 0
            ? `You have ${needsReviewCount} topic${needsReviewCount > 1 ? "s" : ""} that need review. Let's strengthen them!`
            : "Ready to learn something new today?"}
        </p>
      </div>

      {/* Stats */}
      {!loading && summary && (
        <div style={{ display: "flex", gap: 14, marginBottom: 36, flexWrap: "wrap" }}>
          <StatCard label="Questions Answered" value={summary.total_questions_answered} />
          <StatCard label="Overall Accuracy" value={`${summary.overall_accuracy}%`} />
          <StatCard
            label="Study Streak"
            value={`${summary.current_streak} ${summary.current_streak === 1 ? "day" : "days"}`}
            sub={summary.current_streak > 0 ? "🔥 Keep it up!" : "Start your streak today"}
          />
          <StatCard label="Quizzes Taken" value={summary.total_sessions} />
        </div>
      )}

      {/* Subject cards */}
      <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", marginBottom: 16 }}>Choose a Subject</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 40 }}>
        {SUBJECTS.map((subj) => (
          <button
            key={subj.key}
            onClick={() => navigate(`/quiz/${subj.key}`)}
            style={{
              background: "#fff", border: `2px solid ${subj.color}20`,
              borderRadius: 16, padding: "28px 24px", textAlign: "left",
              cursor: "pointer", transition: "all 0.15s", boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
            }}
          >
            <div style={{ width: 52, height: 52, borderRadius: 14, background: subj.bg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26, marginBottom: 14 }}>
              {subj.emoji}
            </div>
            <div style={{ fontSize: 17, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>{subj.key}</div>
            <div style={{ fontSize: 13, color: "#64748b", lineHeight: 1.4 }}>{subj.description}</div>
            <div style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600, color: subj.color }}>
              Start Adaptive Quiz →
            </div>
          </button>
        ))}
      </div>

      {/* Topic mastery grids */}
      {!loading && topics.length > 0 && SUBJECTS.map((subj) => {
        const subjectTopics = topicsFor(subj.key);
        if (subjectTopics.length === 0) return null;
        const reviewTopics = subjectTopics.filter((t) => t.needs_review);
        return (
          <div key={subj.key} style={{ marginBottom: 40 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", margin: 0 }}>
                {subj.emoji} {subj.key} — Topic Mastery
              </h2>
              {reviewTopics.length > 0 && (
                <span style={{ background: "#fef2f2", color: "#ef4444", borderRadius: 8, padding: "3px 10px", fontSize: 12, fontWeight: 700 }}>
                  {reviewTopics.length} need review
                </span>
              )}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
              {subjectTopics.map((t) => (
                <TopicCard
                  key={t.topic}
                  {...t}
                  onClick={() => navigate(`/quiz/${subj.key}`)}
                />
              ))}
            </div>
          </div>
        );
      })}

      {/* Recent sessions */}
      <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", marginBottom: 16 }}>Recent Sessions</h2>
      {loading ? (
        <p style={{ color: "#94a3b8", fontSize: 14 }}>Loading...</p>
      ) : recentSessions.length === 0 ? (
        <div style={{ background: "#f8fafc", borderRadius: 14, padding: "28px 24px", border: "1px dashed #e2e8f0", color: "#94a3b8", fontSize: 14, textAlign: "center" }}>
          No quizzes completed yet. Pick a subject above to get started!
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {recentSessions.map((session) => {
            const pct = session.total_questions ? Math.round((session.score / session.total_questions) * 100) : 0;
            const date = new Date(session.completed_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
            return (
              <div key={session.id} style={{ background: "#fff", borderRadius: 12, padding: "14px 20px", border: "1px solid #e2e8f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <span style={{ fontWeight: 600, fontSize: 14, color: "#0f172a" }}>{session.subject}</span>
                  <span style={{ fontSize: 13, color: "#94a3b8", marginLeft: 10 }}>{date}</span>
                </div>
                <div style={{ fontWeight: 700, fontSize: 15, color: pct >= 70 ? "#10b981" : "#ef4444" }}>
                  {session.score}/{session.total_questions} &nbsp;({pct}%)
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
