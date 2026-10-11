import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function minutes(words) {
  return Math.max(2, Math.round(words / 200))
}

function PassageCard({ p, onOpen }) {
  const locked = !p.unlocked
  return (
    <button
      onClick={() => !locked && onOpen(p.id)}
      disabled={locked}
      className={`text-left bg-white rounded-xl border shadow-sm p-4 flex flex-col gap-2 transition-shadow ${
        locked ? 'opacity-60 cursor-default border-slate-200' : 'hover:shadow-md ' + (p.passed ? 'border-green-200' : 'border-slate-200')
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-slate-500">{p.genre}</span>
        {p.best_score != null && (
          <span className={`text-xs font-bold ${p.best_score >= 80 ? 'text-green-600' : p.best_score >= 60 ? 'text-amber-600' : 'text-red-400'}`}>
            {p.passed ? '✓ ' : ''}{Math.round(p.best_score)}%
          </span>
        )}
      </div>
      <h3 className="font-semibold text-slate-800 leading-snug">{locked ? '🔒 ' : ''}{p.title}</h3>
      <p className="text-xs text-slate-400 mt-auto">{p.word_count} words · about {minutes(p.word_count)} min read</p>
    </button>
  )
}

export default function Reading() {
  const navigate = useNavigate()
  const [passages, setPassages] = useState([])
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getPassages(), api.getReadingProgress()])
      .then(([ps, pr]) => { setPassages(ps); setProgress(pr) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (passages.length === 0) return <div className="text-center py-20 text-slate-400">No reading passages yet.</div>

  const core = passages.filter(p => p.level === 'core')
  const levelUp = passages.filter(p => p.level === 'level_up')
  const open = id => navigate(`/reading/${id}`)

  return (
    <div>
      <div className="mb-8 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📖 Reading Comprehension</h1>
          <p className="text-slate-500 mt-1">Read closely, answer the questions, then write a short response and get feedback.</p>
        </div>
        {progress && (
          <div className="flex gap-3">
            <div className="bg-white rounded-xl border border-slate-200 px-4 py-3 text-center shadow-sm">
              <div className="text-xl font-bold text-slate-800">{progress.passages_done}/{progress.passages_total}</div>
              <div className="text-xs text-slate-400">passages read</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 px-4 py-3 text-center shadow-sm">
              <div className="text-xl font-bold text-slate-800">{progress.average_score != null ? `${Math.round(progress.average_score)}%` : '—'}</div>
              <div className="text-xs text-slate-400">avg score</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 px-4 py-3 text-center shadow-sm">
              <div className="text-xl font-bold text-slate-800">{progress.written_average != null ? `${progress.written_average.toFixed(1)}/4` : '—'}</div>
              <div className="text-xs text-slate-400">writing avg</div>
            </div>
          </div>
        )}
      </div>

      <section className="mb-10 rounded-2xl border border-rose-100 bg-gradient-to-b from-rose-50 to-white p-5">
        <h2 className="font-semibold text-slate-600 text-sm uppercase tracking-wide mb-4">Core · Grade 8</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {core.map(p => <PassageCard key={p.id} p={p} onOpen={open} />)}
        </div>
      </section>

      {levelUp.length > 0 && (
        <section className="rounded-2xl border border-amber-200 bg-gradient-to-b from-amber-50 to-white p-5">
          <h2 className="font-semibold text-slate-600 text-sm uppercase tracking-wide mb-1">🚀 Level Up · Grade 9</h2>
          {!progress?.level_up_unlocked && (
            <p className="text-sm text-amber-700 mb-4">
              Score 80% or higher on {progress?.core_passed_needed} more Core {progress?.core_passed_needed === 1 ? 'passage' : 'passages'} to unlock these.
            </p>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {levelUp.map(p => <PassageCard key={p.id} p={p} onOpen={open} />)}
          </div>
        </section>
      )}
    </div>
  )
}
