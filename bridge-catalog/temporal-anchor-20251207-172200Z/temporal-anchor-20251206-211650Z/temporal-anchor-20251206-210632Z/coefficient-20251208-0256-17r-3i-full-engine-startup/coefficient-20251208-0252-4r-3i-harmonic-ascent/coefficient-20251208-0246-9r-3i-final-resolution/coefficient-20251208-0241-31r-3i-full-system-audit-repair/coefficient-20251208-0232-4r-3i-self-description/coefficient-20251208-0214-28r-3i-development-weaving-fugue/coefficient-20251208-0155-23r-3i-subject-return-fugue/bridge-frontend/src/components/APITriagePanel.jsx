import React, { useEffect, useState } from "react";

export default function APITriagePanel() {
  const [triage, setTriage] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const res = await fetch("/api/diagnostics/timeline");
      const data = await res.json();
      const latest = data.events?.find(e => e.type === "API_TRIAGE");
      setTriage(latest || null);
    } catch (err) {
      console.error("API Triage fetch failed:", err);
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
      <div className="p-4 bg-white/10 border border-gray-200 rounded-lg shadow">
        <h3 className="text-lg font-semibold">🧬 API Triage</h3>
        <p className="text-sm text-gray-500">Loading API Triage...</p>
      </div>
    );
  }

  if (!triage) {
    return (
      <div className="p-4 bg-white/10 border border-gray-200 rounded-lg shadow">
        <h3 className="text-lg font-semibold">🧬 API Triage</h3>
        <p className="text-sm text-gray-500">No triage data available yet.</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white/10 border border-gray-200 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">🧬 API Triage</h3>
      
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

      {triage.meta?.failedChecks && triage.meta.failedChecks.length > 0 && (
        <div className="mt-3 p-2 bg-red-50 rounded border border-red-200">
          <p className="text-xs font-semibold text-red-800 mb-1">Failed Checks:</p>
          <ul className="list-disc ml-4 text-xs text-red-700">
            {triage.meta.failedChecks.map((f, i) => (
              <li key={i}>{f.name}: {f.error}</li>
            ))}
          </ul>
        </div>
      )}

      {triage.meta?.results && (
        <div className="mt-3">
          <p className="text-xs font-semibold mb-1 text-gray-700">API Check Details:</p>
          <div className="space-y-1">
            {triage.meta.results.map((result, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-gray-700">{result.name}</span>
                <span className={result.status === "OK" ? "text-green-600" : "text-red-600"}>
                  {result.status === "OK" ? "✓" : "✗"} {result.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
