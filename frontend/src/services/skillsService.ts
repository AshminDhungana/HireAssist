import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export const skillsService = {
  // Get all available skills
  getAvailableSkills: async () => {
    try {
      const response = await api.get('/api/v1/skills/available')
      return {
        success: true,
        data: response.data.skills
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to load skills'
      }
    }
  },

  // Search skills
  searchSkills: async (query: string) => {
    try {
      const response = await api.get('/api/v1/skills/search', {
        params: { query }
      })
      return {
        success: true,
        data: response.data.results
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to search skills'
      }
    }
  },

  // Normalize skills
  normalizeSkills: async (skills: string[]) => {
    try {
      const response = await api.post('/api/v1/skills/normalize', skills)
      return {
        success: true,
        data: response.data.standardized
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to normalize skills'
      }
    }
  },

  // Get categories
  getCategories: async () => {
    try {
      const response = await api.get('/api/v1/skills/categories')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to load categories'
      }
    }
  }
}
