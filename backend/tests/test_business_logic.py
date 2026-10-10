from datetime import datetime, timedelta, timezone

from app.services.matching_service import calculate_match_score, find_candidates
from app.services.pricing_service import estimate_storage_quote
from app.services.booking_service import validate_booking_request
from app.utils.time_utils import calculate_usable_window_minutes


def test_usable_time_matches_spec_example():
    assert calculate_usable_window_minutes(480, 60, 60) == 360
    assert calculate_usable_window_minutes(480, 30, 30) == 420
    assert calculate_usable_window_minutes(480, 90, 90) == 300


def test_matching_score_and_candidates():
    layover_a = {
        "airport_code": "DXB",
        "arrival_time": "2025-01-01T12:00:00+00:00",
        "departure_time": "2025-01-01T18:00:00+00:00",
        "interests": ["food", "shopping", "spa"],
        "baggage_size": "medium",
    }
    layover_b = {
        "airport_code": "DXB",
        "arrival_time": "2025-01-01T15:00:00+00:00",
        "departure_time": "2025-01-01T19:00:00+00:00",
        "interests": ["food", "shopping", "museum"],
        "baggage_size": "medium",
    }
    score = calculate_match_score(layover_a, layover_b)
    assert score >= 60
    candidates = find_candidates([layover_a], [layover_b])
    assert len(candidates) == 1
    assert candidates[0]["score"] >= 60


def test_matching_keeps_legacy_city_names_compatible_with_iata_codes():
    legacy_layover = {
        "airport_code": "Delhi",
        "arrival_time": "2025-01-01T12:00:00+00:00",
        "departure_time": "2025-01-01T18:00:00+00:00",
        "interests": ["food"],
        "baggage_size": "medium",
    }
    coded_layover = {
        **legacy_layover,
        "airport_code": "DEL",
        "arrival_time": "2025-01-01T14:00:00+00:00",
        "departure_time": "2025-01-01T20:00:00+00:00",
    }
    assert calculate_match_score(legacy_layover, coded_layover) > 0


def test_pricing_quote_honors_sharing_rules():
    facility = {
        "id": "locker-1",
        "name": "Terminal Lockers",
        "base_price": 24.0,
        "sharing_allowed": True,
        "share_min_users": 2,
        "share_max_users": 4,
        "currency": "USD",
    }
    quote = estimate_storage_quote(facility, 2, 2)
    assert quote["solo_price"] == 24.0
    assert quote["per_person_price"] < quote["solo_price"]
    assert quote["savings_percent"] > 0


def test_booking_validation_rejects_invalid_window():
    layover = {
        "id": "layover-1",
        "airport_code": "LHR",
        "arrival_time": "2025-01-01T10:00:00+00:00",
        "departure_time": "2025-01-01T18:00:00+00:00",
    }
    facility = {
        "id": "facility-1",
        "opening_hours": {"start": "08:00", "end": "20:00"},
        "max_group_size": 4,
    }
    request = {
        "layover_id": "layover-1",
        "facility_id": "facility-1",
        "start_time": "2025-01-01T09:00:00+00:00",
        "end_time": "2025-01-01T10:30:00+00:00",
        "members": ["u1", "u2"],
    }
    error = validate_booking_request(request, layover, facility)
    assert error is not None
    assert "inside the layover" in error.lower()
