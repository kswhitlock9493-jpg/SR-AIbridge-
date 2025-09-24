import React, { useEffect, useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { getStatus } from '../api';
import { useWebSocket } from '../hooks/useWebSocket';
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

// === Main App ===
const App = () => {
  const [status, setStatus] = useState({
    agentsOnline: 0,
    activeMissions: 0,
    admiral: "Logged Out"
  });
  const [connectionError, setConnectionError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [missionRefreshKey, setMissionRefreshKey] = useState(0);
  const [realTimeData, setRealTimeData] = useState({
    missions: [],
    vaultLogs: [],
    chatMessages: [],
    fleetData: []
  });
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [guardianActive, setGuardianActive] = useState(false);

  // Handle real-time WebSocket messages
  const handleWebSocketMessage = useCallback((message) => {
    console.log('📡 Real-time update:', message.type);
    
    switch (message.type) {
      case 'mission_updated':
        setRealTimeData(prev => ({
          ...prev,
          missions: [...prev.missions, message.mission]
        }));
        setMissionRefreshKey(prev => prev + 1);
        break;
        
      case 'vault_log':
        setRealTimeData(prev => ({
          ...prev,
          vaultLogs: [message.log, ...prev.vaultLogs.slice(0, 49)] // Keep last 50
        }));
        break;
        
      case 'chat_message':
        setRealTimeData(prev => ({
          ...prev,
          chatMessages: [message.message, ...prev.chatMessages.slice(0, 49)]
        }));
        break;
        
      case 'fleet_updated':
        setRealTimeData(prev => ({
          ...prev,
          fleetData: message.fleet
        }));
        break;
        
      case 'armada_order_executed':
        console.log('🚢 Fleet order executed:', message.result);
        break;
        
      default:
        console.log('📦 Unhandled message type:', message.type);
    }
  }, []);

  // Initialize WebSocket connection
  const { connected: wsConnected, error: wsError } = useWebSocket(handleWebSocketMessage);

  // Handle mission dispatch to trigger instant refresh in MissionLog
  const handleMissionDispatch = (missionData) => {
    setMissionRefreshKey(prev => prev + 1);
  };

  // Handle system alerts from AutonomyDaemon
  const handleSystemAlert = useCallback((alerts) => {
    setSystemAlerts(alerts);
  }, []);

  // Handle Guardian Mode activation
  const handleGuardianActivate = useCallback((reason) => {
    setGuardianActive(true);
    console.log('🛡️ Guardian Mode activated:', reason);
  }, []);

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
            
            <Routes>
              <Route path="/" element={<Dashboard realTimeData={realTimeData} />} />
              <Route path="/controls" element={<MissionControls onMissionDispatch={handleMissionDispatch} />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/chat" element={<CaptainsChat realTimeMessages={realTimeData.chatMessages} />} />
              <Route path="/vault" element={<VaultLogs realTimeLogs={realTimeData.vaultLogs} />} />
              <Route path="/missions" element={<MissionLog refreshKey={missionRefreshKey} realTimeMissions={realTimeData.missions} />} />
              <Route path="/armada" element={<ArmadaMap realTimeFleet={realTimeData.fleetData} />} />
              <Route path="/captains" element={<CaptainToCaptain realTimeMessages={realTimeData.chatMessages} />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;