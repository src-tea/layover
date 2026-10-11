import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import StorageCard from '../components/StorageCard';
import { airports } from '../data/airports';
import { storageFacilities } from '../data/storage';
import { apiFetch } from '../lib/api';
import { formatCurrency, formatUsd } from '../utils/currency';

export default function StoragePage({ airportCode = 'DEL', onSelectStorage }) {
  const [filters, setFilters] = useState({ maxPrice: 100, sharedOnly: false, baggage: 'Any' });
  const [providerPrices, setProviderPrices] = useState([]);
  const [priceStatus, setPriceStatus] = useState('loading');
  const [priceMessage, setPriceMessage] = useState('');
  const airport = airports.find((item) => item.iataCode === airportCode);

  useEffect(() => {
    let isCurrent = true;
    setPriceStatus('loading');
    apiFetch(`/storage/prices?airport_code=${encodeURIComponent(airportCode)}`)
      .then((response) => {
        if (!isCurrent) return;
        setProviderPrices(response.items || []);
        setPriceStatus(response.status || 'unavailable');
        setPriceMessage(response.message || '');
      })
      .catch((error) => {
        if (!isCurrent) return;
        const localQuotes = storageFacilities.find((facility) => facility.airportCode === airportCode && facility.quoteOnly)?.quoteTiers || [];
        setProviderPrices(localQuotes);
        const noApiConfigured = error.message?.includes('API is not configured');
        setPriceStatus(localQuotes.length ? 'provider_quoted' : (error.status === 404 || noApiConfigured) ? 'unavailable' : 'error');
        setPriceMessage(localQuotes.length
          ? 'Showing the bundled provider quote; refresh when online.'
          : (error.status === 404 || noApiConfigured)
            ? 'No verified provider quote is available for this airport.'
            : error.message);
      });

    return () => { isCurrent = false; };
  }, [airportCode]);

  const filtered = useMemo(() => storageFacilities.filter((facility) => {
    if (facility.quoteOnly || facility.airportCode !== airportCode) return false;
    const budgetMatch = facility.price <= filters.maxPrice;
    const baggageMatch = filters.baggage === 'Any' || facility.baggageTypes.includes(filters.baggage);
    const sharedMatch = !filters.sharedOnly || facility.sharedBooking;
    return budgetMatch && baggageMatch && sharedMatch;
  }), [airportCode, filters]);

  return (
    <main className="page-shell">
      <div className="container">
        <div className="section-heading inline-heading">
          <div>
            <span className="eyebrow">Storage discovery</span>
            <h2>Storage at {airport?.name || airportCode}</h2>
          </div>
        </div>

        <div className="filter-panel card-panel">
          <label className="field inline-field">
            <span>Max price</span>
            <input type="range" min="0" max="100" step="1" value={filters.maxPrice} onChange={(event) => setFilters({ ...filters, maxPrice: Number(event.target.value) })} />
            <strong>{formatUsd(filters.maxPrice)}</strong>
          </label>

          <label className="field inline-field">
            <span>Baggage</span>
            <select value={filters.baggage} onChange={(event) => setFilters({ ...filters, baggage: event.target.value })}>
              <option>Any</option>
              <option>Carry-on</option>
              <option>Checked</option>
            </select>
          </label>

          <label className="checkbox-row">
            <input type="checkbox" checked={filters.sharedOnly} onChange={(event) => setFilters({ ...filters, sharedOnly: event.target.checked })} />
            <span>Only show shared-booking eligible</span>
          </label>
        </div>

        <div className="results-grid storage-grid">
          {filtered.map((facility) => (
            <StorageCard key={facility.id} facility={facility} onSelect={() => onSelectStorage(facility)} />
          ))}
        </div>

        {providerPrices.length ? (
          <section className="price-quote-section">
            <div className="section-heading">
              <span className="eyebrow">Provider quote · converted to USD</span>
              <h2>Left luggage at {airport?.iataCode}</h2>
              <p>Per item. Reference conversion only; provider checkout remains in the original currency.</p>
            </div>
            <div className="price-quote-list">
              {providerPrices.map((quote) => (
                <div className="price-row" key={quote.id}>
                  <span>{quote.duration}</span>
                  <strong>{formatUsd(quote.amount_usd)} <small>({formatCurrency(quote.original_amount, quote.original_currency)})</small></strong>
                </div>
              ))}
            </div>
            <p className="price-provenance">
              Verified {providerPrices[0].verified_at} from <a href={providerPrices[0].source_url} target="_blank" rel="noreferrer">{providerPrices[0].source_name}</a>.
              {' '}Converted at ECB reference rates dated {providerPrices[0].exchange_rate_date || '2026-10-09'}.
              {' '}Rates are indicative, not live availability or provider settlement prices.
            </p>
          </section>
        ) : null}

        {priceStatus === 'loading' ? <p className="price-provenance">Loading provider prices…</p> : null}
        {priceStatus === 'error' ? <div className="alert-box warning-box" role="status">{priceMessage || 'Provider prices could not be loaded.'}</div> : null}
        {priceStatus === 'unavailable' && !filtered.length ? (
          <div className="empty-state">
            <h3>No verified storage price for this airport</h3>
            <p>{priceMessage || 'No provider quote has been added yet. Existing sample prices are limited to their tagged airports.'}</p>
            <Link className="btn btn-secondary small" to="/">Choose another airport</Link>
          </div>
        ) : null}
      </div>
    </main>
  );
}
