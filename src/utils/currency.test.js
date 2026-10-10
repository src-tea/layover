import { describe, expect, it } from 'vitest';
import { formatUsd, toMinorUnits, toUsdMinorUnits } from './currency.js';

describe('USD money utilities', () => {
  it('formats amounts consistently with two fractional digits', () => {
    expect(formatUsd('25')).toBe('$25.00');
    expect(formatUsd('149.99')).toBe('$149.99');
    expect(formatUsd('1250')).toBe('$1,250.00');
  });

  it('rounds source amounts to cents without binary floating point', () => {
    expect(toMinorUnits('1.005')).toBe(101);
    expect(toMinorUnits('0.10') + toMinorUnits('0.20')).toBe(30);
  });

  it('converts INR and GBP with the dated ECB reference snapshot', () => {
    expect(toUsdMinorUnits('600', 'INR')).toBe(620);
    expect(toUsdMinorUnits('10', 'GBP')).toBe(1322);
    expect(() => toUsdMinorUnits('10', 'EUR')).toThrow('Unsupported currency conversion');
  });
});