import { useState, useCallback } from 'react';

export const useError = () => {
  const [error, setError] = useState(null);

  const handleError = useCallback((err) => {
    setError(err.message);
    setTimeout(() => setError(null), 3000);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError
  };
}; 