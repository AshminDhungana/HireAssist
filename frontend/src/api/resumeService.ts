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
  resume_id?: string
  filename?: string
  data?: {
    id: string
    filename: string
    parsedData: Record<string, unknown>
  }
  error?: string
}

// ========== RESUME FUNCTIONS ==========

export const uploadResume = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      `/api/v1/resumes/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    console.log('Raw backend response:', response.data)

    // Transform backend response to match frontend expectations
    // Backend returns: { message, resume_id, filename }
    // Frontend expects: { success, message, data: { id, filename } }
    return {
      success: true,
      message: response.data.message,
      resume_id: response.data.resume_id,
      filename: response.data.filename,
      data: {
        id: response.data.resume_id,
        filename: response.data.filename,
        parsedData: {},
      }
    }
  } catch (error) {
    console.error('Upload error:', error)
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Upload failed',
      }
    }
    throw error
  }
}

export const listResumes = async (params?: { skill?: string[]; min_experience_years?: number; education_contains?: string }) => {
  try {
    const response = await api.get('/api/v1/resumes/list', { params })
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
