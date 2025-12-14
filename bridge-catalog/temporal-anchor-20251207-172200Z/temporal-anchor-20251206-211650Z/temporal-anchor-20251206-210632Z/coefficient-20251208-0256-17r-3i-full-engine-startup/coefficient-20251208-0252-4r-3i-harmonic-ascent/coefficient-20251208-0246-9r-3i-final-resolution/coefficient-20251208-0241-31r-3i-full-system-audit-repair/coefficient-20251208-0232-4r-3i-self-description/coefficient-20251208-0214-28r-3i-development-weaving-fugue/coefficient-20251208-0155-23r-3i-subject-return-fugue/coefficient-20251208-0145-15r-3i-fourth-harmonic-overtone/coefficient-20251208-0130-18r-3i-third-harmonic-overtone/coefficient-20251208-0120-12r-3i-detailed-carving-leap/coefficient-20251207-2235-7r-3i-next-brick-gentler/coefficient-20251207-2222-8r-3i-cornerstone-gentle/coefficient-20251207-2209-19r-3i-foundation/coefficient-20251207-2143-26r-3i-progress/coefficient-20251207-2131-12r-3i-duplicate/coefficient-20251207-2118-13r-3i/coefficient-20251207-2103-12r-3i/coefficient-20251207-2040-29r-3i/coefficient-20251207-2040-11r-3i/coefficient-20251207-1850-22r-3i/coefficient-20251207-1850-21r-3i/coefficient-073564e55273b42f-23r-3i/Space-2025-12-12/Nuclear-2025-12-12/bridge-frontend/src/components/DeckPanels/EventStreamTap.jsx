/**
 * EventStreamTap - Raw event stream viewer
 */

export default function EventStreamTap({ events }) {
  return (
    <div className="card event-stream">
      <h3>📡 Event Stream</h3>
      <div className="stream-list">
        {events.length === 0 ? (
          <p className="empty-state">Waiting for events...</p>
        ) : (
          events.slice(0, 20).map((event, idx) => (
            <div key={idx} className="stream-item">
              <span className="stream-kind badge">{event.kind}</span>
              <span className="stream-data">
                {JSON.stringify(event.payload || {}).slice(0, 60)}...
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
