import React from 'react';
import CaptainsChat from './CaptainsChat';

const CaptainToCaptain = ({ realTimeMessages = [] }) => {
  return (
    <div className="captain-to-captain">
      <h2>⚔️ Captain-to-Captain Communications</h2>
      <div className="communication-wrapper">
        <CaptainsChat realTimeMessages={realTimeMessages} />
      </div>
    </div>
  );
};

export default CaptainToCaptain;