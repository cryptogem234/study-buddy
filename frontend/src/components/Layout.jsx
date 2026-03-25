import { NavLink } from "react-router-dom";

const STUDENT_NAME = "Sophia";

const navItems = [
  { to: "/",            label: "Home",         emoji: "🏠", end: true },
  { to: "/topics",      label: "Topics",       emoji: "📖", end: false },
  { to: "/quiz/English",label: "Quick Quiz",   emoji: "⚡", end: false },
  { to: "/progress",    label: "Progress",     emoji: "📈", end: false },
  { to: "/achievements",label: "Achievements", emoji: "🏆", end: false },
];

export default function Layout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <aside style={{
        width: 224,
        minHeight: "100vh",
        background: "#0f172a",
        display: "flex",
        flexDirection: "column",
        padding: "20px 0",
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{ padding: "0 20px 24px", borderBottom: "1px solid #1e293b", marginBottom: 8 }}>
          <div style={{ fontSize: 19, fontWeight: 800, color: "#f1f5f9", letterSpacing: "-0.3px" }}>
            📚 Study Buddy
          </div>
          <div style={{ fontSize: 12, color: "#475569", marginTop: 3, fontWeight: 500 }}>
            Grade 7 Learning Platform
          </div>
        </div>

        {/* Nav section label */}
        <div style={{ padding: "10px 20px 6px", fontSize: 10, fontWeight: 700, color: "#334155", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Learn
        </div>

        {/* Nav items */}
        <nav style={{ flex: 1, padding: "0 10px", display: "flex", flexDirection: "column", gap: 2 }}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "9px 12px",
                borderRadius: 9,
                textDecoration: "none",
                fontSize: 14,
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "#fff" : "#64748b",
                background: isActive ? "#6366f1" : "transparent",
                transition: "all 0.12s",
              })}
              onMouseEnter={e => {
                if (!e.currentTarget.classList.contains("active")) {
                  e.currentTarget.style.background = "#1e293b";
                  e.currentTarget.style.color = "#e2e8f0";
                }
              }}
              onMouseLeave={e => {
                if (!e.currentTarget.dataset.active) {
                  e.currentTarget.style.background = "";
                  e.currentTarget.style.color = "";
                }
              }}
            >
              <span style={{ fontSize: 16, width: 20, textAlign: "center" }}>{item.emoji}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid #1e293b",
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}>
          <div style={{
            width: 34, height: 34, borderRadius: "50%",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 14, fontWeight: 800, color: "#fff", flexShrink: 0,
          }}>
            {STUDENT_NAME[0]}
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>{STUDENT_NAME}</div>
            <div style={{ fontSize: 11, color: "#475569" }}>Grade 7 Student</div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        background: "#f8fafc",
        overflow: "auto",
      }}>
        <div style={{ flex: 1, padding: "32px 40px", maxWidth: 960, width: "100%", margin: "0 auto" }}>
          {children}
        </div>
      </main>
    </div>
  );
}
