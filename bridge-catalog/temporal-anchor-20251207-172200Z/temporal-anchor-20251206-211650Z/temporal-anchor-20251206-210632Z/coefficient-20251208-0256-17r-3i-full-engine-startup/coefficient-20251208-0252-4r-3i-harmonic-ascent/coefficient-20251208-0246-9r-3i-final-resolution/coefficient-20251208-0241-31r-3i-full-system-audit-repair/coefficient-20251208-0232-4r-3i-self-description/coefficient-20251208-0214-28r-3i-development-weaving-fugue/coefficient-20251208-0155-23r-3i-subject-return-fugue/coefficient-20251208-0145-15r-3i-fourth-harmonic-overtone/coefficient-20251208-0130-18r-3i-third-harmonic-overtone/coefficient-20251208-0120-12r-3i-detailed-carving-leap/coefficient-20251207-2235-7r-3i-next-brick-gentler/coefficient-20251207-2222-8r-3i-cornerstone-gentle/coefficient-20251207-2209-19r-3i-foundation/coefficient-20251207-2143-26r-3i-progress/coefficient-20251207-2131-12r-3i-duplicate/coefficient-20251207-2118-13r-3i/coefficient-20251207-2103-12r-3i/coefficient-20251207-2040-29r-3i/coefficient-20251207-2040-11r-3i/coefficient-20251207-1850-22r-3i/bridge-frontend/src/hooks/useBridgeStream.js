/**
 * useBridgeStream - WebSocket hook for Heritage Bridge event streaming
 */

import { useEffect, useRef, useState } from "react";

const WS_BASE = import.meta.env.VITE_WS_BASE || "ws://localhost:8000";

export function useBridgeStream() {
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState({
    queue: 0,
    active: 0,
    completed: 0,
    winRates: {},
    health: {}
  });
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/heritage/ws/stats`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("🔌 WebSocket connected to Heritage Bridge");
    };

    ws.onmessage = (msg) => {
      try {
        const e = JSON.parse(msg.data);
        
        // Handle heritage events
        if (e.kind?.startsWith("heritage") || e.kind?.startsWith("demo") || 
            e.kind?.startsWith("bridge") || e.kind?.startsWith("fault") || 
            e.kind?.startsWith("heal") || e.kind?.startsWith("federation") ||
            e.kind?.startsWith("anchor")) {
          setEvents(prev => [e, ...prev].slice(0, 250));
        }
        
        // Handle metrics updates
        if (e.kind === "metrics.update") {
          setMetrics(e.payload || e);
        }
      } catch (err) {
        console.error("WebSocket message parse error:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket disconnected");
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const send = (obj) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(obj));
    }
  };

  return { events, metrics, send };
}
