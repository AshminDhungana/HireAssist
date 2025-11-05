import { useEffect, useState } from 'react'

interface ApiStatus {
  isOnline: boolean
  message: string
  color: string
}

export const useApiStatus = () => {
  const [status, setStatus] = useState<ApiStatus>({
    isOnline: false,
    message: 'Checking API...',
    color: 'gray',
  })

  useEffect(() => {
    const checkApi = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const healthUrl = `${apiUrl}/api/v1/health`
        
        console.log('🔍 [API Status] Checking:', healthUrl)
        
        const response = await fetch(healthUrl, {
          method: 'GET',
          headers: { 
            'Content-Type': 'application/json'
          },
          mode: 'cors',  // ✅ ADD CORS MODE
          credentials: 'omit',  // ✅ Don't send credentials for health check
        })

        console.log('📊 [API Status] Response Status:', response.status)
        console.log('📊 [API Status] Response OK:', response.ok)

        if (response.ok) {
          const data = await response.json()
          console.log('✅ [API Status] Connected! Data:', data)
          
          setStatus({
            isOnline: true,
            message: '✓ API Connected',
            color: 'green',
          })
        } else {
          console.error('❌ [API Status] Response not OK:', response.status, response.statusText)
          setStatus({
            isOnline: false,
            message: `✗ API Error (${response.status})`,
            color: 'red',
          })
        }
      } catch (error) {
        console.error('❌ [API Status] Fetch Error:', error)
        
        // More specific error message
        const errorMsg = error instanceof Error ? error.message : 'Unknown error'
        
        setStatus({
          isOnline: false,
          message: `✗ API Offline (${errorMsg})`,
          color: 'red',
        })
      }
    }

    // ✅ Check immediately
    checkApi()
    
    // ✅ Check every 30 seconds
    const interval = setInterval(checkApi, 30000)
    
    // ✅ Cleanup
    return () => clearInterval(interval)
  }, [])

  return status
}
