import { describe, expect, it } from 'vitest';
import { airports, filterAirports, findAirport } from './airports.js';

describe('airport catalog', () => {
  it('contains unique airport codes and required metadata', () => {
    expect(airports).toHaveLength(72);
    expect(new Set(airports.map((airport) => airport.iataCode)).size).toBe(72);
    expect(new Set(airports.map((airport) => airport.icaoCode)).size).toBe(72);
    expect(airports.every((airport) => airport.name && airport.country && airport.timezone)).toBe(true);
  });

  it('filters by name, city, country, and IATA code', () => {
    expect(filterAirports('London Heathrow').map((airport) => airport.iataCode)).toEqual(['LHR']);
    expect(filterAirports('New York').map((airport) => airport.iataCode).sort()).toEqual(['JFK', 'LGA']);
    expect(filterAirports('United States').some((airport) => airport.iataCode === 'SFO')).toBe(true);
    expect(filterAirports('JFK')[0].name).toBe('John F. Kennedy International Airport');
  });

  it('resolves legacy cities without guessing when the city has multiple airports', () => {
    expect(findAirport('Delhi').iataCode).toBe('DEL');
    expect(findAirport('London Heathrow Airport').iataCode).toBe('LHR');
    expect(findAirport('New York')).toBeNull();
  });
});
