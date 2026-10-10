import pricingData from '../../data/pricing.json';

const legacyPrices = new Map(pricingData.legacy_estimates.map((record) => [record.id, record]));

const legacyActivities = [
  {
    id: 'attraction-1',
    name: 'Connaught Place',
    airportCode: 'DEL',
    category: 'Sights',
    duration: '90 min',
    durationMinutes: 90,
    travelTime: '15 min',
    priceEstimateId: null,
    window: 'Morning to late afternoon',
  },
  {
    id: 'attraction-2',
    name: 'Chandni Chowk Food Walk',
    airportCode: 'DEL',
    category: 'Food',
    duration: '75 min',
    durationMinutes: 75,
    travelTime: '20 min',
    priceEstimateId: 'attraction-2',
    window: 'Late morning',
  },
  {
    id: 'attraction-3',
    name: 'National Museum',
    airportCode: 'DEL',
    category: 'Culture',
    duration: '120 min',
    durationMinutes: 120,
    travelTime: '25 min',
    priceEstimateId: 'attraction-3',
    window: 'Afternoon',
  },
  {
    id: 'attraction-4',
    name: 'Local Market Trail',
    airportCode: 'DEL',
    category: 'Shopping',
    duration: '60 min',
    durationMinutes: 60,
    travelTime: '18 min',
    priceEstimateId: 'attraction-4',
    window: 'Any time',
  },
  {
    id: 'attraction-5',
    name: 'Fort Kochi Walk',
    airportCode: 'COK',
    category: 'Sights',
    duration: '100 min',
    durationMinutes: 100,
    travelTime: '22 min',
    priceEstimateId: 'attraction-5',
    window: 'Late afternoon',
  },
  {
    id: 'attraction-6',
    name: 'Tea House & Heritage Route',
    airportCode: 'COK',
    category: 'Culture',
    duration: '70 min',
    durationMinutes: 70,
    travelTime: '15 min',
    priceEstimateId: 'attraction-6',
    window: 'Morning',
  },
];

export const attractions = legacyActivities.map((activity) => {
  const priceSource = activity.priceEstimateId ? legacyPrices.get(activity.priceEstimateId) : null;
  return {
    ...activity,
    price: priceSource?.amount_usd ?? null,
    currency: 'USD',
    priceStatus: priceSource?.status || 'unavailable',
    priceSource,
  };
});
