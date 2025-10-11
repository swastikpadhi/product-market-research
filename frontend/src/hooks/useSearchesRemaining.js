import { useState, useCallback } from 'react';
import { API_BASE } from '../config/api';

export default function useSearchesRemaining() {
  const [searchesRemaining, setSearchesRemaining] = useState(null); // null = loading or unavailable
  const [isLoading, setIsLoading] = useState(true);

  const fetchSearches = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE}/searches-remaining`);
      if (response.ok) {
        const data = await response.json();
        if (data.searches_remaining) {
          setSearchesRemaining(data.searches_remaining);
        } else {
          // No searches remaining data available
          setSearchesRemaining(null);
        }
      } else {
        // API error, don't show misleading default values
        console.error('Failed to load searches remaining: API error');
        setSearchesRemaining(null);
      }
    } catch (err) {
      console.error('Failed to load searches remaining:', err);
      // Network error, don't show misleading default values
      setSearchesRemaining(null);
    } finally {
      setIsLoading(false);
    }
  }, []); // Empty dependency array is correct here

  return {
    searchesRemaining,
    isLoading,
    fetchSearches
  };
}

