# Command Deck V1 Guide

## Overview

Command Deck V1 is the Heritage Bridge UI - a nostalgic CRT-style command interface for monitoring and controlling the Heritage subsystem.

## Features

- **Real-time Event Streaming**: WebSocket-powered live event feed
- **Task Monitoring**: Queue, active, and completed task metrics
- **Agent Health**: Win rates and health indicators for all agents
- **Fault Injection**: Control fault types (corrupt, drop, delay)
- **Demo Launcher**: One-click demo execution
- **Event Stream Tap**: Raw event stream viewer

## Access

Navigate to `/deck` in the frontend:

```
http://localhost:3000/deck
```

## UI Panels

### Task Status Card

Displays current task queue metrics:
- Queue size
- Active tasks
- Completed tasks

### Agent Metrics Table

Shows agent performance:
- Agent ID
- Win rate percentage
- Health score with color coding:
  - Green (>80%): Good
  - Yellow (50-80%): Fair
  - Red (<50%): Poor

### Anomaly Feed

Real-time event feed with color-coded event types:
- **Red**: Fault events
- **Green**: Heal events
- **Yellow**: Demo events
- **Blue**: Heritage events
- **Purple**: Federation events

### Fault Controls

Inject faults for resilience testing:
- **Corrupt**: Corrupt message content
- **Drop**: Drop messages
- **Delay**: Add artificial delays

### Demo Launchpad

Launch heritage demos:
- **Shakedown**: Basic system stress test
- **MAS Healing**: Fault injection + self-healing demo
- **Federation**: Cross-bridge communication demo

### Event Stream Tap

Raw event stream viewer showing:
- Event kind (badge)
- Event payload preview

## Keyboard Shortcuts

*(Coming soon)*

## Modes

### Deck Mode

- Nostalgic CRT aesthetic
- Real-time monitoring
- Heritage subsystem focus

### Ops Mode

Toggle back to standard Command Deck:
Navigate to `/` for the main Command Deck.

## WebSocket Connection

The Deck connects to:
```
ws://localhost:8000/heritage/ws/stats
```

Configure via environment:
```bash
VITE_WS_BASE=ws://your-host:8000
```

## Event Types

Events displayed in the deck:

| Kind | Description |
|------|-------------|
| `heritage.*` | General heritage events |
| `bridge.events` | MAS bridge events |
| `fault.*` | Fault injection events |
| `heal.*` | Self-healing events |
| `federation.*` | Federation events |
| `anchor.*` | Agent anchor events |
| `demo.*` | Demo control events |
| `metrics.update` | Metrics updates |

## Troubleshooting

### WebSocket Not Connecting

1. Check backend is running: `http://localhost:8000/heritage/status`
2. Verify VITE_WS_BASE environment variable
3. Check browser console for errors

### No Events Showing

1. Run a demo to generate events
2. Check WebSocket connection status
3. Verify backend event bus is publishing

### Demos Not Starting

1. Check backend logs for errors
2. Verify `/heritage/demo/{mode}` endpoint is accessible
3. Check CORS settings if running on different ports

## Styling

The Deck uses a retro CRT aesthetic:
- Dark background (#0b0f14)
- Cyan glow (#93e5ff)
- Color-coded subsystems
- Monospace font (Courier New)

To customize, edit:
```
bridge-frontend/src/styles/deck.css
```

## Performance

- Event buffer: 250 events max
- Auto-cleanup of old events
- Efficient WebSocket reconnection
- Minimal re-renders with React hooks

## Next Steps

1. Explore demos to see the system in action
2. Monitor agent health and task metrics
3. Test fault injection and healing
4. Customize panels for your needs
