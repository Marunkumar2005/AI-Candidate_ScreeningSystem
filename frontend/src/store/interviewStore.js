import { create } from 'zustand'

export const useInterviewStore = create((set, get) => ({
  // Current step: 'upload' | 'processing' | 'interview' | 'summary'
  step: 'upload',
  
  // Resume data
  resumeText: '',
  extractedInfo: null,
  selectedRole: '',

  // Session data
  sessionId: null,
  sessionData: null,
  
  // Interview progress
  currentQuestionIndex: 0,
  answers: {}, // questionId -> answer text
  evaluations: {}, // questionId -> evaluation
  
  // Loading states
  isLoading: false,
  
  // Actions
  setStep: (step) => set({ step }),
  setResumeData: (text, info) => set({ resumeText: text, extractedInfo: info }),
  setSelectedRole: (role) => set({ selectedRole: role }),
  setSession: (id, data) => set({ sessionId: id, sessionData: data }),
  setLoading: (v) => set({ isLoading: v }),
  
  setAnswer: (questionId, answer) => set((state) => ({
    answers: { ...state.answers, [questionId]: answer }
  })),
  
  setEvaluation: (questionId, evaluation) => set((state) => ({
    evaluations: { ...state.evaluations, [questionId]: evaluation }
  })),
  
  nextQuestion: () => set((state) => ({
    currentQuestionIndex: state.currentQuestionIndex + 1
  })),
  
  updateSessionData: (data) => set({ sessionData: data }),
  
  reset: () => set({
    step: 'upload',
    resumeText: '',
    extractedInfo: null,
    selectedRole: '',
    sessionId: null,
    sessionData: null,
    currentQuestionIndex: 0,
    answers: {},
    evaluations: {},
    isLoading: false,
  })
}))
