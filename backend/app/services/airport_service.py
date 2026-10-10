from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


CATALOG_PATH = Path(__file__).resolve().parents[3] / "data" / "airports.json"


@lru_cache(maxsize=1)
def load_airport_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open(encoding="utf-8") as catalog_file:
        raw_catalog = json.load(catalog_file)

    fields = raw_catalog["fields"]
    airports = [dict(zip(fields, row, strict=True)) for row in raw_catalog["airports"]]
    seen_codes: set[str] = set()
    seen_icao_codes: set[str] = set()
    for airport in airports:
        iata_code = airport["iata_code"]
        icao_code = airport.get("icao_code")
        if not re.fullmatch(r"[A-Z]{3}", iata_code) or iata_code in seen_codes:
            raise ValueError(f"Invalid or duplicate IATA airport code: {iata_code}")
        if icao_code and icao_code in seen_icao_codes:
            raise ValueError(f"Duplicate ICAO airport code: {icao_code}")
        if not -90 <= airport["latitude"] <= 90 or not -180 <= airport["longitude"] <= 180:
            raise ValueError(f"Invalid coordinates for airport {iata_code}")
        try:
            ZoneInfo(airport["timezone"])
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Invalid timezone for airport {iata_code}") from exc
        seen_codes.add(iata_code)
        if icao_code:
            seen_icao_codes.add(icao_code)

    return {"source": raw_catalog["source"], "airports": airports}


def airport_search_text(airport: dict[str, Any]) -> str:
    return " ".join(str(airport.get(field) or "") for field in (
        "iata_code", "icao_code", "name", "city", "country", "country_code",
    )).casefold()


def search_airports(airports: list[dict[str, Any]], query: str | None = None) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return sorted(airports, key=lambda airport: (airport["city"], airport["name"]))
    terms = query.casefold().strip().split()
    return [
        airport for airport in airports
        if all(term in airport_search_text(airport) for term in terms)
    ]


def resolve_airport(airports: list[dict[str, Any]], value: str) -> dict[str, Any] | None:
    normalized = value.strip().casefold()
    exact_code = next((airport for airport in airports if airport["iata_code"].casefold() == normalized), None)
    if exact_code:
        return exact_code

    exact_text = [
        airport for airport in airports
        if normalized in {
            airport["name"].casefold(), airport["city"].casefold(), airport["country"].casefold(),
        }
    ]
    if len(exact_text) == 1:
        return exact_text[0]

    legacy_city_aliases = {
        "bengaluru": "BLR",
        "delhi": "DEL",
        "kochi": "COK",
        "mumbai": "BOM",
        "singapore": "SIN",
    }
    if code := legacy_city_aliases.get(normalized):
        return next((airport for airport in airports if airport["iata_code"] == code), None)

    matches = search_airports(airports, value)
    return matches[0] if len(matches) == 1 else None
