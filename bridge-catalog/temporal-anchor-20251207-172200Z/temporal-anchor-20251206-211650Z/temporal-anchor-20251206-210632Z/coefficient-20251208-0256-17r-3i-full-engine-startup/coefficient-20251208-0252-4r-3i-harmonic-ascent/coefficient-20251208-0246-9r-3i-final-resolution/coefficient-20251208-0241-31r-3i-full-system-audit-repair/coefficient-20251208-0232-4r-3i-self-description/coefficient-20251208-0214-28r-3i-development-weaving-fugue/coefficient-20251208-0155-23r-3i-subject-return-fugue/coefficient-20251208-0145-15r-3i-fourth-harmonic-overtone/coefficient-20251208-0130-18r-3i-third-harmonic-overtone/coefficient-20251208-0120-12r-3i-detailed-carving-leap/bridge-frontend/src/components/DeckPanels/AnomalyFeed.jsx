/**
 * AnomalyFeed - Display heritage events and anomalies
 */

export default function AnomalyFeed({ events }) {
  return (
    <div className="card anomaly-feed">
      <h3>⚠️ Event Feed</h3>
      <div className="event-list">
        {events.length === 0 ? (
          <p className="empty-state">No events detected</p>
        ) : (
          events.slice(0, 10).map((event, idx) => (
            <div key={idx} className={`event-item ${getEventClass(event.kind)}`}>
              <div className="event-kind">{event.kind}</div>
              <div className="event-time">
                {new Date(event.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function getEventClass(kind) {
  if (kind?.includes('fault')) return 'fault';
  if (kind?.includes('heal')) return 'heal';
  if (kind?.includes('demo')) return 'demo';
  if (kind?.includes('heritage')) return 'heritage';
  if (kind?.includes('federation')) return 'federation';
  return 'default';
}
