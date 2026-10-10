from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

import jwt

from app.core.config import settings


def demo_user() -> dict[str, Any]:
    return {
        "id": "demo-user-id",
        "email": "demo@layover.app",
        "full_name": "Demo Traveller",
        "role": "demo",
    }


def lock_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or not password:
        return False
    try:
        prefix, salt, digest_hex = stored_hash.split('$', 2)
        if prefix != 'pbkdf2_sha256':
            return False
        computed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
        return computed.hex() == digest_hex
    except ValueError:
        return False


def generate_otp(length: int = 6) -> str:
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def create_auth_token(user: dict[str, Any]) -> str:
    secret = settings.jwt_secret or settings.supabase_anon_key or settings.supabase_service_role_key or 'layover-dev-secret-change-me-long-enough-32-bytes'
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user['id']),
        'email': user.get('email'),
        'full_name': user.get('full_name'),
        'role': user.get('role', 'member'),
        'iat': int(now.timestamp()),
        'exp': int((now.timestamp() + 60 * 60 * 24 * 7)),
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def decode_auth_token(token: str) -> dict[str, Any]:
    if not token:
        raise ValueError('Missing bearer token')

    secret = settings.jwt_secret or settings.supabase_anon_key or settings.supabase_service_role_key or 'layover-dev-secret-change-me-long-enough-32-bytes'
    payload = jwt.decode(token, secret, algorithms=['HS256'], options={'require': ['sub', 'exp']})
    if not payload.get('sub'):
        raise ValueError('JWT is missing subject')

    return {
        'id': str(payload.get('sub')),
        'email': payload.get('email') or '',
        'full_name': payload.get('full_name') or 'LAYOVER User',
        'role': payload.get('role', 'member'),
    }


def is_offline_mode() -> bool:
    return not settings.supabase_url and not settings.supabase_anon_key and not settings.supabase_service_role_key


def decode_supabase_token(token: str) -> dict[str, Any]:
    if not token:
        raise ValueError('Missing bearer token')
    if is_offline_mode():
        return demo_user()

    secret = settings.supabase_anon_key or settings.supabase_service_role_key
    if not secret:
        raise ValueError('Supabase keys are not configured')

    options: dict[str, Any] = {'require': ['sub', 'exp'], 'verify_aud': False}
    issuer = settings.supabase_jwt_issuer or settings.supabase_url
    payload = jwt.decode(
        token,
        secret,
        algorithms=['HS256'],
        issuer=issuer,
        options=options,
    )

    if not payload.get('sub'):
        raise ValueError('JWT is missing subject')

    return {
        'id': payload.get('sub'),
        'email': payload.get('email') or f"{payload.get('sub')}@supabase.local",
        'full_name': payload.get('full_name') or 'Supabase User',
        'role': payload.get('role', 'member'),
    }


def current_timestamp() -> datetime:
    return datetime.now(timezone.utc)
