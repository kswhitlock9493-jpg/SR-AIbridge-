import React, { useEffect, useState } from 'react';
import BridgePanel from './components/BridgePanel.jsx';

export default function App() {
  const [message, setMessage] = useState('Pinging backend...');

  useEffect(() => {
    fetch('http://localhost:4000/api/ping')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(() => setMessage('Error contacting backend ⚠️'));
  }, []);

  return (
    <div className="app-container">
      <h1>Bridge Frontend Ignition</h1>
      <BridgePanel status={message} />
    </div>
  );
}