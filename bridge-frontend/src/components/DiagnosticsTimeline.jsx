import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function DiagnosticsTimeline() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTimeline = async () => {
    try {
      const res = await fetch("/api/diagnostics/timeline");
      const data = await res.json();
      setEvents(data.events || []);
    } catch (err) {
      console.error("Timeline fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
    const interval = setInterval(fetchTimeline, 30000);
    return () => clearInterval(interval);
  }, []);

  const eventIcon = (type) => {
    const map = {
      BUILD_SUCCESS: "🧱",
      BUILD_FAILURE: "💥",
      DEPLOYMENT_SUCCESS: "🚀",
      DEPLOYMENT_FAILURE: "⚠️",
      DEPLOYMENT_REPAIR: "🩹",
      DEPLOYMENT_ROLLBACK: "♻️",
      DEPLOYMENT_REDEPLOY: "🔁",
      DIAGNOSTIC_CLEANUP: "🧹",
    };
    return map[type] || "ℹ️";
  };

  return (
    <Card className="w-full max-w-3xl mx-auto mt-6 shadow-lg bg-white/10 backdrop-blur-md rounded-2xl border border-gray-200">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center gap-2">
          🧭 Bridge Diagnostics Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 overflow-y-auto max-h-[500px]">
        {loading ? (
          <p className="text-sm text-gray-500">Fetching timeline...</p>
        ) : events.length === 0 ? (
          <p className="text-sm text-gray-500">No diagnostics events logged yet.</p>
        ) : (
          events.map((e, idx) => (
            <div
              key={e.id || idx}
              className="p-3 rounded-md bg-white/20 hover:bg-white/30 transition-all timeline-event"
              style={{
                animationDelay: `${idx * 0.03}s`
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{eventIcon(e.type)}</span>
                  <strong className="text-sm">
                    {e.type.replaceAll("_", " ")}
                  </strong>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(e.timestamp).toLocaleString()}
                </span>
              </div>
              <p className="text-xs text-gray-700 mt-1">
                <strong>Status:</strong> {e.status}
              </p>
              <p className="text-xs text-gray-700">
                <strong>Source:</strong> {e.source} ({e.environment})
              </p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
