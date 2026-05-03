import { useNavigate } from 'react-router-dom'

const GRADE_COLORS = {
  7: 'from-violet-400 to-purple-500',
  8: 'from-cyan-400 to-blue-500',
}

export default function SubjectCard({ subject }) {
  const navigate = useNavigate()
  const gradient = GRADE_COLORS[subject.grade] ?? 'from-slate-400 to-slate-500'

  return (
    <button
      onClick={() => navigate(`/subjects/${subject.id}`)}
      className="group text-left rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-shadow w-full"
    >
      <div className={`bg-gradient-to-br ${gradient} p-6 text-white`}>
        <div className="text-4xl mb-2">{subject.icon}</div>
        <div className="text-xs font-semibold uppercase tracking-widest opacity-80 mb-1">
          Grade {subject.grade}
        </div>
        <h2 className="text-xl font-bold">{subject.name}</h2>
      </div>
      <div className="bg-white p-4">
        <p className="text-slate-500 text-sm mb-2">{subject.description}</p>
        <span className="text-xs font-medium text-brand-600">
          {subject.topic_count} {subject.topic_count === 1 ? 'topic' : 'topics'} →
        </span>
      </div>
    </button>
  )
}
