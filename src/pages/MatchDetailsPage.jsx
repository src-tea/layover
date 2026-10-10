import { ArrowRight, BriefcaseBusiness, Clock3, MapPin, ShieldCheck, Sparkles, Users } from 'lucide-react';
import { useMemo } from 'react';
import PriceBreakdown from '../components/PriceBreakdown';
import SafetyNotice from '../components/SafetyNotice';
import { formatUsd, toUsd } from '../utils/currency';

export default function MatchDetailsPage({ match, search, onSelectStorage, onConnect }) {
  const price = useMemo(() => ({
    total: toUsd(600, 'INR'),
    eligible: 2,
    solo: toUsd(600, 'INR'),
    fee: 0,
  }), []);

  if (!match) {
    return <main className="page-shell"><div className="container card-panel">Match not found.</div></main>;
  }

  return (
    <main className="page-shell">
      <div className="container details-layout">
        <div className="card-panel detail-card">
          <div className="section-heading inline-heading">
            <div>
              <span className="eyebrow">Selected traveller</span>
              <h2>{match.name}</h2>
            </div>
            <span className="compatibility-badge large"><Sparkles size={12} /> {match.score}% compatible</span>
          </div>

          <div className="meta-grid detail-grid">
            <div><MapPin size={14} /> {match.airport}</div>
            <div><Clock3 size={14} /> Overlap: {match.window}</div>
            <div><BriefcaseBusiness size={14} /> {match.baggage}</div>
            <div><Users size={14} /> {formatUsd(match.budgetCurrency === 'USD' ? match.budget : toUsd(match.budget, 'INR'))} budget</div>
          </div>

          <div className="safe-box">
            <ShieldCheck size={16} /> Shared-storage eligibility: <strong>{match.sharedStorage ? 'Eligible' : 'Not approved for shared booking'}</strong>
          </div>

          <div className="tags-wrap">
            {(match.interests || []).map((interest) => <span key={interest} className="tag">{interest}</span> )}
          </div>

          <div className="summary-card compact">
            <div><span>Layover</span><strong>{search.arrival ? new Date(search.arrival).toLocaleString([], { month:'short', day:'numeric', hour:'numeric', minute:'2-digit' }) : '—'}</strong></div>
            <div><span>Next flight</span><strong>{search.departure ? new Date(search.departure).toLocaleString([], { month:'short', day:'numeric', hour:'numeric', minute:'2-digit' }) : '—'}</strong></div>
            <div><span>Overlap</span><strong>{match.overlapMinutes || 180} minutes</strong></div>
          </div>

          <SafetyNotice />

          <div className="action-row sticky-row">
            <button className="btn btn-primary" type="button" onClick={onSelectStorage}>Select storage <ArrowRight size={16} /></button>
          </div>
        </div>

        <div className="sidebar-stack">
          <PriceBreakdown totalPrice={price.total} eligibleParticipants={price.eligible} soloPrice={price.solo} platformFee={price.fee} />
          <p className="price-provenance">Illustrative legacy sample converted from INR at the ECB reference rate dated 2026-10-09; no storage provider price is verified.</p>
        </div>
      </div>
    </main>
  );
}
