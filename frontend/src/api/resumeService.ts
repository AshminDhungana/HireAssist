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

interface UploadResponse {
  success: boolean
  message?: string
  data?: {
    id: string
    filename: string
    parsedData: Record<string, unknown>
  }
  error?: string
}

// ========== EXISTING FUNCTIONS ==========

export const uploadResume = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadResponse>(
      `/api/v1/resumes/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: error.response?.data?.error || 'Upload failed',
      }
    }
    throw error
  }
}

// ========== NEW FUNCTIONS (ADD THESE) ==========

// NEW 1: List all resumes for user
export const listResumes = async () => {
  try {
    const response = await api.get('/api/v1/resumes/list')
    return {
      success: true,
      data: response.data
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to list resumes',
      }
    }
    throw error
  }
}

// NEW 2: Get resume details with parsed data
export const getResumeDetails = async (resumeId: string) => {
  try {
    const response = await api.get(`/api/v1/resumes/${resumeId}/details`)
    return {
      success: true,
      data: response.data
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to get resume details',
      }
    }
    throw error
  }
}

// NEW 3: Delete a resume
export const deleteResume = async (resumeId: string) => {
  try {
    const response = await api.delete(`/api/v1/resumes/${resumeId}`)
    return {
      success: true,
      data: response.data,
      message: 'Resume deleted successfully'
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete resume',
      }
    }
    throw error
  }
}
