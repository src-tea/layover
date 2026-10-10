import { Clock3, MapPin, ShieldCheck, Tag } from 'lucide-react';
import { formatCurrency, formatUsd } from '../utils/currency';

export default function StorageCard({ facility, onSelect, selected = false }) {
  return (
    <article className={`storage-card ${selected ? 'selected' : ''}`}>
      <div className="storage-header">
        <div>
          <h3>{facility.name}</h3>
          <p><MapPin size={14} /> {facility.airport}</p>
        </div>
        <span className="price-tag">{formatUsd(facility.price)}{facility.quoteOnly ? ' / item' : ''}</span>
      </div>

      <div className="storage-meta">
        <span>Shared booking: {facility.sharedBooking ? 'Allowed' : 'Not permitted'}</span>
        <span>Hours: {facility.hours}</span>
        <span>Baggage: {facility.baggageTypes.join(', ')}</span>
        <span>Distance: {facility.distance}</span>
      </div>

      <div className="storage-detail-list">
        <div><Tag size={14} /> Min duration: {facility.minDuration}</div>
        <div><Clock3 size={14} /> Capacity: {facility.capacity}</div>
        <div><ShieldCheck size={14} /> Access: {facility.accessControl}</div>
      </div>

      <p className="price-provenance">
        {facility.priceSource?.status === 'provider_quoted_converted'
          ? `Provider quote, verified ${facility.priceSource.verified_at}. Original: ${formatCurrency(facility.originalAmount, facility.originalCurrency)}. `
          : `Illustrative estimate converted from ${formatCurrency(facility.originalAmount, facility.originalCurrency)} using the ECB rate dated ${facility.priceSource?.conversion_rate_date}. `}
        {facility.priceSource?.source_url
          ? <a href={facility.priceSource.source_url} target="_blank" rel="noreferrer">{facility.priceSource.source_name} source</a>
          : 'Underlying provider price is not verified.'}
      </p>

      {facility.quoteOnly ? (
        <a className="btn btn-primary full" href={facility.priceSource?.source_url} target="_blank" rel="noreferrer">View provider tariff</a>
      ) : (
        <button className="btn btn-primary full" type="button" onClick={onSelect}>
          {selected ? 'Selected' : 'Select Storage'}
        </button>
      )}
    </article>
  );
}
