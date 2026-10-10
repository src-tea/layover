from __future__ import annotations

from app.core.config import settings
from app.services.airport_service import load_airport_catalog
from supabase import create_client


def main() -> None:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before seeding airports.")

    catalog = load_airport_catalog()
    source = catalog["source"]
    rows = [
        {
            **airport,
            "source_name": source["name"],
            "source_url": source["url"],
            "source_snapshot_date": source["snapshot_date"],
        }
        for airport in catalog["airports"]
    ]
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    client.table("airports").upsert(rows, on_conflict="iata_code").execute()
    print(f"Upserted {len(rows)} airports from {source['name']} ({source['snapshot_date']}).")


if __name__ == "__main__":
    main()
