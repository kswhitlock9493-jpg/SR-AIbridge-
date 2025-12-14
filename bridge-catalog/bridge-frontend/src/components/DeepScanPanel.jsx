import { useEffect, useState } from "react";

export default function DeepScanPanel() {
  const [status, setStatus] = useState("Checking...");
  const [endpoints, setEndpoints] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDeepScan = async () => {
    try {
      const res = await fetch("/api/diagnostics/timeline");
      const data = await res.json();
      
      // Find the latest ENDPOINT_DEEPSCAN event
      const latest = data.events?.find(e => e.type === "ENDPOINT_DEEPSCAN");
      
      if (latest) {
        setStatus(latest.status || "Unknown");
        setEndpoints(latest.meta?.diagnostics?.results || []);
      } else {
        setStatus("No Data");
        setEndpoints([]);
      }
    } catch (err) {
      console.error("DeepScan fetch failed:", err);
      setStatus("Offline");
      setEndpoints([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeepScan();
    const interval = setInterval(fetchDeepScan, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    if (status === "complete" || status === "Healthy") return "text-green-400";
    if (status === "Offline" || status === "failed") return "text-red-400";
    return "text-yellow-400";
  };

  if (loading) {
    return (
      <div className="p-3 bg-slate-900 text-gray-100 rounded-lg shadow">
        <h3 className="text-lg font-semibold">🛰️ Endpoint DeepScan</h3>
        <p className="text-sm text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-3 bg-slate-900 text-gray-100 rounded-lg shadow">
      <h3 className="text-lg font-semibold">🛰️ Endpoint DeepScan</h3>
      <p className="text-sm">
        Status: <span className={getStatusColor(status)}>{status}</span>
      </p>
      
      {endpoints.length > 0 && (
        <ul className="mt-2">
          {endpoints.map((e, i) => (
            <li key={i} className="text-sm text-gray-400">{e}</li>
          ))}
        </ul>
      )}
      
      {endpoints.length === 0 && status !== "Checking..." && (
        <p className="text-xs text-gray-500 mt-2">No endpoint data available</p>
      )}
    </div>
  );
}
