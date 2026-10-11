import { useEffect, useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'
import Reveal from '../components/Reveal'

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

// Split lesson markdown at "## " headings so add-ons can be placed between sections
function splitH2(content) {
  const parts = []
  let current = { heading: '', text: [] }
  for (const line of content.split('\n')) {
    const h = line.match(/^## (.+)/)
    if (h) {
      parts.push(current)
      current = { heading: h[1].trim(), text: [line] }
    } else {
      current.text.push(line)
    }
  }
  parts.push(current)
  return parts.filter(p => p.text.some(l => l.trim())).map(p => ({ heading: p.heading, text: p.text.join('\n') }))
}

function checkYourselfIndex(parts) {
  for (const prefix of ['Real-World', 'Practice It', 'Think About It', 'Key Vocabulary', 'Summary']) {
    const i = parts.findIndex(p => p.heading.startsWith(prefix))
    if (i > 0) return i
  }
  return parts.length
}

function CheckYourself({ items }) {
  return (
    <div className="my-8 rounded-2xl border-2 border-sky-200 bg-sky-50 p-5">
      <h2 className="text-lg font-bold text-sky-800 mb-1">✅ Check Yourself</h2>
      <p className="text-sm text-sky-700 mb-4">Answer each one in your head (or out loud) before you peek.</p>
      <div className="space-y-3">
        {items.map((c, i) => <Reveal key={i} label={`Question ${i + 1}`} question={c.question} answer={c.answer} />)}
      </div>
    </div>
  )
}

function ThinkAnswers({ items }) {
  return (
    <div className="mb-6 space-y-3">
      {items.map(a => (
        <Reveal key={a.number} label={items.length > 1 ? `Model answer ${a.number}` : 'Model answer'} answer={a.answer} />
      ))}
    </div>
  )
}

function LevelUp({ levelUp, unlocked, quizCount, topicId, navigate }) {
  return (
    <div id="level-up" className="mt-10 rounded-2xl overflow-hidden border-2 border-amber-300 scroll-mt-6">
      <div className="bg-gradient-to-r from-amber-400 to-orange-500 px-6 py-4 text-white">
        <div className="text-xs font-semibold uppercase tracking-widest opacity-90">🚀 Level Up · Grade 9</div>
        <h2 className="text-xl font-bold">{levelUp.title}</h2>
        <div className="text-xs opacity-90 mt-0.5">{levelUp.standard}</div>
      </div>
      {unlocked ? (
        <div className="bg-amber-50/40 p-6">
          <ReactMarkdown components={mdComponents}>{levelUp.content}</ReactMarkdown>
          <h3 className="text-lg font-semibold text-slate-700 mt-6 mb-3">Check Yourself</h3>
          <div className="space-y-3 mb-6">
            {levelUp.checks.map((c, i) => <Reveal key={i} label={`Question ${i + 1}`} question={c.question} answer={c.answer} />)}
          </div>
          {quizCount > 0 ? (
            <button onClick={() => navigate(`/topics/${topicId}/quiz?level=level_up`)}
              className="px-5 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-semibold text-sm transition-colors">
              🚀 Take the Level Up Quiz
            </button>
          ) : (
            <p className="text-sm text-slate-500 italic">The Level Up quiz for this topic is coming soon.</p>
          )}
        </div>
      ) : (
        <div className="bg-white p-6 text-center">
          <div className="text-4xl mb-2">🔒</div>
          <p className="text-slate-700 font-medium">Pass the Core quiz with 80% or higher to unlock this Grade 9 challenge.</p>
          <button onClick={() => navigate(`/topics/${topicId}/quiz`)}
            className="mt-4 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold text-sm transition-colors">
            🧪 Take the Core Quiz
          </button>
        </div>
      )}
    </div>
  )
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
  const location = useLocation()
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
    if (location.hash === '#level-up' && lessons.length) {
      document.getElementById('level-up')?.scrollIntoView()
      return
    }
    window.scrollTo(0, 0)
    setReadPct(0)
  }, [current, lessons.length, location.hash])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (lessons.length === 0)
    return <div className="text-center py-20 text-slate-400">No lessons for this topic yet.</div>

  const lesson = lessons[current]
  const sections = parseSections(lesson.content)
  const extras = lesson.extras
  const parts = splitH2(lesson.content)
  const checkAt = checkYourselfIndex(parts)

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
            {parts.map((part, i) => (
              <div key={i}>
                {i === checkAt && extras?.check_yourself?.length > 0 && <CheckYourself items={extras.check_yourself} />}
                <ReactMarkdown components={mdComponents}>{part.text}</ReactMarkdown>
                {part.heading.startsWith('Think About It') && extras?.think_answers?.length > 0 && (
                  <ThinkAnswers items={extras.think_answers} />
                )}
              </div>
            ))}
            {checkAt === parts.length && extras?.check_yourself?.length > 0 && <CheckYourself items={extras.check_yourself} />}
            {extras?.level_up && (
              <LevelUp levelUp={extras.level_up} unlocked={lesson.level_up_unlocked} quizCount={lesson.level_up_count} topicId={topicId} navigate={navigate} />
            )}
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
