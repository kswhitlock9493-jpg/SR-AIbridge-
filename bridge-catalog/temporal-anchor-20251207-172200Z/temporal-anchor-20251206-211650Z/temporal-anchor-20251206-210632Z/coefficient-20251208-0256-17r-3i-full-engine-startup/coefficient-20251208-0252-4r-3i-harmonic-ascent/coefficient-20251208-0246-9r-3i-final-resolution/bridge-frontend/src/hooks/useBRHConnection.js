/**
 * Custom React Hook for BRH Backend Connection
 * Manages connection state, data fetching, and real-time updates
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import BRHService from '../services/brh-api';

/**
 * useBRHConnection Hook
 * @param {Object} options - Configuration options
 * @param {number} options.refreshInterval - Auto-refresh interval in ms (default: 30000)
 * @param {boolean} options.autoConnect - Auto-connect on mount (default: true)
 * @returns {Object} Connection state and methods
 */
export function useBRHConnection(options = {}) {
  const {
    refreshInterval = 30000,
    autoConnect = true,
  } = options;

  const [connectionState, setConnectionState] = useState({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastUpdate: null,
    data: null,
  });

  const intervalRef = useRef(null);
  const mountedRef = useRef(false);

  /**
   * Connect to BRH backend
   */
  const connect = useCallback(async () => {
    if (!mountedRef.current) return;

    setConnectionState(prev => ({ 
      ...prev, 
      isConnecting: true, 
      error: null 
    }));

    try {
      const result = await BRHService.connect();
      
      if (!mountedRef.current) return;

      if (result.error) {
        setConnectionState({
          isConnected: false,
          isConnecting: false,
          error: result.error,
          lastUpdate: new Date(),
          data: null,
        });
      } else {
        setConnectionState({
          isConnected: true,
          isConnecting: false,
          error: null,
          lastUpdate: new Date(),
          data: result,
        });
      }
    } catch (error) {
      if (!mountedRef.current) return;

      setConnectionState({
        isConnected: false,
        isConnecting: false,
        error: error.message,
        lastUpdate: new Date(),
        data: null,
      });
    }
  }, []);

  /**
   * Disconnect and clear interval
   */
  const disconnect = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setConnectionState({
      isConnected: false,
      isConnecting: false,
      error: null,
      lastUpdate: null,
      data: null,
    });
  }, []);

  /**
   * Refresh connection data
   */
  const refresh = useCallback(() => {
    return connect();
  }, [connect]);

  // Auto-connect on mount
  useEffect(() => {
    mountedRef.current = true;

    if (autoConnect) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoConnect, connect]);

  // Setup auto-refresh interval
  useEffect(() => {
    if (connectionState.isConnected && refreshInterval > 0) {
      intervalRef.current = setInterval(() => {
        connect();
      }, refreshInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [connectionState.isConnected, refreshInterval, connect]);

  return {
    ...connectionState,
    connect,
    disconnect,
    refresh,
  };
}

/**
 * useRealtimeData Hook
 * Manages real-time data updates from BRH backend
 */
export function useRealtimeData(endpoint, options = {}) {
  const {
    refreshInterval = 5000,
    enabled = true,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const mountedRef = useRef(false);
  const intervalRef = useRef(null);

  const fetchData = useCallback(async () => {
    if (!enabled || !mountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      let result;
      
      // Route to appropriate BRH service method
      switch (endpoint) {
        case 'agents':
          result = await BRHService.getAgents();
          break;
        case 'missions':
          result = await BRHService.getMissions();
          break;
        case 'fleet':
          result = await BRHService.getFleetStatus();
          break;
        case 'health':
          result = await BRHService.getHealth();
          break;
        case 'health/full':
          result = await BRHService.getFullHealth();
          break;
        case 'vault/logs':
          result = await BRHService.getVaultLogs();
          break;
        default:
          throw new Error(`Unknown endpoint: ${endpoint}`);
      }

      if (!mountedRef.current) return;

      setData(result);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (err) {
      if (!mountedRef.current) return;

      setError(err.message);
      setLoading(false);
    }
  }, [endpoint, enabled]);

  // Initial fetch and cleanup
  useEffect(() => {
    mountedRef.current = true;
    fetchData();

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData]);

  // Setup auto-refresh
  useEffect(() => {
    if (enabled && refreshInterval > 0) {
      intervalRef.current = setInterval(fetchData, refreshInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [enabled, refreshInterval, fetchData]);

  return {
    data,
    loading,
    error,
    lastUpdate,
    refetch: fetchData,
  };
}

export default useBRHConnection;
