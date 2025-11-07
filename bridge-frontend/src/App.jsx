import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import CommandDeck from './components/CommandDeck.jsx';
import CommandDeckV1 from './pages/CommandDeckV1.jsx';
import CaptainsChat from './components/CaptainsChat.jsx';
import CaptainToCaptain from './components/CaptainToCaptain.jsx';
import VaultLogs from './components/VaultLogs.jsx';
import MissionLog from './components/MissionLog.jsx';
import ArmadaMap from './components/ArmadaMap.jsx';
import SystemSelfTest from './components/SystemSelfTest.jsx';
import BrainConsole from './components/BrainConsole.jsx';
import AdmiralKeysPanel from './components/AdmiralKeysPanel.jsx';
import IndoctrinationPanel from './components/IndoctrinationPanel.jsx';
import AgentFoundry from './components/AgentFoundry.jsx';
import TierPanel from './components/dashboard/TierPanel.jsx';
import PermissionsConsole from './components/PermissionsConsole.jsx';
import './styles.css';

const App = () => {
  const navigationItems = [
    { path: '/', label: '📊 Command Deck' },
    { path: '/deck', label: '🌉 Heritage Deck' },
    { path: '/captains-chat', label: '💬 Captains Chat' },
    { path: '/captain-to-captain', label: '⚔️ Captain-to-Captain' },
    { path: '/vault-logs', label: '📜 Vault Logs' },
    { path: '/mission-log', label: '🚀 Mission Log' },
    { path: '/armada-map', label: '🗺️ Armada Map' },
    { path: '/brain', label: '🧠 Brain' },
    { path: '/custody', label: '🔑 Custody' },
    { path: '/agent-foundry', label: '🛠️ Agent Foundry' },
    { path: '/tier-dashboard', label: '⭐ Tier Dashboard' },
    { path: '/indoctrination', label: '⚔️ Indoctrination' },
    { path: '/permissions', label: '🔒 Permissions' },
    { path: '/system-health', label: '🔍 System Health' }
  ];

  return (
    <Router>
      <div className="sr-aibridge-app">
        <header className="app-header">
          <div className="header-content">
            <h1 className="app-title">
              <span className="title-icon">🌉</span>
              SR-AIbridge Command Center
            </h1>
            <div className="connection-status">
              <span className="status-indicator online">●</span>
              <span className="status-text">Connected</span>
            </div>
          </div>
        </header>

        {/* Desktop horizontal navigation */}
        <nav className="app-navigation desktop-nav">
          <div className="nav-tabs">
            {navigationItems.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `nav-tab ${isActive ? 'active' : ''}`}
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </nav>

        {/* Main layout with sidebar for mobile/tablet */}
        <div className="app-layout">
          {/* Mobile/tablet sidebar navigation */}
          <nav className="app-sidebar mobile-nav">
            <div className="sidebar-nav">
              {navigationItems.map(item => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          </nav>

          <main className="app-content">
            <div className="content-wrapper">
              <Routes>
                <Route path="/" element={
                  <ErrorBoundary name="CommandDeck">
                    <CommandDeck />
                  </ErrorBoundary>
                } />
                <Route path="/deck" element={
                  <ErrorBoundary name="HeritageDeck">
                    <CommandDeckV1 />
                  </ErrorBoundary>
                } />
                <Route path="/captains-chat" element={
                  <ErrorBoundary name="CaptainsChat">
                    <CaptainsChat />
                  </ErrorBoundary>
                } />
                <Route path="/captain-to-captain" element={
                  <ErrorBoundary name="CaptainToCaptain">
                    <CaptainToCaptain />
                  </ErrorBoundary>
                } />
                <Route path="/vault-logs" element={
                  <ErrorBoundary name="VaultLogs">
                    <VaultLogs />
                  </ErrorBoundary>
                } />
                <Route path="/mission-log" element={
                  <ErrorBoundary 
                    name="MissionLog"
                    errorMessage="Mission Log is temporarily unavailable. The system is recovering."
                  >
                    <MissionLog />
                  </ErrorBoundary>
                } />
                <Route path="/armada-map" element={
                  <ErrorBoundary name="ArmadaMap">
                    <ArmadaMap />
                  </ErrorBoundary>
                } />
                <Route path="/brain" element={
                  <ErrorBoundary 
                    name="BrainConsole"
                    errorMessage="Brain Console is temporarily unavailable. Memory systems are stabilizing."
                  >
                    <BrainConsole />
                  </ErrorBoundary>
                } />
                <Route path="/custody" element={
                  <ErrorBoundary 
                    name="AdmiralKeys"
                    errorMessage="Admiral Keys panel is temporarily unavailable. Cryptographic systems are recovering."
                  >
                    <AdmiralKeysPanel />
                  </ErrorBoundary>
                } />
                <Route path="/agent-foundry" element={
                  <ErrorBoundary 
                    name="AgentFoundry"
                    errorMessage="Agent Foundry is temporarily unavailable. Agent creation systems are recovering."
                  >
                    <AgentFoundry />
                  </ErrorBoundary>
                } />
                <Route path="/tier-dashboard" element={
                  <ErrorBoundary name="TierDashboard">
                    <TierPanel />
                  </ErrorBoundary>
                } />
                <Route path="/indoctrination" element={
                  <ErrorBoundary 
                    name="Indoctrination"
                    errorMessage="Indoctrination Engine is temporarily unavailable."
                  >
                    <IndoctrinationPanel />
                  </ErrorBoundary>
                } />
                <Route path="/permissions" element={
                  <ErrorBoundary name="Permissions">
                    <PermissionsConsole />
                  </ErrorBoundary>
                } />
                <Route path="/system-health" element={
                  <ErrorBoundary name="SystemHealth">
                    <SystemSelfTest />
                  </ErrorBoundary>
                } />
                {/* Redirect any unknown paths to command deck */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </main>
        </div>

        <footer className="app-footer">
          <div className="footer-content">
            <span>SR-AIbridge v2.0.0 | Production Ready | All Endpoints Wired</span>
            <span className="footer-status">
              Backend: /status | /missions | /vault/logs | /armada/status | /captains/messages | /health
            </span>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;