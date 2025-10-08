import fs from "node:fs";
const badgePath = "bridge-frontend/public/bridge_sync_badge.json";

const status = process.env.BRIDGE_SYNC_STATUS || "unknown";
const color =
  status === "stable" ? "brightgreen" :
  status === "degraded" ? "orange" :
  status === "down" ? "red" : "lightgrey";

const payload = {
  schemaVersion: 1,
  label: "Bridge Sync",
  message: String(status).toUpperCase(),
  color
};

fs.writeFileSync(badgePath, JSON.stringify(payload));
console.log("Updated badge:", payload);
