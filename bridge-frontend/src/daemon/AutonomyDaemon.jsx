import React, { useState, useEffect, useCallback, useRef } from 'react';
import { getSystemHealth, runSelfTest, getSystemMetrics } from '../api';

/**
 * AutonomyDaemon - Global heartbeat system for SR-AIbridge
 * Provides self-test, self-repair, self-defense (Guardian banner), and self-logging
 */
const AutonomyDaemon = ({ onSystemAlert, onGuardianActivate }) => {
  const [daemonStatus, setDaemonStatus] = useState({
    active: false,
    lastHeartbeat: null,
    health: 'unknown',
    alerts: [],
    defenseMode: false,
    repairAttempts: 0,
    metrics: {}
  });

  const [guardianMode, setGuardianMode] = useState(false);
  const [logs, setLogs] = useState([]);
  const heartbeatInterval = useRef(null);
  const healthCheckInterval = useRef(null);
  const heartbeatFrequency = 30000; // 30 seconds
  const healthCheckFrequency = 60000; // 60 seconds

  /**
   * Log daemon activity
   */
  const logActivity = useCallback((level, message, details = null) => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      level,
      message,
      details,
      source: 'AutonomyDaemon'
    };
    
    setLogs(prevLogs => [logEntry, ...prevLogs.slice(0, 49)]); // Keep last 50 logs
    console.log(`[AutonomyDaemon] ${level.toUpperCase()}: ${message}`, details || '');
  }, []);

  /**
   * Perform system heartbeat
   */
  const performHeartbeat = useCallback(async () => {
    try {
      const timestamp = new Date().toISOString();
      setDaemonStatus(prev => ({
        ...prev,
        lastHeartbeat: timestamp,
        active: true
      }));

      logActivity('info', 'Heartbeat pulse sent', { timestamp });
      return true;
    } catch (error) {
      logActivity('error', 'Heartbeat failed', error.message);
      return false;
    }
  }, [logActivity]);

  /**
   * Perform system health check
   */
  const performHealthCheck = useCallback(async () => {
    try {
      const [healthData, metricsData] = await Promise.all([
        getSystemHealth().catch(() => ({ status: 'degraded', errors: ['Health endpoint unreachable'] })),
        getSystemMetrics().catch(() => ({ cpu: 0, memory: 0, connections: 0 }))
      ]);

      // Adapt /status endpoint response to health check format
      const isHealthy = healthData.agents_online !== undefined && healthData.admiral !== undefined;
      const derivedStatus = isHealthy ? 'healthy' : 'degraded';
      const hasErrors = healthData.errors && healthData.errors.length > 0;

      setDaemonStatus(prev => ({
        ...prev,
        health: derivedStatus,
        metrics: {
          ...metricsData,
          agents_online: healthData.agents_online || 0,
          active_missions: healthData.active_missions || 0,
          total_agents: healthData.total_agents || 0
        },
        alerts: hasErrors ? healthData.errors : []
      }));

      if (!isHealthy) {
        logActivity('warning', 'System health degraded', {
          status: derivedStatus,
          errors: healthData.errors
        });
      } else {
        logActivity('info', 'System health check passed', {
          status: derivedStatus,
          agents_online: healthData.agents_online,
          active_missions: healthData.active_missions
        });
      }

      return isHealthy;
    } catch (error) {
      logActivity('error', 'Health check failed', error.message);
      setDaemonStatus(prev => ({
        ...prev,
        health: 'error',
        alerts: [`Health check error: ${error.message}`]
      }));
      return false;
    }
  }, [logActivity]);

  /**
   * Activate Guardian Mode - enhanced defense protocols
   */
  const activateGuardianMode = useCallback(async (reason) => {
    if (guardianMode) return; // Already active

    setGuardianMode(true);
    logActivity('warning', 'Guardian Mode ACTIVATED', { reason });

    // Notify parent component
    if (onGuardianActivate) {
      onGuardianActivate(reason);
    }

    // Auto-deactivate after 5 minutes unless manually extended
    setTimeout(() => {
      setGuardianMode(prevMode => {
        if (prevMode) {
          logActivity('info', 'Guardian Mode deactivated', { reason: 'Auto-timeout' });
          return false;
        }
        return prevMode;
      });
    }, 300000); // 5 minutes
  }, [guardianMode, logActivity, onGuardianActivate]);

  /**
   * Deactivate Guardian Mode
   */
  const deactivateGuardianMode = useCallback((reason) => {
    setGuardianMode(false);
    logActivity('info', 'Guardian Mode deactivated', { reason });
  }, [logActivity]);

  /**
   * Run comprehensive self-test
   */
  const runComprehensiveSelfTest = useCallback(async () => {
    try {
      logActivity('info', 'Starting comprehensive self-test');

      const testResult = await runSelfTest();
      
      if (testResult.success) {
        logActivity('info', 'Self-test completed successfully', testResult);
      } else {
        logActivity('warning', 'Self-test found issues', testResult);
        
        // Alert system if critical issues found
        if (testResult.critical) {
          await activateGuardianMode('Critical issues found in self-test');
        }
      }

      return testResult;
    } catch (error) {
      logActivity('error', 'Self-test failed to execute', error.message);
      return { success: false, error: error.message };
    }
  }, [logActivity, activateGuardianMode]);

  /**
   * Start daemon operations
   */
  const startDaemon = useCallback(() => {
    if (daemonStatus.active) return;

    logActivity('info', 'Starting Autonomy Daemon');

    // Start heartbeat
    heartbeatInterval.current = setInterval(performHeartbeat, heartbeatFrequency);
    
    // Start health checks
    healthCheckInterval.current = setInterval(performHealthCheck, healthCheckFrequency);

    // Initial health check
    performHealthCheck();
    
    // Initial heartbeat
    performHeartbeat();

    setDaemonStatus(prev => ({ ...prev, active: true }));
  }, [daemonStatus.active, performHeartbeat, performHealthCheck, logActivity]);

  /**
   * Stop daemon operations
   */
  const stopDaemon = useCallback(() => {
    if (!daemonStatus.active) return;

    logActivity('info', 'Stopping Autonomy Daemon');

    if (heartbeatInterval.current) {
      clearInterval(heartbeatInterval.current);
      heartbeatInterval.current = null;
    }

    if (healthCheckInterval.current) {
      clearInterval(healthCheckInterval.current);
      healthCheckInterval.current = null;
    }

    setDaemonStatus(prev => ({
      ...prev,
      active: false,
      lastHeartbeat: null
    }));
  }, [daemonStatus.active, logActivity]);

  /**
   * Auto-start daemon on mount
   */
  useEffect(() => {
    startDaemon();

    // Cleanup on unmount
    return () => {
      stopDaemon();
    };
  }, [startDaemon, stopDaemon]);

  /**
   * Handle system alerts
   */
  useEffect(() => {
    if (daemonStatus.alerts.length > 0 && onSystemAlert) {
      onSystemAlert(daemonStatus.alerts);
    }
  }, [daemonStatus.alerts, onSystemAlert]);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Get status color based on health
  const getStatusColor = (health) => {
    switch (health) {
      case 'healthy': return '#00ff00';
      case 'degraded': return '#ffaa00';
      case 'critical': return '#ff4444';
      case 'error': return '#ff0000';
      default: return '#888';
    }
  };

  return (
    <div className="autonomy-daemon">
      {/* Guardian Mode Banner */}
      {guardianMode && (
        <div className="guardian-banner">
          <div className="guardian-content">
            <span className="guardian-icon">🛡️</span>
            <span className="guardian-text">GUARDIAN MODE ACTIVE</span>
            <span className="guardian-status">Enhanced Defense Protocols Engaged</span>
            <button 
          onClick={() => deactivateGuardianMode('Manual')} 
          className="guardian-dismiss"
        >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Daemon Status Display */}
      <div className="daemon-status">
        <div className="status-row">
          <span className="status-label">Autonomy Daemon:</span>
          <span className={`status-value ${daemonStatus.active ? 'active' : 'inactive'}`}>
            {daemonStatus.active ? '🟢 ACTIVE' : '🔴 INACTIVE'}
          </span>
        </div>
        
        <div className="status-row">
          <span className="status-label">System Health:</span>
          <span 
            className="status-value" 
            style={{ color: getStatusColor(daemonStatus.health) }}
          >
            {daemonStatus.health.toUpperCase()}
          </span>
        </div>
        
        {daemonStatus.lastHeartbeat && (
          <div className="status-row">
            <span className="status-label">Last Heartbeat:</span>
            <span className="status-value">
              {formatTimestamp(daemonStatus.lastHeartbeat)}
            </span>
          </div>
        )}

        {daemonStatus.alerts.length > 0 && (
          <div className="status-alerts">
            <span className="alerts-label">System Alerts:</span>
            <ul className="alerts-list">
              {daemonStatus.alerts.map((alert, index) => (
                <li key={index} className="alert-item">⚠️ {alert}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Daemon Controls */}
      <div className="daemon-controls">
        <button 
          onClick={startDaemon} 
          disabled={daemonStatus.active}
          className="control-button start"
        >
          Start Daemon
        </button>
        <button 
          onClick={stopDaemon} 
          disabled={!daemonStatus.active}
          className="control-button stop"
        >
          Stop Daemon
        </button>
        <button 
          onClick={runComprehensiveSelfTest}
          className="control-button test"
        >
          Run Self-Test
        </button>
        <button 
          onClick={() => activateGuardianMode('Manual activation')}
          disabled={guardianMode}
          className="control-button guardian"
        >
          Activate Guardian
        </button>
      </div>

      {/* Recent Daemon Logs */}
      <div className="daemon-logs">
        <h4>Recent Daemon Activity</h4>
        <div className="logs-list">
          {logs.slice(0, 10).map((log) => (
            <div key={log.id} className={`log-entry level-${log.level}`}>
              <span className="log-timestamp">{formatTimestamp(log.timestamp)}</span>
              <span className="log-level">{log.level.toUpperCase()}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AutonomyDaemon;