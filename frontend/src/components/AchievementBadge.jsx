import React from "react";

export default function AchievementBadge({ achievement }) {
  const unlocked = !!achievement.unlocked_at;

  const cardStyle = {
    background: unlocked ? "#fff" : "#f8fafc",
    borderRadius: 16,
    padding: "24px 20px",
    border: unlocked ? "2px solid #6366f1" : "2px solid #e2e8f0",
    textAlign: "center",
    opacity: unlocked ? 1 : 0.6,
    filter: unlocked ? "none" : "grayscale(80%)",
    transition: "all 0.2s",
    boxShadow: unlocked ? "0 4px 16px rgba(99,102,241,0.12)" : "none",
    position: "relative",
    overflow: "hidden",
  };

  const emojiStyle = {
    fontSize: 44,
    marginBottom: 12,
    display: "block",
    lineHeight: 1,
  };

  const nameStyle = {
    fontSize: 15,
    fontWeight: 700,
    color: unlocked ? "#0f172a" : "#64748b",
    marginBottom: 6,
  };

  const descStyle = {
    fontSize: 13,
    color: "#64748b",
    lineHeight: 1.4,
    marginBottom: unlocked && achievement.unlocked_at ? 10 : 0,
  };

  const dateStyle = {
    fontSize: 11,
    color: "#10b981",
    fontWeight: 600,
  };

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <div style={cardStyle}>
      {!unlocked && (
        <div
          style={{
            position: "absolute",
            top: 10,
            right: 10,
            fontSize: 16,
            opacity: 0.4,
          }}
        >
          🔒
        </div>
      )}
      <span style={emojiStyle}>{achievement.icon_emoji}</span>
      <div style={nameStyle}>{achievement.name}</div>
      <div style={descStyle}>{achievement.description}</div>
      {unlocked && achievement.unlocked_at && (
        <div style={dateStyle}>Unlocked {formatDate(achievement.unlocked_at)}</div>
      )}
    </div>
  );
}
