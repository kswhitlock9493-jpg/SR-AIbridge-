#!/usr/bin/env node
/**
 * Forge Banner Event Updater v1.9.7s
 * 
 * Updates forge_pulse_banner.svg with live event data from Dominion pulse.
 * Can run in watch mode to continuously update the banner.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const PULSE_STATE_FILE = path.join(__dirname, '..', '.alik', 'forge_pulse.json');
const BANNER_FILE = path.join(__dirname, '..', 'assets', 'forge_pulse_banner.svg');
const FORGE_STATE_FILE = path.join(__dirname, '..', '.alik', 'forge_state.json');

// Color gradients for pulse states
const PULSE_COLORS = {
  gold: {
    gradient: 'goldGradient',
    text: 'HEALTHY',
    color: '#FFD700'
  },
  silver: {
    gradient: 'silverGradient', 
    text: 'MANUAL REVIEW',
    color: '#C0C0C0'
  },
  red: {
    gradient: 'redGradient',
    text: 'RATE LIMITED',
    color: '#FF0000'
  }
};

/**
 * Load pulse events from state file
 */
function loadPulseEvents() {
  try {
    if (!fs.existsSync(PULSE_STATE_FILE)) {
      return [];
    }
    
    const data = fs.readFileSync(PULSE_STATE_FILE, 'utf8');
    const state = JSON.parse(data);
    return state.events || [];
  } catch (error) {
    console.error('[Banner] Error loading pulse events:', error.message);
    return [];
  }
}

/**
 * Load forge state for resonance score
 */
function loadForgeState() {
  try {
    if (!fs.existsSync(FORGE_STATE_FILE)) {
      return { resonance_score: 100.0, health_status: 'normal' };
    }
    
    const data = fs.readFileSync(FORGE_STATE_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('[Banner] Error loading forge state:', error.message);
    return { resonance_score: 100.0, health_status: 'normal' };
  }
}

/**
 * Calculate pulse status from events
 */
function calculatePulseStatus(events) {
  const now = new Date();
  const fiveMinutesAgo = new Date(now - 5 * 60 * 1000);
  const twentyMinutesAgo = new Date(now - 20 * 60 * 1000);
  
  // Filter events in last 5 minutes
  const recentEvents = events.filter(e => {
    const eventTime = new Date(e.timestamp);
    return eventTime > fiveMinutesAgo;
  });
  
  // Count event types
  const mints = recentEvents.filter(e => e.event_type === 'mint').length;
  const renews = recentEvents.filter(e => e.event_type === 'renew').length;
  
  // Check for rate limits
  if (mints > 5 || renews > 10) {
    return { strength: 'red', message: 'rate limit triggered' };
  }
  
  // Check for inactivity
  if (events.length > 0) {
    const lastEvent = new Date(events[events.length - 1].timestamp);
    if (lastEvent < twentyMinutesAgo) {
      return { strength: 'silver', message: 'manual review required' };
    }
  }
  
  return { strength: 'gold', message: 'healthy' };
}

/**
 * Get last event description
 */
function getLastEventDescription(events) {
  if (events.length === 0) {
    return 'No events recorded';
  }
  
  const lastEvent = events[events.length - 1];
  const now = new Date();
  const eventTime = new Date(lastEvent.timestamp);
  const secondsAgo = Math.floor((now - eventTime) / 1000);
  
  let timeStr;
  if (secondsAgo < 60) {
    timeStr = `${secondsAgo}s ago`;
  } else if (secondsAgo < 3600) {
    const minutes = Math.floor(secondsAgo / 60);
    timeStr = `${minutes}m ago`;
  } else {
    const hours = Math.floor(secondsAgo / 3600);
    timeStr = `${hours}h ago`;
  }
  
  const provider = lastEvent.provider || 'unknown';
  const eventType = lastEvent.event_type || 'event';
  
  return `${eventType} • ${provider} • ${timeStr}`;
}

/**
 * Update SVG banner with current pulse data
 */
function updateBanner() {
  try {
    // Load current data
    const events = loadPulseEvents();
    const forgeState = loadForgeState();
    const pulseStatus = calculatePulseStatus(events);
    const lastEventDesc = getLastEventDescription(events);
    
    // Read current banner
    if (!fs.existsSync(BANNER_FILE)) {
      console.error('[Banner] Banner file not found:', BANNER_FILE);
      return false;
    }
    
    let svgContent = fs.readFileSync(BANNER_FILE, 'utf8');
    
    // Update last event
    svgContent = svgContent.replace(
      /<tspan id="lastEvent">.*?<\/tspan>/,
      `<tspan id="lastEvent">${escapeXml(lastEventDesc)}</tspan>`
    );
    
    // Update pulse text
    const pulseConfig = PULSE_COLORS[pulseStatus.strength];
    svgContent = svgContent.replace(
      /<text x="730" y="125"[^>]*id="pulseText"[^>]*>.*?<\/text>/,
      `<text x="730" y="125" font-family="monospace" font-size="12" font-weight="bold" fill="url(#${pulseConfig.gradient})" id="pulseText">${pulseConfig.text}</text>`
    );
    
    // Update pulse indicator circle
    svgContent = svgContent.replace(
      /<circle cx="700" cy="120"[^>]*>/,
      `<circle cx="700" cy="120" r="15" fill="url(#${pulseConfig.gradient})" filter="url(#glow)">`
    );
    
    // Update resonance score
    const resonance = forgeState.resonance_score || 100.0;
    const resonanceWidth = Math.floor((resonance / 100) * 600);
    
    svgContent = svgContent.replace(
      /<rect x="140" y="150" width="\d+" height="12" fill="url\(#goldGradient\)"/,
      `<rect x="140" y="150" width="${resonanceWidth}" height="12" fill="url(#goldGradient)"`
    );
    
    svgContent = svgContent.replace(
      /<text x="750" y="160"[^>]*>[\d.]+<\/text>/,
      `<text x="750" y="160" font-family="monospace" font-size="12" fill="#e6edf3">${resonance.toFixed(1)}</text>`
    );
    
    // Write updated banner
    fs.writeFileSync(BANNER_FILE, svgContent, 'utf8');
    
    console.log('[Banner] Updated successfully');
    console.log(`  Pulse: ${pulseStatus.strength} (${pulseStatus.message})`);
    console.log(`  Last event: ${lastEventDesc}`);
    console.log(`  Resonance: ${resonance.toFixed(1)}`);
    
    return true;
    
  } catch (error) {
    console.error('[Banner] Error updating banner:', error.message);
    return false;
  }
}

/**
 * Escape XML special characters
 */
function escapeXml(unsafe) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Main entry point
 */
function main() {
  const args = process.argv.slice(2);
  const watchMode = args.includes('--watch') || args.includes('-w');
  
  console.log('========================================');
  console.log('🜂 Forge Banner Updater v1.9.7s');
  console.log('========================================');
  console.log();
  
  if (watchMode) {
    console.log('[Banner] Starting in watch mode...');
    console.log('[Banner] Press Ctrl+C to stop');
    console.log();
    
    // Initial update
    updateBanner();
    
    // Watch for changes every 10 seconds
    setInterval(() => {
      updateBanner();
    }, 10000);
    
  } else {
    // Single update
    const success = updateBanner();
    process.exit(success ? 0 : 1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { updateBanner, loadPulseEvents, calculatePulseStatus };
