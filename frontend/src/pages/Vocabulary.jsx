import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export default function Vocabulary() {
  const { topicId } = useParams()
  const navigate = useNavigate()
  const [words, setWords] = useState([])
  const [current, setCurrent] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getVocabulary(topicId)
      .then(ws => setWords(ws))
      .finally(() => setLoading(false))
  }, [topicId])

  function prev() {
    setFlipped(false)
    setTimeout(() => setCurrent(c => Math.max(0, c - 1)), 50)
  }

  function next() {
    setFlipped(false)
    setTimeout(() => setCurrent(c => Math.min(words.length - 1, c + 1)), 50)
  }

  function doShuffle() {
    setFlipped(false)
    setWords(w => shuffle(w))
    setCurrent(0)
  }

  if (loading) return <div className="text-center py-20 text-slate-400">Loading...</div>
  if (words.length === 0) return (
    <div className="text-center py-20 text-slate-400">
      <p className="text-4xl mb-4">📚</p>
      <p>No vocabulary words yet for this topic.</p>
      <button onClick={() => navigate(-1)} className="mt-4 text-brand-600 hover:underline text-sm">← Back</button>
    </div>
  )

  const word = words[current]
  const isLast = current === words.length - 1
  const progress = ((current + 1) / words.length) * 100

  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => navigate(-1)}
        className="text-brand-600 hover:underline text-sm mb-5 inline-flex items-center gap-1">
        ← Back
      </button>

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Vocabulary Flashcards</h1>
        <button onClick={doShuffle}
          className="text-sm px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
          🔀 Shuffle
        </button>
      </div>

      {/* Progress bar */}
      <div className="flex justify-between text-sm text-slate-500 mb-2">
        <span>Card {current + 1} of {words.length}</span>
        <span className="text-xs text-slate-400">Tap card to flip</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full mb-6 overflow-hidden">
        <div className="h-full bg-purple-400 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }} />
      </div>

      {/* Flashcard with 3D flip */}
      <div
        style={{ perspective: '1200px' }}
        className="cursor-pointer mb-6 select-none"
        onClick={() => setFlipped(f => !f)}
      >
        <div style={{
          position: 'relative',
          height: '320px',
          transformStyle: 'preserve-3d',
          transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
          transition: 'transform 0.45s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          {/* Front — word */}
          <div
            style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
            className="absolute inset-0 bg-white rounded-2xl border-2 border-purple-200 shadow-md flex flex-col items-center justify-center p-8"
          >
            <p className="text-xs uppercase tracking-widest text-purple-400 mb-6 font-medium">Vocabulary Word</p>
            <p className="text-4xl font-bold text-slate-800 text-center leading-tight">{word.word}</p>
            {word.part_of_speech && (
              <p className="mt-5 text-sm text-slate-400 italic">{word.part_of_speech}</p>
            )}
            <p className="mt-8 text-xs text-slate-300">tap to reveal definition</p>
          </div>

          {/* Back — definition + example */}
          <div
            style={{
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
            }}
            className="absolute inset-0 bg-purple-50 rounded-2xl border-2 border-purple-300 shadow-md flex flex-col justify-center p-8"
          >
            <p className="text-xs uppercase tracking-widest text-purple-400 mb-3 font-medium">Definition</p>
            <p className="text-lg text-slate-800 leading-relaxed font-medium mb-5">{word.definition}</p>
            {word.example_sentence && (
              <>
                <p className="text-xs uppercase tracking-widest text-purple-400 mb-2 font-medium">Example</p>
                <p className="text-sm text-slate-600 italic leading-relaxed">"{word.example_sentence}"</p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-3 justify-center">
        <button
          onClick={prev}
          disabled={current === 0}
          className="px-6 py-3 rounded-xl border border-slate-200 text-slate-600 font-medium hover:bg-slate-50 transition-colors disabled:opacity-30 disabled:cursor-default"
        >
          ← Previous
        </button>
        <button
          onClick={next}
          disabled={isLast}
          className="px-6 py-3 rounded-xl bg-purple-500 text-white font-medium hover:bg-purple-600 transition-colors disabled:opacity-30 disabled:cursor-default"
        >
          Next →
        </button>
      </div>

      {/* Completion message */}
      {isLast && (
        <div className="mt-8 text-center bg-purple-50 rounded-2xl border border-purple-200 p-6">
          <p className="text-2xl mb-2">🎉</p>
          <p className="text-slate-700 font-medium mb-1">You've reviewed all {words.length} words!</p>
          <p className="text-slate-400 text-sm mb-4">Shuffle and go again to strengthen your memory.</p>
          <button
            onClick={doShuffle}
            className="px-5 py-2.5 rounded-xl border border-purple-400 text-purple-600 font-medium hover:bg-purple-100 transition-colors"
          >
            🔀 Shuffle & Start Over
          </button>
        </div>
      )}
    </div>
  )
}
