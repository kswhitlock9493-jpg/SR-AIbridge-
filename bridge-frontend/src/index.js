import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './Dashboard';
import CaptainsChat from './CaptainsChat';
import VaultLogs from './VaultLogs';
import MissionLog from './MissionLog';
import ArmadaMap from './ArmadaMap';
import CaptainToCaptain from './CaptainToCaptain';
import { getStatus } from '../api';
import './styles.css';

const App = () => {
  const [status, setStatus] = useState({
    agentsOnline: 0,
    activeMissions: 0,
    admiral: "Logged Out"
  });

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await getStatus();
        setStatus({
          agentsOnline: data.agents_online ?? 0,
          activeMissions: data.active_missions ?? 0,
          admiral: data.admiral ?? "Unknown"
        });
      } catch (err) {
        console.error("Status fetch failed:", err);
      }
    }

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="bridge-layout">
        <aside className="sidebar">
          <h1 className="bridge-title">⚓ SR-AIbridge</h1>
          <nav>
            <ul>
              <li><NavLink to="/" end className="nav-link">📊 Dashboard</NavLink></li>
              <li><NavLink to="/chat" className="nav-link">💬 Captains Chat</NavLink></li>
              <li><NavLink to="/vault" className="nav-link">📜 Vault Logs</NavLink></li>
              <li><NavLink to="/missions" className="nav-link">🚀 Mission Log</NavLink></li>
              <li><NavLink to="/armada" className="nav-link">🗺️ Armada Map</NavLink></li>
              <li><NavLink to="/captains" className="nav-link">⚔️ Captain-to-Captain</NavLink></li>
            </ul>
          </nav>
        </aside>
        <div className="main-panel">
          <header className="status-bar">
            <div className="status-item">🛰️ Agents Online: <span className="status-value">{status.agentsOnline}</span></div>
            <div className="status-item">📡 Active Missions: <span className="status-value">{status.activeMissions}</span></div>
            <div className="status-item">⚓ Admiral: <span className="status-value">{status.admiral}</span></div>
          </header>
          <div className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/chat" element={<CaptainsChat />} />
              <Route path="/vault" element={<VaultLogs />} />
              <Route path="/missions" element={<MissionLog />} />
              <Route path="/armada" element={<ArmadaMap />} />
              <Route path="/captains" element={<CaptainToCaptain />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;
import React from 'react';

const Dashboard = () => (
  <div className="placeholder">
    <h2>📊 Dashboard</h2>
    <p>Bridge overview and metrics coming soon.</p>
  </div>
);

export default Dashboard;
import React from 'react';

const CaptainsChat = () => (
  <div className="placeholder">
    <h2>💬 Captains Chat</h2>
    <p>Command chat will be live when backend connects.</p>
  </div>
);

export default CaptainsChat;
import React from 'react';

const VaultLogs = () => (
  <div className="placeholder">
    <h2>📜 Vault Logs</h2>
    <p>Logs and records for agents and missions.</p>
  </div>
);

export default VaultLogs;
import React from 'react';

const MissionLog = () => (
  <div className="placeholder">
    <h2>🚀 Mission Log</h2>
    <p>Live and historical mission details.</p>
  </div>
);

export default MissionLog;
import React from 'react';

const ArmadaMap = () => (
  <div className="placeholder">
    <h2>🗺️ Armada Map</h2>
    <p>The fleet map will render here (interactive once backend is live).</p>
  </div>
);

export default ArmadaMap;
import React from 'react';

const CaptainToCaptain = () => (
  <div className="placeholder">
    <h2>⚔️ Captain-to-Captain Chat</h2>
    <p>Direct channel for Captain communications (placeholder until Railway connects).</p>
  </div>
);

export default CaptainToCaptain;

