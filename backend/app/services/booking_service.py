from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.services.pricing_service import estimate_storage_quote
from app.utils.time_utils import parse_datetime


def validate_booking_request(request: dict, layover: dict, facility: dict) -> str | None:
    if not request:
        return "Booking request is empty"

    start_dt = parse_datetime(request["start_time"])
    end_dt = parse_datetime(request["end_time"])
    layover_start = parse_datetime(layover["arrival_time"])
    layover_end = parse_datetime(layover["departure_time"])

    if end_dt <= start_dt:
        return "Booking end time must be after the start time"

    if start_dt < layover_start or end_dt > layover_end:
        return "Booking window must sit inside the layover"

    if start_dt < datetime.utcnow() or end_dt < datetime.utcnow():
        return "Booking cannot be in the past"

    opening = facility.get("opening_hours", {})
    if opening:
        start_h = opening.get("start", "00:00")
        end_h = opening.get("end", "23:59")
        opening_start = datetime.strptime(f"{start_dt.date()} {start_h}", "%Y-%m-%d %H:%M")
        opening_end = datetime.strptime(f"{start_dt.date()} {end_h}", "%Y-%m-%d %H:%M")
        if start_dt < opening_start or end_dt > opening_end:
            return "Booking must fall within the facility opening hours"

    members = request.get("members") or []
    max_group = int(facility.get("max_group_size") or facility.get("share_max_users") or 1)
    if len(members) > max_group:
        return "Group size exceeds the maximum allowed for this facility"

    return None


def compute_booking_total(request: dict, facility: dict) -> dict:
    members = request.get("members") or []
    group_size = max(1, len(members or ["member"]))
    quote = estimate_storage_quote(facility, requested_users=group_size, group_size=group_size)
    total = Decimal(str(quote["total_shared_price"]))
    per_person = Decimal(str(quote["per_person_price"]))
    price_metadata = {
        key: str(value) if isinstance(value, Decimal) else value
        for key, value in quote["price"].items()
    }
    return {
        "total_price": total,
        "per_person_price": per_person,
        "currency": quote["currency"],
        "price": price_metadata,
    }
