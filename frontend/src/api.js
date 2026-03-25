const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Request failed: ${res.status}`);
  }
  return res.json();
}

// Questions
export const getQuestions = (subject, topic, limit = 10) => {
  const p = new URLSearchParams();
  if (subject) p.set("subject", subject);
  if (topic)   p.set("topic", topic);
  p.set("limit", limit);
  return request(`/api/questions?${p.toString()}`);
};

export const checkAnswer = (questionId, answer, sessionId = null) =>
  request("/api/questions/check", {
    method: "POST",
    body: JSON.stringify({ question_id: questionId, answer, session_id: sessionId }),
  });

// Adaptive quiz
export const getAdaptiveQuiz = (subject, limit = 10) =>
  request(`/api/quiz/adaptive?subject=${encodeURIComponent(subject)}&limit=${limit}`);

// Sessions
export const startSession  = (subject) =>
  request("/api/sessions", { method: "POST", body: JSON.stringify({ subject }) });

export const completeSession = (id, score, totalQuestions) =>
  request(`/api/sessions/${id}/complete`, {
    method: "PUT",
    body: JSON.stringify({ score, total_questions: totalQuestions }),
  });

export const getSessions = () => request("/api/sessions");

// Achievements
export const getAchievements  = ()  => request("/api/achievements");
export const checkAchievements = () => request("/api/achievements/check", { method: "POST" });

// Progress
export const getProgressSummary   = () => request("/api/progress/summary");
export const getProgressBySubject = () => request("/api/progress/by-subject");
export const getProgressChart     = () => request("/api/progress/chart");

// Mastery
export const getMastery = (subject) => {
  const p = new URLSearchParams();
  if (subject) p.set("subject", subject);
  return request(`/api/mastery?${p.toString()}`);
};

export const getTopics = (subject) => {
  const p = new URLSearchParams();
  if (subject) p.set("subject", subject);
  return request(`/api/topics?${p.toString()}`);
};

export const getLesson = (subject, topic) =>
  request(`/api/lessons?subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(topic)}`);
