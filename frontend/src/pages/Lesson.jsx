import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

function parseSections(content) {
  const lines = content.split('\n')
  const sections = []
  let current = { heading: 'Introduction', lines: [] }
  for (const line of lines) {
    const h = line.match(/^#{2,3} (.+)/)
    if (h) {
      if (current.lines.some(l => l.trim())) sections.push(current)
      current = { heading: h[1], lines: [line] }
    } else {
      current.lines.push(line)
    }
  }
  if (current.lines.some(l => l.trim())) sections.push(current)
  return sections
}

const mdComponents = {
  h2: ({ children }) => (
    <h2 className="text-xl font-bold text-brand-700 mt-8 mb-3 pb-1 border-b-2 border-brand-100">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-lg font-semibold text-slate-700 mt-6 mb-2">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-slate-700 leading-relaxed mb-4 text-base">{children}</p>
  ),
  ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-1 text-slate-700">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-1 text-slate-700">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => (
    <strong className="font-semibold text-slate-900 bg-yellow-50 px-0.5 rounded">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-slate-600">{children}</em>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-brand-400 pl-4 py-2 my-4 bg-brand-50 rounded-r-xl text-slate-700 not-italic">
      {children}
    </blockquote>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-5 rounded-xl border border-slate-200 shadow-sm">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-brand-50">{children}</thead>,
  th: ({ children }) => (
    <th className="px-4 py-2 text-left font-semibold text-brand-700 border-b border-slate-200">{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2 border-b border-slate-100 text-slate-700">{children}</td>
  ),
  code: ({ children }) => (
    <code className="bg-slate-100 text-brand-700 px-1.5 py-0.5 rounded font-mono text-sm">{children}</code>
  ),
}

export default function Lesson() {
  const { topicId } = useParams()
  const navigate = useNavigate()
  const [lessons, setLessons] = useState([])
  const [current, setCurrent] = useState(0)
  const [loading, setLoading] = useState(true)
  const [marking, setMarking] = useState(false)
  const [readPct, setReadPct] = useState(0)

  useEffect(() => {
    api.getLessons(topicId)
      .then(setLessons)
      .finally(() => setLoading(false))
  }, [topicId])

  // Track reading progress via window scroll
  useEffect(() => {
    const onScroll = () => {
      const scrolled = window.scrollY
      const total = document.documentElement.scrollHeight - window.innerHeight
      setReadPct(total > 0 ? Math.min(100, Math.round((scrolled / total) * 100)) : 100)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [current])

  useEffect(() => {
    window.scrollTo(0, 0)
    setReadPct(0)
  }, [current])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (lessons.length === 0)
    return <div className="text-center py-20 text-slate-400">No lessons for this topic yet.</div>

  const lesson = lessons[current]
  const sections = parseSections(lesson.content)

  async function handleDone() {
    if (!lesson.completed) {
      setMarking(true)
      await api.markLessonComplete(topicId, lesson.id)
      setLessons(prev => prev.map(l => l.id === lesson.id ? { ...l, completed: true } : l))
      setMarking(false)
    }
    if (current < lessons.length - 1) {
      setCurrent(current + 1)
    } else {
      navigate(-1)
    }
  }

  return (
    <div className="w-full">
      {/* Sticky reading progress bar at top of viewport */}
      <div className="fixed top-0 left-0 right-0 h-1 z-50 bg-transparent">
        <div className="h-full bg-brand-500 transition-all duration-200" style={{ width: `${readPct}%` }} />
      </div>

      <button onClick={() => navigate(-1)}
        className="text-brand-600 hover:underline text-sm mb-4 inline-flex items-center gap-1">
        ← Back to topics
      </button>

      {/* Hero */}
      <div className="bg-gradient-to-r from-brand-600 to-violet-600 rounded-2xl p-6 mb-6 text-white shadow-lg">
        <div className="text-xs font-semibold uppercase tracking-widest opacity-70 mb-1">
          Lesson {current + 1} of {lessons.length}
        </div>
        <h1 className="text-2xl font-bold">{lesson.title}</h1>
        <div className="flex items-center gap-3 mt-3">
          <div className="flex-1 h-1.5 bg-white/30 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full transition-all duration-300" style={{ width: `${readPct}%` }} />
          </div>
          <span className="text-xs opacity-70 whitespace-nowrap">{readPct}% read</span>
        </div>
      </div>

      <div className="flex gap-6 items-start">
        {/* Sticky table of contents */}
        {sections.length > 1 && (
          <aside className="hidden lg:block w-56 shrink-0 sticky top-8">
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">Contents</p>
              <ul className="space-y-1">
                {sections.map((s, i) => (
                  <li key={i} className="text-sm text-slate-500 leading-snug py-0.5 truncate" title={s.heading}>
                    {s.heading}
                  </li>
                ))}
              </ul>
            </div>
          </aside>
        )}

        {/* Main content — natural height, page scrolls */}
        <div className="flex-1 min-w-0">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
            <ReactMarkdown components={mdComponents}>
              {lesson.content}
            </ReactMarkdown>
          </div>

          {/* Bottom action bar */}
          <div className="mt-6 flex items-center justify-between pb-8">
            {lessons.length > 1 && (
              <div className="flex gap-2">
                {lessons.map((l, i) => (
                  <button key={l.id} onClick={() => setCurrent(i)} title={l.title}
                    className={`w-3 h-3 rounded-full transition-all ${
                      i === current ? 'bg-brand-500 scale-125'
                      : l.completed ? 'bg-violet-300' : 'bg-slate-200'
                    }`} />
                ))}
              </div>
            )}
            <div className="flex gap-3 ml-auto">
              <button onClick={() => navigate(`/topics/${topicId}/quiz`)}
                className="px-4 py-2.5 rounded-xl border border-brand-300 text-brand-600 font-medium text-sm hover:bg-brand-50 transition-colors">
                🧪 Take Quiz
              </button>
              <button onClick={handleDone} disabled={marking}
                className="px-6 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold rounded-xl transition-colors disabled:opacity-50 text-sm">
                {marking ? 'Saving...'
                  : lesson.completed
                  ? current < lessons.length - 1 ? 'Next →' : 'Done'
                  : current < lessons.length - 1 ? 'Mark Read & Next →' : 'Mark as Done ✓'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
