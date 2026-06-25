import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getSessionSummary } from '../utils/api.js'
import {
  CheckCircle2, XCircle, AlertCircle, Loader2,
  RotateCcw, TrendingUp, Star, ChevronDown, ChevronUp
} from 'lucide-react'

const RECOMMENDATION_STYLES = {
  'Strong Hire': { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-300', icon: CheckCircle2, iconColor: 'text-green-600' },
  'Hire': { bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-300', icon: CheckCircle2, iconColor: 'text-blue-600' },
  'Maybe': { bg: 'bg-yellow-50', text: 'text-yellow-800', border: 'border-yellow-300', icon: AlertCircle, iconColor: 'text-yellow-600' },
  'No Hire': { bg: 'bg-red-50', text: 'text-red-800', border: 'border-red-300', icon: XCircle, iconColor: 'text-red-600' },
  'Review Required': { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-300', icon: AlertCircle, iconColor: 'text-gray-500' },
}

function ScoreCircle({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color = pct >= 70 ? '#22c55e' : pct >= 40 ? '#eab308' : '#ef4444'
  const r = 40
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ

  return (
    <div className="relative w-28 h-28">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle
          cx="50" cy="50" r={r} fill="none"
          stroke={color} strokeWidth="10"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-gray-800">{pct}%</span>
        <span className="text-xs text-gray-400">Score</span>
      </div>
    </div>
  )
}

function QuestionCard({ q, index }) {
  const [open, setOpen] = useState(false)
  const score = q.answer_score != null ? Math.round(q.answer_score * 100) : null

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 text-left"
      >
        <div className="flex items-center gap-3">
          <span className="w-6 h-6 bg-brand-100 text-brand-700 rounded-full text-xs font-bold flex items-center justify-center flex-shrink-0">
            {index + 1}
          </span>
          <span className="text-sm text-gray-700 font-medium line-clamp-1">{q.question_text}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {score != null && (
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${score >= 70 ? 'bg-green-100 text-green-700' : score >= 40 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
              {score}%
            </span>
          )}
          <span className={`text-xs px-2 py-0.5 rounded-full ${q.difficulty === 'easy' ? 'bg-green-100 text-green-600' : q.difficulty === 'hard' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'}`}>
            {q.difficulty}
          </span>
          {open ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
        </div>
      </button>
      {open && (
        <div className="px-4 pb-4 border-t border-gray-100 pt-3 space-y-3">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">Question</p>
            <p className="text-sm text-gray-700">{q.question_text}</p>
          </div>
          {q.answer ? (
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">Your Answer</p>
              <p className="text-sm text-gray-600">{q.answer}</p>
            </div>
          ) : (
            <p className="text-sm text-gray-400 italic">Not answered</p>
          )}
          {q.answer_feedback && (
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">AI Feedback</p>
              <p className="text-sm text-gray-600">{q.answer_feedback}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function SummaryPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSessionSummary(sessionId)
      .then(setData)
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-brand-500" size={32} />
      </div>
    )
  }

  if (!data) return null

  const { session, summary, questions } = data
  const rec = summary.recommendation || 'Review Required'
  const recStyle = RECOMMENDATION_STYLES[rec] || RECOMMENDATION_STYLES['Review Required']
  const RecIcon = recStyle.icon
  const answeredCount = questions.filter(q => q.answer).length

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Interview Complete</h1>
        <p className="text-gray-500">{session.candidate_name} · {session.role}</p>
      </div>

      {/* Top summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="card flex flex-col items-center py-6">
          <ScoreCircle score={summary.overall_score} />
          <p className="text-sm text-gray-500 mt-2">Overall Score</p>
        </div>

        <div className={`card border ${recStyle.border} ${recStyle.bg} flex flex-col items-center justify-center py-6`}>
          <RecIcon size={32} className={`${recStyle.iconColor} mb-2`} />
          <p className={`font-bold text-lg ${recStyle.text}`}>{rec}</p>
          <p className="text-xs text-gray-400 mt-1">Recommendation</p>
        </div>

        <div className="card flex flex-col items-center justify-center py-6">
          <p className="text-3xl font-bold text-gray-800">{answeredCount}/{questions.length}</p>
          <p className="text-sm text-gray-500 mt-1">Questions Answered</p>
        </div>
      </div>

      {/* Summary text */}
      {summary.summary_text && (
        <div className="card mb-4">
          <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Star size={16} className="text-brand-500" />
            Assessment Summary
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed">{summary.summary_text}</p>
        </div>
      )}

      {/* Strengths & Improvements */}
      <div className="grid sm:grid-cols-2 gap-4 mb-4">
        {summary.strengths?.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <TrendingUp size={16} className="text-green-500" />
              Strengths
            </h3>
            <ul className="space-y-2">
              {summary.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <CheckCircle2 size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        {summary.improvements?.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <AlertCircle size={16} className="text-orange-500" />
              Areas to Improve
            </h3>
            <ul className="space-y-2">
              {summary.improvements.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <AlertCircle size={14} className="text-orange-400 mt-0.5 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Skills detected */}
      {session.skills?.length > 0 && (
        <div className="card mb-4">
          <h3 className="font-semibold text-gray-800 mb-3">Detected Skills</h3>
          <div className="flex flex-wrap gap-2">
            {session.skills.map(s => (
              <span key={s} className="bg-brand-50 text-brand-700 text-xs font-medium px-3 py-1 rounded-full border border-brand-200">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Q&A Review */}
      <div className="card mb-6">
        <h3 className="font-semibold text-gray-800 mb-4">Interview Q&A Review</h3>
        <div className="space-y-2">
          {questions.map((q, i) => (
            <QuestionCard key={q.id} q={q} index={i} />
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 justify-center">
        <Link to="/" className="btn-secondary flex items-center gap-2">
          <RotateCcw size={16} />
          New Interview
        </Link>
      </div>
    </div>
  )
}
