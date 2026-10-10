import { MapPin, Clock3, Tag, Plus } from 'lucide-react';
import { attractions } from '../data/attractions';
import { findAirport } from '../data/airports';
import EmptyState from '../components/EmptyState';
import { formatUsd } from '../utils/currency';

export default function ExplorePage({ airportCode, onAddActivity }) {
  const airportActivities = attractions.filter((place) => place.airportCode === airportCode);
  const airport = findAirport(airportCode);

  return (
    <main className="page-shell">
      <div className="container">
        <div className="section-heading">
          <span className="eyebrow">Explore the city</span>
          <h2>Activities around {airport?.city || airportCode} ({airportCode})</h2>
        </div>

        {airportActivities.length ? <div className="results-grid attraction-grid">
          {airportActivities.map((place) => (
            <article key={place.id} className="card-panel attraction-card">
              <div className="attraction-visual">{place.name.charAt(0)}</div>
              <div className="attraction-content">
                <div className="attraction-header">
                  <h3>{place.name}</h3>
                  <span className="tag">{place.category}</span>
                </div>
                <div className="meta-grid compact-grid">
                  <span><Clock3 size={14} /> {place.duration}</span>
                  <span><MapPin size={14} /> {place.travelTime}</span>
                  <span><Tag size={14} /> {place.price === null ? 'Price unavailable' : `${formatUsd(place.price)} estimated`}</span>
                </div>
                <p>{place.window}</p>
                {place.priceSource ? <small className="price-provenance">Legacy illustrative estimate; original INR market price is unverified.</small> : null}
                <button className="btn btn-primary small" type="button" onClick={() => onAddActivity(place)}>
                  <Plus size={14} /> Add to Itinerary
                </button>
              </div>
            </article>
          ))}
        </div> : <EmptyState title="No activity data for this airport" message="LAYOVER has no locally sourced activities or prices for this airport yet." />}
      </div>
    </main>
  );
}
