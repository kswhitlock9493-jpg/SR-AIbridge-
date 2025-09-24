import React, { useState, useEffect } from 'react';
import { getGuardianStatus, runGuardianSelftest, activateGuardian } from '../api';

/**
 * GuardianBanner - Always-visible notification bar showing Guardian PASS/FAIL/Unknown status
 * Polls the backend /guardian/status endpoint for live status updates every 5 seconds
 */
const GuardianBanner = () => {
  const [guardianStatus, setGuardianStatus] = useState({
    status: 'Unknown',
    active: false,
    last_selftest: null,
    last_action: null,
    last_result: null,
    heartbeat: null,
    next_selftest: null
  });
  
  const [loading, setLoading] = useState({
    selftest: false,
    activate: false
  });
  
  const [error, setError] = useState(null);

  // Poll Guardian status from backend every 5 seconds
  useEffect(() => {
    const fetchGuardianStatus = async () => {
      try {
        const data = await getGuardianStatus();
        setGuardianStatus(data);
        setError(null); // Clear any previous errors
      } catch (error) {
        console.error('Guardian status fetch error:', error);
        setError('Failed to fetch Guardian status');
        setGuardianStatus(prev => ({ ...prev, status: 'Unknown', active: false }));
      }
    };

    // Initial fetch
    fetchGuardianStatus();

    // Poll every 5 seconds for live updates
    const interval = setInterval(fetchGuardianStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleRunSelfTest = async () => {
    setLoading(prev => ({ ...prev, selftest: true }));
    setError(null);
    
    try {
      const result = await runGuardianSelftest();
      console.log('Self-test result:', result);
      // Refresh status immediately after self-test
      const updatedStatus = await getGuardianStatus();
      setGuardianStatus(updatedStatus);
    } catch (error) {
      console.error('Self-test error:', error);
      setError('Failed to run self-test');
    } finally {
      setLoading(prev => ({ ...prev, selftest: false }));
    }
  };

  const handleActivateGuardian = async () => {
    setLoading(prev => ({ ...prev, activate: true }));
    setError(null);
    
    try {
      const result = await activateGuardian();
      console.log('Activation result:', result);
      // Refresh status immediately after activation
      const updatedStatus = await getGuardianStatus();
      setGuardianStatus(updatedStatus);
    } catch (error) {
      console.error('Activation error:', error);
      setError('Failed to activate Guardian');
    } finally {
      setLoading(prev => ({ ...prev, activate: false }));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PASS': return '✅';
      case 'FAIL': return '❌';
      default: return '❓';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'PASS': return 'guardian-banner-pass';
      case 'FAIL': return 'guardian-banner-fail';
      default: return 'guardian-banner-unknown';
    }
  };

  const getTimeSince = (timestamp) => {
    if (!timestamp) return '';
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ${diffMins % 60}m ago`;
  };

  return (
    <div className={`guardian-banner ${getStatusClass(guardianStatus.status)}`}>
      <div className="guardian-banner-content">
        <span className="guardian-banner-icon">
          🛡️ {getStatusIcon(guardianStatus.status)}
        </span>
        <span className="guardian-banner-text">
          <strong>GUARDIAN:</strong> {guardianStatus.status}
        </span>
        <span className="guardian-banner-timestamp">
          {guardianStatus.last_selftest ? (
            <>
              Last Test: {getTimeSince(guardianStatus.last_selftest)}
            </>
          ) : (
            'No test data'
          )}
        </span>
        <span className="guardian-banner-heartbeat">
          {guardianStatus.heartbeat ? (
            <>
              💓 {getTimeSince(guardianStatus.heartbeat)}
            </>
          ) : (
            '💔 No heartbeat'
          )}
        </span>
        <span className="guardian-banner-action">
          {guardianStatus.last_action && guardianStatus.last_result ? (
            <>
              Last: {guardianStatus.last_action} ({guardianStatus.last_result})
            </>
          ) : null}
        </span>
        {guardianStatus.active && (
          <span className="guardian-banner-active">
            🔄 Active
          </span>
        )}
      </div>
      
      <div className="guardian-banner-controls">
        <button 
          onClick={handleRunSelfTest} 
          disabled={loading.selftest}
          className="guardian-button guardian-button-test"
          title="Run Guardian Self-Test"
        >
          {loading.selftest ? '⏳ Testing...' : '🔍 Run Self-Test'}
        </button>
        <button 
          onClick={handleActivateGuardian} 
          disabled={loading.activate}
          className="guardian-button guardian-button-activate"
          title="Activate Guardian"
        >
          {loading.activate ? '⏳ Activating...' : '⚡ Activate Guardian'}
        </button>
      </div>
      
      {error && (
        <div className="guardian-banner-error">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
};

export default GuardianBanner;