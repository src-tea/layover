from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.repositories import store
from app.services.itinerary_service import build_itinerary

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])


@router.get("")
def list_itineraries():
    return {"items": store.list_itineraries()}


@router.post("")
def create_itinerary(payload: dict):
    layover = store.get_layover(payload["layover_id"])
    if not layover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layover not found")
    itinerary = build_itinerary(layover)
    record = store.create_itinerary({
        **payload,
        "user_id": payload.get("user_id", "user-1"),
        **itinerary,
    })
    return {"item": record}
