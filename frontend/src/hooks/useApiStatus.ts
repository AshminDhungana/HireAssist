import { useEffect, useState, useRef } from 'react'

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

  // Use refs to track if we've already logged to avoid console spam
  const hasCheckedRef = useRef(false)
  const lastStatusRef = useRef<string>('')

  useEffect(() => {
    const checkApi = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        const healthUrl = `${apiUrl}/api/v1/health`
        
        // ✅ Only log first check
        if (!hasCheckedRef.current) {
          console.log('🔍 [API Status] Checking:', healthUrl)
        }
        
        const response = await fetch(healthUrl, {
          method: 'GET',
          headers: { 
            'Content-Type': 'application/json'
          },
          mode: 'cors',  // ✅ CORS MODE
          credentials: 'omit',  // ✅ Don't send credentials for health check
        })

        if (response.ok) {
          const data = await response.json()
          
          // ✅ Only log on first success
          if (!hasCheckedRef.current || lastStatusRef.current !== 'online') {
            console.log('✅ [API Status] Connected! Backend healthy:', data)
            lastStatusRef.current = 'online'
          }
          
          setStatus({
            isOnline: true,
            message: '✓ API Connected',
            color: 'green',
          })
        } else {
          // ✅ Only log on first error
          if (!hasCheckedRef.current || lastStatusRef.current !== 'error') {
            console.error('❌ [API Status] Response not OK:', response.status, response.statusText)
            lastStatusRef.current = 'error'
          }
          
          setStatus({
            isOnline: false,
            message: `✗ API Error (${response.status})`,
            color: 'red',
          })
        }
      } catch (error) {
        // ✅ Only log on first error
        if (!hasCheckedRef.current || lastStatusRef.current !== 'offline') {
          console.error('❌ [API Status] Fetch Error:', error instanceof Error ? error.message : 'Unknown error')
          lastStatusRef.current = 'offline'
        }
        
        const errorMsg = error instanceof Error ? error.message : 'Unknown error'
        
        setStatus({
          isOnline: false,
          message: `✗ API Offline (${errorMsg})`,
          color: 'red',
        })
      }
      
      // ✅ Mark first check as complete
      hasCheckedRef.current = true
    }

    // ✅ Check immediately
    checkApi()
    
    // ✅ Check every 30 seconds (NOT every render!)
    const interval = setInterval(checkApi, 30000)
    
    // ✅ Cleanup interval on unmount
    return () => clearInterval(interval)
  }, []) // ✅ Empty dependency array - run ONCE only

  return status
}
