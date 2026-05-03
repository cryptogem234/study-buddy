const BASE = ''  // proxied through Vite to localhost:8000

async function get(path) {
  const res = await fetch(BASE + path)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`)
  return res.json()
}

export const api = {
  getSubjects: () => get('/subjects'),
  getTopics: (subjectId) => get(`/subjects/${subjectId}/topics`),
  getLessons: (topicId) => get(`/topics/${topicId}/lessons`),
  getQuestions: (topicId) => get(`/topics/${topicId}/questions`),
  saveQuizAttempt: (topicId, score, total) =>
    post('/quiz-attempts', { topic_id: topicId, score, total }),
  markLessonComplete: (topicId, lessonId) =>
    post(`/topics/${topicId}/lesson-progress`, { lesson_id: lessonId }),
  getProgress: () => get('/progress'),
  getSubjectProgress: () => get('/progress/subjects'),
}
