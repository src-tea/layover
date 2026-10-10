import { calculateSharedCost } from '../utils/pricing';
import { formatUsd } from '../utils/currency';

export default function PriceBreakdown({ totalPrice, eligibleParticipants, soloPrice, platformFee = 0 }) {
  const pricing = calculateSharedCost({ totalPrice, eligibleParticipants, soloPrice, platformFee });

  return (
    <div className="price-breakdown card-panel">
      <h3>Price breakdown</h3>
      <div className="price-row"><span>Total sample storage (estimate)</span><strong>{formatUsd(totalPrice)}</strong></div>
      <div className="price-row"><span>Eligible participants</span><strong>{eligibleParticipants}</strong></div>
      <div className="price-row"><span>Demo platform fee</span><strong>{formatUsd(platformFee)}</strong></div>
      <div className="price-row"><span>Per traveller</span><strong>{formatUsd(pricing.perParticipant)}</strong></div>
      <div className="price-row"><span>Original solo estimate</span><strong>{formatUsd(soloPrice)}</strong></div>
      <div className="price-row"><span>Estimated savings</span><strong>{formatUsd(pricing.savings)}</strong></div>
    </div>
  );
}
