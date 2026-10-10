import { ArrowRight, CheckCircle2, ShieldCheck } from 'lucide-react';
import { useMemo, useState } from 'react';
import BookingSummary from '../components/BookingSummary';
import CostCalculator from '../components/CostCalculator';
import DemoModeNotice from '../components/DemoModeNotice';
import { calculateSharedCost } from '../utils/pricing';

export default function BookingPage({ search, selectedStorage, selectedMatch, onConfirmBooking }) {
  const [accepted, setAccepted] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [participantCount, setParticipantCount] = useState(2);
  const [demoFee, setDemoFee] = useState(0);

  const calculation = useMemo(() => calculateSharedCost({
    totalPrice: selectedStorage?.price || 600,
    eligibleParticipants: participantCount,
    soloPrice: selectedStorage?.price || 600,
    platformFee: demoFee,
  }), [selectedStorage, participantCount, demoFee]);

  const handleConfirm = () => {
    if (!accepted) return;
    const ref = `LAY-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
    setSubmitted(true);
    onConfirmBooking({
      facility: selectedStorage?.name || 'Demo storage',
      window: `${search.arrival || 'Arrival'} → ${search.departure || 'Departure'}`,
      member: selectedMatch?.name || 'Solo traveller',
      price: calculation.finalTotal,
      location: `${selectedStorage?.airport || 'Airport'} demo location`,
      status: 'Demo booking',
      ref,
    });
  };

  if (submitted) {
    return (
      <main className="page-shell narrow-shell">
        <div className="card-panel success-panel">
          <CheckCircle2 size={32} />
          <h2>Demo booking confirmed</h2>
          <p>Your sample reservation has been created and saved in My Trips.</p>
          <p><strong>Reference:</strong> {`LAY-${Math.random().toString(36).slice(2, 8).toUpperCase()}`}</p>
          <DemoModeNotice />
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <div className="container booking-layout">
        <div className="card-panel booking-panel">
          <div className="section-heading">
            <span className="eyebrow">Booking</span>
            <h2>Review and confirm your demo booking</h2>
          </div>

          <div className="booking-steps">
            <div className="step-pill active">1. Storage</div>
            <div className="step-pill">2. Time</div>
            <div className="step-pill">3. Cost</div>
            <div className="step-pill">4. Confirm</div>
          </div>

          <div className="booking-summary-box">
            <h3>{selectedStorage?.name}</h3>
            <p>{selectedStorage?.airport} • {selectedStorage?.hours}</p>
            <p>Storage: {selectedStorage?.baggageTypes.join(', ')}</p>
          </div>

          <CostCalculator
            totalPrice={selectedStorage?.price || 600}
            soloPrice={selectedStorage?.price || 600}
            initialParticipants={participantCount}
            initialFee={demoFee}
            onChange={(key, value) => {
              if (key === 'participants') setParticipantCount(value);
              if (key === 'fee') setDemoFee(value);
            }}
          />

          <label className="checkbox-row accept-row">
            <input type="checkbox" checked={accepted} onChange={(event) => setAccepted(event.target.checked)} />
            <span>I accept the demo terms and understand this is a sample booking only.</span>
          </label>

          <button className="btn btn-primary full" type="button" onClick={handleConfirm} disabled={!accepted}>
            Confirm Demo Booking <ArrowRight size={16} />
          </button>
        </div>

        <aside className="sidebar-stack">
          <BookingSummary booking={{
            facility: selectedStorage?.name || 'Demo facility',
            window: `${search.arrival || 'Arrival'} → ${search.departure || 'Departure'}`,
            member: selectedMatch?.name || 'Travelling solo',
            price: calculation.finalTotal,
          }} />
          <div className="card-panel small-panel">
            <ShieldCheck size={16} /> No real payment or reservation has been created.
          </div>
        </aside>
      </div>
    </main>
  );
}
