/**
 * DemoLaunchPad - Launch heritage demo modes
 */

import { useState } from "react";

export default function DemoLaunchPad({ onStart }) {
  const [running, setRunning] = useState(null);

  const handleStart = async (mode) => {
    setRunning(mode);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/heritage/demo/${mode}`, {
        method: 'POST'
      });
      const data = await response.json();
      console.log('Demo started:', data);
      setTimeout(() => setRunning(null), 3000);
    } catch (err) {
      console.error('Demo start error:', err);
      setRunning(null);
    }
    onStart(mode);
  };

  return (
    <div className="card demo-launchpad">
      <h3>🚀 Demo Launcher</h3>
      <div className="demo-buttons">
        <button 
          className="demo-btn shakedown"
          onClick={() => handleStart('shakedown')}
          disabled={running === 'shakedown'}
        >
          {running === 'shakedown' ? '⏳ Running...' : '🔄 Shakedown'}
        </button>
        <button 
          className="demo-btn mas"
          onClick={() => handleStart('mas')}
          disabled={running === 'mas'}
        >
          {running === 'mas' ? '⏳ Running...' : '🔧 MAS Healing'}
        </button>
        <button 
          className="demo-btn federation"
          onClick={() => handleStart('federation')}
          disabled={running === 'federation'}
        >
          {running === 'federation' ? '⏳ Running...' : '🌐 Federation'}
        </button>
      </div>
    </div>
  );
}
