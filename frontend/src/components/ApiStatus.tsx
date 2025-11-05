import React from 'react'
import { useApiStatus } from '../hooks/useApiStatus'
import { Check, X } from 'lucide-react'

export const ApiStatus: React.FC = () => {
  const status = useApiStatus()

  console.log('🎨 [ApiStatus Component] Current status:', status)

  if (status.isOnline) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-400 rounded-full hover:bg-green-200 transition-colors cursor-default group relative">
        <Check className="w-4 h-4 text-green-600" />
        <span className="text-xs font-semibold text-green-700">{status.message}</span>
        
        {/* Tooltip */}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
          API is healthy
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 border border-red-400 rounded-full hover:bg-red-200 transition-colors cursor-default group relative">
      <X className="w-4 h-4 text-red-600" />
      <span className="text-xs font-semibold text-red-700">{status.message}</span>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
        Click to retry
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900"></div>
      </div>
    </div>
  )
}

export default ApiStatus
