import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const getAuthToken = () => localStorage.getItem('access_token')

const api = axios.create({ baseURL: API_BASE_URL })

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const analyticsService = {
  getSummary: async () => {
    try {
      const response = await api.get('/api/v1/analytics/summary')
      return { success: true, data: response.data }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return { success: false, error: error.response?.data?.detail || 'Failed to load analytics' }
      }
      throw error
    }
  }
}


