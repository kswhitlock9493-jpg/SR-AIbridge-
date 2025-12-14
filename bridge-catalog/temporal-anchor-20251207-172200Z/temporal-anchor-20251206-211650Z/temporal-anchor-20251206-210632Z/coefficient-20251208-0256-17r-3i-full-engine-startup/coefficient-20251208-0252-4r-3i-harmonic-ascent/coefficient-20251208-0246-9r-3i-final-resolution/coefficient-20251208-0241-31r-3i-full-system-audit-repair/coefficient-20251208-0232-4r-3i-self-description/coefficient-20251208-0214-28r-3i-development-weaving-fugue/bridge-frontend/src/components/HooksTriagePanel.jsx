import React, { useEffect, useState } from "react";

export default function HooksTriagePanel() {
  const [triage, setTriage] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const res = await fetch("/api/diagnostics/timeline");
      const data = await res.json();
      const latest = data.events?.find(e => e.type === "HOOKS_TRIAGE");
      setTriage(latest || null);
    } catch (err) {
      console.error("Hooks Triage fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      HEALTHY: "text-green-600 bg-green-100",
      DEGRADED: "text-yellow-600 bg-yellow-100",
      CRITICAL: "text-red-600 bg-red-100"
    };
    return colors[status] || "text-gray-600 bg-gray-100";
  };

  const getStatusIcon = (status) => {
    const icons = {
      HEALTHY: "✅",
      DEGRADED: "⚠️",
      CRITICAL: "🚨"
    };
    return icons[status] || "ℹ️";
  };

  if (loading) {
    return (
      <div className="p-4 bg-white/10 border border-gray-200 rounded-xl shadow">
        <h3 className="text-lg font-semibold">🪝 Hooks Triage</h3>
        <p className="text-sm text-gray-500">Loading Hooks Triage...</p>
      </div>
    );
  }

  if (!triage) {
    return (
      <div className="p-4 bg-white/10 border border-gray-200 rounded-xl shadow">
        <h3 className="text-lg font-semibold">🪝 Hooks Triage</h3>
        <p className="text-sm text-gray-500">No hooks triage data available yet.</p>
      </div>
    );
  }

  const results = triage.meta?.results || [];

  return (
    <div className="p-4 bg-white/10 border border-gray-200 rounded-xl shadow">
      <h3 className="text-lg font-semibold mb-2">🪝 Hooks Triage</h3>
      
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{getStatusIcon(triage.status)}</span>
        <div>
          <p className="text-sm font-medium">
            Status: 
            <span className={`ml-2 px-2 py-1 rounded text-xs font-bold ${getStatusColor(triage.status)}`}>
              {triage.status}
            </span>
          </p>
          {triage.meta?.timestamp && (
            <p className="text-xs text-gray-600 mt-1">
              Last check: {new Date(triage.meta.timestamp).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      {results.length > 0 && (
        <div className="mt-3 space-y-2">
          {results.map((r, i) => (
            <div key={i} className="p-2 rounded-md bg-white/20">
              <div className="flex justify-between items-center text-sm">
                <span className="font-medium">{r.name}</span>
                <span>{r.status === "OK" ? "✅" : "❌"}</span>
              </div>
              <div className="text-xs text-gray-700 mt-1 space-y-0.5">
                {r.url && <div>URL: {r.url}</div>}
                {r.latencyMs !== undefined && <div>Latency: {r.latencyMs} ms</div>}
                {r.code !== undefined && <div>HTTP: {r.code}</div>}
                {r.error && <div className="text-red-700">Error: {r.error}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
