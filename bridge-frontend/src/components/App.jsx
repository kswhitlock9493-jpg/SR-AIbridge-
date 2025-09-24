import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { BridgeProvider, useBridge } from '../hooks/useBridge';
import './styles.css';
import Dashboard from './Dashboard';
import CaptainsChat from './CaptainsChat';
import VaultLogs from './VaultLogs';
import MissionLog from './MissionLog';
import ArmadaMap from './ArmadaMap';
import CaptainToCaptain from './CaptainToCaptain';
import MissionControls from './MissionControls';
import Agents from './Agents';
import AutonomyDaemon from '../daemon/AutonomyDaemon';
import DaemonGuardian from './DaemonGuardian';
import GuardianBanner from './GuardianBanner';

// === Bridge App Component ===
const BridgeApp = () => {
  const { 
    status, 
    loading: isLoading, 
    error: connectionError, 
    connected: wsConnected, 
    wsError,
    systemAlerts, 
    guardianActive,
    handleSystemAlert,
    handleGuardianActivate
  } = useBridge();

  const [missionRefreshKey, setMissionRefreshKey] = useState(0);

  // Handle mission dispatch to trigger instant refresh in MissionLog
  const handleMissionDispatch = useCallback((missionData) => {
    setMissionRefreshKey(prev => prev + 1);
    console.log('🚀 Mission dispatched, refreshing mission log');
  }, []);

  return (
    <Router>
      <div className="bridge-layout">
        <aside className="sidebar">
          <h1 className="bridge-title">⚓ SR-AIbridge</h1>
          <nav>
            <ul>
              <li><NavLink to="/" end className="nav-link">📊 Dashboard</NavLink></li>
              <li><NavLink to="/controls" className="nav-link">🎯 Mission Controls</NavLink></li>
              <li><NavLink to="/agents" className="nav-link">🤖 Agents</NavLink></li>
              <li><NavLink to="/chat" className="nav-link">💬 Captains Chat</NavLink></li>
              <li><NavLink to="/vault" className="nav-link">📜 Vault Logs</NavLink></li>
              <li><NavLink to="/missions" className="nav-link">🚀 Mission Log</NavLink></li>
              <li><NavLink to="/armada" className="nav-link">🗺️ Armada Map</NavLink></li>
              <li><NavLink to="/captains" className="nav-link">⚔️ Captain-to-Captain</NavLink></li>
            </ul>
          </nav>
        </aside>

        <div className="main-panel">
          {/* Guardian Banner - Always visible status */}
          <GuardianBanner />
          
          <header className="status-bar">
            <div className="status-item">🛰️ Agents Online: <span className="status-value">{status.agentsOnline}</span></div>
            <div className="status-item">📡 Active Missions: <span className="status-value">{status.activeMissions}</span></div>
            <div className="status-item">⚓ Admiral: <span className="status-value">{status.admiral}</span></div>
            <div className="status-item">🔌 WebSocket: 
              <span className={`status-value ${wsConnected ? 'connected' : 'disconnected'}`}>
                {wsConnected ? '🟢 Live' : '🔴 Offline'}
              </span>
            </div>
          </header>

          {(connectionError || wsError || systemAlerts.length > 0) && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span className="error-message">
                {connectionError || wsError || `System alerts: ${systemAlerts.join(', ')}`}
              </span>
              <span className="error-info">
                {wsConnected ? 'REST API issue' : 'Real-time features may be limited'}
              </span>
            </div>
          )}

          {guardianActive && (
            <div className="guardian-system-banner">
              <span className="guardian-icon">🛡️</span>
              <span className="guardian-message">GUARDIAN DEFENSE PROTOCOLS ACTIVE</span>
            </div>
          )}

          {isLoading && !connectionError && (
            <div className="loading-banner">
              <span className="loading-icon">⏳</span>
              <span className="loading-message">Connecting to Agent Manager...</span>
            </div>
          )}

          <div className="main-content">
            {/* Autonomy Daemon - Global System Monitor */}
            <AutonomyDaemon 
              onSystemAlert={handleSystemAlert}
              onGuardianActivate={handleGuardianActivate}
            />
            
            {/* DaemonGuardian - Enhanced monitoring with unified state */}
            <DaemonGuardian 
              onSystemAlert={handleSystemAlert}
              onGuardianActivate={handleGuardianActivate}
            />
            
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/controls" element={<MissionControls onMissionDispatch={handleMissionDispatch} />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/chat" element={<CaptainsChat />} />
              <Route path="/vault" element={<VaultLogs />} />
              <Route path="/missions" element={<MissionLog refreshKey={missionRefreshKey} />} />
              <Route path="/armada" element={<ArmadaMap />} />
              <Route path="/captains" element={<CaptainToCaptain />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

// === Main App Wrapper with Bridge Provider ===
const App = () => {
  return (
    <BridgeProvider>
      <BridgeApp />
    </BridgeProvider>
  );
};

export default App;