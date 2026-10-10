import { describe, expect, it } from 'vitest';
import { findMatches } from './matching.js';

describe('matching logic', () => {
  it('finds compatible travellers for overlapping layovers', () => {
    const travellers = [
      {
        id: 't1',
        airport: 'Delhi',
        arrival: '2026-10-10T08:00',
        departure: '2026-10-10T14:00',
        baggage: 'Carry-on',
        budget: 450,
        interests: ['food', 'sightseeing'],
      },
      {
        id: 't2',
        airport: 'Delhi',
        arrival: '2026-10-10T09:00',
        departure: '2026-10-10T16:00',
        baggage: 'Carry-on',
        budget: 500,
        interests: ['food'],
      },
      {
        id: 't3',
        airport: 'Kochi',
        arrival: '2026-10-10T08:30',
        departure: '2026-10-10T12:30',
        baggage: 'Carry-on',
        budget: 300,
        interests: ['culture'],
      },
    ];

    const search = {
      airport: 'Delhi',
      arrival: '2026-10-10T07:30',
      departure: '2026-10-10T15:30',
      baggage: 'Carry-on',
      budget: 600,
      interests: ['food'],
    };

    const matches = findMatches(search, travellers);
    expect(matches.length).toBeGreaterThanOrEqual(1);
    expect(matches[0].id).toBe('t2');
  });

  it('rejects travellers whose layover does not overlap', () => {
    const travellers = [{
      id: 't1',
      airport: 'Delhi',
      arrival: '2026-10-10T18:00',
      departure: '2026-10-10T20:00',
      baggage: 'Checked',
      budget: 450,
      interests: ['shopping'],
    }];

    const search = {
      airport: 'Delhi',
      arrival: '2026-10-10T08:00',
      departure: '2026-10-10T09:00',
      baggage: 'Carry-on',
      budget: 600,
      interests: ['food'],
    };

    const matches = findMatches(search, travellers);
    expect(matches).toEqual([]);
  });
});
