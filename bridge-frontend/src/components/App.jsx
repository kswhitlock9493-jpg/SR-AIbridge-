import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { getStatus } from '../api';
import './styles.css';
import Dashboard from './Dashboard';
import CaptainsChat from './CaptainsChat';
import VaultLogs from './VaultLogs';
import MissionLog from './MissionLog';
import ArmadaMap from './ArmadaMap';
import CaptainToCaptain from './CaptainToCaptain';

// === Main App ===
const App = () => {
  const [status, setStatus] = useState({
    agentsOnline: 0,
    activeMissions: 0,
    admiral: "Logged Out"
  });
  const [connectionError, setConnectionError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchStatus() {
      try {
        setIsLoading(true);
        const data = await getStatus();
        setStatus({
          agentsOnline: data.agents_online ?? 0,
          activeMissions: data.active_missions ?? 0,
          admiral: data.admiral ?? "Unknown"
        });
        setConnectionError(null);
      } catch (err) {
        console.error("Status fetch failed:", err);
        setConnectionError(`Failed to connect to backend: ${err.message}`);
      } finally {
        setIsLoading(false);
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

          {connectionError && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{connectionError}</span>
              <span className="error-info">Please check your internet connection and try refreshing the page.</span>
            </div>
          )}

          {isLoading && !connectionError && (
            <div className="loading-banner">
              <span className="loading-icon">⏳</span>
              <span className="loading-message">Connecting to Agent Manager...</span>
            </div>
          )}

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