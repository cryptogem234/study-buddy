import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import SubjectCard from '../components/SubjectCard'

export default function Home() {
  const [subjects, setSubjects] = useState([])
  const [progress, setProgress] = useState(null)
  const [reading, setReading] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([api.getSubjects(), api.getProgress(), api.getReadingProgress()])
      .then(([s, p, r]) => { setSubjects(s); setProgress(p); setReading(r) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>

  const streak = progress?.current_streak ?? 0
  const lessonsDone = progress?.lessons_completed ?? 0
  const totalLessons = progress?.total_lessons ?? 0
  const quizzesTaken = progress?.quizzes_taken ?? 0
  const avgScore = progress?.average_score != null ? Math.round(progress.average_score) : null

  return (
    <div>
      {/* Welcome */}
      <div className="mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Hi Aashi! 👋</h1>
          <p className="text-slate-500 mt-1 text-lg">What do you want to study today?</p>
        </div>

        {/* Streak badge */}
        {streak > 0 && (
          <div className="flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-2xl px-5 py-3 shadow-sm">
            <span className="text-3xl">🔥</span>
            <div>
              <div className="text-2xl font-black text-orange-500">{streak}</div>
              <div className="text-xs text-orange-400 font-medium leading-tight">day streak</div>
            </div>
          </div>
        )}
      </div>

      {/* Quick stats */}
      {progress && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {[
            { icon: '📖', value: `${lessonsDone}/${totalLessons}`, label: 'Lessons Read' },
            { icon: '🧪', value: quizzesTaken, label: 'Quizzes Taken' },
            { icon: '🎯', value: avgScore != null ? `${avgScore}%` : '—', label: 'Avg Quiz Score' },
            { icon: streak > 0 ? '🔥' : '⭐', value: streak > 0 ? `${streak} days` : 'Start!', label: 'Study Streak' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl border border-slate-200 p-4 text-center shadow-sm">
              <div className="text-2xl mb-1">{s.icon}</div>
              <div className="text-xl font-bold text-slate-800">{s.value}</div>
              <div className="text-xs text-slate-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Reading Comprehension */}
      {reading?.passages_total > 0 && (
        <button onClick={() => navigate('/reading')}
          className="w-full text-left mb-8 rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-shadow bg-gradient-to-r from-rose-400 to-pink-500 text-white p-6 flex items-center gap-5 flex-wrap">
          <span className="text-5xl">📖</span>
          <div className="flex-1 min-w-[12rem]">
            <div className="text-xs font-semibold uppercase tracking-widest opacity-80">Grade 8 · Level Up to Grade 9</div>
            <h2 className="text-2xl font-bold">Reading Comprehension</h2>
            <p className="text-sm opacity-90 mt-1">Read a passage, answer MCAS-style questions, and get feedback on your writing.</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-black">{reading.passages_done}/{reading.passages_total}</div>
            <div className="text-xs opacity-80">passages read</div>
          </div>
        </button>
      )}

      {/* Subject cards */}
      <h2 className="text-lg font-semibold text-slate-700 mb-4">Choose a Subject</h2>
      {subjects.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          No subjects yet. Run <code className="text-sm bg-slate-100 px-1 rounded">python seed_data.py</code> in the backend folder.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {subjects.filter(s => !s.archived).map(s => <SubjectCard key={s.id} subject={s} />)}
          </div>
          {subjects.some(s => s.archived) && (
            <>
              <h2 className="text-lg font-semibold text-slate-700 mt-10 mb-1">Review: 7th Grade</h2>
              <p className="text-sm text-slate-400 mb-4">You finished these — come back any time to refresh.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 opacity-80">
                {subjects.filter(s => s.archived).map(s => <SubjectCard key={s.id} subject={s} />)}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
