import { useState, useEffect } from 'react';
import { DeploymentValidator } from '../services/deployment-validator';

/**
 * PlaceholderComponent - Shown when true deployment not achieved
 * Displays a friendly message while systems are initializing
 */
const PlaceholderComponent = ({ componentName, systemsRequired = [] }) => {
  return (
    <div className="deployment-placeholder">
      <div className="placeholder-content">
        <div className="placeholder-icon">🔒</div>
        <h3>{componentName || 'Component'} - Initializing</h3>
        <p className="placeholder-message">
          This component is waiting for backend systems to be fully deployed.
        </p>
        {systemsRequired.length > 0 && (
          <div className="systems-required">
            <p className="systems-label">Required Systems:</p>
            <ul className="systems-list">
              {systemsRequired.map(system => (
                <li key={system} className="system-item">
                  <span className="system-dot">•</span> {system}
                </li>
              ))}
            </ul>
          </div>
        )}
        <p className="placeholder-status">
          Currently operating in safe placeholder mode.
        </p>
      </div>
      <style>{`
        .deployment-placeholder {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 400px;
          padding: 2rem;
          background: linear-gradient(135deg, rgba(20, 30, 48, 0.8) 0%, rgba(36, 59, 85, 0.6) 100%);
          border-radius: 8px;
          border: 1px solid rgba(100, 150, 255, 0.3);
        }
        
        .placeholder-content {
          text-align: center;
          max-width: 500px;
        }
        
        .placeholder-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
          opacity: 0.8;
        }
        
        .placeholder-content h3 {
          color: #6495ff;
          margin-bottom: 1rem;
          font-size: 1.5rem;
        }
        
        .placeholder-message {
          color: #a0b0c0;
          margin-bottom: 1.5rem;
          line-height: 1.6;
        }
        
        .systems-required {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 6px;
          padding: 1rem;
          margin: 1.5rem 0;
        }
        
        .systems-label {
          color: #8aa5c0;
          font-weight: 600;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
        }
        
        .systems-list {
          list-style: none;
          padding: 0;
          margin: 0;
          text-align: left;
        }
        
        .system-item {
          color: #90a5b5;
          padding: 0.25rem 0;
          font-size: 0.9rem;
        }
        
        .system-dot {
          color: #6495ff;
          margin-right: 0.5rem;
        }
        
        .placeholder-status {
          color: #7a8a9a;
          font-size: 0.9rem;
          font-style: italic;
          margin-top: 1.5rem;
        }
      `}</style>
    </div>
  );
};

/**
 * SovereignRevealGate - Deployment Gate Component
 * Only reveals children when true deployment is achieved
 * Wraps components that should only appear when backends are fully operational
 */
