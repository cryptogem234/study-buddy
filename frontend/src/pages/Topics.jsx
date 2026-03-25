import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTopics } from "../api.js";

const MASTERY = {
  mastered:    { bg: "#d1fae5", color: "#065f46", label: "Mastered",    bar: "#10b981", icon: "🏆" },
  proficient:  { bg: "#dbeafe", color: "#1e40af", label: "Proficient",  bar: "#6366f1", icon: "⭐" },
  developing:  { bg: "#fef3c7", color: "#92400e", label: "Developing",  bar: "#f59e0b", icon: "📈" },
  beginner:    { bg: "#f1f5f9", color: "#475569", label: "Beginner",    bar: "#94a3b8", icon: "🌱" },
  not_started: { bg: "#f8fafc", color: "#94a3b8", label: "Not Started", bar: "#e2e8f0", icon: "📖" },
};

const SUBJECT_META = {
  English: {
    emoji: "📚", color: "#6366f1", gradient: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    description: "Grammar · Vocabulary · Literary Devices · Reading · Text Structure",
  },
  Science: {
    emoji: "🔬", color: "#10b981", gradient: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
    description: "Cells · Genetics · Ecosystems · Forces · Energy · Earth Science",
  },
};

function TopicCard({ subject, topic, mastery_level, accuracy, total_attempts, needs_review, onClick }) {
  const s = MASTERY[mastery_level] || MASTERY.not_started;
  const isNew = total_attempts === 0;
  const subjectMeta = SUBJECT_META[subject] || SUBJECT_META.English;

  return (
    <div
      onClick={onClick}
      style={{
        background: "#fff",
        borderRadius: 16,
        border: `1.5px solid ${needs_review ? "#fca5a5" : "#e2e8f0"}`,
        padding: "20px",
        cursor: "pointer",
        transition: "all 0.15s",
        position: "relative",
        display: "flex",
        flexDirection: "column",
        gap: 0,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,0.1)";
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.borderColor = needs_review ? "#f87171" : subjectMeta.color + "60";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.boxShadow = "none";
        e.currentTarget.style.transform = "none";
        e.currentTarget.style.borderColor = needs_review ? "#fca5a5" : "#e2e8f0";
      }}
    >
      {/* top badge */}
      {needs_review && (
        <div style={{ position: "absolute", top: 12, right: 12, background: "#fef2f2", color: "#ef4444", borderRadius: 6, padding: "2px 8px", fontSize: 10, fontWeight: 700, letterSpacing: "0.03em" }}>
          REVIEW
        </div>
      )}
      {isNew && !needs_review && (
        <div style={{ position: "absolute", top: 12, right: 12, background: "#eef2ff", color: "#6366f1", borderRadius: 6, padding: "2px 8px", fontSize: 10, fontWeight: 700 }}>
          NEW
        </div>
      )}

      {/* mastery icon */}
      <div style={{ fontSize: 22, marginBottom: 10 }}>{s.icon}</div>

      {/* topic name */}
      <div style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 14, paddingRight: 52, lineHeight: 1.3 }}>
        {topic}
      </div>

      {/* accuracy bar */}
      <div style={{ height: 5, background: "#f1f5f9", borderRadius: 99, marginBottom: 12, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${isNew ? 0 : Math.min(accuracy, 100)}%`,
          background: s.bar,
          borderRadius: 99,
          transition: "width 0.5s ease",
        }} />
      </div>

      {/* level + stat */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
        <span style={{ fontSize: 11, fontWeight: 700, background: s.bg, color: s.color, borderRadius: 6, padding: "3px 8px" }}>
          {s.label}
        </span>
        <span style={{ fontSize: 11, color: "#94a3b8" }}>
          {total_attempts > 0 ? `${accuracy}% · ${total_attempts}Q` : "Not started"}
        </span>
      </div>

      {/* CTA */}
      <div style={{
        paddingTop: 12,
        borderTop: "1px solid #f1f5f9",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        fontSize: 13,
        fontWeight: 600,
        color: subjectMeta.color,
      }}>
        <span>{isNew ? "Start Lesson" : needs_review ? "Review Lesson" : "Continue"}</span>
        <span style={{ fontSize: 16 }}>→</span>
      </div>
    </div>
  );
}

export default function Topics() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("English");

  useEffect(() => {
    getTopics().then(setTopics).catch(console.error).finally(() => setLoading(false));
  }, []);

  const subjectTopics = topics.filter(t => t.subject === activeTab);
  const started   = subjectTopics.filter(t => t.total_attempts > 0).length;
  const mastered  = subjectTopics.filter(t => t.mastery_level === "mastered").length;
  const reviewing = subjectTopics.filter(t => t.needs_review).length;
  const overall   = subjectTopics.length > 0
    ? Math.round(subjectTopics.reduce((sum, t) => sum + (t.accuracy || 0), 0) / subjectTopics.length)
    : 0;

  const subjectMeta = SUBJECT_META[activeTab];

  // Sort: needs_review first, then not_started, then by mastery level asc (weakest first)
  const ORDER = { not_started: 0, beginner: 1, developing: 2, proficient: 3, mastered: 4 };
  const sorted = [...subjectTopics].sort((a, b) => {
    if (a.needs_review !== b.needs_review) return a.needs_review ? -1 : 1;
    return (ORDER[a.mastery_level] ?? 0) - (ORDER[b.mastery_level] ?? 0);
  });

  return (
    <div>
      {/* Page header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>Topics</h1>
        <p style={{ fontSize: 15, color: "#64748b" }}>
          Choose a topic to study, practice, and master.
        </p>
      </div>

      {/* Subject tabs */}
      <div style={{ display: "flex", background: "#f1f5f9", borderRadius: 12, padding: 4, marginBottom: 28 }}>
        {["English", "Science"].map(subj => {
          const m = SUBJECT_META[subj];
          return (
            <button
              key={subj}
              onClick={() => setActiveTab(subj)}
              style={{
                flex: 1, padding: "11px 0", border: "none", cursor: "pointer",
                borderRadius: 9, fontSize: 14, fontWeight: 600,
                background: activeTab === subj ? "#fff" : "transparent",
                color: activeTab === subj ? "#0f172a" : "#64748b",
                boxShadow: activeTab === subj ? "0 1px 4px rgba(0,0,0,0.1)" : "none",
                transition: "all 0.15s",
              }}
            >
              {m.emoji} {subj}
            </button>
          );
        })}
      </div>

      {/* Subject hero strip */}
      {!loading && (
        <div style={{
          background: subjectMeta.gradient,
          borderRadius: 16,
          padding: "22px 28px",
          marginBottom: 24,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 16,
        }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#fff", marginBottom: 4 }}>
              {subjectMeta.emoji} {activeTab}
            </div>
            <div style={{ fontSize: 13, color: "rgba(255,255,255,0.8)" }}>
              {subjectMeta.description}
            </div>
          </div>
          <div style={{ display: "flex", gap: 20 }}>
            {[
              { label: "Topics",   val: subjectTopics.length },
              { label: "Started",  val: started },
              { label: "Mastered", val: mastered },
              { label: "Avg",      val: started > 0 ? `${overall}%` : "—" },
            ].map(s => (
              <div key={s.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: "#fff" }}>{s.val}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.7)", fontWeight: 600 }}>{s.label}</div>
              </div>
            ))}
          </div>
          <button
            onClick={() => navigate(`/quiz/${activeTab}`)}
            style={{
              padding: "10px 20px", background: "rgba(255,255,255,0.2)",
              border: "1.5px solid rgba(255,255,255,0.4)", borderRadius: 10,
              color: "#fff", fontWeight: 700, fontSize: 13, cursor: "pointer",
              backdropFilter: "blur(4px)",
            }}
          >
            Adaptive Quiz →
          </button>
        </div>
      )}

      {/* Review alert */}
      {reviewing > 0 && (
        <div style={{
          background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 12,
          padding: "12px 18px", marginBottom: 20,
          display: "flex", alignItems: "center", gap: 10,
          fontSize: 14, color: "#991b1b",
        }}>
          <span style={{ fontSize: 18 }}>⚠️</span>
          <span>
            <strong>{reviewing} topic{reviewing > 1 ? "s" : ""}</strong> need review — your accuracy has dropped below 65%. Focus on these first!
          </span>
        </div>
      )}

      {/* Topics grid */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "#94a3b8" }}>Loading topics...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 14 }}>
          {sorted.map(t => (
            <TopicCard
              key={t.topic}
              {...t}
              onClick={() => navigate(`/lesson/${t.subject}/${encodeURIComponent(t.topic)}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
