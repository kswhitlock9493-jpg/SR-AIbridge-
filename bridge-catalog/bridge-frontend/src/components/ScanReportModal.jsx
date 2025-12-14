import { useEffect, useState } from "react";
import { fetchScan } from "../api/scans";

export default function ScanReportModal({ open, onClose, scanId }) {
  const [data, setData] = useState(null);
  useEffect(() => { if (open && scanId) fetchScan(scanId).then(setData).catch(console.error); }, [open, scanId]);
  if (!open) return null;
  
  const payload = data?.payload;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Scan Report: {scanId}</h2>
          <button className="px-3 py-1 rounded bg-gray-200" onClick={onClose}>Close</button>
        </div>
        {!payload ? <div>Loading…</div> : (
          <div className="space-y-4">
            <div className="text-sm">Policy state: <b className={
              payload.policy_state === "blocked" ? "text-red-600" :
              payload.policy_state === "flagged" ? "text-amber-600" : "text-emerald-700"}>
              {payload.policy_state.toUpperCase()}
            </b></div>
            
            <div>
              <h3 className="font-medium">License Summary</h3>
              <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto">
                {JSON.stringify(payload.license.summary, null, 2)}
              </pre>
            </div>
            
            <div>
              <h3 className="font-medium">Counterfeit Hits</h3>
              <table className="w-full text-sm">
                <thead><tr className="text-left">
                  <th className="py-1">Path</th><th>Score</th><th>Match</th>
                </tr></thead>
                <tbody>
                  {payload.counterfeit.map((c, i) => (
                    <tr key={i} className="border-t">
                      <td className="py-1">{c.path}</td>
                      <td>{(c.score*100).toFixed(1)}%</td>
                      <td>{c.match_path || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div>
              <h3 className="font-medium">Metadata</h3>
              <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto">
                {JSON.stringify(payload.meta, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
