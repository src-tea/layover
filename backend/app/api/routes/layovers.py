from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.repositories import store
from app.schemas.core import LayoverCreate
from app.services.airport_service import resolve_airport

router = APIRouter(prefix="/api/layovers", tags=["layovers"])


@router.get("")
def list_layovers():
    pairing_locked_ids = store.list_pairing_locked_user_ids()
    items = []
    for item in store.list_layovers():
        if item.get("user_id") in pairing_locked_ids:
            continue
        owner = store.get_user(item.get("user_id")) or {}
        items.append({
            **item,
            "full_name": owner.get("display_name") or owner.get("full_name"),
        })
    return {"items": items}


@router.post("")
def create_layover(payload: LayoverCreate, current_user: dict = Depends(get_current_user)):
    if payload.departure_time <= payload.arrival_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Departure time must be after arrival time")
    airport = resolve_airport(store.list_airports(), payload.airport_code)
    if airport is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown airport code or name")
    if payload.user_id is None:
        payload.user_id = current_user.get("id") or "user-1"
    record = store.create_layover({**payload.model_dump(), "airport_code": airport["iata_code"]})
    return {"item": record}
