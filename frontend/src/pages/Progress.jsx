import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

const STATUS_STYLE = {
  completed:   { dot: 'bg-green-400',  text: 'text-green-600',  label: 'Done' },
  in_progress: { dot: 'bg-amber-400',  text: 'text-amber-600',  label: 'In Progress' },
  not_started: { dot: 'bg-slate-300',  text: 'text-slate-400',  label: 'Not Started' },
}

function fmt(dt) {
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Progress() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [subjects, setSubjects] = useState([])
  const [expanded, setExpanded] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getProgress(), api.getSubjectProgress()])
      .then(([s, sp]) => { setSummary(s); setSubjects(sp) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>

  const avgPct = summary?.average_score != null ? Math.round(summary.average_score) : null

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-6">Your Progress</h1>

      {/* Top stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Study Streak',   value: summary?.current_streak > 0 ? `${summary.current_streak} days` : '—', icon: '🔥' },
          { label: 'Lessons Read',   value: `${summary?.lessons_completed ?? 0}/${summary?.total_lessons ?? 0}`, icon: '📖' },
          { label: 'Quizzes Taken',  value: summary?.quizzes_taken ?? 0, icon: '🧪' },
          { label: 'Avg Score',      value: avgPct != null ? `${avgPct}%` : '—', icon: avgPct >= 80 ? '🌟' : avgPct >= 60 ? '👍' : '💪' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-slate-200 p-5 text-center shadow-sm">
            <div className="text-3xl mb-1">{s.icon}</div>
            <div className="text-2xl font-bold text-slate-800">{s.value}</div>
            <div className="text-xs text-slate-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Per-subject topic breakdown */}
      <h2 className="text-lg font-semibold text-slate-700 mb-4">Topics by Subject</h2>
      <div className="space-y-4 mb-8">
        {subjects.map(subj => {
          const isOpen = expanded[subj.subject_id] ?? false
          const pct = subj.total_count > 0 ? Math.round((subj.completed_count / subj.total_count) * 100) : 0

          return (
            <div key={subj.subject_id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              {/* Subject header — clickable to expand */}
              <button
                onClick={() => setExpanded(e => ({ ...e, [subj.subject_id]: !isOpen }))}
                className="w-full flex items-center gap-4 px-6 py-4 hover:bg-slate-50 transition-colors text-left"
              >
                <span className="text-2xl">{subj.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-800">{subj.subject_name}</div>
                  <div className="text-xs text-slate-400">Grade {subj.grade} · {subj.completed_count}/{subj.total_count} topics complete</div>
                  <div className="mt-1.5 h-1.5 bg-slate-100 rounded-full overflow-hidden w-full">
                    <div className="h-full bg-green-400 rounded-full transition-all" style={{ width: `${pct}%` }} />
                  </div>
                </div>
                <div className="text-lg font-bold text-slate-600">{pct}%</div>
                <span className="text-slate-400 ml-1">{isOpen ? '▲' : '▼'}</span>
              </button>

              {/* Topic list */}
              {isOpen && (
                <div className="border-t border-slate-100 divide-y divide-slate-50">
                  {subj.topics.map(t => {
                    const s = STATUS_STYLE[t.status] ?? STATUS_STYLE.not_started
                    return (
                      <div key={t.topic_id} className="flex items-center gap-3 px-6 py-3 hover:bg-slate-50 cursor-pointer"
                        onClick={() => navigate(`/topics/${t.topic_id}/lesson`)}>
                        <span className={`w-2 h-2 rounded-full shrink-0 ${s.dot}`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-700 truncate">{t.topic_name}</p>
                          <p className="text-xs text-slate-400">Term {t.term} · {t.unit}</p>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          {t.best_score != null && (
                            <span className={`text-xs font-semibold ${
                              t.best_score >= 80 ? 'text-green-600' : t.best_score >= 60 ? 'text-amber-600' : 'text-red-400'
                            }`}>
                              {Math.round(t.best_score)}%
                            </span>
                          )}
                          <span className={`text-xs font-medium ${s.text}`}>{s.label}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Recent quiz history */}
      {summary?.recent_attempts?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-700">Recent Quizzes</h2>
          </div>
          <ul className="divide-y divide-slate-100">
            {summary.recent_attempts.map(a => {
              const pct = Math.round((a.score / a.total) * 100)
              return (
                <li key={a.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-slate-700">{a.score}/{a.total} correct</div>
                    <div className="text-xs text-slate-400 mt-0.5">{fmt(a.attempted_at)}</div>
                  </div>
                  <span className={`text-lg font-bold ${pct >= 80 ? 'text-green-500' : pct >= 60 ? 'text-yellow-500' : 'text-red-400'}`}>
                    {pct}%
                  </span>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}
