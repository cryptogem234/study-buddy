// Talk to the backend directly so the app doesn't depend on the dev server's proxy list
const BASE = `http://${window.location.hostname}:8000`

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
  getQuestions: (topicId, level = 'core') => get(`/topics/${topicId}/questions?level=${level}`),
  saveQuizAttempt: (topicId, score, total, level = 'core', answers = null) =>
    post('/quiz-attempts', { topic_id: topicId, score, total, level, answers }),
  markLessonComplete: (topicId, lessonId) =>
    post(`/topics/${topicId}/lesson-progress`, { lesson_id: lessonId }),
  getProgress: () => get('/progress'),
  getSubjectProgress: () => get('/progress/subjects'),
  getVocabulary: (topicId) => get(`/topics/${topicId}/vocabulary`),
  getPassages: () => get('/passages'),
  getPassage: (passageId) => get(`/passages/${passageId}`),
  savePassageAttempt: (passageId, score, total, answers) =>
    post('/passage-attempts', { passage_id: passageId, score, total, answers }),
  gradeWritten: (attemptId, answer) => post(`/passage-attempts/${attemptId}/written`, { answer }),
  getReadingProgress: () => get('/reading-progress'),
}
