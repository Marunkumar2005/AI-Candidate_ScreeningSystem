import { Link } from 'react-router-dom'
import { Brain } from 'lucide-react'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <nav className="bg-white/80 backdrop-blur border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-lg text-brand-700">
            <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center">
              <Brain size={18} className="text-white" />
            </div>
            <span>AI Interview</span>
            <span className="text-xs bg-brand-100 text-brand-600 px-2 py-0.5 rounded-full font-medium">PGAGI</span>
          </Link>
          <div className="text-sm text-gray-500">RAG-Powered Candidate Screening</div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
