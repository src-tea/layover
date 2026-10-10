import pricingData from '../../data/pricing.json';

function decimalFraction(value) {
  const [whole, fraction = ''] = String(value).split('.');
  const denominator = 10n ** BigInt(fraction.length);
  return { numerator: BigInt(whole) * denominator + BigInt(fraction || '0'), denominator };
}

function divideFractions(first, second) {
  return {
    numerator: first.numerator * second.denominator,
    denominator: first.denominator * second.numerator,
  };
}

const rates = pricingData.exchange_rate_snapshot;
const usdPerEur = decimalFraction(rates.usd_per_eur);
const exchangeRates = {
  snapshotDate: rates.date,
  source: rates.source,
  sourceUrl: rates.source_url,
  usdPerInr: divideFractions(usdPerEur, decimalFraction(rates.inr_per_eur)),
  usdPerGbp: divideFractions(usdPerEur, decimalFraction(rates.gbp_per_eur)),
};

export function toMinorUnits(value) {
  const text = String(value ?? 0).trim();
  const match = text.match(/^(-?)(\d+)(?:\.(\d*))?$/);
  if (!match) throw new TypeError(`Invalid monetary amount: ${text}`);

  const [, sign, whole, fraction = ''] = match;
  const cents = Number((fraction + '00').slice(0, 2));
  const roundUp = Number((fraction + '000').charAt(2)) >= 5;
  const absolute = BigInt(whole) * 100n + BigInt(cents) + (roundUp ? 1n : 0n);
  const result = Number(sign === '-' ? -absolute : absolute);
  if (!Number.isSafeInteger(result)) throw new RangeError('Monetary amount exceeds the safe minor-unit range');
  return result;
}

function roundRatio(numerator, denominator) {
  const isNegative = numerator < 0n;
  const absolute = isNegative ? -numerator : numerator;
  const rounded = (absolute + denominator / 2n) / denominator;
  return Number(isNegative ? -rounded : rounded);
}

export function toUsdMinorUnits(value, currency = 'USD') {
  const minorUnits = BigInt(toMinorUnits(value));
  const normalizedCurrency = String(currency || 'USD').toUpperCase();
  if (normalizedCurrency === 'USD') return Number(minorUnits);

  const rate = normalizedCurrency === 'INR'
    ? exchangeRates.usdPerInr
    : normalizedCurrency === 'GBP'
      ? exchangeRates.usdPerGbp
      : null;
  if (!rate) throw new RangeError(`Unsupported currency conversion: ${normalizedCurrency}`);
  return roundRatio(minorUnits * rate.numerator, rate.denominator);
}

export function fromMinorUnits(minorUnits) {
  return Number(minorUnits) / 100;
}

export function toUsd(value, currency = 'USD') {
  return fromMinorUnits(toUsdMinorUnits(value, currency));
}

export function formatUsd(value) {
  const amount = fromMinorUnits(toMinorUnits(value));
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatCurrency(value, currency) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

export function formatConvertedUsd(value, sourceCurrency) {
  return formatUsd(toUsd(value, sourceCurrency));
}

export function conversionSnapshot() {
  return {
    date: exchangeRates.snapshotDate,
    source: exchangeRates.source,
    sourceUrl: exchangeRates.sourceUrl,
  };
}
