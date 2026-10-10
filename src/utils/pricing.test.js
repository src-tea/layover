import { describe, expect, it } from 'vitest';
import { calculateSharedCost } from './pricing.js';

describe('pricing logic', () => {
  it('splits a shared storage cost evenly between eligible participants', () => {
    const result = calculateSharedCost({ totalPrice: 600, eligibleParticipants: 2, soloPrice: 600, platformFee: 0 });
    expect(result.perParticipant).toBe(300);
    expect(result.savings).toBe(300);
    expect(result.finalTotal).toBe(300);
  });

  it('includes a demo fee when configured', () => {
    const result = calculateSharedCost({ totalPrice: 600, eligibleParticipants: 2, soloPrice: 600, platformFee: 40 });
    expect(result.platformFee).toBe(40);
    expect(result.finalTotal).toBe(340);
  });

  it('splits uneven cents with deterministic half-up rounding', () => {
    const result = calculateSharedCost({ totalPrice: 10, eligibleParticipants: 3, soloPrice: 10 });
    expect(result.perParticipant).toBe(3.33);
    expect(result.finalTotal).toBe(3.33);
  });
});
