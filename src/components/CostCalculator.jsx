import { useMemo } from 'react';
import { calculateSharedCost } from '../utils/pricing';
import { formatUsd } from '../utils/currency';

export default function CostCalculator({ totalPrice, soloPrice, initialParticipants = 2, initialFee = 0, onChange }) {
  const result = useMemo(() => calculateSharedCost({
    totalPrice,
    eligibleParticipants: initialParticipants,
    soloPrice,
    platformFee: initialFee,
  }), [totalPrice, soloPrice, initialParticipants, initialFee]);

  return (
    <div className="card-panel calculator-widget">
      <h3>Cost-sharing calculator</h3>
      <div className="field-group">
        <label className="field">
          <span>Eligible participants</span>
          <input type="number" min="1" max="6" value={initialParticipants} onChange={(event) => onChange?.('participants', Number(event.target.value) || 1)} />
        </label>
        <label className="field">
          <span>Demo fee (USD)</span>
          <input type="number" min="0" step="0.01" value={initialFee} onChange={(event) => onChange?.('fee', Number(event.target.value) || 0)} />
        </label>
      </div>

      <div className="price-breakdown compact">
        <div className="price-row"><span>Total sample storage (estimate)</span><strong>{formatUsd(result.total)}</strong></div>
        <div className="price-row"><span>Each participant</span><strong>{formatUsd(result.perParticipant)}</strong></div>
        <div className="price-row"><span>Estimated savings</span><strong>{formatUsd(result.savings)}</strong></div>
        <div className="price-row"><span>Final amount</span><strong>{formatUsd(result.finalTotal)}</strong></div>
      </div>
    </div>
  );
}
