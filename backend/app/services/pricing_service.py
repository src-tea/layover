from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.services.currency_service import convert_to_usd


CENT = Decimal("0.01")


def estimate_storage_quote(facility: dict, requested_users: int = 1, group_size: int = 1) -> dict:
    original_amount = Decimal(str(facility.get("base_price", 0.0) or 0.0))
    original_currency = facility.get("currency")
    base_price, conversion = convert_to_usd(original_amount, original_currency)
    sharing_allowed = bool(facility.get("sharing_allowed", False))
    share_min = int(facility.get("share_min_users", 1) or 1)
    share_max = int(facility.get("share_max_users", 1) or 1)
    effective_group = max(1, int(group_size or requested_users or 1))
    price_status = facility.get("price_status", "illustrative_estimate")
    price_source = {
        "status": price_status,
        "source_name": facility.get("price_source_name"),
        "source_url": facility.get("price_source_url"),
        "verified_at": facility.get("price_verified_at"),
        "assumptions": facility.get("price_assumptions"),
    }
    if conversion:
        price_source.update(conversion)

    if sharing_allowed and effective_group >= share_min and effective_group <= share_max:
        per_person_price = (base_price / effective_group).quantize(CENT, rounding=ROUND_HALF_UP)
        savings_percent = (
            ((Decimal("1") - (per_person_price / base_price)) * Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
            if base_price > 0 else Decimal("0.00")
        )
        return {
            "solo_price": base_price,
            "per_person_price": per_person_price,
            "total_shared_price": base_price,
            "savings_percent": savings_percent,
            "sharing_allowed": True,
            "group_size": effective_group,
            "currency": "USD",
            "original_amount": original_amount,
            "original_currency": original_currency,
            "price": price_source,
        }

    return {
        "solo_price": base_price,
        "per_person_price": base_price,
        "total_shared_price": base_price,
        "savings_percent": Decimal("0.00"),
        "sharing_allowed": False,
        "group_size": effective_group,
        "currency": "USD",
        "original_amount": original_amount,
        "original_currency": original_currency,
        "price": price_source,
    }
