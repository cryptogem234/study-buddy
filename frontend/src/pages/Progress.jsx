import React, { useEffect, useState } from "react";
import { getProgressSummary, getProgressBySubject, getProgressChart, getTopics } from "../api.js";
import ProgressChart from "../components/ProgressChart.jsx";

const MASTERY_STYLES = {
  mastered:    { bg: "#d1fae5", color: "#065f46", label: "Mastered",    bar: "#10b981", pct: 100 },
  proficient:  { bg: "#dbeafe", color: "#1e40af", label: "Proficient",  bar: "#6366f1", pct: 75 },
  developing:  { bg: "#fef3c7", color: "#92400e", label: "Developing",  bar: "#f59e0b", pct: 45 },
  beginner:    { bg: "#f1f5f9", color: "#475569", label: "Beginner",    bar: "#94a3b8", pct: 15 },
  not_started: { bg: "#f8fafc", color: "#cbd5e1", label: "Not Started", bar: "#e2e8f0", pct: 0 },
};

function StatPill({ emoji, label, value, color }) {
  return (
    <div style={{ background: "#fff", borderRadius: 14, padding: "20px 24px", border: "1px solid #e2e8f0", flex: 1, minWidth: 140, display: "flex", flexDirection: "column", gap: 6 }}>
      <span style={{ fontSize: 26 }}>{emoji}</span>
      <span style={{ fontSize: 26, fontWeight: 800, color: color || "#0f172a" }}>{value}</span>
      <span style={{ fontSize: 13, color: "#64748b" }}>{label}</span>
    </div>
  );
}

function MasteryRow({ topic, mastery_level, accuracy, total_attempts, needs_review }) {
  const s = MASTERY_STYLES[mastery_level] || MASTERY_STYLES.not_started;
  return (
    <tr style={{ borderTop: "1px solid #f1f5f9" }}>
      <td style={{ padding: "12px 20px", fontSize: 14, color: "#0f172a", fontWeight: 500 }}>
        {needs_review && <span style={{ background: "#fef2f2", color: "#ef4444", borderRadius: 5, padding: "1px 6px", fontSize: 10, fontWeight: 700, marginRight: 7 }}>REVIEW</span>}
        {topic}
      </td>
      <td style={{ padding: "12px 20px" }}>
        <span style={{ background: s.bg, color: s.color, borderRadius: 8, padding: "4px 10px", fontSize: 12, fontWeight: 700 }}>
          {s.label}
        </span>
      </td>
      <td style={{ padding: "12px 20px", fontSize: 14, color: "#64748b" }}>{total_attempts}</td>
      <td style={{ padding: "12px 20px" }}>
        {total_attempts > 0 ? (
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ flex: 1, height: 6, background: "#f1f5f9", borderRadius: 99, overflow: "hidden", minWidth: 80 }}>
              <div style={{ height: "100%", width: `${accuracy}%`, background: s.bar, borderRadius: 99, transition: "width 0.4s" }} />
            </div>
            <span style={{ fontSize: 13, fontWeight: 700, color: s.color, minWidth: 36 }}>{accuracy}%</span>
          </div>
        ) : (
          <span style={{ fontSize: 12, color: "#cbd5e1" }}>—</span>
        )}
      </td>
    </tr>
  );
}

