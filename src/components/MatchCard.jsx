import { ArrowRight, BriefcaseBusiness, Clock3, MapPin, Users, Sparkles } from 'lucide-react';
import { findAirport } from '../data/airports';
import { formatUsd } from '../utils/currency';

export default function MatchCard({ traveller, onView, onConnect, connectionStatus }) {
  const airport = findAirport(traveller.airportCode || traveller.airport);
  return (
    <article className="match-card">
      <div className="match-topline">
        <div className="avatar-wrap">
          {traveller.name.charAt(0)}
        </div>
        <div>
          <h3>{traveller.name}</h3>
          <p>{traveller.intro}</p>
        </div>
        <span className="compatibility-badge">
          <Sparkles size={12} /> {traveller.score || 86}% match
        </span>
      </div>

      <div className="meta-grid">
        <div><MapPin size={14} /> {airport ? `${airport.name} (${airport.iataCode})` : traveller.airport}</div>
        <div><Clock3 size={14} /> {traveller.window}</div>
        <div><BriefcaseBusiness size={14} /> {traveller.baggage}</div>
        <div><Users size={14} /> {traveller.budget} budget</div>
      </div>

      <div className="tag-row">
        {(traveller.interests || []).slice(0, 3).map((interest) => (
          <span key={interest} className="tag">{interest}</span>
        ))}
      </div>

      <div className="match-footer">
        <div className="cost-box">
          <span>Estimated shared cost</span>
          <strong>{formatUsd(traveller.cost || 0)}</strong>
        </div>
        <div className="action-row">
          <button className="btn btn-secondary small" type="button" onClick={onView}>View Match</button>
          <button className="btn btn-primary small" type="button" onClick={onConnect} disabled={Boolean(connectionStatus)}>
            {connectionStatus || (traveller.userId ? 'Request to connect' : 'Sign in to connect')}
          </button>
        </div>
      </div>
    </article>
  );
}
