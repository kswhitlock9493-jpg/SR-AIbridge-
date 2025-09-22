import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState({
    connection: 'Online',
    tasksInQueue: 0,
    activeAssistants: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);

  // Fetch system status
  const fetchStatus = async () => {
    const response = await fetch('http://localhost:8000/status');
    const data = await response.json();
    setSystemStatus(data);
  };

  // Fetch recent activity
  const fetchActivity = async () => {
    const response = await fetch('http://localhost:8000/activity');
    const data = await response.json();
    setRecentActivity(data);
  };

  // Create new task
  const createNewTask = async () => {
    const taskTitle = prompt('Enter new task command:');
    if (taskTitle) {
      await fetch('http://localhost:8000/tasks?title=' + encodeURIComponent(taskTitle), {
        method: 'POST'
      });
      fetchStatus(); // Refresh status
      fetchActivity(); // Refresh activity
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchActivity();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Assistant</h1>
        <p>Manage your AI helpers</p>
        <div className="connection-status">
          <span className="status-indicator"></span>
          <span>Connected</span>
        </div>
      </header>

      <nav className="navigation">
        <ul>
          <li className="active">Overview</li>
          <li>Assistants</li>
          <li>Tasks</li>
          <li>Settings</li>
        </ul>
      </nav>

      <div className="content-wrapper">
        <section className="system-status">
          <h2>System Status</h2>
          <div className="status-grid">
            <div className="status-item">
              <label>Connection:</label>
              <span className={systemStatus.connection.toLowerCase()}>
                {systemStatus.connection}
              </span>
            </div>
            <div className="status-item">
              <label>Tasks in Queue:</label>
              <span>{systemStatus.tasksInQueue}</span>
            </div>
            <div className="status-item">
              <label>Active Assistants:</label>
              <span>{systemStatus.activeAssistants}</span>
            </div>
          </div>
        </section>

        <section className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button onClick={createNewTask} className="action-button">
              Create New Task
            </button>
            <button className="action-button">
              View Assistants
            </button>
          </div>
        </section>

        <section className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.map(item => (
              <div key={item.id} className="activity-item">
                <div className="activity-action">{item.action}</div>
                <div className="activity-time">{item.time}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;