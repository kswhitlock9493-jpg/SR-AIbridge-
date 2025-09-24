import { useState, useEffect, useRef, useCallback } from 'react';
import config from '../config';

/**
 * Custom hook for WebSocket connection management
 * Provides real-time updates for SR-AIbridge frontend
 */
export const useWebSocket = (onMessage = null) => {
  const [connected, setConnected] = useState(false);
  const [connectionStats, setConnectionStats] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000; // 1 second
  
  // Get WebSocket URL from config
  const getWebSocketUrl = () => {
    const baseUrl = config.API_BASE_URL || 'http://localhost:8000';
    return baseUrl.replace(/^http/, 'ws') + '/ws';
  };

  const send = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message));
        return true;
      } catch (err) {
        console.error('Failed to send WebSocket message:', err);
        return false;
      }
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
      return false;
    }
  }, []);

  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return; // Already connected
      }

      const wsUrl = getWebSocketUrl();
      console.log('🔌 Connecting to WebSocket:', wsUrl);
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        
        // Send initial ping
        send({ type: 'ping' });
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage({ ...message, timestamp: new Date().toISOString() });
          
          // Call external message handler if provided
          if (onMessage && typeof onMessage === 'function') {
            onMessage(message);
          }
          
          // Handle connection-specific messages
          if (message.type === 'connection_established') {
            setConnectionStats(message);
          }
          
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      wsRef.current.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        setConnected(false);
        
        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts.current);
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached');
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };
      
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [onMessage, send]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setConnected(false);
    setConnectionStats(null);
  }, []);

  const subscribe = useCallback((channel) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({ type: 'subscribe', channel }));
        return true;
      } catch (err) {
        console.error('Failed to send subscribe message:', err);
        return false;
      }
    } else {
      console.warn('WebSocket not connected, cannot subscribe to channel:', channel);
      return false;
    }
  }, []);

  const unsubscribe = useCallback((channel) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({ type: 'unsubscribe', channel }));
        return true;
      } catch (err) {
        console.error('Failed to send unsubscribe message:', err);
        return false;
      }
    } else {
      console.warn('WebSocket not connected, cannot unsubscribe from channel:', channel);
      return false;
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      disconnect();
    };
  }, [connect, disconnect]);

  // Periodic ping to keep connection alive
  useEffect(() => {
    if (!connected) return;
    
    const pingInterval = setInterval(() => {
      send({ type: 'ping' });
    }, 30000); // 30 seconds
    
    return () => clearInterval(pingInterval);
  }, [connected, send]);

  return {
    connected,
    connectionStats,
    lastMessage,
    error,
    send,
    subscribe,
    unsubscribe,
    reconnect: connect,
    disconnect
  };
};

export default useWebSocket;