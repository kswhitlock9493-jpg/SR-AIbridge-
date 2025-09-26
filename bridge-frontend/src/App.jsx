import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import CommandDeck from './components/CommandDeck.jsx';
import CaptainsChat from './components/CaptainsChat.jsx';
import CaptainToCaptain from './components/CaptainToCaptain.jsx';
import VaultLogs from './components/VaultLogs.jsx';
import MissionLog from './components/MissionLog.jsx';
import ArmadaMap from './components/ArmadaMap.jsx';
import SystemSelfTest from './components/SystemSelfTest.jsx';
import BrainConsole from './components/BrainConsole.jsx';
import AdmiralKeysPanel from './components/AdmiralKeysPanel.jsx';
import './styles.css';

const App = () => {
  const navigationItems = [
    { path: '/', label: '📊 Command Deck' },
    { path: '/captains-chat', label: '💬 Captains Chat' },
    { path: '/captain-to-captain', label: '⚔️ Captain-to-Captain' },
    { path: '/vault-logs', label: '📜 Vault Logs' },
    { path: '/mission-log', label: '🚀 Mission Log' },
    { path: '/armada-map', label: '🗺️ Armada Map' },
    { path: '/brain', label: '🧠 Brain' },
    { path: '/custody', label: '🔑 Custody' },
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
                <Route path="/" element={<CommandDeck />} />
                <Route path="/captains-chat" element={<CaptainsChat />} />
                <Route path="/captain-to-captain" element={<CaptainToCaptain />} />
                <Route path="/vault-logs" element={<VaultLogs />} />
                <Route path="/mission-log" element={<MissionLog />} />
                <Route path="/armada-map" element={<ArmadaMap />} />
                <Route path="/brain" element={<BrainConsole />} />
                <Route path="/custody" element={<AdmiralKeysPanel />} />
                <Route path="/system-health" element={<SystemSelfTest />} />
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