import React, { useState } from 'react';
import Dashboard from './components/Dashboard.jsx';
import CaptainsChat from './components/CaptainsChat.jsx';
import CaptainToCaptain from './components/CaptainToCaptain.jsx';
import VaultLogs from './components/VaultLogs.jsx';
import MissionLog from './components/MissionLog.jsx';
import ArmadaMap from './components/ArmadaMap.jsx';
import SystemSelfTest from './components/SystemSelfTest.jsx';
import './styles.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard', component: Dashboard },
    { id: 'captains-chat', label: '💬 Captains Chat', component: CaptainsChat },
    { id: 'captain-to-captain', label: '⚔️ Captain-to-Captain', component: CaptainToCaptain },
    { id: 'vault-logs', label: '📜 Vault Logs', component: VaultLogs },
    { id: 'mission-log', label: '🚀 Mission Log', component: MissionLog },
    { id: 'armada-map', label: '🗺️ Armada Map', component: ArmadaMap },
    { id: 'system-health', label: '🔍 System Health', component: SystemSelfTest }
  ];

  const renderTabContent = () => {
    const activeTabData = tabs.find(tab => tab.id === activeTab);
    if (!activeTabData) return null;
    
    const Component = activeTabData.component;
    return <Component />;
  };

  return (
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

      <nav className="app-navigation">
        <div className="nav-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="app-content">
        <div className="content-wrapper">
          {renderTabContent()}
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <span>SR-AIbridge v2.0.0 | Production Ready | All Endpoints Wired</span>
          <span className="footer-status">
            Backend: /status | /missions | /vault/logs | /armada/status | /captains/messages | /health
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;