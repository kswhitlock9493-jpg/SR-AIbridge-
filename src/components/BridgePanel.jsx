import React from 'react';

export default function BridgePanel({ status }) {
  return (
    <div className="bridge-panel">
      <p>{status}</p>
    </div>
  );
}