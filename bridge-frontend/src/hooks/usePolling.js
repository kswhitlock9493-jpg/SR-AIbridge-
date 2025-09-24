import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook for managing polling intervals with optimal data fetching practices
 * 
 * Features:
 * - Configurable polling intervals (default: 30 seconds for reduced network load)
 * - Debounced loading states to prevent unnecessary re-renders during rapid updates
 * - Manual refresh capability
 * - Automatic cleanup on component unmount
 * - Error handling with retry capability
 * 
 * @param {Function} fetchFunction - Function that returns a Promise for data fetching
 * @param {Object} options - Configuration options
 * @param {number} options.interval - Polling interval in milliseconds (default: 30000)
 * @param {boolean} options.immediate - Whether to fetch immediately on mount (default: true)
 * @param {number} options.debounceDelay - Debounce delay for loading states (default: 200ms)
 * @returns {Object} - { data, loading, error, refresh, isPolling }
 */
export const usePolling = (fetchFunction, options = {}) => {
  const {
    interval = 30000, // 30 seconds - reduced from 5 seconds for better performance
    immediate = true,
    debounceDelay = 200
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  
  // Use refs to store interval and timeout IDs for cleanup
  const intervalRef = useRef(null);
  const debounceTimeoutRef = useRef(null);
  const mountedRef = useRef(true);

  /**
   * Debounced loading state setter to prevent rapid UI changes
   * Only shows loading state if fetch takes longer than debounceDelay
   */
  const setLoadingDebounced = useCallback((isLoading) => {
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    if (isLoading) {
      // Delay showing loading state to avoid flicker for fast requests
      debounceTimeoutRef.current = setTimeout(() => {
        if (mountedRef.current) {
          setLoading(true);
        }
      }, debounceDelay);
    } else {
      // Immediately hide loading state
      setLoading(false);
    }
  }, [debounceDelay]);

  /**
   * Core fetch function with error handling and loading state management
   */
  const fetchData = useCallback(async (showLoading = true) => {
    if (!fetchFunction || typeof fetchFunction !== 'function') {
      console.error('usePolling: fetchFunction must be a valid function');
      return;
    }

    try {
      if (showLoading) {
        setLoadingDebounced(true);
      }
      
      const result = await fetchFunction();
      
      // Only update state if component is still mounted
      if (mountedRef.current) {
        setData(result);
        setError(null);
      }
    } catch (err) {
      console.error('Polling fetch error:', err);
      if (mountedRef.current) {
        setError(err.message || 'Failed to fetch data');
      }
    } finally {
      if (mountedRef.current) {
        setLoadingDebounced(false);
      }
    }
  }, [fetchFunction, setLoadingDebounced]);

  /**
   * Manual refresh function for user-initiated updates
   * Always shows loading state for manual refreshes to provide user feedback
   */
  const refresh = useCallback(() => {
    fetchData(true);
  }, [fetchData]);

  /**
   * Start polling with the configured interval
   */
  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    setIsPolling(true);
    intervalRef.current = setInterval(() => {
      // Background polling doesn't need to show loading state
      fetchData(false);
    }, interval);
  }, [fetchData, interval]);

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // Initialize polling on mount
  useEffect(() => {
    mountedRef.current = true;

    if (immediate) {
      fetchData(true);
    }
    
    startPolling();

    // Cleanup function
    return () => {
      mountedRef.current = false;
      stopPolling();
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [immediate, startPolling, stopPolling, fetchData]);

  // Restart polling when interval changes
  useEffect(() => {
    if (isPolling) {
      startPolling();
    }
  }, [interval, isPolling, startPolling]);

  return {
    data,
    loading,
    error,
    refresh,
    isPolling,
    startPolling,
    stopPolling
  };
};

export default usePolling;