import React from 'react';
import { useApiStatus } from '../hooks/useApiStatus';
import { Check, X } from 'lucide-react';

export const ApiStatus: React.FC = () => {
  const status = useApiStatus();

  if (status.isOnline) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-400 rounded-full hover:bg-green-200 transition-colors cursor-default">
        <Check className="w-4 h-4 text-green-600" />
        <span className="text-xs font-semibold text-green-700">API Live</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 border border-red-400 rounded-full hover:bg-red-200 transition-colors cursor-default">
      <X className="w-4 h-4 text-red-600" />
      <span className="text-xs font-semibold text-red-700">API Down</span>
    </div>
  );
};

export default ApiStatus;