const SovereignRevealGate = ({ 
  children, 
  componentName = 'Component',
  requiredSystems = ['brh', 'healing-net', 'crypto', 'indoctrination'],
  fallback = null 
}) => {
  const [trueDeployment, setTrueDeployment] = useState(false);
  const [loading, setLoading] = useState(true);
  const [validationDetails, setValidationDetails] = useState(null);

  useEffect(() => {
    const checkTrueDeployment = async () => {
      try {
        setLoading(true);
        const deploymentStatus = await DeploymentValidator.validateTrueDeployment();
        
        setValidationDetails(deploymentStatus);
        
        // Only reveal when truly deployed
        if (deploymentStatus.trueDeployment === true) {
          setTrueDeployment(true);
          console.log(`🕵️ TRUE BRIDGE REVEALED for ${componentName}: Paranoid conditions met`);
        } else {
          setTrueDeployment(false);
          console.log(`🔒 ${componentName} in placeholder mode: ${deploymentStatus.systemsOnline}/${deploymentStatus.totalSystems} systems online`);
        }
      } catch (error) {
        console.error(`[DeploymentGate] Validation failed for ${componentName}:`, error);
        setTrueDeployment(false);
      } finally {
        setLoading(false);
      }
    };

    checkTrueDeployment();
    
    // Re-check periodically (every 2 minutes)
    const interval = setInterval(checkTrueDeployment, 120000);
    
    return () => clearInterval(interval);
  }, [componentName]);

  // Show loading state briefly
  if (loading && !validationDetails) {
    return (
      <div className="deployment-gate-loading">
        <div className="loading-spinner">⏳</div>
        <p>Validating deployment status...</p>
        <style>{`
          .deployment-gate-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            color: #a0b0c0;
          }
          .loading-spinner {
            font-size: 2rem;
            margin-bottom: 1rem;
            animation: spin 2s linear infinite;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // True deployment achieved - reveal real component
  if (trueDeployment) {
    return <>{children}</>;
  }

  // Not deployed - show placeholder or custom fallback
  if (fallback) {
    return <>{fallback}</>;
  }

  return (
    <PlaceholderComponent 
      componentName={componentName}
      systemsRequired={requiredSystems}
    />
  );
};

/**
 * DeploymentStatusBadge - Shows current deployment mode
 * Can be used in header or status bar
 */
const DeploymentStatusBadge = () => {
  const [status, setStatus] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const updateStatus = async () => {
      await DeploymentValidator.validateTrueDeployment();
      const currentStatus = DeploymentValidator.getValidationStatus();
      setStatus(currentStatus);
    };

    updateStatus();
    const interval = setInterval(updateStatus, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, []);

  if (!status) {
    return null;
  }

  const modeColors = {
    production: '#28a745',
    degraded: '#ffc107',
    development: '#6c757d',
    unknown: '#6c757d'
  };

  const modeIcons = {
    production: '✅',
    degraded: '⚠️',
    development: '🛠️',
    unknown: '❓'
  };

  return (
    <div className="deployment-status-badge">
      <div 
        className="badge-main"
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer' }}
      >
        <span className="badge-icon">{modeIcons[status.mode]}</span>
        <span className="badge-text">{status.mode.toUpperCase()}</span>
        <span 
          className="badge-indicator"
          style={{ backgroundColor: modeColors[status.mode] }}
        />
      </div>
      
      {expanded && (
        <div className="badge-details">
          <div className="badge-message">{status.message}</div>
          <div className="badge-systems">
            Systems: {status.systemsOnline || 0}/{status.totalSystems || 5}
          </div>
          {status.details && (
            <div className="badge-systems-list">
              {Object.entries(status.details).map(([system, online]) => (
                <div key={system} className="system-status">
                  <span className={online ? 'online' : 'offline'}>
                    {online ? '●' : '○'}
                  </span>
                  <span>{system.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <style>{`
        .deployment-status-badge {
          position: relative;
          display: inline-block;
        }
        
        .badge-main {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.25rem 0.75rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 4px;
          font-size: 0.85rem;
        }
        
        .badge-icon {
          font-size: 1rem;
        }
        
        .badge-text {
          font-weight: 600;
          color: #e0e0e0;
        }
        
        .badge-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .badge-details {
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 0.5rem;
          background: rgba(20, 30, 48, 0.95);
          border: 1px solid rgba(100, 150, 255, 0.3);
          border-radius: 6px;
          padding: 1rem;
          min-width: 250px;
          z-index: 1000;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        .badge-message {
          color: #a0b0c0;
          margin-bottom: 0.75rem;
          font-size: 0.9rem;
        }
        
        .badge-systems {
          color: #8090a0;
          font-size: 0.85rem;
          margin-bottom: 0.75rem;
        }
        
        .badge-systems-list {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .system-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #90a0b0;
        }
        
        .system-status .online {
          color: #28a745;
        }
        
        .system-status .offline {
          color: #6c757d;
        }
      `}</style>
    </div>
  );
};

export { SovereignRevealGate, DeploymentStatusBadge, PlaceholderComponent };
export default SovereignRevealGate;
