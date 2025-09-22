import { useEffect, useState } from "react";
import { getVaultLogs } from "../api";

const VaultLogs = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    getVaultLogs().then(setLogs).catch(console.error);
  }, []);

  return (
    <div className="placeholder">
      <h2>📜 Vault Logs</h2>
      <ul>
        {logs.map((log, i) => (
          <li key={i}>{JSON.stringify(log)}</li>
        ))}
      </ul>
    </div>
  );
};

export default VaultLogs;