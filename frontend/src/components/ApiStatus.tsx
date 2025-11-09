import React, { useState, useCallback } from 'react'
import { useApiStatus } from '../hooks/useApiStatus'
import { Check, X, RefreshCw } from 'lucide-react'

export const ApiStatus: React.FC = () => {
  const status = useApiStatus()
  const [isRetrying, setIsRetrying] = useState(false)

  // Only log once on mount
  React.useEffect(() => {
    if (status?.isOnline) {
      console.log('✅ [ApiStatus] Backend connected:', status.message)
    } else if (status?.isOnline === false) {
      console.warn('⚠️ [ApiStatus] Backend disconnected:', status.message)
    }
  }, [status?.isOnline]) // Only depend on isOnline, not the whole object

  const handleRetry = useCallback(async () => {
    setIsRetrying(true)
    try {
      const response = await fetch(
        import.meta.env.VITE_API_BASE_URL + '/api/v1/health' || 'http://localhost:8000/api/v1/health',
        { timeout: 5000 }
      )
      if (response.ok) {
        console.log('✅ [ApiStatus] Retry successful')
      }
    } catch (error) {
      console.error('❌ [ApiStatus] Retry failed:', error)
    } finally {
      setIsRetrying(false)
    }
  }, [])

  // Safe null check
  if (!status) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 border border-gray-400 rounded-full">
        <div className="w-4 h-4 bg-gray-400 rounded-full animate-pulse" />
        <span className="text-xs font-semibold text-gray-700">Checking...</span>
      </div>
    )
  }

  // Online state
  if (status.isOnline) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-400 rounded-full hover:bg-green-200 transition-colors cursor-default group relative">
        <Check className="w-4 h-4 text-green-600" />
        <span className="text-xs font-semibold text-green-700">{status.message || 'Online'}</span>
        
        {/* Tooltip */}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
          API is healthy
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900"></div>
        </div>
      </div>
    )
  }

  // Offline state
  return (
    <button
      onClick={handleRetry}
      disabled={isRetrying}
      className="flex items-center gap-2 px-3 py-1.5 bg-red-100 border border-red-400 rounded-full hover:bg-red-200 transition-colors cursor-pointer group relative disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isRetrying ? (
        <RefreshCw className="w-4 h-4 text-red-600 animate-spin" />
      ) : (
        <X className="w-4 h-4 text-red-600" />
      )}
      <span className="text-xs font-semibold text-red-700">
        {isRetrying ? 'Retrying...' : (status.message || 'Offline')}
      </span>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
        Click to retry
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900"></div>
      </div>
    </button>
  )
}

export default ApiStatus
