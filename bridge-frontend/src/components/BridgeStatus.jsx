import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function BridgeStatus() {
  const [status, setStatus] = useState("loading");
  const [uptime, setUptime] = useState(null);
  const [latency, setLatency] = useState(null);
  const [message, setMessage] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "/api";

  const fetchStatus = async () => {
    const start = performance.now();
    try {
      const res = await fetch(`${API_URL}/netlify/ping`);
      const elapsed = performance.now() - start;

      if (!res.ok) throw new Error("Ping failed");
      const data = await res.json();

      setStatus("online");
      setUptime(data.api_health?.uptime_seconds || null);
      setLatency(Math.round(elapsed));
      setMessage(data.message || "Bridge backend link alive!");
    } catch (err) {
      setStatus("offline");
      setMessage("No response from backend");
      setLatency(null);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const getColor = () => {
    switch (status) {
      case "online": return "text-green-500";
      case "offline": return "text-red-500";
      default: return "text-yellow-500";
    }
  };

  return (
    <Card className="max-w-md mx-auto mt-4 shadow-xl rounded-2xl border border-gray-800 bg-black/40 backdrop-blur-md">
      <CardContent className="p-6 text-center text-gray-100">
        <h2 className="text-xl font-bold mb-2">Bridge Backend Status</h2>
        <p className={`${getColor()} text-lg font-semibold`}>
          {status === "online" ? "🟢 Online" : status === "offline" ? "🔴 Offline" : "🟡 Checking..."}
        </p>
        <p className="text-sm mt-2">{message}</p>
        {uptime && (
          <p className="text-xs text-gray-400 mt-1">
            Uptime: {Math.floor(uptime / 60)}m {Math.floor(uptime % 60)}s | Latency: {latency} ms
          </p>
        )}
      </CardContent>
    </Card>
  );
}
