import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import {
  Upload, FileText, ChevronRight, Loader2, Sparkles,
  Code2, Brain, BarChart2, Layers, Monitor
} from 'lucide-react'
import { uploadResume, parseResumeText, createSession } from '../utils/api.js'

const ROLES = [
  { id: 'AI/ML Engineer', label: 'AI/ML Engineer', icon: Brain, color: 'bg-purple-100 text-purple-700' },
  { id: 'Backend Engineer', label: 'Backend Engineer', icon: Code2, color: 'bg-blue-100 text-blue-700' },
  { id: 'Data Scientist', label: 'Data Scientist', icon: BarChart2, color: 'bg-green-100 text-green-700' },
  { id: 'Full Stack Engineer', label: 'Full Stack Engineer', icon: Layers, color: 'bg-orange-100 text-orange-700' },
  { id: 'Frontend Engineer', label: 'Frontend Engineer', icon: Monitor, color: 'bg-pink-100 text-pink-700' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const [selectedRole, setSelectedRole] = useState('')
  const [resumeFile, setResumeFile] = useState(null)
  const [resumeText, setResumeText] = useState('')
  const [inputMode, setInputMode] = useState('file') // 'file' | 'text'
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1) // 1=role, 2=resume, 3=confirm

  const onDrop = useCallback((accepted) => {
    if (accepted[0]) setResumeFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'] },
    maxFiles: 1,
  })

  const handleStart = async () => {
    if (!selectedRole) return toast.error('Please select a role')
    if (inputMode === 'file' && !resumeFile) return toast.error('Please upload your resume')
    if (inputMode === 'text' && !resumeText.trim()) return toast.error('Please paste your resume')

    setIsLoading(true)
    try {
      let parsed
      if (inputMode === 'file') {
        parsed = await uploadResume(resumeFile, selectedRole)
      } else {
        parsed = await parseResumeText(resumeText, selectedRole)
      }

      toast.loading('Generating personalized questions...', { id: 'gen' })

      const session = await createSession({
        role: selectedRole,
        resume_text: parsed.resume_text,
        candidate_name: parsed.extracted_info?.candidate_name || 'Candidate',
        extracted_skills: parsed.extracted_info?.skills || [],
        extracted_technologies: parsed.extracted_info?.technologies || [],
      })

      toast.success('Interview ready!', { id: 'gen' })
      navigate(`/interview/${session.session_id}`)
    } catch (err) {
      toast.dismiss('gen')
      toast.error(err.response?.data?.detail || 'Something went wrong')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-brand-100 text-brand-700 px-4 py-1.5 rounded-full text-sm font-medium mb-4">
          <Sparkles size={14} />
          RAG-Powered Technical Interviews
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          AI Candidate Screening
        </h1>
        <p className="text-gray-500 text-lg">
          Upload your resume, pick a role — get a personalized technical interview powered by AI.
        </p>
      </div>

      {/* Step 1: Role Selection */}
      <div className="card mb-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-6 h-6 bg-brand-500 text-white rounded-full text-xs flex items-center justify-center font-bold">1</span>
          <h2 className="font-semibold text-gray-800">Select Target Role</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {ROLES.map(({ id, label, icon: Icon, color }) => (
            <button
              key={id}
              onClick={() => setSelectedRole(id)}
              className={`flex items-center gap-2 p-3 rounded-xl border-2 text-sm font-medium transition-all ${
                selectedRole === id
                  ? 'border-brand-500 bg-brand-50 text-brand-700'
                  : 'border-gray-200 hover:border-brand-300 text-gray-600'
              }`}
            >
              <span className={`p-1.5 rounded-lg ${color}`}>
                <Icon size={14} />
              </span>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Resume Upload */}
      <div className="card mb-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-6 h-6 bg-brand-500 text-white rounded-full text-xs flex items-center justify-center font-bold">2</span>
          <h2 className="font-semibold text-gray-800">Upload Your Resume</h2>
        </div>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setInputMode('file')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${inputMode === 'file' ? 'bg-brand-500 text-white' : 'bg-gray-100 text-gray-600'}`}
          >
            Upload File
          </button>
          <button
            onClick={() => setInputMode('text')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${inputMode === 'text' ? 'bg-brand-500 text-white' : 'bg-gray-100 text-gray-600'}`}
          >
            Paste Text
          </button>
        </div>

        {inputMode === 'file' ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragActive ? 'border-brand-500 bg-brand-50' : 'border-gray-300 hover:border-brand-400'
            } ${resumeFile ? 'bg-green-50 border-green-400' : ''}`}
          >
            <input {...getInputProps()} />
            {resumeFile ? (
              <div className="flex items-center justify-center gap-2 text-green-700">
                <FileText size={20} />
                <span className="font-medium">{resumeFile.name}</span>
              </div>
            ) : (
              <>
                <Upload size={28} className="mx-auto text-gray-400 mb-2" />
                <p className="text-gray-600 font-medium">Drop your resume here</p>
                <p className="text-sm text-gray-400 mt-1">PDF or TXT file</p>
              </>
            )}
          </div>
        ) : (
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume content here..."
            className="w-full border border-gray-200 rounded-xl p-4 text-sm text-gray-700 h-40 resize-none focus:outline-none focus:ring-2 focus:ring-brand-400"
          />
        )}
      </div>

      {/* Start Button */}
      <button
        onClick={handleStart}
        disabled={isLoading || !selectedRole || (inputMode === 'file' ? !resumeFile : !resumeText.trim())}
        className="w-full btn-primary flex items-center justify-center gap-2 py-3 text-base"
      >
        {isLoading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Preparing your interview...
          </>
        ) : (
          <>
            Start Interview
            <ChevronRight size={18} />
          </>
        )}
      </button>

      {/* Info */}
      <div className="mt-6 grid grid-cols-3 gap-4 text-center text-sm text-gray-500">
        {['RAG-powered questions', 'Tailored to your skills', 'Instant AI feedback'].map(t => (
          <div key={t} className="flex flex-col items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-brand-400" />
            {t}
          </div>
        ))}
      </div>
    </div>
  )
}
