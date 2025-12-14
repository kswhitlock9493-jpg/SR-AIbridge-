import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function BridgeStatus() {
  const [status, setStatus] = useState("checking");
  const [uptime, setUptime] = useState(null);
  const [latency, setLatency] = useState(null);
  const [message, setMessage] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "/api";

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const start = performance.now();
        const res = await fetch(`${API_URL}/netlify/ping`);
        const elapsed = performance.now() - start;

        if (!res.ok) throw new Error("Failed to reach backend");
        const data = await res.json();

        setStatus("online");
        setUptime(data.api_health?.uptime_seconds || 0);
        setLatency(Math.round(elapsed));
        setMessage(data.message || "Bridge backend link alive!");
      } catch {
        setStatus("offline");
        setUptime(null);
        setLatency(null);
        setMessage("No response from backend");
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, [API_URL]);

  const colorMap = {
    online: "#22c55e", // green
    offline: "#ef4444", // red
    checking: "#eab308", // yellow
  };

  const pulseAnimation = `
    @keyframes glowPulse {
      0%, 100% { box-shadow: 0 0 15px 2px ${colorMap[status]}; }
      50% { box-shadow: 0 0 25px 6px ${colorMap[status]}; }
    }
  `;

  const signalBars = (() => {
    if (latency === null) return [false, false, false];
    if (latency < 100) return [true, true, true]; // Excellent
    if (latency < 300) return [true, true, false]; // Moderate
    return [true, false, false]; // Weak
  })();

  return (
    <Card
      style={{
        backgroundColor: "#0f172a",
        color: "white",
        borderRadius: "1rem",
        border: `1px solid ${colorMap[status]}`,
        boxShadow: `0 0 10px ${colorMap[status]}`,
        animation: "glowPulse 2.5s ease-in-out infinite",
        transition: "all 0.5s ease-in-out",
      }}
    >
      <style>{pulseAnimation}</style>
      <CardContent className="p-4 text-center">
        <h3
          style={{
            fontSize: "1.1rem",
            fontWeight: "600",
            marginBottom: "0.75rem",
          }}
        >
          🌐 Bridge Backend Status
        </h3>
        <p>
          Status:{" "}
          <span
            style={{
              color: colorMap[status],
              fontWeight: 600,
              transition: "color 0.4s ease",
            }}
          >
            {status.toUpperCase()}
          </span>
        </p>
        <p style={{ marginTop: "0.25rem", fontSize: "0.9rem" }}>{message}</p>

        {/* Signal Bars */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            gap: "4px",
            marginTop: "0.75rem",
            height: "20px",
            transition: "opacity 0.5s ease",
          }}
        >
          {signalBars.map((active, i) => (
            <div
              key={i}
              style={{
                width: "6px",
                height: `${8 + i * 6}px`,
                backgroundColor: active ? colorMap[status] : "#334155",
                borderRadius: "2px",
                transition: "background-color 0.4s ease, height 0.4s ease",
              }}
            ></div>
          ))}
        </div>

        {uptime && (
          <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", opacity: 0.8 }}>
            Uptime: {Math.floor(uptime / 60)}m {Math.floor(uptime % 60)}s |{" "}
            Latency: {latency} ms
          </p>
        )}
      </CardContent>
    </Card>
  );
}
