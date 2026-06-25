import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const uploadResume = async (file, role) => {
  const form = new FormData()
  form.append('file', file)
  form.append('role', role)
  const { data } = await api.post('/resume/upload', form)
  return data
}

export const parseResumeText = async (text, role) => {
  const { data } = await api.post('/resume/parse-text', { text, role })
  return data
}

export const createSession = async (payload) => {
  const { data } = await api.post('/sessions/create', payload)
  return data
}

export const getSession = async (sessionId) => {
  const { data } = await api.get(`/sessions/${sessionId}`)
  return data
}

export const submitAnswer = async (questionId, answer) => {
  const { data } = await api.post(`/questions/${questionId}/answer`, { answer })
  return data
}

export const completeSession = async (sessionId) => {
  const { data } = await api.post(`/sessions/${sessionId}/complete`)
  return data
}

export const getSessionSummary = async (sessionId) => {
  const { data } = await api.get(`/sessions/${sessionId}/summary`)
  return data
}

export const generateMoreQuestions = async (sessionId) => {
  const { data } = await api.post('/questions/generate-more', { session_id: sessionId })
  return data
}

export const healthCheck = async () => {
  const { data } = await api.get('/health')
  return data
}
