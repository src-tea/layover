import { CalendarClock, MapPinned, Plane, ShieldCheck } from 'lucide-react';
import EmptyState from '../components/EmptyState';
import { formatUsd } from '../utils/currency';

export default function TripsPage({ bookings, onCancel }) {
  if (!bookings.length) {
    return (
      <main className="page-shell narrow-shell">
        <EmptyState title="No demo trips yet" message="Create a layover plan and confirm a sample booking to see it here." action={{ label: 'Plan my layover', onClick: () => window.location.href = '/' }} />
      </main>
    );
  }

  return (
    <main className="page-shell">
      <div className="container">
        <div className="section-heading">
          <span className="eyebrow">My trips</span>
          <h2>Current and upcoming demo bookings</h2>
        </div>

        <div className="results-grid booking-grid">
          {bookings.map((booking) => (
            <article key={booking.id} className="card-panel trip-card">
              <div className="trip-header">
                <div>
                  <span className="status-pill">Demo booking</span>
                  <h3>{booking.facility}</h3>
                </div>
                <span className="price-tag">{formatUsd(booking.price)}</span>
              </div>
              <ul className="summary-list compact-list">
                <li><CalendarClock size={14} /> <span>{booking.window}</span></li>
                <li><MapPinned size={14} /> <span>{booking.location}</span></li>
                <li><Plane size={14} /> <span>{booking.member}</span></li>
                <li><ShieldCheck size={14} /> <span>{booking.status}</span></li>
              </ul>
              <button className="btn btn-secondary full" type="button" onClick={() => onCancel(booking.id)}>Cancel</button>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
