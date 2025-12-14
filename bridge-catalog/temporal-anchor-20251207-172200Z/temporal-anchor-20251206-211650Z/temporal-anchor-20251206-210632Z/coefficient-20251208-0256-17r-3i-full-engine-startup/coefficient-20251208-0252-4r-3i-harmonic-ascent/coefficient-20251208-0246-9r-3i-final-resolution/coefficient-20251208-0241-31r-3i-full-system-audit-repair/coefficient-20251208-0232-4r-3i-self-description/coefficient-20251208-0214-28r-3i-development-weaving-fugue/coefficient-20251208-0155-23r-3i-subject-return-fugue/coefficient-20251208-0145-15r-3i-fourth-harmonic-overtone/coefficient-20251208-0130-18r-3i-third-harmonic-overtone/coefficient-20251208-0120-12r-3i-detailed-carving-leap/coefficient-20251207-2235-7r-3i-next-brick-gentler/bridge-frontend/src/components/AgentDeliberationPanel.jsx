/**
 * Agent Deliberation Panel
 * Streams agent reasoning, decisions, and job status updates via WebSocket
 * Shows real-time agent activity for a specific mission
 */
import React, { useEffect, useState, useRef } from 'react';
import config from '../config';

export default function AgentDeliberationPanel({ missionId }) {
  const [log, setLog] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const logEndRef = useRef(null);

  useEffect(() => {
    if (!missionId) return;

    // Construct WebSocket URL
    const wsBase = config.WS_BASE_URL || 
                   (config.API_BASE_URL?.replace('http://', 'ws://').replace('https://', 'wss://') || 
                    'ws://localhost:8000');
    const wsUrl = `${wsBase}/ws/mission/${missionId}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected for mission', missionId);
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLog((prev) => {
            const newLog = [message, ...prev].slice(0, 200); // Keep last 200 messages
            return newLog;
          });
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket closed for mission', missionId);
        setConnected(false);
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close();
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to establish connection');
    }
  }, [missionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  const getEventColor = (event) => {
    const type = event.type?.toLowerCase() || '';
    const status = event.status?.toLowerCase() || '';
    
    if (type.includes('error') || status === 'failed') return 'text-red-600';
    if (type.includes('success') || status === 'done') return 'text-green-600';
    if (type.includes('warning') || status === 'running') return 'text-yellow-600';
    return 'text-gray-700';
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="deliberation-panel bg-white border border-gray-300 rounded-lg shadow-sm p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">Agent Deliberation</h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-600">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-3 py-2 rounded text-sm mb-3">
          {error}
        </div>
      )}

      {!missionId ? (
        <div className="text-center text-gray-500 py-8">
          Select a mission to view agent deliberation
        </div>
      ) : log.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          {connected ? 'Waiting for agent activity...' : 'Connecting...'}
        </div>
      ) : (
        <div className="deliberation-log space-y-2 max-h-96 overflow-y-auto">
          {log.map((event, idx) => (
            <div
              key={idx}
              className={`text-sm border-l-2 pl-3 py-1 ${getEventColor(event)} border-current`}
            >
              <div className="flex items-baseline gap-2">
                <code className="text-xs text-gray-500">
                  {formatTimestamp(event.time || event.timestamp)}
                </code>
                <span className="flex-1">
                  {event.msg || event.message || event.type || 'Unknown event'}
                </span>
              </div>
              {event.agent && (
                <div className="text-xs text-gray-500 mt-1">
                  Agent: {event.agent}
                </div>
              )}
              {event.task_key && (
                <div className="text-xs text-gray-500">
                  Task: {event.task_key}
                </div>
              )}
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          {log.length} events • Mission #{missionId}
        </div>
      </div>
    </div>
  );
}
