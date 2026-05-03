import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import TopicCard from '../components/TopicCard'

const TERM_COLORS = {
  1: 'bg-violet-100 text-violet-700 border-violet-300',
  2: 'bg-cyan-100 text-cyan-700 border-cyan-300',
  3: 'bg-amber-100 text-amber-700 border-amber-300',
}

const TERM_BG = {
  1: 'from-violet-50 to-white border-violet-100',
  2: 'from-cyan-50 to-white border-cyan-100',
  3: 'from-amber-50 to-white border-amber-100',
}

export default function Topics() {
  const { subjectId } = useParams()
  const navigate = useNavigate()
  const [topics, setTopics] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTerm, setActiveTerm] = useState(0) // 0 = all

  useEffect(() => {
    api.getTopics(subjectId)
      .then(setTopics)
      .finally(() => setLoading(false))
  }, [subjectId])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>

  // Derive unique terms in order
  const terms = [...new Set(topics.map(t => t.term))].sort()

  // Group by term → unit
  const grouped = {}
  for (const term of terms) {
    const termTopics = topics.filter(t => t.term === term)
    const units = [...new Set(termTopics.map(t => t.unit))]
    grouped[term] = units.map(unit => ({
      unit,
      topics: termTopics.filter(t => t.unit === unit),
    }))
  }

  const visibleTerms = activeTerm === 0 ? terms : [activeTerm]

  const total = topics.length
  const completed = topics.filter(t => t.status === 'completed').length
  const inProgress = topics.filter(t => t.status === 'in_progress').length

  return (
    <div>
      {/* Header */}
      <button
        onClick={() => navigate('/')}
        className="text-brand-600 hover:underline text-sm mb-5 inline-flex items-center gap-1"
      >
        ← Back to subjects
      </button>

      {/* Summary bar */}
      <div className="flex items-center gap-6 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Topics</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {completed} completed · {inProgress} in progress · {total - completed - inProgress} not started
          </p>
        </div>
        <div className="ml-auto flex-1 max-w-xs">
          <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-400 rounded-full transition-all"
              style={{ width: `${total > 0 ? (completed / total) * 100 : 0}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-1 text-right">{Math.round((completed / total) * 100)}% complete</p>
        </div>
      </div>

      {/* Term filter tabs */}
      <div className="flex gap-2 mb-7 flex-wrap">
        <button
          onClick={() => setActiveTerm(0)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            activeTerm === 0
              ? 'bg-slate-700 text-white border-slate-700'
              : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'
          }`}
        >
          All Terms
        </button>
        {terms.map(term => (
          <button
            key={term}
            onClick={() => setActiveTerm(term)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              activeTerm === term
                ? 'bg-slate-700 text-white border-slate-700'
                : `${TERM_COLORS[term] || 'bg-white text-slate-600 border-slate-200'} hover:opacity-80`
            }`}
          >
            Term {term}
          </button>
        ))}
      </div>

      {/* Terms + units */}
      {visibleTerms.map(term => (
        <div key={term} className="mb-10">
          <div className={`flex items-center gap-3 mb-4`}>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${TERM_COLORS[term] || ''}`}>
              TERM {term}
            </span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          {grouped[term].map(({ unit, topics: unitTopics }) => (
            <div key={unit} className={`mb-6 rounded-2xl border bg-gradient-to-b p-5 ${TERM_BG[term] || 'from-slate-50 to-white border-slate-100'}`}>
              <h3 className="font-semibold text-slate-600 text-sm uppercase tracking-wide mb-4">{unit}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {unitTopics.map(t => (
                  <TopicCard key={t.id} topic={t} />
                ))}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
