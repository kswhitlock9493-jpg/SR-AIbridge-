import React, { useState, useEffect } from 'react';
import { getGuardianStatus } from '../api';

/**
 * GuardianBanner - Always-visible notification bar showing Guardian PASS/FAIL/Unknown status
 * Polls the backend /guardian/status endpoint for live status updates
 */
const GuardianBanner = () => {
  const [guardianStatus, setGuardianStatus] = useState({
    status: 'Unknown',
    active: false,
    last_selftest: null,
    next_selftest: null
  });
  const [lastUpdated, setLastUpdated] = useState(null);

  // Poll Guardian status from backend
  useEffect(() => {
    const fetchGuardianStatus = async () => {
      try {
        const data = await getGuardianStatus();
        setGuardianStatus(data);
        setLastUpdated(new Date());
      } catch (error) {
        console.error('Guardian status fetch error:', error);
        setGuardianStatus(prev => ({ ...prev, status: 'Unknown', active: false }));
        setLastUpdated(new Date());
      }
    };

    // Initial fetch
    fetchGuardianStatus();

    // Poll every 30 seconds for live updates
    const interval = setInterval(fetchGuardianStatus, 30000);

    return () => clearInterval(interval);
  }, []);

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

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
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
        {guardianStatus.active && (
          <span className="guardian-banner-active">
            🔄 Active
          </span>
        )}
      </div>
    </div>
  );
};

export default GuardianBanner;