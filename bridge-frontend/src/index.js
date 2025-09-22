// src/components/App.js
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './Dashboard';
import CaptainsChat from './CaptainsChat';
import VaultLogs from './VaultLogs';
import MissionLog from './MissionLog';
import ArmadaMap from './ArmadaMap';
import CaptainToCaptain from './CaptainToCaptain';
import { getStatus } from './api';
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

// src/components/Dashboard.js
import React from 'react';

const Dashboard = () => (
  <div className="placeholder">
    <h2>📊 Dashboard</h2>
    <p>Bridge overview and metrics coming soon.</p>
  </div>
);

export default Dashboard;

// src/components/CaptainsChat.js
import React from 'react';

const CaptainsChat = () => (
  <div className="placeholder">
    <h2>💬 Captains Chat</h2>
    <p>Command chat will be live when backend connects.</p>
  </div>
);

export default CaptainsChat;

// src/components/VaultLogs.js
import React from 'react';

const VaultLogs = () => (
  <div className="placeholder">
    <h2>📜 Vault Logs</h2>
    <p>Logs and records for agents and missions.</p>
  </div>
);

export default VaultLogs;

// src/components/MissionLog.js
import React from 'react';

const MissionLog = () => (
  <div className="placeholder">
    <h2>🚀 Mission Log</h2>
    <p>Live and historical mission details.</p>
  </div>
);

export default MissionLog;

// src/components/ArmadaMap.js
import React from 'react';

const ArmadaMap = () => (
  <div className="placeholder">
    <h2>🗺️ Armada Map</h2>
    <p>The fleet map will render here (interactive once backend is live).</p>
  </div>
);

export default ArmadaMap;

// src/components/CaptainToCaptain.js
import React from 'react';

const CaptainToCaptain = () => (
  <div className="placeholder">
    <h2>⚔️ Captain-to-Captain Chat</h2>
    <p>Direct channel for Captain communications (placeholder until Railway connects).</p>
  </div>
);

export default CaptainToCaptain;

// src/components/api.js
export async function getStatus() {
  const response = await fetch("http://localhost:8000/status");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
}

// src/components/config.js
const config = {
  API_BASE_URL: "http://localhost:8000"
};

export default config;

// src/components/styles.css
body {
  margin: 0;
  font-family: system-ui, sans-serif;
  background: #0d1117;
  color: white;
}

.bridge-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: #161b22;
  padding: 20px;
  box-sizing: border-box;
}

.bridge-title {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
}

.nav-link {
  display: block;
  color: rgba(255,255,255,0.8);
  padding: 10px;
  text-decoration: none;
  border-radius: 6px;
}

.nav-link.active {
  background: #238636;
  color: white;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.status-bar {
  display: flex;
  justify-content: space-around;
  background: #21262d;
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.status-item {
  font-size: 0.9rem;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.placeholder {
  background: rgba(255,255,255,0.05);
  padding: 20px;
  border-radius: 8px;
}

// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './components/App';
import './components/styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
