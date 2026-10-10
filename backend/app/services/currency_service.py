from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from typing import Any


PRICING_DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "pricing.json"
CENT = Decimal("0.01")


@lru_cache(maxsize=1)
def load_pricing_data() -> dict[str, Any]:
    with PRICING_DATA_PATH.open(encoding="utf-8") as pricing_file:
        return json.load(pricing_file)


def convert_to_usd(amount: Decimal | str | int | float, currency: str) -> tuple[Decimal, dict[str, Any] | None]:
    if not currency:
        raise ValueError("Price currency is unknown; it cannot be safely displayed as USD")
    normalized_currency = str(currency or "USD").upper()
    original_amount = Decimal(str(amount)).quantize(CENT, rounding=ROUND_HALF_UP)
    if normalized_currency == "USD":
        return original_amount, None

    snapshot = load_pricing_data()["exchange_rate_snapshot"]
    usd_per_eur = Decimal(str(snapshot["usd_per_eur"]))
    if normalized_currency == "INR":
        rate = usd_per_eur / Decimal(str(snapshot["inr_per_eur"]))
    elif normalized_currency == "GBP":
        rate = usd_per_eur / Decimal(str(snapshot["gbp_per_eur"]))
    else:
        raise ValueError(f"No verified exchange-rate snapshot for {normalized_currency}")

    converted = (original_amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)
    return converted, {
        "original_amount": original_amount,
        "original_currency": normalized_currency,
        "exchange_rate": rate,
        "exchange_rate_date": snapshot["date"],
        "exchange_rate_source": snapshot["source"],
        "exchange_rate_source_url": snapshot["source_url"],
    }


def to_usd_amount(amount: Decimal | str | int | float) -> Decimal:
    return Decimal(str(amount)).quantize(CENT, rounding=ROUND_HALF_UP)
