from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.services.airport_service import load_airport_catalog, resolve_airport, search_airports
from app.services.currency_service import convert_to_usd
from app.services.pricing_service import estimate_storage_quote


client = TestClient(app)


def test_airport_catalog_codes_coordinates_and_requested_regions():
    catalog = load_airport_catalog()
    airports = catalog["airports"]
    iata_codes = [airport["iata_code"] for airport in airports]

    assert len(airports) == 72
    assert len(set(iata_codes)) == len(iata_codes)
    assert {"LHR", "CDG", "AMS", "FRA", "JFK", "EWR", "LAX", "SFO", "ORD", "DFW", "ATL", "SEA"} <= set(iata_codes)
    assert all(-90 <= airport["latitude"] <= 90 for airport in airports)
    assert all(-180 <= airport["longitude"] <= 180 for airport in airports)
    assert all(airport["timezone"] for airport in airports)


def test_airport_search_matches_name_city_country_and_iata():
    airports = load_airport_catalog()["airports"]
    assert [airport["iata_code"] for airport in search_airports(airports, "London Heathrow")] == ["LHR"]
    assert {airport["iata_code"] for airport in search_airports(airports, "New York")} == {"JFK", "LGA"}
    assert {airport["iata_code"] for airport in search_airports(airports, "United States")}
    assert resolve_airport(airports, "Delhi")["iata_code"] == "DEL"
    assert resolve_airport(airports, "lhr")["iata_code"] == "LHR"
    assert resolve_airport(airports, "London") is None


def test_airport_and_price_api_contracts():
    airports_response = client.get("/api/airports", params={"q": "Paris Charles de Gaulle"})
    assert airports_response.status_code == 200
    assert airports_response.json()["items"][0]["iata_code"] == "CDG"

    known_quote_response = client.get("/api/storage/prices", params={"airport_code": "LHR"})
    assert known_quote_response.status_code == 200
    quote_payload = known_quote_response.json()
    assert quote_payload["currency"] == "USD"
    assert quote_payload["status"] == "provider_quoted"
    assert len(quote_payload["items"]) == 6
    assert quote_payload["items"][0]["original_currency"] == "GBP"
    assert quote_payload["items"][0]["source_url"].startswith("https://")
    assert quote_payload["items"][0]["verified_at"] == "2026-10-11"

    unavailable_response = client.get("/api/storage/prices", params={"airport_code": "JFK"})
    assert unavailable_response.status_code == 200
    assert unavailable_response.json()["status"] == "unavailable"


def test_layover_api_canonicalizes_airports_and_rejects_unknown_codes():
    response = client.post("/api/layovers", json={
        "airport_code": "Delhi",
        "arrival_time": "2026-11-01T08:00:00Z",
        "departure_time": "2026-11-01T14:00:00Z",
        "budget": "25.50",
        "budget_currency": "USD",
    })
    assert response.status_code == 200
    assert response.json()["item"]["airport_code"] == "DEL"
    assert response.json()["item"]["budget_currency"] == "USD"

    unknown = client.post("/api/layovers", json={
        "airport_code": "ZZZ",
        "arrival_time": "2026-11-01T08:00:00Z",
        "departure_time": "2026-11-01T14:00:00Z",
    })
    assert unknown.status_code == 400


def test_decimal_conversion_and_storage_quote_preserve_source_currency():
    converted_inr, inr_metadata = convert_to_usd("600", "INR")
    converted_gbp, gbp_metadata = convert_to_usd("10", "GBP")
    assert converted_inr == Decimal("6.20")
    assert inr_metadata["original_currency"] == "INR"
    assert inr_metadata["exchange_rate_date"] == "2026-10-09"
    assert converted_gbp == Decimal("13.22")
    assert gbp_metadata["original_amount"] == Decimal("10.00")

    quote = estimate_storage_quote({
        "base_price": "600.00",
        "currency": "INR",
        "sharing_allowed": True,
        "share_min_users": 2,
        "share_max_users": 4,
        "price_status": "illustrative_estimate",
        "price_source_name": "Legacy sample",
    }, group_size=3)
    assert quote["currency"] == "USD"
    assert quote["solo_price"] == Decimal("6.20")
    assert quote["per_person_price"] == Decimal("2.07")
    assert quote["original_currency"] == "INR"
    assert quote["price"]["exchange_rate_date"] == "2026-10-09"


def test_non_usd_without_a_supported_reference_rate_is_not_relabelled():
    try:
        convert_to_usd("10", "EUR")
        assert False, "unsupported currency should not be relabelled"
    except ValueError as error:
        assert "No verified exchange-rate snapshot" in str(error)


def test_missing_storage_currency_is_not_assumed_to_be_usd():
    try:
        estimate_storage_quote({"base_price": "25.00"})
        assert False, "a denomination-free price must not be quoted"
    except ValueError as error:
        assert "Price currency is unknown" in str(error)
