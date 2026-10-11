import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

const STATUS_STYLE = {
  completed:   { dot: 'bg-green-400',  text: 'text-green-600',  label: 'Done' },
  in_progress: { dot: 'bg-amber-400',  text: 'text-amber-600',  label: 'In Progress' },
  not_started: { dot: 'bg-slate-300',  text: 'text-slate-400',  label: 'Not Started' },
}

const TREND_STYLE = {
  up:   { icon: '▲', text: 'text-green-500' },
  down: { icon: '▼', text: 'text-red-400' },
  flat: { icon: '▬', text: 'text-slate-400' },
}

const SKILL_LABELS = {
  central_idea: 'Central idea / theme',
  inference: 'Inference',
  textual_evidence: 'Text evidence',
  vocabulary_in_context: 'Vocabulary in context',
  author_purpose: "Author's purpose",
  text_structure: 'Text structure',
  point_of_view: 'Point of view',
  figurative_language: 'Figurative language',
  argument_rhetoric: 'Argument & rhetoric',
  character_plot: 'Character & plot',
}

function ReadingCard({ reading, onOpen }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mb-8">
      <div className="flex items-center justify-between gap-4 flex-wrap mb-4">
        <h2 className="text-lg font-semibold text-slate-700">📖 Reading Comprehension</h2>
        <button onClick={onOpen} className="text-sm text-brand-600 hover:underline">Go to Reading →</button>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {[
          { label: 'Passages read', value: `${reading.passages_done}/${reading.passages_total}` },
          { label: 'Passed (80%+)', value: reading.passages_passed },
          { label: 'Avg question score', value: reading.average_score != null ? `${Math.round(reading.average_score)}%` : '—' },
          { label: 'Writing avg', value: reading.written_average != null ? `${reading.written_average.toFixed(1)}/4` : '—' },
        ].map(s => (
          <div key={s.label} className="bg-slate-50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-slate-800">{s.value}</div>
            <div className="text-xs text-slate-500">{s.label}</div>
          </div>
        ))}
      </div>
      {reading.skills.length > 0 ? (
        <>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Reading skills (weakest first)</p>
          <div className="space-y-2">
            {reading.skills.map(sk => {
              const pct = Math.round((sk.correct / sk.total) * 100)
              return (
                <div key={sk.skill} className="flex items-center gap-3 text-sm">
                  <span className="w-44 shrink-0 text-slate-600">{SKILL_LABELS[sk.skill] ?? sk.skill}</span>
                  <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${pct >= 80 ? 'bg-green-400' : pct >= 60 ? 'bg-yellow-400' : 'bg-red-300'}`} style={{ width: `${pct}%` }} />
                  </div>
                  <span className="w-20 text-right text-xs text-slate-500">{pct}% ({sk.correct}/{sk.total})</span>
                </div>
              )
            })}
          </div>
        </>
      ) : (
        <p className="text-sm text-slate-400">Skill breakdown appears after the first passage.</p>
      )}
    </div>
  )
}

function fmt(dt) {
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Progress() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [subjects, setSubjects] = useState([])
  const [expanded, setExpanded] = useState({})
  const [historyOpen, setHistoryOpen] = useState({})
  const [reading, setReading] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getProgress(), api.getSubjectProgress(), api.getReadingProgress()])
      .then(([s, sp, r]) => { setSummary(s); setSubjects(sp); setReading(r) })
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

      {reading?.passages_total > 0 && <ReadingCard reading={reading} onOpen={() => navigate('/reading')} />}

      {/* Per-subject topic breakdown */}
      {[
        { title: 'Topics by Subject', list: subjects.filter(s => !s.archived) },
        { title: 'Review: 7th Grade', list: subjects.filter(s => s.archived) },
      ].filter(g => g.list.length > 0).map(group => (
      <div key={group.title}>
      <h2 className="text-lg font-semibold text-slate-700 mb-4">{group.title}</h2>
      <div className="space-y-4 mb-8">
        {group.list.map(subj => {
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
                  <div className="text-xs text-slate-400">
                    Grade {subj.grade} · {subj.completed_count}/{subj.total_count} topics complete
                    {subj.level_up_total > 0 && <> · ⭐ {subj.level_up_passed_count}/{subj.level_up_total} Level Up</>}
                  </div>
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
                    const trend = TREND_STYLE[t.trend]
                    const historyIsOpen = historyOpen[t.topic_id] ?? false
                    return (
                      <div key={t.topic_id}>
                        <div className="flex items-center gap-3 px-6 py-3 hover:bg-slate-50 cursor-pointer"
                          onClick={() => navigate(`/topics/${t.topic_id}/lesson`)}>
                          <span className={`w-2 h-2 rounded-full shrink-0 ${s.dot}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-slate-700 truncate">
                              {t.topic_name}
                              {t.level_up_passed && <span className="ml-1" title="Level Up star (Grade 9)">⭐</span>}
                            </p>
                            <p className="text-xs text-slate-400">Term {t.term} · {t.unit}</p>
                          </div>
                          <div className="flex items-center gap-3 shrink-0">
                            {t.best_score != null && (
                              <span className={`text-xs font-semibold inline-flex items-center gap-1 ${
                                t.best_score >= 80 ? 'text-green-600' : t.best_score >= 60 ? 'text-amber-600' : 'text-red-400'
                              }`}>
                                {Math.round(t.best_score)}%
                                {trend && <span className={trend.text}>{trend.icon}</span>}
                              </span>
                            )}
                            <span className={`text-xs font-medium ${s.text}`}>{s.label}</span>
                            {t.attempts.length > 0 && (
                              <button
                                onClick={(e) => { e.stopPropagation(); setHistoryOpen(h => ({ ...h, [t.topic_id]: !historyIsOpen })) }}
                                className="text-xs text-slate-400 hover:text-brand-600 underline"
                              >
                                {t.attempts.length} {t.attempts.length === 1 ? 'quiz' : 'quizzes'}
                              </button>
                            )}
                          </div>
                        </div>
                        {historyIsOpen && t.attempts.length > 0 && (
                          <div className="px-6 pb-3 pl-11">
                            <ul className="space-y-1">
                              {t.attempts.map(a => {
                                const pct = Math.round((a.score / a.total) * 100)
                                return (
                                  <li key={a.id} className="flex items-center justify-between text-xs text-slate-500 bg-slate-50 rounded-lg px-3 py-1.5">
                                    <span>
                                      {fmt(a.attempted_at)}
                                      {a.level === 'level_up' && <span className="ml-2 font-semibold text-orange-500">🚀 Level Up</span>}
                                    </span>
                                    <span className={`font-semibold ${pct >= 80 ? 'text-green-600' : pct >= 60 ? 'text-amber-600' : 'text-red-400'}`}>
                                      {a.score}/{a.total} · {pct}%
                                    </span>
                                  </li>
                                )
                              })}
                            </ul>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>

      </div>
      ))}

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
