import React from "react";

const OPTIONS = ["A", "B", "C", "D"];

export default function QuizCard({ question, onAnswer, answered, result }) {
  const getOptionText = (letter) => {
    const map = { A: question.option_a, B: question.option_b, C: question.option_c, D: question.option_d };
    return map[letter];
  };

  const getButtonStyle = (letter) => {
    const base = {
      display: "flex",
      alignItems: "flex-start",
      gap: 12,
      width: "100%",
      padding: "14px 18px",
      borderRadius: 12,
      border: "2px solid #e2e8f0",
      background: "#fff",
      cursor: answered ? "default" : "pointer",
      fontSize: 15,
      fontWeight: 500,
      color: "#1e293b",
      textAlign: "left",
      transition: "all 0.15s",
      marginBottom: 10,
    };

    if (!answered) {
      return {
        ...base,
        ":hover": { borderColor: "#6366f1", background: "#eef2ff" },
      };
    }

    if (letter === result?.correct_answer) {
      return { ...base, borderColor: "#10b981", background: "#d1fae5", color: "#065f46" };
    }
    if (answered && letter === answered && !result?.correct) {
      return { ...base, borderColor: "#ef4444", background: "#fee2e2", color: "#991b1b" };
    }
    return { ...base, opacity: 0.5 };
  };

  const badgeStyle = (letter) => ({
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 26,
    height: 26,
    borderRadius: 6,
    background: "#f1f5f9",
    fontSize: 13,
    fontWeight: 700,
    color: "#64748b",
    flexShrink: 0,
    marginTop: 1,
  });

  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 16,
        padding: "28px 32px",
        boxShadow: "0 1px 6px rgba(0,0,0,0.07)",
        border: "1px solid #e2e8f0",
      }}
    >
      <p
        style={{
          fontSize: 17,
          fontWeight: 600,
          color: "#0f172a",
          lineHeight: 1.5,
          marginBottom: 24,
        }}
      >
        {question.question_text}
      </p>

      <div>
        {OPTIONS.map((letter) => (
          <button
            key={letter}
            onClick={() => !answered && onAnswer(letter)}
            style={getButtonStyle(letter)}
            disabled={!!answered}
          >
            <span style={badgeStyle(letter)}>{letter}</span>
            <span style={{ paddingTop: 2 }}>{getOptionText(letter)}</span>
          </button>
        ))}
      </div>

      {answered && result && (
        <div
          style={{
            marginTop: 16,
            padding: "14px 18px",
            borderRadius: 12,
            background: result.correct ? "#d1fae5" : "#fee2e2",
            border: `1px solid ${result.correct ? "#6ee7b7" : "#fca5a5"}`,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: result.correct ? "#065f46" : "#991b1b",
              marginBottom: 6,
            }}
          >
            {result.correct ? "✅ Correct!" : `❌ Incorrect — the answer is ${result.correct_answer}`}
          </div>
          <div style={{ fontSize: 14, color: result.correct ? "#047857" : "#b91c1c", lineHeight: 1.5 }}>
            {result.explanation}
          </div>
        </div>
      )}
    </div>
  );
}
