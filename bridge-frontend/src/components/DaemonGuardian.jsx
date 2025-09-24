import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useBridge } from '../hooks/useBridge';
import { 
  getSystemHealth, 
  getGuardianStatus, 
  runGuardianSelftest, 
  activateGuardian,
  runSelfTest,
  getSystemMetrics 
} from '../api';

/**
 * DaemonGuardian - Enhanced autonomous system guardian for SR-AIbridge
 * Integrates with unified bridge state and provides advanced monitoring
 */
const DaemonGuardian = ({ onSystemAlert, onGuardianActivate }) => {
  const { 
    handleSystemAlert, 
    handleGuardianActivate, 
    setGuardianActive,
    connected,
    sendMessage 
  } = useBridge();

  const [guardianStatus, setGuardianStatus] = useState({
    active: false,
    lastHeartbeat: null,
    health: 'unknown',
    alerts: [],
    defenseMode: false,
    repairAttempts: 0,
    metrics: {},
    selfTestStatus: 'idle'
  });

  const heartbeatInterval = useRef(null);
  const healthCheckInterval = useRef(null);
  const selfTestInterval = useRef(null);
  
  // Configuration
  const heartbeatFrequency = 15000; // 15 seconds
  const healthCheckFrequency = 45000; // 45 seconds
  const selfTestFrequency = 300000; // 5 minutes

  /**
   * Log guardian activity with bridge integration
   */
  const logActivity = useCallback((level, message, details = null) => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      level,
      message,
      details,
      source: 'DaemonGuardian'
    };
    
    // setLogs(prevLogs => [logEntry, ...prevLogs.slice(0, 99)]); // Keep last 100 logs - removed unused state
    console.log(`[DaemonGuardian] ${level.toUpperCase()}: ${message}`, details || '');
    
    // Send critical alerts to bridge system
    if (level === 'error' || level === 'critical') {
      const alert = {
        id: logEntry.id,
        type: 'guardian_alert',
        level,
        message,
        details,
        timestamp: logEntry.timestamp
      };
      
      if (handleSystemAlert) {
        handleSystemAlert(alert);
      }
      if (onSystemAlert) {
        onSystemAlert(alert);
      }
    }
  }, [handleSystemAlert, onSystemAlert]);

  /**
   * Perform system heartbeat with enhanced monitoring
   */
  const performHeartbeat = useCallback(async () => {
    try {
      const timestamp = new Date().toISOString();
      const metrics = await getSystemMetrics().catch(() => ({}));
      
      setGuardianStatus(prev => ({
        ...prev,
        active: true,
        lastHeartbeat: timestamp,
        metrics
      }));

      // Send heartbeat via WebSocket if connected
      if (connected && sendMessage) {
        sendMessage({
          type: 'guardian_heartbeat',
          timestamp,
          metrics,
          status: 'active'
        });
      }

      logActivity('info', 'Guardian heartbeat completed', { timestamp, metrics });
      
    } catch (error) {
      logActivity('error', 'Heartbeat failed', { error: error.message });
      setGuardianStatus(prev => ({
        ...prev,
        health: 'degraded',
        alerts: [...prev.alerts, `Heartbeat failed: ${error.message}`]
      }));
    }
  }, [connected, sendMessage, logActivity]);

  /**
   * Perform comprehensive health check
   */
  const performHealthCheck = useCallback(async () => {
    try {
      logActivity('info', 'Starting comprehensive health check');
      
      const [systemHealth, guardianHealth] = await Promise.all([
        getSystemHealth().catch(() => ({ status: 'unknown' })),
        getGuardianStatus().catch(() => ({ status: 'unknown' }))
      ]);

      const overallHealth = systemHealth.status === 'healthy' && guardianHealth.status === 'active' ? 'healthy' : 'degraded';
      
      setGuardianStatus(prev => ({
        ...prev,
        health: overallHealth,
        lastHealthCheck: new Date().toISOString()
      }));

      logActivity('info', 'Health check completed', { 
        systemHealth: systemHealth.status, 
        guardianHealth: guardianHealth.status,
        overallHealth 
      });

      // Activate guardian mode if system health is critical
      if (systemHealth.status === 'critical' || guardianHealth.status === 'error') {
        await activateGuardianDefense('Critical system health detected');
      }

    } catch (error) {
      logActivity('error', 'Health check failed', { error: error.message });
      setGuardianStatus(prev => ({
        ...prev,
        health: 'error',
        alerts: [...prev.alerts, `Health check failed: ${error.message}`]
      }));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Perform autonomous self-test
   */
  const performSelfTest = useCallback(async () => {
    try {
      setGuardianStatus(prev => ({ ...prev, selfTestStatus: 'running' }));
      logActivity('info', 'Starting autonomous self-test');

      const [systemTest, guardianTest] = await Promise.all([
        runSelfTest().catch(() => ({ status: 'failed' })),
        runGuardianSelftest().catch(() => ({ status: 'failed' }))
      ]);

      const testsPassed = systemTest.status === 'passed' && guardianTest.status === 'passed';
      
      setGuardianStatus(prev => ({
        ...prev,
        selfTestStatus: testsPassed ? 'passed' : 'failed',
        lastSelfTest: new Date().toISOString()
      }));

      logActivity(testsPassed ? 'info' : 'warning', 'Self-test completed', {
        systemTest: systemTest.status,
        guardianTest: guardianTest.status,
        overall: testsPassed ? 'passed' : 'failed'
      });

      if (!testsPassed) {
        await activateGuardianDefense('Self-test failures detected');
      }

    } catch (error) {
      setGuardianStatus(prev => ({ ...prev, selfTestStatus: 'error' }));
      logActivity('error', 'Self-test failed', { error: error.message });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Activate guardian defense mode
   */
  const activateGuardianDefense = useCallback(async (reason = 'System defense required') => {
    try {
      logActivity('critical', 'Activating Guardian Defense Mode', { reason });
      
      setGuardianStatus(prev => ({
        ...prev,
        defenseMode: true
      }));

      // Notify bridge system
      if (handleGuardianActivate) {
        handleGuardianActivate(reason);
      }
      if (onGuardianActivate) {
        onGuardianActivate(reason);
      }
      
      // Update global guardian state
      if (setGuardianActive) {
        setGuardianActive(true);
      }

      // Send activation signal via WebSocket
      if (connected && sendMessage) {
        sendMessage({
          type: 'guardian_activated',
          reason,
          timestamp: new Date().toISOString()
        });
      }

      // Call backend guardian activation
      await activateGuardian().catch(err => 
        logActivity('error', 'Failed to activate backend guardian', { error: err.message })
      );

    } catch (error) {
      logActivity('error', 'Failed to activate guardian defense', { error: error.message });
    }
  }, [handleGuardianActivate, onGuardianActivate, setGuardianActive, connected, sendMessage, logActivity]);

  /**
   * Initialize guardian daemon
   */
  const initializeDaemon = useCallback(() => {
    logActivity('info', 'Initializing DaemonGuardian');
    
    // Start heartbeat
    heartbeatInterval.current = setInterval(performHeartbeat, heartbeatFrequency);
    
    // Start health checks
    healthCheckInterval.current = setInterval(performHealthCheck, healthCheckFrequency);
    
    // Start periodic self-tests
    selfTestInterval.current = setInterval(performSelfTest, selfTestFrequency);
    
    // Initial checks
    performHeartbeat();
    performHealthCheck();
    
    setGuardianStatus(prev => ({ ...prev, active: true }));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [performHeartbeat, performHealthCheck, performSelfTest]);

  /**
   * Shutdown guardian daemon
   */
  const shutdownDaemon = useCallback(() => {
    logActivity('info', 'Shutting down DaemonGuardian');
    
    if (heartbeatInterval.current) {
      clearInterval(heartbeatInterval.current);
    }
    if (healthCheckInterval.current) {
      clearInterval(healthCheckInterval.current);
    }
    if (selfTestInterval.current) {
      clearInterval(selfTestInterval.current);
    }
    
    setGuardianStatus(prev => ({ ...prev, active: false }));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Initialize on mount
  useEffect(() => {
    initializeDaemon();
    return shutdownDaemon;
  }, [initializeDaemon, shutdownDaemon]);

  // Manual controls for debugging/administration
  const manualHealthCheck = () => performHealthCheck();
  const manualSelfTest = () => performSelfTest();
  const manualGuardianActivation = () => activateGuardianDefense('Manual activation');

  // Component render - minimal UI for status display
  return (
    <div className="daemon-guardian" style={{ display: 'none' }}>
      {/* Hidden component - operates in background */}
      {/* Status can be accessed via useBridge hook by other components */}
      <div className="guardian-status">
        <span className={`status-indicator ${guardianStatus.active ? 'active' : 'inactive'}`}>
          {guardianStatus.active ? '🛡️' : '⏸️'}
        </span>
        <span className="status-text">
          Guardian: {guardianStatus.active ? 'Active' : 'Inactive'}
        </span>
        {guardianStatus.health && (
          <span className={`health-indicator ${guardianStatus.health}`}>
            Health: {guardianStatus.health}
          </span>
        )}
      </div>
      
      {/* Dev controls - only visible in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="guardian-controls">
          <button onClick={manualHealthCheck}>Health Check</button>
          <button onClick={manualSelfTest}>Self Test</button>
          <button onClick={manualGuardianActivation}>Activate Guardian</button>
        </div>
      )}
    </div>
  );
};

export default DaemonGuardian;