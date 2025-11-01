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

// ========== CANDIDATE SERVICE ==========

export const candidateService = {
  // Create candidate profile
  createProfile: async (data: {
    name: string
    email: string
    phone?: string
    location?: string
    summary?: string
  }) => {
    try {
      const response = await api.post('/api/v1/candidates/create-profile', data)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to create profile'
        }
      }
      throw error
    }
  },

  // Get my profile with resumes
  getMyProfile: async () => {
    try {
      const response = await api.get('/api/v1/candidates/me')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to get profile'
        }
      }
      throw error
    }
  },

  // Update my profile
  updateProfile: async (data: {
    name?: string
    email?: string
    phone?: string
    location?: string
    summary?: string
  }) => {
    try {
      const response = await api.put('/api/v1/candidates/update-profile', data)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to update profile'
        }
      }
      throw error
    }
  },

  // List all candidates (paginated)
  listCandidates: async (skip = 0, limit = 20) => {
    try {
      const response = await api.get('/api/v1/candidates/list', {
        params: { skip, limit }
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to list candidates'
        }
      }
      throw error
    }
  },

  // Get specific candidate details
  getCandidate: async (candidateId: string) => {
    try {
      const response = await api.get(`/api/v1/candidates/${candidateId}`)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to get candidate'
        }
      }
      throw error
    }
  },

  // Delete my profile
  deleteProfile: async () => {
    try {
      const response = await api.delete('/api/v1/candidates/delete-profile')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to delete profile'
        }
      }
      throw error
    }
  }
}
