import React, { useEffect, useState } from "react";

export default function TriageBootstrapBanner() {
  const [seeded, setSeeded] = useState(false);
  
  useEffect(() => {
    fetch("/api/diagnostics/timeline/unified")
      .then(res => res.json())
      .then(data => {
        const triageTypes = ["CI_CD_TRIAGE", "ENDPOINT_TRIAGE", "API_TRIAGE", "HOOKS_TRIAGE"];
        const allSeeded = triageTypes.every(t => 
          data.events?.some((e) => e.type === t)
        );
        setSeeded(allSeeded);
      })
      .catch(() => {
        // Silently fail - banner just won't show
      });
  }, []);
  
  if (!seeded) return null;
  
  return (
    <div className="p-2 bg-green-700 text-white text-sm rounded-md shadow mb-3">
      ✅ Triage systems seeded and synchronized. Bridge health baseline established.
    </div>
  );
}
