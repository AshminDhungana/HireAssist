import { useEffect, useState } from 'react';

interface ApiStatus {
  isOnline: boolean;
  message: string;
  color: string;
}

export const useApiStatus = () => {
  const [status, setStatus] = useState<ApiStatus>({
    isOnline: false,
    message: 'Checking API...',
    color: 'gray',
  });

  useEffect(() => {
    const checkApi = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/health`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        if (response.ok) {
          setStatus({
            isOnline: true,
            message: '✓ API Connected',
            color: 'green',
          });
        } else {
          setStatus({
            isOnline: false,
            message: '✗ API Error',
            color: 'red',
          });
        }
      } catch (error) {
        setStatus({
          isOnline: false,
          message: '✗ API Offline',
          color: 'red',
        });
      }
    };

    checkApi();
    // Check every 30 seconds
    const interval = setInterval(checkApi, 30000);
    return () => clearInterval(interval);
  }, []);

  return status;
};
