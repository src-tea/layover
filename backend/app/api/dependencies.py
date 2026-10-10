from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_auth_token, decode_supabase_token, demo_user, is_offline_mode

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None and not is_offline_mode():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials is None:
        return demo_user()

    try:
        if is_offline_mode():
            return decode_auth_token(credentials.credentials)
        return decode_supabase_token(credentials.credentials)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
