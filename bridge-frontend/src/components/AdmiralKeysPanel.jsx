import { useState, useEffect } from 'react';

const AdmiralKeysPanel = () => {
  const [custodyState, setCustodyState] = useState({
    keys: [],
    admiralInfo: null,
    loading: true,
    error: null,
    status: null
  });

  const [showSignModal, setShowSignModal] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [signPayload, setSignPayload] = useState('');
  const [verifyEnvelope, setVerifyEnvelope] = useState('');
  const [operationResult, setOperationResult] = useState(null);

  const API_BASE = 'http://localhost:8000';

  useEffect(() => {
    fetchCustodyData();
  }, []);

  const fetchCustodyData = async () => {
    try {
      setCustodyState(prev => ({ ...prev, loading: true, error: null }));
      
      // Fetch custody status, keys, and admiral info in parallel
      const [statusRes, keysRes, admiralRes] = await Promise.all([
        fetch(`${API_BASE}/custody/status`),
        fetch(`${API_BASE}/custody/keys`),
        fetch(`${API_BASE}/custody/admiral`).catch(() => ({ ok: false })) // Admiral keys might not exist
      ]);

      if (!statusRes.ok || !keysRes.ok) {
        throw new Error('Failed to fetch custody data');
      }

      const status = await statusRes.json();
      const keys = await keysRes.json();
      const admiralInfo = admiralRes.ok ? await admiralRes.json() : null;

      setCustodyState(prev => ({
        ...prev,
        status,
        keys,
        admiralInfo: admiralInfo?.admiral_info || null,
        loading: false
      }));
    } catch (error) {
      console.error('Custody data fetch error:', error);
      setCustodyState(prev => ({
        ...prev,
        error: error.message,
        loading: false
      }));
    }
  };

  const rotateAdmiralKeys = async () => {
    if (!confirm('⚠️ This will replace the current Admiral keys. Are you sure?')) {
      return;
    }

    try {
      setCustodyState(prev => ({ ...prev, loading: true }));
      
      const response = await fetch(`${API_BASE}/custody/admiral/rotate`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Key rotation failed');

      const result = await response.json();
      setOperationResult({
        type: 'success',
        message: 'Admiral keys rotated successfully',
        details: result
      });

      fetchCustodyData(); // Refresh data
    } catch (error) {
      setOperationResult({
        type: 'error',
        message: error.message
      });
      setCustodyState(prev => ({ ...prev, loading: false }));
    }
  };

  const signPayloadAction = async () => {
    try {
      const payload = JSON.parse(signPayload);
      
      const response = await fetch(`${API_BASE}/custody/sign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payload,
          signer_name: 'admiral'
        })
      });

      if (!response.ok) throw new Error('Signing failed');

      const result = await response.json();
      setOperationResult({
        type: 'success',
        message: 'Payload signed successfully',
        details: result.signed_envelope
      });

      setShowSignModal(false);
      setSignPayload('');
    } catch (error) {
      setOperationResult({
        type: 'error',
        message: error.message
      });
    }
  };

  const verifySignatureAction = async () => {
    try {
      const envelope = JSON.parse(verifyEnvelope);
      
      const response = await fetch(`${API_BASE}/custody/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          signed_envelope: envelope
        })
      });

      if (!response.ok) throw new Error('Verification failed');

      const result = await response.json();
      setOperationResult({
        type: result.valid ? 'success' : 'warning',
        message: result.valid ? 'Signature is valid' : 'Signature is invalid',
        details: result
      });

      setShowVerifyModal(false);
      setVerifyEnvelope('');
    } catch (error) {
      setOperationResult({
        type: 'error',
        message: error.message
      });
    }
  };

  const createDockDayDrop = async () => {
    if (!confirm('Create a Dock-Day drop? This will export the entire brain state.')) {
      return;
    }

    try {
      setCustodyState(prev => ({ ...prev, loading: true }));
      
      const response = await fetch(`${API_BASE}/custody/dock-day-drop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          include_database: true,
          include_keys: false,
          compress: true
        })
      });

      if (!response.ok) throw new Error('Dock-Day drop creation failed');

      const result = await response.json();
      setOperationResult({
        type: 'success',
        message: 'Dock-Day drop created successfully',
        details: result.drop_info
      });

      setCustodyState(prev => ({ ...prev, loading: false }));
    } catch (error) {
      setOperationResult({
        type: 'error',
        message: error.message
      });
      setCustodyState(prev => ({ ...prev, loading: false }));
    }
  };

  if (custodyState.loading && !custodyState.status) {
    return (
      <div className="custody-panel loading">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <p>Loading Custody Panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="custody-panel">
      <div className="custody-header">
        <div className="header-title">
          <h2>🔑 Admiral Keys & Custody</h2>
          <p>Cryptographic key management and custody operations</p>
        </div>
        <div className="header-actions">
          <button 
            className="action-btn primary"
            onClick={() => setShowSignModal(true)}
            disabled={!custodyState.admiralInfo}
          >
            🔐 Sign Payload
          </button>
          <button 
            className="action-btn secondary"
            onClick={() => setShowVerifyModal(true)}
          >
            ✅ Verify Signature
          </button>
          <button 
            className="action-btn refresh"
            onClick={fetchCustodyData}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {custodyState.error && (
        <div className="error-banner">
          <span>❌ {custodyState.error}</span>
          <button onClick={() => setCustodyState(prev => ({ ...prev, error: null }))}>
            ✕
          </button>
        </div>
      )}

      {operationResult && (
        <div className={`result-banner ${operationResult.type}`}>
          <div className="result-content">
            <span className="result-message">
              {operationResult.type === 'success' && '✅'}
              {operationResult.type === 'warning' && '⚠️'}
              {operationResult.type === 'error' && '❌'}
              {' ' + operationResult.message}
            </span>
            {operationResult.details && (
              <details className="result-details">
                <summary>View Details</summary>
                <pre>{JSON.stringify(operationResult.details, null, 2)}</pre>
              </details>
            )}
          </div>
          <button onClick={() => setOperationResult(null)}>✕</button>
        </div>
      )}

      {/* Custody Status */}
      {custodyState.status && (
        <div className="custody-status">
          <div className="status-card">
            <div className="status-header">
              <h3>🛡️ Custody Status</h3>
              <div className={`status-indicator ${custodyState.status.status}`}>
                {custodyState.status.status}
              </div>
            </div>
            <div className="status-details">
              <div className="status-item">
                <span className="label">Available Keys:</span>
                <span className="value">{custodyState.status.available_keys}</span>
              </div>
              <div className="status-item">
                <span className="label">Admiral Keys:</span>
                <span className={`value ${custodyState.status.admiral_keys_present ? 'success' : 'warning'}`}>
                  {custodyState.status.admiral_keys_present ? 'Present' : 'Missing'}
                </span>
              </div>
              <div className="status-item">
                <span className="label">Signing Ready:</span>
                <span className={`value ${custodyState.status.signing_ready ? 'success' : 'error'}`}>
                  {custodyState.status.signing_ready ? 'Ready' : 'Not Ready'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Admiral Key Information */}
      {custodyState.admiralInfo ? (
        <div className="admiral-keys">
          <div className="key-card admiral">
            <div className="key-header">
              <h3>👑 Admiral Keys</h3>
              <button 
                className="action-btn warning"
                onClick={rotateAdmiralKeys}
              >
                🔄 Rotate Keys
              </button>
            </div>
            <div className="key-details">
              <div className="key-item">
                <span className="label">Name:</span>
                <span className="value">{custodyState.admiralInfo.name}</span>
              </div>
              <div className="key-item">
                <span className="label">Created:</span>
                <span className="value">
                  {new Date(custodyState.admiralInfo.created_at).toLocaleString()}
                </span>
              </div>
              <div className="key-item">
                <span className="label">Public Key:</span>
                <div className="key-display">
                  <code className="public-key">
                    {custodyState.admiralInfo.public_key}
                  </code>
                  <button 
                    className="copy-btn"
                    onClick={() => navigator.clipboard.writeText(custodyState.admiralInfo.public_key)}
                    title="Copy to clipboard"
                  >
                    📋
                  </button>
                </div>
              </div>
              <div className="key-item">
                <span className="label">Hex:</span>
                <div className="key-display">
                  <code className="key-hex">
                    {custodyState.admiralInfo.public_key_hex}
                  </code>
                  <button 
                    className="copy-btn"
                    onClick={() => navigator.clipboard.writeText(custodyState.admiralInfo.public_key_hex)}
                    title="Copy to clipboard"
                  >
                    📋
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="admiral-keys missing">
          <div className="key-card warning">
            <div className="key-header">
              <h3>⚠️ Admiral Keys Missing</h3>
            </div>
            <div className="key-message">
              <p>No Admiral keys found. Initialize keys to enable signing operations.</p>
              <button 
                className="action-btn primary"
                onClick={() => {
                  // This would typically call an initialize endpoint
                  alert('Please run the key rotation ritual to initialize Admiral keys.');
                }}
              >
                🔧 Initialize Keys
              </button>
            </div>
          </div>
        </div>
      )}

      {/* All Keys List */}
      {custodyState.keys.length > 0 && (
        <div className="all-keys">
          <div className="keys-header">
            <h3>🗝️ All Keys ({custodyState.keys.length})</h3>
          </div>
          <div className="keys-list">
            {custodyState.keys.map(key => (
              <div key={key.name} className={`key-item ${key.name === 'admiral' ? 'admiral' : ''}`}>
                <div className="key-info">
                  <div className="key-name">
                    {key.name === 'admiral' && '👑 '}
                    {key.name}
                  </div>
                  <div className="key-created">
                    Created: {new Date(key.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="key-actions">
                  <button 
                    className="copy-btn small"
                    onClick={() => navigator.clipboard.writeText(key.public_key_hex)}
                    title="Copy hex"
                  >
                    📋 Hex
                  </button>
                  <button 
                    className="copy-btn small"
                    onClick={() => navigator.clipboard.writeText(key.public_key)}
                    title="Copy base64"
                  >
                    📋 B64
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dock-Day Operations */}
      <div className="dock-day-operations">
        <div className="operations-header">
          <h3>🚢 Dock-Day Operations</h3>
        </div>
        <div className="operations-grid">
          <button 
            className="operation-btn"
            onClick={createDockDayDrop}
            disabled={!custodyState.admiralInfo}
          >
            <div className="operation-icon">📦</div>
            <div className="operation-text">
              <div className="operation-title">Create Drop</div>
              <div className="operation-desc">Export signed brain state</div>
            </div>
          </button>
        </div>
      </div>

      {/* Sign Payload Modal */}
      {showSignModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>🔐 Sign Payload</h3>
              <button 
                className="modal-close"
                onClick={() => setShowSignModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Payload (JSON) *</label>
                <textarea
                  value={signPayload}
                  onChange={(e) => setSignPayload(e.target.value)}
                  placeholder='{"message": "Hello, sovereign world!", "timestamp": "2024-01-01T00:00:00Z"}'
                  rows={6}
                  required
                />
              </div>
              <p className="modal-note">
                The payload will be signed with the Admiral key and include cryptographic attestation.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                className="action-btn secondary"
                onClick={() => setShowSignModal(false)}
              >
                Cancel
              </button>
              <button 
                className="action-btn primary"
                onClick={signPayloadAction}
                disabled={!signPayload.trim()}
              >
                🔐 Sign Payload
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Verify Signature Modal */}
      {showVerifyModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>✅ Verify Signature</h3>
              <button 
                className="modal-close"
                onClick={() => setShowVerifyModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Signed Envelope (JSON) *</label>
                <textarea
                  value={verifyEnvelope}
                  onChange={(e) => setVerifyEnvelope(e.target.value)}
                  placeholder='{"payload": {...}, "metadata": {...}, "signature": {...}}'
                  rows={8}
                  required
                />
              </div>
              <p className="modal-note">
                Paste the complete signed envelope including payload, metadata, and signature.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                className="action-btn secondary"
                onClick={() => setShowVerifyModal(false)}
              >
                Cancel
              </button>
              <button 
                className="action-btn primary"
                onClick={verifySignatureAction}
                disabled={!verifyEnvelope.trim()}
              >
                ✅ Verify Signature
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdmiralKeysPanel;