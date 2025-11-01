import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token')
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add auth header to all requests
api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ========== MATCHING SERVICE ==========

export const matchingService = {
  // Match candidate to job
  matchCandidateToJob: async (data: {
    job_id: string
    candidate_id: string
    resume_id: string
  }) => {
    try {
      const response = await api.post('/api/v1/matching/match', data)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to match candidate'
        }
      }
      throw error
    }
  },

  // Get match results for a job
  getMatchResults: async (jobId: string, skip = 0, limit = 20, minScore?: number) => {
    try {
      const response = await api.get(`/api/v1/matching/results/${jobId}`, {
        params: {
          skip,
          limit,
          ...(minScore !== undefined && { min_score: minScore })
        }
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to get match results'
        }
      }
      throw error
    }
  }
}
