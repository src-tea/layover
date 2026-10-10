from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.repositories import store
from app.services.airport_service import load_airport_catalog
from app.services.currency_service import load_pricing_data
from app.services.pricing_service import estimate_storage_quote

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("")
def list_storage(airport_code: str | None = Query(default=None)):
    return {"items": store.list_storage_facilities(airport_code)}


@router.get("/prices")
def list_storage_prices(airport_code: str | None = Query(default=None, min_length=3, max_length=3)):
    code = airport_code.upper() if airport_code else None
    if code and store.get_airport(code) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown airport code")
    data = load_pricing_data()
    snapshot = data["exchange_rate_snapshot"]
    items = [
        {
            **quote,
            "exchange_rate_date": snapshot["date"],
            "exchange_rate_source": snapshot["source"],
            "exchange_rate_source_url": snapshot["source_url"],
        }
        for quote in data["provider_quotes"]
        if code is None or quote["airport_code"] == code
    ]
    return {
        "items": items,
        "currency": "USD",
        "status": "provider_quoted" if items else "unavailable",
        "exchange_rate_snapshot": data["exchange_rate_snapshot"],
        "message": None if items else "No current provider quote is available for this airport.",
    }


@router.get("/{facility_id}")
def read_storage(facility_id: str):
    facility = store.get_storage_facility(facility_id)
    if not facility:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage facility not found")
    return {"item": facility}


@router.get("/{facility_id}/quote")
def storage_quote(facility_id: str, people_count: int = 1, group_size: int = 1):
    facility = store.get_storage_facility(facility_id)
    if not facility:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage facility not found")
    try:
        quote = estimate_storage_quote(facility, requested_users=max(1, people_count), group_size=max(1, group_size))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {"facility_id": facility_id, "quote": quote}
