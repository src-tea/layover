import { useEffect, useMemo, useRef, useState } from 'react';
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import MatchesPage from './pages/MatchesPage';
import MatchDetailsPage from './pages/MatchDetailsPage';
import StoragePage from './pages/StoragePage';
import ExplorePage from './pages/ExplorePage';
import ItineraryPage from './pages/ItineraryPage';
import TripsPage from './pages/TripsPage';
import ProfilePage from './pages/ProfilePage';
import BookingPage from './pages/BookingPage';
import AuthPage from './pages/AuthPage';
import { travellers } from './data/travellers';
import { storageFacilities } from './data/storage';
import { findAirport } from './data/airports';
import { readStorage, writeStorage } from './utils/storage';
import { findMatches } from './utils/matching';
import { conversionSnapshot, toUsd } from './utils/currency';
import { apiFetch, normalizeLayoverToTraveller, toApiBaggageSize, toIsoDate } from './lib/api';

const defaultSearch = {
  airport: 'DEL',
  arrival: '2026-10-10T08:00',
  departure: '2026-10-10T14:00',
  bags: 1,
  baggage: 'Carry-on',
  budget: toUsd(450, 'INR'),
  currency: 'USD',
  companion: true,
  interests: ['food', 'sightseeing'],
};

const fxSnapshot = conversionSnapshot();

function readInitialSearch() {
  const storedSearch = readStorage('layover-search', null);
  if (!storedSearch) return defaultSearch;

  const hasSavedBudget = storedSearch.budget !== undefined && storedSearch.budget !== null;
  const legacyCurrency = String(storedSearch.currency || (hasSavedBudget ? 'INR' : 'USD')).toUpperCase();
  const storedAirport = findAirport(storedSearch.airport);
  const budget = hasSavedBudget
    ? legacyCurrency === 'USD' ? Number(storedSearch.budget) : toUsd(storedSearch.budget, legacyCurrency)
    : defaultSearch.budget;
  return {
    ...defaultSearch,
    ...storedSearch,
    airport: storedAirport?.iataCode || storedSearch.airport,
    budget,
    currency: 'USD',
    ...(!hasSavedBudget || legacyCurrency === 'USD' ? {} : {
      budgetOriginalAmount: storedSearch.budget,
      budgetOriginalCurrency: legacyCurrency,
      budgetConversionRateDate: fxSnapshot.date,
    }),
  };
}

function readInitialStorage() {
  const savedFacility = readStorage('layover-selected-storage', storageFacilities[0]);
  const canonicalFacility = storageFacilities.find((facility) => facility.id === savedFacility?.id);
  if (canonicalFacility) return { ...savedFacility, ...canonicalFacility };
  if (!savedFacility || savedFacility.currency === 'USD') return savedFacility || storageFacilities[0];
  return {
    ...savedFacility,
    price: toUsd(savedFacility.price, savedFacility.currency || 'INR'),
    currency: 'USD',
    originalPrice: savedFacility.price,
    originalCurrency: savedFacility.currency || 'INR',
    priceConversionRateDate: fxSnapshot.date,
  };
}

function readInitialBookings() {
  return readStorage('layover-bookings', []).map((booking) => {
    if (booking.currency === 'USD') return booking;
    const originalCurrency = booking.currency || 'INR';
    return {
      ...booking,
      originalPrice: booking.price,
      originalCurrency,
      price: toUsd(booking.price, originalCurrency),
      currency: 'USD',
      priceConversionRateDate: fxSnapshot.date,
    };
  });
}

function readInitialMatch() {
  const selectedMatch = readStorage('layover-selected-match', travellers[0]);
  if (!selectedMatch || selectedMatch.budgetCurrency === 'USD') return selectedMatch;
  const originalCurrency = selectedMatch.budgetCurrency || 'INR';
  return {
    ...selectedMatch,
    budget: toUsd(selectedMatch.budget || 0, originalCurrency),
    budgetCurrency: 'USD',
    originalBudget: selectedMatch.budget,
    originalBudgetCurrency: originalCurrency,
    cost: selectedMatch.cost === undefined ? undefined : toUsd(selectedMatch.cost, originalCurrency),
  };
}

