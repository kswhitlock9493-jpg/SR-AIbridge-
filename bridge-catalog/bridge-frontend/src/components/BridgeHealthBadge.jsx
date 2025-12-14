import React, { useEffect, useState } from "react";

export default function BridgeHealthBadge() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    fetch("/api/bridge/health")
      .then(r => r.json())
      .then(d => setStatus(d.status || "unknown"))
      .catch(() => setStatus("offline"));
  }, []);

  const color = {
    healthy: "bg-green-500",
    issues: "bg-yellow-500",
    offline: "bg-red-500",
    loading: "bg-gray-400",
  }[status] || "bg-gray-400";

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-white font-semibold ${color}`}>
      🩺 Healer-Net: {status.toUpperCase()}
    </div>
  );
}
