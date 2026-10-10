from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.repositories import store
from app.schemas.core import BookingCreate
from app.services.booking_service import compute_booking_total, validate_booking_request

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("")
def list_bookings(current_user: dict = Depends(get_current_user)):
    return {"items": store.list_bookings(current_user.get("id"))}


@router.post("")
def create_booking(payload: BookingCreate, current_user: dict = Depends(get_current_user)):
    layover = store.get_layover(payload.layover_id)
    facility = store.get_storage_facility(payload.facility_id)
    if not layover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layover not found")
    if not facility:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage facility not found")

    validation_error = validate_booking_request(payload.model_dump(), layover, facility)
    if validation_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)

    members = payload.members or [current_user.get("id") or "user-1"]
    try:
        pricing = compute_booking_total({**payload.model_dump(), "members": members}, facility)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    booking = store.create_booking({
        **payload.model_dump(),
        "user_id": payload.user_id or current_user.get("id") or "user-1",
        "members": members,
        "status": "confirmed",
        "total_price": pricing["total_price"],
        "per_person_price": pricing["per_person_price"],
        "currency": pricing["currency"],
        "price_metadata": pricing["price"],
    })
    return {"item": booking, "pricing": pricing}


@router.post("/{booking_id}/cancel")
def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    try:
        booking = store.cancel_booking(booking_id, current_user.get("id") or "user-1")
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can cancel the booking") from exc
    return {"item": booking}
