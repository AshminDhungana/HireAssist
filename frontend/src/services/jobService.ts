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

// ========== JOB SERVICE ==========

export const jobService = {
  // Create new job posting
  createJob: async (data: {
    title: string
    description: string
    requirements: string
    location: string
    salary_min?: number
    salary_max?: number
  }) => {
    try {
      const response = await api.post('/api/v1/jobs/create', data)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to create job'
        }
      }
      throw error
    }
  },

  // List jobs (paginated)
  listJobs: async (skip = 0, limit = 20, statusFilter?: string) => {
    try {
      const response = await api.get('/api/v1/jobs/list', {
        params: {
          skip,
          limit,
          ...(statusFilter && { status_filter: statusFilter })
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
          error: error.response?.data?.detail || 'Failed to list jobs'
        }
      }
      throw error
    }
  },

  // Get job details
  getJob: async (jobId: string) => {
    try {
      const response = await api.get(`/api/v1/jobs/${jobId}`)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to get job'
        }
      }
      throw error
    }
  },

  // Update job
  updateJob: async (jobId: string, data: {
    title?: string
    description?: string
    requirements?: string
    location?: string
    salary_min?: number
    salary_max?: number
  }) => {
    try {
      const response = await api.put(`/api/v1/jobs/${jobId}`, data)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to update job'
        }
      }
      throw error
    }
  },

  // Delete job
  deleteJob: async (jobId: string) => {
    try {
      const response = await api.delete(`/api/v1/jobs/${jobId}`)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to delete job'
        }
      }
      throw error
    }
  }
}
