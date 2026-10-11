import { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { shuffleOptions } from '../lib/shuffle'

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

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// Underline glossary words so she can tap them for a definition
function withGlossary(text, glossary, onPick) {
  if (!glossary.length) return text
  const pattern = new RegExp(`\\b(${glossary.map(g => escapeRegExp(g.word)).join('|')})\\b`, 'gi')
  return text.split(pattern).map((piece, i) => {
    const entry = glossary.find(g => g.word.toLowerCase() === piece.toLowerCase())
    if (!entry) return piece
    return (
      <button key={i} onClick={() => onPick(entry)}
        className="underline decoration-dotted decoration-rose-400 underline-offset-4 hover:bg-rose-50 rounded">
        {piece}
      </button>
    )
  })
}

export default function ReadingPassage() {
  const { passageId } = useParams()
  const navigate = useNavigate()
  const [passage, setPassage] = useState(null)
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [chosen, setChosen] = useState({})
  const [checked, setChecked] = useState(false)
  const [attemptId, setAttemptId] = useState(null)
  const [word, setWord] = useState(null)
  const [written, setWritten] = useState('')
  const [grading, setGrading] = useState(false)
  const [result, setResult] = useState(null)
  const [showModel, setShowModel] = useState(false)

  useEffect(() => {
    api.getPassage(passageId).then(p => {
      setPassage(p)
      setQuestions(p.questions.map(shuffleOptions))
    }).finally(() => setLoading(false))
  }, [passageId])

  const paragraphs = useMemo(
    () => (passage ? passage.text.split(/\n\s*\n/).filter(p => p.trim()) : []),
    [passage],
  )

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (!passage) return <div className="text-center py-20 text-slate-400">Passage not found.</div>
  if (!passage.unlocked) return (
    <div className="text-center py-20 text-slate-500">
      🔒 Pass 3 Core passages with 80% or higher to unlock Level Up passages.
      <div><button onClick={() => navigate('/reading')} className="mt-4 text-brand-600 hover:underline text-sm">← Back to Reading</button></div>
    </div>
  )

  const isPoem = passage.genre.startsWith('Poem')
  const allAnswered = questions.every(q => chosen[q.id] !== undefined)
  const score = questions.filter(q => chosen[q.id] === q.correct_index).length

  async function check() {
    setChecked(true)
    const res = await api.savePassageAttempt(
      passage.id, score, questions.length,
      questions.map(q => ({ question_id: q.id, correct: chosen[q.id] === q.correct_index })),
    )
    setAttemptId(res.id)
  }

  async function getFeedback() {
    setGrading(true)
    try {
      setResult(await api.gradeWritten(attemptId, written))
    } catch {
      setResult({ graded: false })
    } finally {
      setGrading(false)
    }
  }

  function tryAgain() {
    setQuestions(passage.questions.map(shuffleOptions))
    setChosen({})
    setChecked(false)
    setAttemptId(null)
    setWritten('')
    setResult(null)
    setShowModel(false)
    window.scrollTo(0, 0)
  }

  const pct = Math.round((score / questions.length) * 100)

  return (
    <div>
      <button onClick={() => navigate('/reading')} className="text-brand-600 hover:underline text-sm mb-4 inline-flex items-center gap-1">
        ← Back to Reading
      </button>

      <div className={`rounded-2xl p-6 mb-6 text-white shadow-lg bg-gradient-to-r ${
        passage.level === 'level_up' ? 'from-amber-400 to-orange-500' : 'from-rose-400 to-pink-500'
      }`}>
        <div className="text-xs font-semibold uppercase tracking-widest opacity-80 mb-1">
          {passage.level === 'level_up' ? '🚀 Level Up · Grade 9' : 'Core · Grade 8'} · {passage.genre}
        </div>
        <h1 className="text-2xl font-bold">{passage.title}</h1>
        <p className="text-sm opacity-90 mt-1">{passage.word_count} words · Tap an underlined word for its meaning.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6 items-start">
        {/* Passage */}
        <div className="lg:sticky lg:top-4">
          {word && (
            <div className="mb-3 bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-slate-700 flex justify-between gap-3">
              <span><span className="font-bold text-rose-700">{word.word}:</span> {word.definition}</span>
              <button onClick={() => setWord(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
          )}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:max-h-[80vh] lg:overflow-y-auto">
            {paragraphs.map((para, i) => (
              <div key={i} className="flex gap-3 mb-4">
                <span className="text-xs font-bold text-slate-300 w-5 shrink-0 pt-1 text-right">{i + 1}</span>
                <p className={`text-slate-800 leading-relaxed ${isPoem ? 'whitespace-pre-line italic' : ''}`}>
                  {withGlossary(para, passage.glossary, setWord)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Questions and writing */}
        <div className="space-y-5">
          {questions.map((q, qi) => {
            const pick = chosen[q.id]
            return (
              <div key={q.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
                <p className="text-xs font-semibold text-slate-400 mb-1">
                  Question {qi + 1}{checked && ` · ${SKILL_LABELS[q.skill] ?? q.skill}`}
                </p>
                <p className="font-semibold text-slate-800 mb-3 leading-relaxed whitespace-pre-line">{q.stem}</p>
                <div className="space-y-2">
                  {q.options.map((opt, i) => {
                    let cls = 'w-full text-left px-4 py-3 rounded-xl border-2 text-sm transition-all '
                    if (!checked) {
                      cls += pick === i ? 'border-brand-400 bg-brand-50 text-slate-800' : 'border-slate-200 hover:border-brand-300 text-slate-700'
                    } else if (i === q.correct_index) {
                      cls += 'border-green-400 bg-green-50 text-green-800'
                    } else if (i === pick) {
                      cls += 'border-red-400 bg-red-50 text-red-700'
                    } else {
                      cls += 'border-slate-100 text-slate-400'
                    }
                    return (
                      <button key={i} className={cls} disabled={checked} onClick={() => setChosen(c => ({ ...c, [q.id]: i }))}>
                        <span className="font-bold mr-2 text-slate-400">{String.fromCharCode(65 + i)}.</span>{opt}
                      </button>
                    )
                  })}
                </div>
                {checked && (
                  <p className={`mt-3 text-sm rounded-xl p-3 ${pick === q.correct_index ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                    <span className="font-bold">{pick === q.correct_index ? '✓ Correct. ' : '✗ Not quite. '}</span>{q.explanation}
                  </p>
                )}
              </div>
            )
          })}

          {!checked ? (
            <button onClick={check} disabled={!allAnswered}
              className="w-full py-3 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold disabled:opacity-40">
              {allAnswered ? 'Check My Answers' : `Answer all ${questions.length} questions to check`}
            </button>
          ) : (
            <>
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 text-center">
                <div className={`text-4xl font-black ${pct >= 80 ? 'text-green-500' : pct >= 60 ? 'text-yellow-500' : 'text-red-400'}`}>{pct}%</div>
                <p className="text-slate-500 text-sm">{score} of {questions.length} correct{pct >= 80 ? ' — passed!' : ' · 80% passes'}</p>
              </div>

              <div className="bg-white rounded-2xl border-2 border-violet-200 shadow-sm p-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-violet-500 mb-1">✍️ Written Response</p>
                <p className="font-semibold text-slate-800 mb-3 leading-relaxed">{passage.written_prompt}</p>
                <textarea
                  value={written}
                  onChange={e => setWritten(e.target.value)}
                  disabled={grading || result?.graded}
                  rows={8}
                  placeholder="Make a claim, then support it with at least two details from the passage. Explain how each detail supports your claim."
                  className="w-full rounded-xl border border-slate-300 p-3 text-sm leading-relaxed focus:outline-none focus:border-violet-400"
                />
                {!result && (
                  <button onClick={getFeedback} disabled={grading || written.trim().split(/\s+/).length < 25}
                    className="mt-3 px-5 py-2.5 rounded-xl bg-violet-500 hover:bg-violet-600 text-white font-semibold text-sm disabled:opacity-40">
                    {grading ? 'Reading your answer…' : written.trim().split(/\s+/).length < 25 ? 'Write at least 25 words' : 'Get Feedback'}
                  </button>
                )}
                {result?.graded && (
                  <div className="mt-4 rounded-xl bg-violet-50 border border-violet-200 p-4">
                    <p className="font-bold text-violet-800 mb-2">Score: {result.score}/4</p>
                    <p className="text-sm text-slate-700 whitespace-pre-line leading-relaxed">{result.feedback}</p>
                  </div>
                )}
                {result && !result.graded && (
                  <div className="mt-4 rounded-xl bg-slate-50 border border-slate-200 p-4 text-sm text-slate-700">
                    <p className="mb-2">Automatic feedback isn't available right now. Your answer is saved — check it against this list:</p>
                    <ul className="list-disc pl-5 space-y-1">{passage.rubric.map((r, i) => <li key={i}>{r}</li>)}</ul>
                  </div>
                )}
                {result && (
                  showModel ? (
                    <div className="mt-4 rounded-xl bg-green-50 border border-green-200 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-green-700 mb-1">A strong example answer</p>
                      <p className="text-sm text-slate-700 leading-relaxed">{passage.model_answer}</p>
                    </div>
                  ) : (
                    <button onClick={() => setShowModel(true)} className="mt-3 text-sm text-brand-600 hover:underline">
                      Compare with a strong example answer →
                    </button>
                  )
                )}
              </div>

              <div className="flex gap-3 justify-end">
                <button onClick={tryAgain} className="px-5 py-2.5 rounded-xl border border-brand-400 text-brand-600 font-medium hover:bg-brand-50">
                  Try Again
                </button>
                <button onClick={() => navigate('/reading')} className="px-5 py-2.5 rounded-xl bg-brand-500 text-white font-medium hover:bg-brand-600">
                  More Passages
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