export default function Progress() {
  const [summary, setSummary]   = useState(null);
  const [bySubject, setBySubject] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [topics, setTopics]     = useState([]);
  const [loading, setLoading]   = useState(true);
  const [activeTab, setActiveTab] = useState("English");

  useEffect(() => {
    Promise.all([getProgressSummary(), getProgressBySubject(), getProgressChart(), getTopics()])
      .then(([sum, subj, chart, topicList]) => {
        setSummary(sum);
        setBySubject(subj);
        setChartData(chart);
        setTopics(topicList);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={{ textAlign: "center", paddingTop: 80, color: "#64748b" }}>Loading progress...</div>;
  }

  const subjectTopics = topics.filter((t) => t.subject.toLowerCase() === activeTab.toLowerCase());
  const masteredCount = subjectTopics.filter((t) => t.mastery_level === "mastered").length;
  const reviewCount   = subjectTopics.filter((t) => t.needs_review).length;

  return (
    <div>
      <h1 style={{ fontSize: 26, fontWeight: 800, color: "#0f172a", marginBottom: 6 }}>My Progress</h1>
      <p style={{ fontSize: 14, color: "#64748b", marginBottom: 28 }}>Track your learning journey over time.</p>

      {/* Stats */}
      {summary && (
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 36 }}>
          <StatPill emoji="📝" label="Questions Answered" value={summary.total_questions_answered} />
          <StatPill emoji="🎯" label="Overall Accuracy" value={`${summary.overall_accuracy}%`} color={summary.overall_accuracy >= 70 ? "#10b981" : "#ef4444"} />
          <StatPill emoji="🔥" label="Study Streak" value={`${summary.current_streak}d`} color="#f59e0b" />
          <StatPill emoji="🏁" label="Quizzes Completed" value={summary.total_sessions} />
        </div>
      )}

      {/* Chart */}
      <div style={{ background: "#fff", borderRadius: 16, padding: "24px 24px 16px", border: "1px solid #e2e8f0", marginBottom: 28, boxShadow: "0 1px 4px rgba(0,0,0,0.05)" }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: "#0f172a", marginBottom: 20 }}>Daily Score — Last 30 Days</h2>
        <ProgressChart data={chartData} />
      </div>

      {/* Subject summary table */}
      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #e2e8f0", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.05)", marginBottom: 28 }}>
        <div style={{ padding: "18px 24px", borderBottom: "1px solid #f1f5f9", fontSize: 16, fontWeight: 700, color: "#0f172a" }}>
          Breakdown by Subject
        </div>
        {bySubject.length === 0 ? (
          <div style={{ padding: "32px 24px", color: "#94a3b8", fontSize: 14, textAlign: "center" }}>
            Complete a quiz to see your subject breakdown.
          </div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                {["Subject", "Questions", "Correct", "Accuracy"].map((h) => (
                  <th key={h} style={{ padding: "12px 24px", fontSize: 12, fontWeight: 600, color: "#64748b", textAlign: "left", textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bySubject.map((row, i) => (
                <tr key={row.subject} style={{ borderTop: "1px solid #f1f5f9", background: i % 2 === 0 ? "#fff" : "#fafafa" }}>
                  <td style={{ padding: "14px 24px", fontWeight: 600, fontSize: 14, color: "#0f172a" }}>
                    {row.subject === "English" ? "📚 " : "🔬 "}{row.subject}
                  </td>
                  <td style={{ padding: "14px 24px", fontSize: 14, color: "#64748b" }}>{row.total_questions}</td>
                  <td style={{ padding: "14px 24px", fontSize: 14, color: "#64748b" }}>{row.correct}</td>
                  <td style={{ padding: "14px 24px" }}>
                    <span style={{ background: row.accuracy >= 70 ? "#d1fae5" : "#fee2e2", color: row.accuracy >= 70 ? "#065f46" : "#991b1b", borderRadius: 8, padding: "4px 10px", fontSize: 13, fontWeight: 700 }}>
                      {row.accuracy}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Per-topic mastery skill tree */}
      {topics.length > 0 && (
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #e2e8f0", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.05)" }}>
          {/* tab header */}
          <div style={{ display: "flex", borderBottom: "1px solid #f1f5f9" }}>
            {["English", "Science"].map((subj) => (
              <button
                key={subj}
                onClick={() => setActiveTab(subj)}
                style={{
                  flex: 1, padding: "16px 24px", border: "none", background: "none", cursor: "pointer",
                  fontSize: 15, fontWeight: 700,
                  color: activeTab === subj ? "#6366f1" : "#94a3b8",
                  borderBottom: activeTab === subj ? "2px solid #6366f1" : "2px solid transparent",
                  transition: "all 0.15s",
                }}
              >
                {subj === "English" ? "📚 " : "🔬 "}{subj}
              </button>
            ))}
          </div>

          {/* mastery summary badges */}
          {subjectTopics.length > 0 && (
            <div style={{ padding: "16px 20px", background: "#fafafa", borderBottom: "1px solid #f1f5f9", display: "flex", gap: 12, flexWrap: "wrap" }}>
              {["mastered","proficient","developing","beginner","not_started"].map((lvl) => {
                const count = subjectTopics.filter((t) => t.mastery_level === lvl || (!t.total_attempts && lvl === "not_started")).length;
                const s = MASTERY_STYLES[lvl];
                if (count === 0) return null;
                return (
                  <span key={lvl} style={{ background: s.bg, color: s.color, borderRadius: 8, padding: "5px 12px", fontSize: 12, fontWeight: 700 }}>
                    {s.label}: {count}
                  </span>
                );
              })}
              {reviewCount > 0 && (
                <span style={{ background: "#fef2f2", color: "#ef4444", borderRadius: 8, padding: "5px 12px", fontSize: 12, fontWeight: 700 }}>
                  Needs Review: {reviewCount}
                </span>
              )}
            </div>
          )}

          {subjectTopics.length === 0 ? (
            <div style={{ padding: "32px 24px", color: "#94a3b8", fontSize: 14, textAlign: "center" }}>
              Start a {activeTab} quiz to see topic mastery.
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  {["Topic", "Level", "Attempts", "Accuracy"].map((h) => (
                    <th key={h} style={{ padding: "12px 20px", fontSize: 12, fontWeight: 600, color: "#64748b", textAlign: "left", textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {subjectTopics
                  .sort((a, b) => {
                    const order = { needs_review: 0, not_started: 1, beginner: 2, developing: 3, proficient: 4, mastered: 5 };
                    const aKey = a.needs_review ? "needs_review" : a.mastery_level;
                    const bKey = b.needs_review ? "needs_review" : b.mastery_level;
                    return (order[aKey] ?? 3) - (order[bKey] ?? 3);
                  })
                  .map((t) => <MasteryRow key={t.topic} {...t} />)
                }
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
