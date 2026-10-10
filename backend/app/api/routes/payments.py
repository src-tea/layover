from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.repositories import store
from app.schemas.core import PaymentCreate

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("")
def create_payment(payload: PaymentCreate):
    record = store.create_payment({
        **payload.model_dump(),
        "reference": f"SIM-{uuid4().hex[:8].upper()}",
        "status": "authorized",
    })
    return {"item": record}
