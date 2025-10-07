import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function UnifiedHealthTimeline() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTimeline = async () => {
    try {
      const res = await fetch("/api/diagnostics/timeline/unified");
      const data = await res.json();
      setEvents(data.events || []);
    } catch (err) {
      console.error("Unified timeline fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
    const interval = setInterval(fetchTimeline, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const eventIcon = (type) => {
    const icons = {
      CI_CD_TRIAGE: "⚙️",
      ENDPOINT_TRIAGE: "🩺",
      API_TRIAGE: "🧬",
      DEPLOYMENT_SUCCESS: "🚀",
      DEPLOYMENT_FAILURE: "🔥",
      DEPLOYMENT_RECOVERY: "💚",
      DEPLOYMENT_REPAIR: "🩹",
      BUILD_SUCCESS: "🧱",
      BUILD_FAILURE: "💥",
      DEPLOYMENT_ROLLBACK: "♻️",
      DEPLOYMENT_REDEPLOY: "🔁",
    };
    return icons[type] || "ℹ️";
  };

  const getStatusColor = (status) => {
    const colors = {
      HEALTHY: "bg-green-500/20 border-green-500/50",
      DEGRADED: "bg-yellow-500/20 border-yellow-500/50",
      CRITICAL: "bg-red-500/20 border-red-500/50",
      success: "bg-green-500/20 border-green-500/50",
      failed: "bg-red-500/20 border-red-500/50",
      "auto-healed": "bg-blue-500/20 border-blue-500/50",
    };
    return colors[status] || "bg-gray-500/20 border-gray-500/50";
  };

  return (
    <Card className="w-full max-w-3xl mx-auto mt-6 shadow-lg bg-white/10 backdrop-blur-md rounded-2xl border border-gray-200">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center gap-2">
          🧭 Unified Health Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 overflow-y-auto max-h-[500px]">
        {loading ? (
          <p className="text-sm text-gray-500">Fetching timeline...</p>
        ) : events.length === 0 ? (
          <p className="text-sm text-gray-500">No health events logged yet.</p>
        ) : (
          events.map((e, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border transition-all ${getStatusColor(e.status)}`}
              style={{
                animation: "fadeInLeft 0.3s ease-out",
                animationDelay: `${idx * 0.02}s`,
                animationFillMode: "both",
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{eventIcon(e.type)}</span>
                  <strong className="text-sm">
                    {e.type.replace(/_/g, " ")}
                  </strong>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(e.meta?.timestamp).toLocaleString()}
                </span>
              </div>
              <p className="text-xs text-gray-700 mt-1">
                <strong>Status:</strong> {e.status}
              </p>
              {e.source && (
                <p className="text-xs text-gray-700">
                  <strong>Source:</strong> {e.source}
                </p>
              )}
              {e.meta?.environment && (
                <p className="text-xs text-gray-700">
                  <strong>Environment:</strong> {e.meta.environment}
                </p>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
