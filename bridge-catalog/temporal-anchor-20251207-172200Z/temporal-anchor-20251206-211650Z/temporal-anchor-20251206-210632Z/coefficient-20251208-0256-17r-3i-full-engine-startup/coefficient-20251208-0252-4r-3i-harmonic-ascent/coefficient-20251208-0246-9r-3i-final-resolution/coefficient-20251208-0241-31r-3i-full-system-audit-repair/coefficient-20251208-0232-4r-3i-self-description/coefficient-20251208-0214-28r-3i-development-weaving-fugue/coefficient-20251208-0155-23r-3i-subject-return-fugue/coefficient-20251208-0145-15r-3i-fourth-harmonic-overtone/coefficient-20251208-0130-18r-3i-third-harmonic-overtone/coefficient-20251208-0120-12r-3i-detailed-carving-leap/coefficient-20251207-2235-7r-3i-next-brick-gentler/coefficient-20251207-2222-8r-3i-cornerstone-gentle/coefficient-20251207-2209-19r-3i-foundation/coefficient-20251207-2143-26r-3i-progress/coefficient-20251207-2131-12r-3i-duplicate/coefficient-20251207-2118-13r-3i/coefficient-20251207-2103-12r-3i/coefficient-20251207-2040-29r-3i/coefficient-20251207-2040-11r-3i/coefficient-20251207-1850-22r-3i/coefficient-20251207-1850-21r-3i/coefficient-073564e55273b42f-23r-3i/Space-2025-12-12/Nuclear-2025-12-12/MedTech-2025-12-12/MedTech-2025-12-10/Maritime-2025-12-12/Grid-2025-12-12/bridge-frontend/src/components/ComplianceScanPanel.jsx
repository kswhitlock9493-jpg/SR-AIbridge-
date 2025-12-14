import { useEffect, useState } from "react";
import { fetchScans } from "../api/scans";
import ScanReportModal from "./ScanReportModal";

export default function ComplianceScanPanel() {
  const [items, setItems] = useState([]);
  const [sel, setSel] = useState(null);
  
  const load = () => fetchScans().then(d => setItems(d.items || [])).catch(console.error);
  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t); }, []);
  
  const badge = (s) => s === "blocked" ? "bg-red-100 text-red-700"
                : s === "flagged" ? "bg-amber-100 text-amber-700"
                : "bg-emerald-100 text-emerald-700";
  
  return (
    <div className="p-4 rounded-2xl shadow bg-white">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Compliance Scans</h2>
        <button onClick={load} className="px-3 py-1 rounded bg-gray-200">Refresh</button>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-left">
          <th className="py-1">Scan</th><th>PR</th><th>Commit</th><th>Status</th><th>When</th><th></th>
        </tr></thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.id} className="border-t">
              <td className="py-1 font-mono">{it.id}</td>
              <td>{it.pr ?? "—"}</td>
              <td className="font-mono">{(it.commit || "—").slice(0,7)}</td>
              <td><span className={`px-2 py-0.5 rounded-full text-xs ${badge(it.policy_state)}`}>{it.policy_state}</span></td>
              <td className="text-xs">{it.meta?.timestamp?.replace("T"," ").replace("Z","")}</td>
              <td><button className="text-blue-600" onClick={()=>setSel(it.id)}>View</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      <ScanReportModal open={!!sel} scanId={sel} onClose={()=>setSel(null)} />
    </div>
  );
}
