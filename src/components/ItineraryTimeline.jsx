export default function ItineraryTimeline({ items = [] }) {
  return (
    <div className="timeline">
      {items.length === 0 ? <p className="muted">No activities planned yet.</p> : items.map((item) => (
        <div key={item.id} className="timeline-item">
          <div className="timeline-dot" />
          <div>
            <h4>{item.name}</h4>
            <p>{item.category} • {item.duration} • {item.travelTime}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
