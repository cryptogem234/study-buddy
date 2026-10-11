import { useState } from 'react'

// A question whose answer stays hidden until she taps "Show answer"
export default function Reveal({ label, question, answer }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      {label && <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-1">{label}</p>}
      {question && <p className="font-medium text-slate-800 mb-3 leading-relaxed">{question}</p>}
      {open ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-900 leading-relaxed whitespace-pre-line">
          {answer}
        </div>
      ) : (
        <button onClick={() => setOpen(true)}
          className="text-sm font-medium text-brand-600 hover:text-brand-700 hover:underline">
          Think first, then tap to show the answer →
        </button>
      )}
    </div>
  )
}
