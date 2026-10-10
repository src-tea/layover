from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.repositories import store

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
async def current_user_profile(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@router.get("")
async def list_users():
    return {"items": store.list_users()}
