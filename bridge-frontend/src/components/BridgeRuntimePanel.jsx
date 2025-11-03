import React, { useEffect, useState } from "react";

export default function BridgeRuntimePanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:7878/status");
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendCommand = async (name, action) => {
    try {
      await fetch(`http://localhost:7878/${action}/${name}`, { method: "POST" });
      fetchStatus();
    } catch (err) {
      console.error(`Failed to ${action} ${name}:`, err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 10000);
    return () => clearInterval(timer);
  }, []);

  if (loading) {
    return <div className="text-center text-gray-400">Loading runtime status...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-600 text-red-400 p-6 rounded-xl">
        <h2 className="text-xl mb-2">⚠️ BRH Connection Error</h2>
        <p>{error}</p>
        <p className="text-sm mt-2">Make sure the BRH node is running on localhost:7878</p>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center text-gray-400">No data available</div>;
  }

  return (
    <div className="bg-black text-green-400 p-6 rounded-xl shadow-lg font-mono border border-green-600">
      <h2 className="text-xl mb-2">🛰️ Bridge Runtime Control Deck</h2>
      <div className="mb-4 space-y-1 text-sm">
        <p><span className="text-gray-400">Forge root:</span> {data.forge_root}</p>
        <p><span className="text-gray-400">Active containers:</span> {data.container_count}</p>
        <p><span className="text-gray-400">Last update:</span> {new Date(data.timestamp * 1000).toLocaleTimeString()}</p>
      </div>
      <div className="mt-4 space-y-3">
        {data.containers && data.containers.length > 0 ? (
          data.containers.map((c) => (
            <div key={c.id} className="border border-green-600 rounded-lg p-3 bg-gray-900/50">
              <div className="mb-2">
                <span className="font-bold text-green-300">{c.name}</span>
                <span className={`ml-3 text-xs px-2 py-1 rounded ${
                  c.status === 'running' ? 'bg-green-700 text-green-100' : 'bg-red-700 text-red-100'
                }`}>
                  {c.status}
                </span>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <p>Image: {c.image}</p>
                <p>Started: {c.started}</p>
              </div>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => sendCommand(c.name, "restart")}
                  className="bg-green-700 hover:bg-green-600 px-3 py-1 rounded text-xs transition-colors"
                >
                  Restart
                </button>
                <button
                  onClick={() => sendCommand(c.name, "drain")}
                  className="bg-red-700 hover:bg-red-600 px-3 py-1 rounded text-xs transition-colors"
                >
                  Drain
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-4">
            No containers running
          </div>
        )}
      </div>
    </div>
  );
}
