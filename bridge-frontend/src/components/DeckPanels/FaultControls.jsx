/**
 * FaultControls - Control fault injection settings
 */

export default function FaultControls({ onInject }) {
  const handleInject = (type) => {
    onInject({
      type,
      enabled: true,
      rate: 0.3
    });
  };

  return (
    <div className="card fault-controls">
      <h3>💥 Fault Injection</h3>
      <div className="control-buttons">
        <button 
          className="fault-btn corrupt"
          onClick={() => handleInject('corrupt')}
        >
          Corrupt
        </button>
        <button 
          className="fault-btn drop"
          onClick={() => handleInject('drop')}
        >
          Drop
        </button>
        <button 
          className="fault-btn delay"
          onClick={() => handleInject('delay')}
        >
          Delay
        </button>
      </div>
    </div>
  );
}