export default function App() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const discoveryRefreshSequence = useRef(0);
  const [search, setSearch] = useState(readInitialSearch);
  const [selectedMatch, setSelectedMatch] = useState(readInitialMatch);
  const [selectedStorage, setSelectedStorage] = useState(readInitialStorage);
  const [bookings, setBookings] = useState(readInitialBookings);
  const [authUser, setAuthUser] = useState(() => readStorage('layover-auth-user', null));
  const [connectionRequests, setConnectionRequests] = useState({ incoming: [], outgoing: [], active: [] });
  const [connectionMessage, setConnectionMessage] = useState('');
  const [itineraryActivities, setItineraryActivities] = useState(() => readStorage('layover-itinerary', []));
  const [backendTravellers, setBackendTravellers] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  async function refreshDiscovery() {
    const sequence = ++discoveryRefreshSequence.current;
    try {
      const response = await apiFetch('/layovers');
      if (sequence !== discoveryRefreshSequence.current) return;
      const items = Array.isArray(response?.items) ? response.items : [];
      setBackendTravellers(items.map((item, index) => normalizeLayoverToTraveller(item, index)));
    } catch (error) {
      if (sequence !== discoveryRefreshSequence.current) return;
      console.info('Backend not available, using local demo data:', error.message);
      setBackendTravellers([]);
    }

    if (!authUser?.id) {
      setConnectionRequests({ incoming: [], outgoing: [], active: [] });
      return;
    }

    try {
      const response = await apiFetch('/auth/connections');
      if (sequence !== discoveryRefreshSequence.current) return;
      setConnectionRequests({
        incoming: response.incoming || [],
        outgoing: response.outgoing || [],
        active: response.active || [],
      });
    } catch (error) {
      if (sequence !== discoveryRefreshSequence.current) return;
      setConnectionMessage(error.message || 'Unable to refresh your connection requests.');
    }
  }

  useEffect(() => {
    refreshDiscovery();
  }, [authUser?.id]);

  useEffect(() => {
    if (pathname !== '/matches' && pathname !== '/buddy') return undefined;
    const refreshId = window.setInterval(refreshDiscovery, 5000);
    return () => window.clearInterval(refreshId);
  }, [pathname, authUser?.id]);

  const matches = useMemo(() => {
    const activeTravellers = backendTravellers.length ? backendTravellers : travellers;
    return findMatches(search, activeTravellers);
  }, [backendTravellers, search]);
  const matchCandidates = authUser
    ? backendTravellers.filter((traveller) => traveller.userId !== authUser.id)
    : travellers;

  useEffect(() => {
    writeStorage('layover-search', search);
  }, [search]);

  useEffect(() => {
    writeStorage('layover-selected-match', selectedMatch);
  }, [selectedMatch]);

  useEffect(() => {
    writeStorage('layover-selected-storage', selectedStorage);
  }, [selectedStorage]);

  useEffect(() => {
    writeStorage('layover-bookings', bookings);
  }, [bookings]);

  useEffect(() => {
    writeStorage('layover-itinerary', itineraryActivities);
  }, [itineraryActivities]);

  useEffect(() => {
    writeStorage('layover-auth-user', authUser);
  }, [authUser]);

  function validateSearch(values) {
    const errors = {};

    if (!values.airport) errors.airport = 'Please choose an airport.';
    if (!values.arrival) errors.arrival = 'Arrival time is required.';
    if (!values.departure) errors.departure = 'Departure time is required.';
    if (values.arrival && values.departure && new Date(values.departure) <= new Date(values.arrival)) {
      errors.departure = 'Departure must be later than arrival.';
    }
    if (!values.bags || Number(values.bags) < 1) errors.bags = 'At least one bag is required.';
    if (!Number.isFinite(Number(values.budget)) || Number(values.budget) <= 0) errors.budget = 'Set a maximum budget above zero.';
    if (!findAirport(values.airport)) errors.airport = 'Choose a listed airport or enter its IATA code.';

    return errors;
  }

  async function handleSearchSubmit(values) {
    const errors = validateSearch(values);

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setFormErrors({});
    setIsSearching(true);

    try {
      const payload = {
        airport_code: findAirport(values.airport).iataCode,
        arrival_time: toIsoDate(values.arrival),
        departure_time: toIsoDate(values.departure),
        baggage_size: toApiBaggageSize(values.baggage || 'Carry-on'),
        interests: values.interests || [],
        budget: Number(values.budget),
        budget_currency: 'USD',
      };

      const createdLayover = await apiFetch('/layovers', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      if (createdLayover?.item) {
        setBackendTravellers((current) => [normalizeLayoverToTraveller(createdLayover.item, current.length), ...current]);
      }
    } catch (error) {
      console.info('API create failed, falling back to local demo state:', error.message);
    }

    setSearch({ ...values, airport: findAirport(values.airport).iataCode, currency: 'USD' });
    setIsSearching(false);
    navigate('/matches');
  }

  function handleViewMatch(match) {
    setSelectedMatch(match);
    navigate('/matches/' + match.id);
  }

  async function handleConnect(match) {
    if (!authUser?.id) {
      navigate('/login');
      return;
    }
    if (!match.userId) {
      setConnectionMessage('This traveller is not available for connection requests.');
      return;
    }

    setConnectionMessage('');
    try {
      await apiFetch('/auth/connections/request', {
        method: 'POST',
        body: JSON.stringify({ target_user_id: match.userId }),
      });
      setConnectionMessage(`Connection request sent to ${match.name}.`);
      await refreshDiscovery();
    } catch (error) {
      setConnectionMessage(error.message || 'Unable to send the connection request.');
      await refreshDiscovery();
    }
  }

  async function handleRespondToRequest(request, status) {
    setConnectionMessage('');
    try {
      await apiFetch(`/auth/connections/${request.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      });
      setConnectionMessage(status === 'accepted' ? 'Connection confirmed.' : 'Connection request updated.');
      await refreshDiscovery();
    } catch (error) {
      setConnectionMessage(error.message || 'Unable to update the connection request.');
      await refreshDiscovery();
    }
  }

  async function handleDisconnect(connection) {
    setConnectionMessage('');
    try {
      await apiFetch(`/auth/connections/${connection.id}/disconnect`, { method: 'POST' });
      setConnectionMessage('Connection ended. You will not be rematched automatically.');
      await refreshDiscovery();
    } catch (error) {
      setConnectionMessage(error.message || 'Unable to disconnect this pair.');
    }
  }

  function handleSelectStorage(facility) {
    setSelectedStorage(facility);
    navigate('/booking');
  }

  function handleConfirmBooking(booking) {
    setBookings((current) => [
      {
        ...booking,
        currency: 'USD',
        id: booking.ref || `booking-${Date.now()}`,
      },
      ...current,
    ]);
    navigate('/trips');
  }

  function handleCancelBooking(id) {
    setBookings((current) => current.filter((item) => item.id !== id));
  }

  function handleAddActivity(place) {
    setItineraryActivities((current) => {
      const exists = current.includes(place.id);
      return exists ? current : [...current, place.id];
    });
    navigate('/itinerary');
  }

  return (
    <>
      <Navbar />
      <Routes>
        <Route
          path="/"
          element={
            <LandingPage
              search={search}
              setSearch={setSearch}
              onSubmit={handleSearchSubmit}
              errors={formErrors}
              isLoading={isSearching}
            />
          }
        />
        <Route
          path="/buddy"
          element={
            <MatchesPage
              search={search}
              candidates={matchCandidates}
              connectionRequests={connectionRequests}
              connectionMessage={connectionMessage}
              onViewMatch={handleViewMatch}
              onConnect={handleConnect}
              onRespondToRequest={handleRespondToRequest}
              onDisconnect={handleDisconnect}
              onReset={() => {
                setSearch(defaultSearch);
                navigate('/');
              }}
            />
          }
        />
        <Route
          path="/matches"
          element={
            <MatchesPage
              search={search}
              candidates={matchCandidates}
              connectionRequests={connectionRequests}
              connectionMessage={connectionMessage}
              onViewMatch={handleViewMatch}
              onConnect={handleConnect}
              onRespondToRequest={handleRespondToRequest}
              onDisconnect={handleDisconnect}
              onReset={() => {
                setSearch(defaultSearch);
                navigate('/');
              }}
            />
          }
        />
        <Route
          path="/matches/:id"
          element={
            <MatchDetailsPage
              match={selectedMatch || matches[0] || null}
              search={search}
              onSelectStorage={() => handleSelectStorage(storageFacilities[0])}
              onConnect={handleConnect}
            />
          }
        />
        <Route path="/storage" element={<StoragePage airportCode={search.airport} onSelectStorage={handleSelectStorage} />} />
        <Route path="/explore" element={<ExplorePage airportCode={search.airport} onAddActivity={handleAddActivity} />} />
        <Route path="/itinerary" element={<ItineraryPage search={search} activities={itineraryActivities} />} />
        <Route path="/layover" element={<TripsPage bookings={bookings} onCancel={handleCancelBooking} />} />
        <Route path="/trips" element={<TripsPage bookings={bookings} onCancel={handleCancelBooking} />} />
        <Route path="/login" element={<AuthPage onAuthenticated={(user) => {
          setAuthUser(user);
          navigate('/matches');
        }} />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route
          path="/booking"
          element={
            <BookingPage
              search={search}
              selectedStorage={selectedStorage}
              selectedMatch={selectedMatch}
              onConfirmBooking={handleConfirmBooking}
            />
          }
        />
      </Routes>
      <Footer />
    </>
  );
}
