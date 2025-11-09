import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const getAuthToken = () => localStorage.getItem('access_token')

const api = axios.create({ baseURL: API_BASE_URL })

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const adminService = {
  getPendingUsers: async () => {
    try {
      const res = await api.get('/api/v1/admin/pending-users')  // ✅ ADDED /admin
      return { success: true, data: res.data }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return { success: false, error: error.response?.data?.detail || 'Failed to load pending users' }
      }
      throw error
    }
  },
  
  approveUser: async (userId: string) => {
    try {
      const res = await api.post(`/api/v1/admin/approve-user/${userId}`)  // ✅ ADDED /admin
      return { success: true, data: res.data }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return { success: false, error: error.response?.data?.detail || 'Failed to approve user' }
      }
      throw error
    }
  },
  
  rejectUser: async (userId: string) => {
    try {
      const res = await api.post(`/api/v1/admin/reject-user/${userId}`)  // ✅ ADDED /admin
      return { success: true, data: res.data }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return { success: false, error: error.response?.data?.detail || 'Failed to reject user' }
      }
      throw error
    }
  },
}
