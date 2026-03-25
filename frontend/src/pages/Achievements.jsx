import React, { useEffect, useState } from "react";
import { getAchievements } from "../api.js";
import AchievementBadge from "../components/AchievementBadge.jsx";

export default function Achievements() {
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAchievements()
      .then(setAchievements)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const unlocked = achievements.filter((a) => a.unlocked_at);
  const locked = achievements.filter((a) => !a.unlocked_at);

  return (
    <div>
      <h1 style={{ fontSize: 26, fontWeight: 800, color: "#0f172a", marginBottom: 6 }}>
        Achievements
      </h1>
      <p style={{ fontSize: 14, color: "#64748b", marginBottom: 28 }}>
        {unlocked.length} of {achievements.length} unlocked
      </p>

      {loading ? (
        <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
          Loading achievements...
        </div>
      ) : (
        <>
          {unlocked.length > 0 && (
            <div style={{ marginBottom: 36 }}>
              <h2 style={{ fontSize: 15, fontWeight: 700, color: "#64748b", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Unlocked
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 16 }}>
                {unlocked.map((a) => (
                  <AchievementBadge key={a.id} achievement={a} />
                ))}
              </div>
            </div>
          )}

          {locked.length > 0 && (
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 700, color: "#64748b", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Locked
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 16 }}>
                {locked.map((a) => (
                  <AchievementBadge key={a.id} achievement={a} />
                ))}
              </div>
            </div>
          )}

          {achievements.length === 0 && (
            <div
              style={{
                textAlign: "center",
                paddingTop: 60,
                color: "#94a3b8",
                fontSize: 14,
              }}
            >
              No achievements found. Run the seed script to add them!
            </div>
          )}
        </>
      )}
    </div>
  );
}
