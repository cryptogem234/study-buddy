import { useNavigate } from 'react-router-dom'

const STATUS = {
  completed:   { label: 'Completed',   cls: 'bg-green-100 text-green-700',   dot: 'bg-green-400' },
  in_progress: { label: 'In Progress', cls: 'bg-amber-100 text-amber-700',   dot: 'bg-amber-400' },
  not_started: { label: 'Not Started', cls: 'bg-slate-100 text-slate-500',   dot: 'bg-slate-300' },
}

export default function TopicCard({ topic }) {
  const navigate = useNavigate()
  const s = STATUS[topic.status] ?? STATUS.not_started
  const lessonPct = topic.lesson_count > 0
    ? Math.round((topic.lessons_completed / topic.lesson_count) * 100)
    : 0

  return (
    <div className={`bg-white rounded-xl border shadow-sm p-4 flex flex-col gap-3 transition-shadow hover:shadow-md ${
      topic.status === 'completed' ? 'border-green-200' : 'border-slate-200'
    }`}>
      {/* Status badge */}
      <div className="flex items-center justify-between">
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${s.cls}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
          {s.label}
        </span>
        {topic.best_score !== null && topic.best_score !== undefined && (
          <span className={`text-xs font-bold ${
            topic.best_score >= 80 ? 'text-green-600' : topic.best_score >= 60 ? 'text-amber-600' : 'text-red-400'
          }`}>
            {Math.round(topic.best_score)}% best
          </span>
        )}
      </div>

      {/* Name */}
      <h3 className="font-semibold text-slate-800 text-sm leading-snug">{topic.name}</h3>

      {/* Lesson progress bar */}
      {topic.lesson_count > 0 && (
        <div>
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>{topic.lessons_completed}/{topic.lesson_count} lessons</span>
            <span>{lessonPct}%</span>
          </div>
          <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-violet-400 rounded-full transition-all"
              style={{ width: `${lessonPct}%` }}
            />
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-1.5 mt-auto pt-1">
        {topic.lesson_count > 0 && (
          <button
            onClick={() => navigate(`/topics/${topic.id}/lesson`)}
            className="flex-1 py-2 rounded-lg bg-violet-50 text-violet-700 font-medium text-xs hover:bg-violet-100 transition-colors"
          >
            📖 Study
          </button>
        )}
        {topic.lesson_count > 0 && (
          <button
            onClick={() => navigate(`/topics/${topic.id}/vocabulary`)}
            className="flex-1 py-2 rounded-lg bg-purple-50 text-purple-700 font-medium text-xs hover:bg-purple-100 transition-colors"
          >
            📚 Vocab
          </button>
        )}
        {topic.question_count > 0 && (
          <button
            onClick={() => navigate(`/topics/${topic.id}/quiz`)}
            className={`flex-1 py-2 rounded-lg font-medium text-xs transition-colors ${
              topic.status === 'completed'
                ? 'bg-green-50 text-green-700 hover:bg-green-100'
                : 'bg-brand-50 text-brand-700 hover:bg-brand-100'
            }`}
          >
            {topic.status === 'completed' ? '🏆 Retry' : '🧪 Quiz'}
          </button>
        )}
      </div>
    </div>
  )
}
