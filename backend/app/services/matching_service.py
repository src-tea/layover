from __future__ import annotations

from typing import Any

from app.services.airport_service import load_airport_catalog, resolve_airport
from app.utils.time_utils import overlap_minutes, parse_datetime


def _canonical_airport_code(value: str | None) -> str:
    if not value:
        return ""
    airport = resolve_airport(load_airport_catalog()["airports"], value)
    return airport["iata_code"] if airport else value.upper()


def _baggage_weight(value: str) -> int:
    mapping = {"light": 1, "medium": 2, "heavy": 3}
    return mapping.get((value or "medium").lower(), 2)


def _shared_interests_score(layover_a: dict[str, Any], layover_b: dict[str, Any]) -> int:
    interests_a = set((layover_a.get("interests") or [])[:])
    interests_b = set((layover_b.get("interests") or [])[:])
    if not interests_a or not interests_b:
        return 0
    overlap = interests_a & interests_b
    union = interests_a | interests_b
    if not union:
        return 0
    return int(round((len(overlap) / len(union)) * 20))


def _baggage_similarity_score(layover_a: dict[str, Any], layover_b: dict[str, Any]) -> int:
    delta = abs(_baggage_weight(layover_a.get("baggage_size")) - _baggage_weight(layover_b.get("baggage_size")))
    if delta == 0:
        return 20
    if delta == 1:
        return 10
    return 0


def calculate_match_score(layover_a: dict[str, Any], layover_b: dict[str, Any]) -> int:
    if not layover_a or not layover_b:
        return 0
    if _canonical_airport_code(layover_a.get("airport_code")) != _canonical_airport_code(layover_b.get("airport_code")):
        return 0

    arrival_a = parse_datetime(layover_a["arrival_time"])
    departure_a = parse_datetime(layover_a["departure_time"])
    arrival_b = parse_datetime(layover_b["arrival_time"])
    departure_b = parse_datetime(layover_b["departure_time"])

    shared_minutes = overlap_minutes(arrival_a, departure_a, arrival_b, departure_b)
    if shared_minutes < 60:
        return 0

    schedule_score = min(60, int((shared_minutes / 180) * 60))
    baggage_score = _baggage_similarity_score(layover_a, layover_b)
    interest_score = _shared_interests_score(layover_a, layover_b)
    total = schedule_score + baggage_score + interest_score
    return min(100, total)


def find_candidates(layovers_a, layovers_b):
    results = []
    seen = set()
    for first in layovers_a:
        for second in layovers_b:
            first_id = first.get("id")
            second_id = second.get("id")
            if first_id is not None and second_id is not None and first_id == second_id:
                continue
            first_user = first.get("user_id")
            second_user = second.get("user_id")
            if first_user and second_user and first_user == second_user:
                continue
            score = calculate_match_score(first, second)
            if score <= 0:
                continue
            pair_key = tuple(sorted([
                str(first.get("id") or id(first)),
                str(second.get("id") or id(second)),
            ]))
            if pair_key in seen:
                continue
            seen.add(pair_key)
            results.append({
                "id": f"match-{len(results) + 1}",
                "user_id": second.get("user_id"),
                "candidate_layover_id": second.get("id"),
                "airport_code": second.get("airport_code"),
                "score": score,
                "shared_minutes": overlap_minutes(
                    parse_datetime(first["arrival_time"]),
                    parse_datetime(first["departure_time"]),
                    parse_datetime(second["arrival_time"]),
                    parse_datetime(second["departure_time"]),
                ),
                "baggage_match": _baggage_similarity_score(first, second),
                "interest_match": _shared_interests_score(first, second),
            })
    return sorted(results, key=lambda item: item["score"], reverse=True)
