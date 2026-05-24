import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'

const QUESTIONS_PER_SESSION = 10

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function shuffleOptions(q) {
  const idx = shuffle(q.options.map((_, i) => i))
  // Keep correct answer within first 4 slots
  const correctPos = idx.indexOf(q.correct_index)
  if (correctPos >= 4) [idx[3], idx[correctPos]] = [idx[correctPos], idx[3]]
  const trimmed = idx.slice(0, 4)
  return {
    ...q,
    options: trimmed.map(i => q.options[i]),
    correct_index: trimmed.indexOf(q.correct_index),
  }
}

function buildSession(questions) {
  return shuffle(questions).slice(0, QUESTIONS_PER_SESSION).map(shuffleOptions)
}

export default function Quiz() {
  const { topicId } = useParams()
  const navigate = useNavigate()
  const [allQuestions, setAllQuestions] = useState([])
  const [session, setSession] = useState([])
  const [loading, setLoading] = useState(true)
  const [current, setCurrent] = useState(0)
  const [selected, setSelected] = useState(null)
  const [answers, setAnswers] = useState([]) // { selected, correct_index, correct }
  const [done, setDone] = useState(false)
  const [saving, setSaving] = useState(false)
  const [reviewing, setReviewing] = useState(false)

  useEffect(() => {
    api.getQuestions(topicId).then(qs => {
      setAllQuestions(qs)
      setSession(buildSession(qs))
    }).finally(() => setLoading(false))
  }, [topicId])

  function restart() {
    setSession(buildSession(allQuestions))
    setCurrent(0)
    setSelected(null)
    setAnswers([])
    setDone(false)
    setReviewing(false)
  }

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (session.length === 0)
    return <div className="text-center py-20 text-slate-400">No questions yet for this topic.</div>

  const q = session[current]

  function choose(idx) {
    if (selected !== null) return
    setSelected(idx)
  }

  async function next() {
    const isCorrect = selected === q.correct_index
    const newAnswers = [...answers, { selected, correct_index: q.correct_index, correct: isCorrect, q }]
    setAnswers(newAnswers)
    setSelected(null)
    if (current < session.length - 1) {
      setCurrent(current + 1)
    } else {
      setDone(true)
      const score = newAnswers.filter(a => a.correct).length
      setSaving(true)
      await api.saveQuizAttempt(Number(topicId), score, session.length)
      setSaving(false)
    }
  }

  // ── Review screen ────────────────────────────────────────────────────────
  if (done && reviewing) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-800">Answer Review</h2>
          <button onClick={() => setReviewing(false)} className="text-sm text-brand-600 hover:underline">
            ← Back to results
          </button>
        </div>

        <div className="space-y-5">
          {answers.map((a, i) => (
            <div key={i} className={`bg-white rounded-xl border p-5 ${a.correct ? 'border-green-200' : 'border-red-200'}`}>
              <div className="flex items-start gap-2 mb-3">
                <span className={`mt-0.5 text-lg ${a.correct ? 'text-green-500' : 'text-red-400'}`}>
                  {a.correct ? '✓' : '✗'}
                </span>
                <p className="font-medium text-slate-800 text-sm leading-relaxed">{a.q.stem}</p>
              </div>
              <div className="space-y-1.5 ml-6">
                {a.q.options.map((opt, oi) => {
                  const isCorrect = oi === a.q.correct_index
                  const wasChosen = oi === a.selected
                  let cls = 'px-3 py-2 rounded-lg text-sm '
                  if (isCorrect) cls += 'bg-green-50 text-green-800 font-medium'
                  else if (wasChosen && !isCorrect) cls += 'bg-red-50 text-red-700 line-through'
                  else cls += 'text-slate-500'
                  return (
                    <div key={oi} className={cls}>
                      <span className="font-bold mr-1 opacity-60">{String.fromCharCode(65 + oi)}.</span>
                      {opt}
                      {isCorrect && <span className="ml-1 text-xs">✓</span>}
                    </div>
                  )
                })}
              </div>
              {a.q.explanation && (
                <p className="ml-6 mt-2 text-xs text-slate-500 italic">{a.q.explanation}</p>
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 flex gap-3 justify-end">
          <button onClick={restart}
            className="px-5 py-2.5 rounded-xl border border-brand-400 text-brand-600 font-medium hover:bg-brand-50">
            Try Again
          </button>
          <button onClick={() => navigate(-1)}
            className="px-5 py-2.5 rounded-xl bg-brand-500 text-white font-medium hover:bg-brand-600">
            Back to Topics
          </button>
        </div>
      </div>
    )
  }

  // ── Results screen ───────────────────────────────────────────────────────
  if (done) {
    const score = answers.filter(a => a.correct).length
    const pct = Math.round((score / session.length) * 100)
    const emoji = pct >= 80 ? '🎉' : pct >= 60 ? '👍' : '💪'
    const msg = pct >= 80 ? 'Amazing work!' : pct >= 60 ? 'Good effort — keep practicing!' : "Keep going — you've got this!"

    return (
      <div className="max-w-lg mx-auto text-center py-10">
        <div className="text-7xl mb-4">{emoji}</div>
        <h1 className="text-3xl font-bold text-slate-800 mb-1">Quiz Complete!</h1>
        <p className="text-slate-500 mb-6 text-lg">{msg}</p>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 mb-6">
          <div className={`text-6xl font-black mb-2 ${pct >= 80 ? 'text-green-500' : pct >= 60 ? 'text-yellow-500' : 'text-red-400'}`}>
            {pct}%
          </div>
          <p className="text-slate-500 mb-4">{score} correct out of {session.length}</p>
          <div className="h-3 bg-slate-100 rounded-full overflow-hidden mb-4">
            <div className={`h-full rounded-full transition-all duration-700 ${pct >= 80 ? 'bg-green-400' : pct >= 60 ? 'bg-yellow-400' : 'bg-red-400'}`}
              style={{ width: `${pct}%` }} />
          </div>

          {/* Per-question mini strip */}
          <div className="flex gap-1 justify-center flex-wrap">
            {answers.map((a, i) => (
              <div key={i} title={`Q${i + 1}`}
                className={`w-7 h-7 rounded-full text-xs flex items-center justify-center font-bold text-white ${a.correct ? 'bg-green-400' : 'bg-red-300'}`}>
                {i + 1}
              </div>
            ))}
          </div>

          <p className="text-xs text-slate-400 mt-3">{allQuestions.length} questions in pool · {QUESTIONS_PER_SESSION} per attempt</p>
        </div>

        {saving && <p className="text-slate-400 text-sm mb-4">Saving score...</p>}

        <div className="flex gap-3 justify-center flex-wrap">
          <button onClick={() => setReviewing(true)}
            className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-600 font-medium hover:bg-slate-50">
            📋 Review Answers
          </button>
          <button onClick={restart}
            className="px-5 py-2.5 rounded-xl border border-brand-400 text-brand-600 font-medium hover:bg-brand-50">
            Try Again
          </button>
          <button onClick={() => navigate(-1)}
            className="px-5 py-2.5 rounded-xl bg-brand-500 text-white font-medium hover:bg-brand-600">
            Back to Topics
          </button>
        </div>
      </div>
    )
  }

  // ── Quiz screen ──────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => navigate(-1)}
        className="text-brand-600 hover:underline text-sm mb-5 inline-flex items-center gap-1">
        ← Back
      </button>

      <div className="flex justify-between text-sm text-slate-500 mb-2">
        <span>Question {current + 1} of {session.length}</span>
        <span>{answers.filter(a => a.correct).length} correct so far</span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full mb-6 overflow-hidden">
        <div className="h-full bg-brand-400 rounded-full transition-all duration-300"
          style={{ width: `${(current / session.length) * 100}%` }} />
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
        <p className="text-lg font-semibold text-slate-800 mb-6 leading-relaxed">{q.stem}</p>
        <div className="space-y-3">
          {q.options.map((opt, i) => {
            let cls = 'w-full text-left px-5 py-4 rounded-xl border-2 font-medium transition-all text-slate-700 '
            if (selected === null) {
              cls += 'border-slate-200 hover:border-brand-400 hover:bg-brand-50 cursor-pointer'
            } else if (i === q.correct_index) {
              cls += 'border-green-400 bg-green-50 text-green-800'
            } else if (i === selected) {
              cls += 'border-red-400 bg-red-50 text-red-700'
            } else {
              cls += 'border-slate-100 opacity-40 cursor-default'
            }
            return (
              <button key={i} className={cls} onClick={() => choose(i)}>
                <span className="mr-3 font-bold text-slate-400">{String.fromCharCode(65 + i)}.</span>
                {opt}
              </button>
            )
          })}
        </div>

        {selected !== null && (
          <div className={`mt-5 p-4 rounded-xl text-sm leading-relaxed ${
            selected === q.correct_index
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            <span className="font-bold">
              {selected === q.correct_index ? '✓ Correct! ' : '✗ Not quite. '}
            </span>
            {q.explanation}
          </div>
        )}
      </div>

      {selected !== null && (
        <div className="mt-4 flex justify-end">
          <button onClick={next}
            className="px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white font-semibold rounded-xl transition-colors">
            {current < session.length - 1 ? 'Next Question →' : 'See Results'}
          </button>
        </div>
      )}
    </div>
  )
}
