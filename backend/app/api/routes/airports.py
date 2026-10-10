from __future__ import annotations

from fastapi import APIRouter, Query

from app.repositories import store
from app.services.airport_service import load_airport_catalog, search_airports

router = APIRouter(prefix="/api/airports", tags=["airports"])


@router.get("")
def list_airports(q: str | None = Query(default=None, max_length=120), limit: int = Query(default=100, ge=1, le=200)):
    items = search_airports(store.list_airports(), q)
    catalog = load_airport_catalog()
    return {"items": items[:limit], "source": catalog["source"]}
