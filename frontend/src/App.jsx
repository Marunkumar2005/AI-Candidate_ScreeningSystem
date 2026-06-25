import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage.jsx'
import InterviewPage from './pages/InterviewPage.jsx'
import SummaryPage from './pages/SummaryPage.jsx'
import Layout from './components/Layout.jsx'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/interview/:sessionId" element={<InterviewPage />} />
        <Route path="/summary/:sessionId" element={<SummaryPage />} />
      </Routes>
    </Layout>
  )
}
