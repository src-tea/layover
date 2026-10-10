from __future__ import annotations

from decimal import Decimal

from app.core.config import settings
from app.services.currency_service import load_pricing_data
from supabase import create_client


def main() -> None:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before seeding prices.")

    data = load_pricing_data()
    snapshot = data["exchange_rate_snapshot"]
    usd_per_gbp = Decimal(str(snapshot["usd_per_eur"])) / Decimal(str(snapshot["gbp_per_eur"]))
    rows = [
        {
            **quote,
            "exchange_rate_to_usd": str(usd_per_gbp),
            "exchange_rate_date": snapshot["date"],
            "exchange_rate_source": snapshot["source"],
            "exchange_rate_source_url": snapshot["source_url"],
        }
        for quote in data["provider_quotes"]
    ]
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    client.table("airport_price_quotes").upsert(rows, on_conflict="id").execute()
    print(f"Upserted {len(rows)} sourced price quotes; all are reference conversions, not live availability.")


if __name__ == "__main__":
    main()
