import { useEffect, useState } from "react";
import { getMissionLog } from "../api";

const MissionLog = () => {
  const [missions, setMissions] = useState([]);

  useEffect(() => {
    getMissionLog().then(setMissions).catch(console.error);
  }, []);

  return (
    <div className="placeholder">
      <h2>🚀 Mission Log</h2>
      <ul>
        {missions.map((m, i) => (
          <li key={i}>{JSON.stringify(m)}</li>
        ))}
      </ul>
    </div>
  );
};

export default MissionLog;