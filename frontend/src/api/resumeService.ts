import axios from 'axios'

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

export const uploadResume = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post<UploadResponse>(
      `${import.meta.env.VITE_API_BASE_URL}/resumes/upload`,
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
