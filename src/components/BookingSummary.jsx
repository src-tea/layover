import { formatUsd } from '../utils/currency';

export default function BookingSummary({ booking }) {
  if (!booking) {
    return null;
  }

  return (
    <div className="card-panel summary-box">
      <h3>Booking summary</h3>
      <ul className="summary-list">
        <li><span>Facility</span><strong>{booking.facility}</strong></li>
        <li><span>Window</span><strong>{booking.window}</strong></li>
        <li><span>Traveller</span><strong>{booking.member}</strong></li>
        <li><span>Cost</span><strong>{formatUsd(booking.price)}</strong></li>
      </ul>
    </div>
  );
}
