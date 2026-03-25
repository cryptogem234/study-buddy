import React from "react";
import { useNavigate } from "react-router-dom";

function gradeEmoji(pct) {
  if (pct >= 90) return "⭐";
  if (pct >= 70) return "😊";
  if (pct >= 50) return "💪";
  return "📚";
}

function gradeLabel(pct) {
  if (pct >= 90) return "Outstanding!";
  if (pct >= 70) return "Great job!";
  if (pct >= 50) return "Keep going!";
  return "Don't give up!";
}

function gradeTip(pct, isPractice) {
  if (pct >= 90) return isPractice ? "You've nailed this topic!" : "You're on fire — keep it up!";
  if (pct >= 70) return isPractice ? "Solid work! Practice once more to reach Proficient." : "Nice performance across the board!";
  if (pct >= 50) return "Review the lesson and try again — you're getting there!";
  return "Head back to the lesson and revisit the key concepts before practicing again.";
}

export default function ScoreBoard({ score, total, subject, topic, isPractice, onRetry, onBackToLesson }) {
  const navigate = useNavigate();
  const pct = total > 0 ? Math.round((score / total) * 100) : 0;
  const isCelebration = pct > 80;

  return (
    <div style={{
      background: "#fff", borderRadius: 20, padding: "44px 40px",
      boxShadow: "0 4px 24px rgba(0,0,0,0.08)", border: "1px solid #e2e8f0",
      textAlign: "center", maxWidth: 500, margin: "0 auto",
    }}>
      {isCelebration && (
        <div style={{ fontSize: 44, marginBottom: 8, letterSpacing: 4 }}>🎉 🎊 🎉</div>
      )}

      <div style={{ fontSize: 68, marginBottom: 8 }}>{gradeEmoji(pct)}</div>

      <h2 style={{ fontSize: 28, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>
        {gradeLabel(pct)}
      </h2>

      <p style={{ fontSize: 14, color: "#64748b", marginBottom: 28 }}>
        {isPractice ? `${topic} Practice` : `${subject} Adaptive Quiz`} Complete
      </p>

      {/* score display */}
      <div style={{
        display: "inline-flex", alignItems: "baseline", gap: 6,
        background: "#f8fafc", border: "2px solid #e2e8f0",
        borderRadius: 16, padding: "18px 36px", marginBottom: 16,
      }}>
        <span style={{ fontSize: 56, fontWeight: 800, color: "#6366f1" }}>{score}</span>
        <span style={{ fontSize: 28, color: "#94a3b8", fontWeight: 600 }}>/ {total}</span>
      </div>

      <div style={{ fontSize: 18, fontWeight: 700, color: pct >= 70 ? "#10b981" : "#ef4444", marginBottom: 12 }}>
        {pct}% accuracy
      </div>

      {/* tip */}
      <div style={{
        background: pct >= 70 ? "#f0fdf4" : "#fff7ed",
        border: `1px solid ${pct >= 70 ? "#bbf7d0" : "#fed7aa"}`,
        borderRadius: 10, padding: "10px 16px", marginBottom: 28,
        fontSize: 13, color: pct >= 70 ? "#166534" : "#9a3412",
      }}>
        {gradeTip(pct, isPractice)}
      </div>

      {/* buttons */}
      <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
        <button onClick={onRetry} style={{
          padding: "11px 22px", borderRadius: 10,
          border: "2px solid #6366f1", background: "transparent",
          color: "#6366f1", fontWeight: 600, fontSize: 14, cursor: "pointer",
        }}>
          Try Again
        </button>

        {onBackToLesson && (
          <button onClick={onBackToLesson} style={{
            padding: "11px 22px", borderRadius: 10,
            border: "none", background: "#f1f5f9",
            color: "#0f172a", fontWeight: 600, fontSize: 14, cursor: "pointer",
          }}>
            Back to Lesson
          </button>
        )}

        <button onClick={() => navigate(isPractice ? "/topics" : "/")} style={{
          padding: "11px 22px", borderRadius: 10,
          border: "none", background: "#6366f1",
          color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer",
        }}>
          {isPractice ? "All Topics" : "Go Home"}
        </button>
      </div>
    </div>
  );
}
