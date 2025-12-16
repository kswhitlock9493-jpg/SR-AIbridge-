# TriageBootstrapBanner Usage Example

## Overview
The TriageBootstrapBanner component automatically detects when all triage systems (CI/CD, Endpoint, API, and Hooks) have been seeded and displays a confirmation banner.

## Basic Usage

### In a Diagnostics/Health Dashboard Page

```jsx
import React from "react";
import TriageBootstrapBanner from "./components/TriageBootstrapBanner";
import UnifiedHealthTimeline from "./components/UnifiedHealthTimeline";
import DiagnosticsTimeline from "./components/DiagnosticsTimeline";

export default function HealthDashboard() {
  return (
    <div className="health-dashboard">
      <h1>System Health Dashboard</h1>
      
      {/* Banner shows when all triage systems are seeded */}
      <TriageBootstrapBanner />
      
      {/* Other diagnostic components */}
      <UnifiedHealthTimeline />
      <DiagnosticsTimeline />
    </div>
  );
}
```

### In the System Self-Test Page

```jsx
import React from "react";
import TriageBootstrapBanner from "./components/TriageBootstrapBanner";
import SystemSelfTest from "./components/SystemSelfTest";

export default function SystemHealthPage() {
  return (
    <div className="system-health-page">
      <TriageBootstrapBanner />
      <SystemSelfTest />
    </div>
  );
}
```

### In a Main Dashboard

```jsx
import React from "react";
import TriageBootstrapBanner from "./components/TriageBootstrapBanner";
import CommandDeck from "./components/CommandDeck";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <header>
        <h1>SR-AIbridge Command Center</h1>
      </header>
      
      {/* Shows at top of dashboard when seeded */}
      <TriageBootstrapBanner />
      
      <CommandDeck />
    </div>
  );
}
```

## Behavior

- **Auto-detection**: Fetches `/api/diagnostics/timeline/unified` on mount
- **Conditional rendering**: Only shows when ALL 4 triage types are detected
- **Silent failure**: If API fails, banner simply doesn't show (no error displayed)
- **Single check**: Checks once on mount, no polling/refresh

## Checked Triage Types

The banner verifies presence of:
1. `CI_CD_TRIAGE` - CI/CD pipeline health
2. `ENDPOINT_TRIAGE` - API endpoint health
3. `API_TRIAGE` - Service integration health
4. `HOOKS_TRIAGE` - Webhook health

## Styling

The banner uses Tailwind CSS classes:
- Green background (`bg-green-700`)
- White text (`text-white`)
- Small text size (`text-sm`)
- Rounded corners (`rounded-md`)
- Shadow (`shadow`)
- Bottom margin (`mb-3`)

### Custom Styling

You can wrap it and add custom styles:

```jsx
<div className="custom-banner-container">
  <TriageBootstrapBanner />
</div>
```

Or modify the component's className directly if needed.

## When to Use

✅ **Good Use Cases:**
- Health/diagnostics dashboards
- System status pages
- Admin panels
- Deployment confirmation pages

❌ **Not Recommended:**
- Login pages
- Public-facing pages
- Pages without diagnostic context
- Every single page (only where relevant)

## Example with Custom Message

If you want a custom message, you can create a wrapper:

```jsx
import React, { useEffect, useState } from "react";

export default function CustomTriageBanner() {
  const [seeded, setSeeded] = useState(false);
  
  useEffect(() => {
    fetch("/api/diagnostics/timeline/unified")
      .then(res => res.json())
      .then(data => {
        const triageTypes = ["CI_CD_TRIAGE", "ENDPOINT_TRIAGE", "API_TRIAGE", "HOOKS_TRIAGE"];
        setSeeded(triageTypes.every(t => data.events?.some(e => e.type === t)));
      })
      .catch(() => {});
  }, []);
  
  if (!seeded) return null;
  
  return (
    <div className="p-3 bg-blue-600 text-white rounded-lg shadow-lg mb-4">
      <h3 className="font-bold">🎯 System Ready</h3>
      <p className="text-sm">All diagnostic systems are initialized and reporting.</p>
    </div>
  );
}
```

## API Integration

The banner integrates with:
- **Backend**: `GET /api/diagnostics/timeline/unified`
- **Response format**: `{ count: number, events: Array<TriageEvent> }`
- **Expected fields**: Each event has a `type` field

## Testing

To test the banner:

1. Start the backend
2. Run the pre-seed: `python3 bridge_backend/scripts/triage_preseed.py`
3. Navigate to a page with the banner
4. Banner should appear with green checkmark message

To test it NOT showing:

1. Delete one of the report files
2. Refresh the page
3. Banner should not appear
