import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Dot,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "#fff",
          border: "1px solid #e2e8f0",
          borderRadius: 10,
          padding: "10px 14px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        }}
      >
        <p style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>{label}</p>
        <p style={{ fontSize: 16, fontWeight: 700, color: "#6366f1" }}>
          {payload[0].value}%
        </p>
      </div>
    );
  }
  return null;
};

export default function ProgressChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height: 200,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#94a3b8",
          fontSize: 14,
          background: "#f8fafc",
          borderRadius: 12,
          border: "1px dashed #e2e8f0",
        }}
      >
        No quiz data yet — complete a quiz to see your chart!
      </div>
    );
  }

  const formatted = data.map((d) => ({
    ...d,
    date: new Date(d.date + "T00:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={formatted} margin={{ top: 8, right: 16, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fontSize: 12, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `${v}%`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#6366f1"
          strokeWidth={2.5}
          dot={{ fill: "#6366f1", r: 4, strokeWidth: 0 }}
          activeDot={{ r: 6, fill: "#6366f1" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
