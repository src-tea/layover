import { findAirport } from '../data/airports';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8001/api' : '');

export async function apiFetch(path, options = {}) {
  if (!API_BASE_URL) {
    throw new Error('The LAYOVER API is not configured for this deployment.');
  }

  const authToken = localStorage.getItem('layover-auth-token');
  const response = await fetch(`${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const responseText = await response.text();
    let message = responseText;

    try {
      const payload = JSON.parse(responseText);
      message = payload.detail || payload.message || responseText;
    } catch {
      // Keep plain-text errors readable when the server does not return JSON.
    }

    const error = new Error(message || `Request failed with status ${response.status}`);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

export function toIsoDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

export function toApiBaggageSize(value) {
  const normalized = String(value || 'Carry-on').trim().toLowerCase().replace(/\s+/g, '-');
  const mapping = {
    'carry-on': 'light',
    'carry-on-1': 'light',
    'checked': 'medium',
    'oversized': 'heavy',
    'any': 'medium',
    'light': 'light',
    'medium': 'medium',
    'heavy': 'heavy',
  };

  return mapping[normalized] || 'medium';
}

export function fromApiBaggageSize(value) {
  const normalized = String(value || 'medium').trim().toLowerCase();
  const mapping = {
    light: 'Carry-on',
    medium: 'Checked',
    heavy: 'Oversized',
  };

  return mapping[normalized] || 'Checked';
}

export function normalizeLayoverToTraveller(layover, index = 0) {
  const arrival = layover.arrival_time || layover.arrival || new Date(Date.now() + 1000 * 60 * 60 * 2).toISOString();
  const departure = layover.departure_time || layover.departure || new Date(Date.now() + 1000 * 60 * 60 * 6).toISOString();

  const airport = findAirport(layover.airport_code || layover.airport);

  return {
    id: layover.id || `api-traveller-${index}`,
    userId: layover.user_id || null,
    name: layover.full_name || layover.user_name || `Traveller ${index + 1}`,
    airport: airport?.name || layover.airport_code || layover.airport || 'DXB',
    airportCode: airport?.iataCode || layover.airport_code || null,
    arrival,
    departure,
    baggage: fromApiBaggageSize(layover.baggage_size || layover.baggage || 'Carry-on'),
    budget: layover.budget ?? 450,
    budgetCurrency: layover.budget_currency || (layover.budget == null ? 'INR' : 'USD'),
    interests: layover.interests || [],
    sharedStorage: true,
    score: 0,
  };
}
