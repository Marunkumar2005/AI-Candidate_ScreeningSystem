import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  ChevronRight, Loader2, CheckCircle2, Clock, Tag,
  AlertCircle, SkipForward, Plus, Send
} from 'lucide-react'
import { getSession, submitAnswer, completeSession, generateMoreQuestions } from '../utils/api.js'

const DIFFICULTY_COLORS = {
  easy: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  hard: 'bg-red-100 text-red-700',
}

function ProgressBar({ current, total }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className="bg-brand-500 h-2 rounded-full transition-all duration-500"
        style={{ width: `${Math.min((current / total) * 100, 100)}%` }}
      />
    </div>
  )
}

function ScoreBadge({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? 'text-green-600 bg-green-50' : pct >= 40 ? 'text-yellow-600 bg-yellow-50' : 'text-red-600 bg-red-50'
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${color}`}>
      {pct}%
    </span>
  )
}

export default function InterviewPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [evaluation, setEvaluation] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const textareaRef = useRef(null)

  useEffect(() => {
    loadSession()
  }, [sessionId])

  const loadSession = async () => {
    try {
      const data = await getSession(sessionId)
      setSession(data)
      // Find first unanswered
      const firstUnanswered = data.questions.findIndex(q => !q.answer)
      if (firstUnanswered > 0) setCurrentIdx(firstUnanswered)
    } catch (err) {
      toast.error('Could not load session')
      navigate('/')
    }
  }

  const currentQuestion = session?.questions?.[currentIdx]
  const totalQuestions = session?.questions?.length || 0
  const answeredCount = session?.questions?.filter(q => q.answer)?.length || 0

  const handleSubmit = async () => {
    if (!answer.trim()) return toast.error('Please write an answer')
    setSubmitting(true)
    try {
      const result = await submitAnswer(currentQuestion.id, answer)
      setEvaluation(result.evaluation)
      setSubmitted(true)
      // Update local session data
      setSession(prev => ({
        ...prev,
        questions: prev.questions.map(q =>
          q.id === currentQuestion.id
            ? { ...q, answer, answer_score: result.evaluation?.score, answer_feedback: result.evaluation?.feedback }
            : q
        )
      }))
    } catch (err) {
      toast.error('Failed to submit answer')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    setAnswer('')
    setEvaluation(null)
    setSubmitted(false)
    setCurrentIdx(i => i + 1)
    setTimeout(() => textareaRef.current?.focus(), 100)
  }

  const handleSkip = async () => {
    setAnswer('')
    setEvaluation(null)
    setSubmitted(false)
    setCurrentIdx(i => i + 1)
  }

  const handleFinish = async () => {
    setFinishing(true)
    try {
      await completeSession(sessionId)
      navigate(`/summary/${sessionId}`)
    } catch (err) {
      toast.error('Error finishing session')
    } finally {
      setFinishing(false)
    }
  }

  const handleGenerateMore = async () => {
    setLoadingMore(true)
    try {
      const result = await generateMoreQuestions(sessionId)
      toast.success(`${result.added} new questions added!`)
      await loadSession()
    } catch (err) {
      toast.error('Could not generate more questions')
    } finally {
      setLoadingMore(false)
    }
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-brand-500" size={32} />
      </div>
    )
  }

  const isLastQuestion = currentIdx >= totalQuestions - 1
  const allAnswered = answeredCount >= totalQuestions

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="card mb-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="font-semibold text-gray-800">{session.candidate_name}</h2>
            <p className="text-sm text-gray-500">{session.role}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-gray-700">
              Question {Math.min(currentIdx + 1, totalQuestions)} of {totalQuestions}
            </p>
            <p className="text-xs text-gray-400">{answeredCount} answered</p>
          </div>
        </div>
        <ProgressBar current={answeredCount} total={totalQuestions} />
      </div>

      {/* Question list sidebar pills */}
      <div className="flex gap-2 flex-wrap mb-4">
        {session.questions.map((q, i) => (
          <button
            key={q.id}
            onClick={() => {
              setCurrentIdx(i)
              setAnswer('')
              setEvaluation(null)
              setSubmitted(false)
            }}
            className={`w-8 h-8 rounded-lg text-xs font-semibold transition-all ${
              i === currentIdx
                ? 'bg-brand-500 text-white'
                : q.answer
                ? 'bg-green-400 text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* Current Question */}
      {currentQuestion && !allAnswered ? (
        <div className="card mb-4">
          <div className="flex items-start justify-between mb-4">
            <div className="flex gap-2 flex-wrap">
              {currentQuestion.topic && (
                <span className="flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                  <Tag size={10} />
                  {currentQuestion.topic}
                </span>
              )}
              {currentQuestion.difficulty && (
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${DIFFICULTY_COLORS[currentQuestion.difficulty] || DIFFICULTY_COLORS.medium}`}>
                  {currentQuestion.difficulty}
                </span>
              )}
            </div>
            {currentQuestion.answer_score != null && <ScoreBadge score={currentQuestion.answer_score} />}
          </div>

          <p className="text-gray-800 font-medium text-base leading-relaxed mb-5">
            {currentQuestion.question_text}
          </p>

          {currentQuestion.answer ? (
            <div className="bg-gray-50 rounded-xl p-4 mb-4">
              <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">Your Answer</p>
              <p className="text-gray-700 text-sm">{currentQuestion.answer}</p>
              {currentQuestion.answer_feedback && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">AI Feedback</p>
                  <p className="text-gray-600 text-sm">{currentQuestion.answer_feedback}</p>
                </div>
              )}
            </div>
          ) : (
            <>
              <textarea
                ref={textareaRef}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
                disabled={submitted}
                className="w-full border border-gray-200 rounded-xl p-4 text-sm text-gray-700 h-36 resize-none focus:outline-none focus:ring-2 focus:ring-brand-400 disabled:bg-gray-50"
              />

              {submitted && evaluation && (
                <div className={`rounded-xl p-4 mt-3 ${evaluation.score >= 0.7 ? 'bg-green-50 border border-green-200' : evaluation.score >= 0.4 ? 'bg-yellow-50 border border-yellow-200' : 'bg-red-50 border border-red-200'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 size={16} className="text-green-600" />
                    <span className="font-medium text-gray-800 text-sm">AI Feedback</span>
                    <ScoreBadge score={evaluation.score} />
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{evaluation.feedback}</p>
                  {evaluation.strengths?.length > 0 && (
                    <div className="text-xs text-gray-500">
                      <span className="font-medium">✓ </span>
                      {evaluation.strengths.join(' · ')}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          <div className="flex gap-2 mt-4">
            {!currentQuestion.answer && !submitted && (
              <>
                <button onClick={handleSubmit} disabled={submitting || !answer.trim()} className="btn-primary flex items-center gap-2">
                  {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Submit Answer
                </button>
                <button onClick={handleSkip} className="btn-secondary flex items-center gap-2">
                  <SkipForward size={16} />
                  Skip
                </button>
              </>
            )}
            {(submitted || currentQuestion.answer) && !isLastQuestion && (
              <button onClick={handleNext} className="btn-primary flex items-center gap-2">
                Next Question
                <ChevronRight size={16} />
              </button>
            )}
            {(submitted || currentQuestion.answer) && isLastQuestion && (
              <button onClick={handleFinish} disabled={finishing} className="bg-green-600 hover:bg-green-700 text-white btn-primary flex items-center gap-2">
                {finishing ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                Finish Interview
              </button>
            )}
          </div>
        </div>
      ) : allAnswered ? (
        <div className="card text-center py-10">
          <CheckCircle2 size={48} className="mx-auto text-green-500 mb-3" />
          <h3 className="text-xl font-bold text-gray-800 mb-2">All questions answered!</h3>
          <p className="text-gray-500 mb-6">Ready to see your results?</p>
          <button onClick={handleFinish} disabled={finishing} className="btn-primary mx-auto flex items-center gap-2">
            {finishing ? <Loader2 size={16} className="animate-spin" /> : null}
            View Summary & Results
          </button>
        </div>
      ) : null}

      {/* Generate More */}
      {!allAnswered && (
        <button
          onClick={handleGenerateMore}
          disabled={loadingMore}
          className="w-full mt-2 flex items-center justify-center gap-2 text-sm text-gray-500 hover:text-brand-600 py-2 transition-colors"
        >
          {loadingMore ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
          Generate additional questions
        </button>
      )}
    </div>
  )
}
