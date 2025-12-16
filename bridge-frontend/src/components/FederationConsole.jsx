import React, { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";

export default function FederationConsole() {
  const [state, setState] = useState({
    leader: null,
    peers: [],
    events: [],
    forgeStatus: "Connecting...",
  });

  // Use environment variable for API base URL with fallback
  const apiBase = import.meta.env.VITE_BRH_API_BASE || "http://localhost:7878";

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/federation/state`);
      const data = await res.json();
      setState((prev) => ({
        ...prev,
        leader: data.leader,
        peers: data.peers || [],
        forgeStatus: "Online",
      }));
    } catch {
      setState((prev) => ({ ...prev, forgeStatus: "Offline" }));
    }
  }, [apiBase]);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/events`);
      const data = await res.json();
      setState((prev) => ({
        ...prev,
        events: data.slice(-20), // show recent 20
      }));
    } catch {
      console.warn("No event feed yet");
    }
  }, [apiBase]);

  useEffect(() => {
    fetchStatus();
    fetchEvents();
    const interval = setInterval(() => {
      fetchStatus();
      fetchEvents();
    }, 8000);
    return () => clearInterval(interval);
  }, [fetchStatus, fetchEvents]);

  return (
    <div className="bg-gray-950 text-green-400 rounded-2xl shadow-lg p-6 font-mono border border-green-600">
      <motion.h2
        className="text-xl mb-4"
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
      >
        🛰 Bridge Federation Console
      </motion.h2>

      <div className="flex justify-between mb-4">
        <div>Forge Status: <b>{state.forgeStatus}</b></div>
        <div>Leader: <b>{state.leader || "?"}</b></div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {state.peers.map((p) => (
          <motion.div
            key={p.node}
            className={`border rounded-lg p-3 ${
              p.node === state.leader
                ? "border-green-500 bg-green-950"
                : "border-green-700 bg-gray-900"
            }`}
            whileHover={{ scale: 1.03 }}
          >
            <div><b>{p.node}</b></div>
            <div>Status: {p.status}</div>
            <div>Epoch: {p.epoch}</div>
            <div>Uptime: {p.uptime || "—"}</div>
          </motion.div>
        ))}
      </div>

      <h3 className="text-lg mb-2">Recent Events</h3>
      <div className="h-48 overflow-y-auto bg-black bg-opacity-60 rounded-lg p-2 border border-green-700 text-xs">
        {state.events.map((e, i) => (
          <div key={i} className="mb-1">
            [{new Date(e.time).toLocaleTimeString()}] {e.message}
          </div>
        ))}
      </div>
    </div>
  );
}
