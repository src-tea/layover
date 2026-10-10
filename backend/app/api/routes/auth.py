from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.repositories import store
from app.schemas.core import (
    ConnectionRequestCreate,
    ConnectionRequestDecision,
    ContactSharingUpdate,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyCodeRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
service = AuthService(store)


@router.get("/me")
async def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@router.post("/register")
def register_user(payload: RegisterRequest):
    try:
        record = service.register_user(payload.model_dump())
        return {"user": record}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login")
def login_user(payload: LoginRequest):
    try:
        identifier = payload.identifier.strip()
        if '@' in identifier:
            result = service.login_with_email(identifier, payload.password)
        else:
            result = service.login_with_phone(identifier, payload.password)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/verify-email")
def verify_email(payload: VerifyCodeRequest):
    try:
        return {"user": service.verify_email_code(payload.identifier, payload.code)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/verify-phone")
def verify_phone(payload: VerifyCodeRequest):
    try:
        return {"user": service.verify_phone_code(payload.identifier, payload.code)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/send-email-code")
def send_email_code(payload: ForgotPasswordRequest):
    try:
        code = service.send_email_verification_code(payload.identifier)
        return {"code": code, "message": "Verification code sent."}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/send-phone-code")
def send_phone_code(payload: ForgotPasswordRequest):
    try:
        code = service.send_phone_otp(payload.identifier)
        return {"code": code, "message": "Verification code sent."}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    try:
        code = service.request_password_reset(payload.identifier)
        return {"code": code, "message": "Password reset code sent."}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    try:
        return {"user": service.reset_password(payload.identifier, payload.code, payload.new_password)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/connections")
def list_requests(current_user: dict = Depends(get_current_user)):
    try:
        incoming = service.list_requests(current_user["id"], direction="incoming")
        outgoing = service.list_requests(current_user["id"], direction="outgoing")
        active = service.list_connected_users(current_user["id"])
        return {"incoming": incoming, "outgoing": outgoing, "active": active}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/connections/request")
def request_connection(payload: ConnectionRequestCreate, current_user: dict = Depends(get_current_user)):
    try:
        record = service.create_connection_request(current_user["id"], payload.target_user_id)
        return {"request": record}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/connections/{request_id}")
def respond_to_request(request_id: str, payload: ConnectionRequestDecision, current_user: dict = Depends(get_current_user)):
    try:
        updated = service.respond_to_connection_request(request_id, current_user["id"], payload.status)
        return {"request": updated}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/connections/{connection_id}/disconnect")
def disconnect_connection(connection_id: str, current_user: dict = Depends(get_current_user)):
    try:
        connection = service.disconnect_connection(connection_id, current_user["id"])
        return {"connection": connection}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/profile/contact-sharing")
def update_contact_sharing(payload: ContactSharingUpdate, current_user: dict = Depends(get_current_user)):
    try:
        user = service.update_contact_sharing(current_user["id"], payload.model_dump())
        return {"user": user}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/profile/contact-sharing")
def read_contact_sharing(current_user: dict = Depends(get_current_user)):
    user = store.get_user(current_user["id"])
    return {"contact_sharing": user.get("contact_sharing", {"email": False, "phone": False})}


@router.get("/demo")
def demo_login():
    return {"user": {"id": "demo-user-id", "email": "demo@layover.app", "full_name": "Demo Traveller", "role": "demo"}, "mode": "offline"}
