import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Topics from "./pages/Topics.jsx";
import Lesson from "./pages/Lesson.jsx";
import Quiz from "./pages/Quiz.jsx";
import Progress from "./pages/Progress.jsx";
import Achievements from "./pages/Achievements.jsx";

const CORRECT_PASSWORD = "131313";

function LockScreen({ onUnlock }) {
  const [input, setInput] = useState("");
  const [error, setError] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    if (input === CORRECT_PASSWORD) {
      onUnlock();
    } else {
      setError(true);
      setInput("");
      setTimeout(() => setError(false), 1500);
    }
  }

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "#0f172a",
    }}>
      <div style={{
        background: "#1e293b", borderRadius: 20, padding: "48px 40px", width: 340,
        boxShadow: "0 20px 60px rgba(0,0,0,0.4)", textAlign: "center",
      }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📚</div>
        <div style={{ fontSize: 22, fontWeight: 800, color: "#f1f5f9", marginBottom: 6 }}>Study Buddy</div>
        <div style={{ fontSize: 14, color: "#475569", marginBottom: 32 }}>Enter your password to continue</div>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Password"
            autoFocus
            style={{
              width: "100%", padding: "12px 16px", borderRadius: 10, border: `2px solid ${error ? "#ef4444" : "#334155"}`,
              background: "#0f172a", color: "#f1f5f9", fontSize: 18, textAlign: "center",
              outline: "none", letterSpacing: 8, boxSizing: "border-box",
              transition: "border-color 0.2s",
            }}
          />
          {error && (
            <div style={{ color: "#ef4444", fontSize: 13, marginTop: 10, fontWeight: 600 }}>
              Incorrect password. Try again.
            </div>
          )}
          <button type="submit" style={{
            marginTop: 20, width: "100%", padding: "12px", borderRadius: 10,
            background: "#6366f1", color: "#fff", fontSize: 15, fontWeight: 700,
            border: "none", cursor: "pointer",
          }}>
            Unlock
          </button>
        </form>
      </div>
    </div>
  );
}

export default function App() {
  const [unlocked, setUnlocked] = useState(false);

  if (!unlocked) {
    return <LockScreen onUnlock={() => setUnlocked(true)} />;
  }

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"                              element={<Home />} />
          <Route path="/topics"                        element={<Topics />} />
          <Route path="/lesson/:subject/:topic"        element={<Lesson />} />
          <Route path="/quiz/:subject"                 element={<Quiz />} />
          <Route path="/quiz/:subject/:topic"          element={<Quiz />} />
          <Route path="/progress"                      element={<Progress />} />
          <Route path="/achievements"                  element={<Achievements />} />
          <Route path="*"                              element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
