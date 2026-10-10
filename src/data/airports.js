import airportCatalog from '../../data/airports.json';

const legacyAirportAliases = {
  bengaluru: 'BLR',
  delhi: 'DEL',
  kochi: 'COK',
  mumbai: 'BOM',
  singapore: 'SIN',
};

export const airports = airportCatalog.airports.map((record) => {
  const [iataCode, icaoCode, name, city, country, countryCode, latitude, longitude, timezone, type] = record;
  return { iataCode, icaoCode, name, city, country, countryCode, latitude, longitude, timezone, type };
});

export function findAirport(value) {
  const normalized = String(value || '').trim().toLocaleLowerCase();
  if (!normalized) return null;
  const aliasCode = legacyAirportAliases[normalized];
  if (aliasCode) return airports.find((airport) => airport.iataCode === aliasCode) || null;
  const codeOrName = airports.find((airport) => [airport.iataCode, airport.icaoCode, airport.name]
    .some((field) => field.toLocaleLowerCase() === normalized));
  if (codeOrName) return codeOrName;
  const cityOrCountry = airports.filter((airport) => [airport.city, airport.country]
    .some((field) => field.toLocaleLowerCase() === normalized));
  return cityOrCountry.length === 1 ? cityOrCountry[0] : null;
}

export function filterAirports(query) {
  const terms = String(query || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return airports;
  return airports.filter((airport) => {
    const searchText = [airport.iataCode, airport.icaoCode, airport.name, airport.city, airport.country]
      .join(' ')
      .toLocaleLowerCase();
    return terms.every((term) => searchText.includes(term));
  });
}