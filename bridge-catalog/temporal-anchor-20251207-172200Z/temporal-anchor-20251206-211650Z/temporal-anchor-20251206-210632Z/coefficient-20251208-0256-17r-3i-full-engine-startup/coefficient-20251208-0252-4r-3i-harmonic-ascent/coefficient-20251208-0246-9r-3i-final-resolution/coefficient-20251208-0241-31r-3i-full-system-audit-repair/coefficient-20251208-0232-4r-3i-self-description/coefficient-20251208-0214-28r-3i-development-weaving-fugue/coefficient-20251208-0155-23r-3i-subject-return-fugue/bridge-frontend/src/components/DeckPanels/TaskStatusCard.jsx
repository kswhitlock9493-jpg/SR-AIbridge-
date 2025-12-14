/**
 * TaskStatusCard - Display task queue status
 */

export default function TaskStatusCard({ metrics }) {
  return (
    <div className="card">
      <h3>📋 Task Status</h3>
      <div className="metrics">
        <div className="metric-row">
          <span className="label">Queue:</span>
          <span className="value">{metrics.queue || 0}</span>
        </div>
        <div className="metric-row">
          <span className="label">Active:</span>
          <span className="value">{metrics.active || 0}</span>
        </div>
        <div className="metric-row">
          <span className="label">Completed:</span>
          <span className="value">{metrics.completed || 0}</span>
        </div>
      </div>
    </div>
  );
}
