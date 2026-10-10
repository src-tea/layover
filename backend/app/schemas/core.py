from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ContactSharingPreferences(BaseModel):
    email: bool = False
    phone: bool = False


class UserOut(BaseModel):
    id: str
    email: str | None = None
    phone: str | None = None
    full_name: str
    role: str = "member"
    display_name: str | None = None
    profile_picture: str | None = None
    is_email_verified: bool = False
    is_phone_verified: bool = False
    contact_sharing: ContactSharingPreferences = Field(default_factory=ContactSharingPreferences)
    created_at: datetime | None = None


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: str | None = None
    phone: str | None = None
    password: str = Field(..., min_length=8)
    airport_code: str | None = None
    interests: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class VerifyCodeRequest(BaseModel):
    identifier: str = Field(..., min_length=3)
    code: str = Field(..., min_length=4, max_length=8)


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., min_length=3)


class ResetPasswordRequest(BaseModel):
    identifier: str = Field(..., min_length=3)
    code: str = Field(..., min_length=4, max_length=8)
    new_password: str = Field(..., min_length=8)


class ContactSharingUpdate(BaseModel):
    email: bool = False
    phone: bool = False


class ConnectionRequestCreate(BaseModel):
    target_user_id: str = Field(..., min_length=1)


class ConnectionRequestDecision(BaseModel):
    status: Literal["accepted", "declined", "cancelled"]


class ConnectionRecord(BaseModel):
    id: str
    user_a_id: str
    user_b_id: str
    status: str = "pending"
    created_at: datetime


class LayoverCreate(BaseModel):
    airport_code: str = Field(..., min_length=3, max_length=10)
    arrival_time: datetime
    departure_time: datetime
    baggage_size: Literal["light", "medium", "heavy"] = "medium"
    interests: list[str] = Field(default_factory=list)
    budget: Decimal = Field(default=Decimal("0.00"), ge=0)
    budget_currency: Literal["USD"] = "USD"
    user_id: Optional[str] = None


class LayoverOut(BaseModel):
    id: str
    user_id: str
    airport_code: str
    arrival_time: datetime
    departure_time: datetime
    baggage_size: str
    interests: list[str]
    budget: Decimal = Decimal("0.00")
    budget_currency: str = "USD"


class MatchCandidate(BaseModel):
    id: str
    user_id: str
    airport_code: str
    score: int
    shared_minutes: int
    baggage_match: int
    interest_match: int


class StorageFacility(BaseModel):
    id: str
    name: str
    airport_code: str
    city: str
    base_price: Decimal
    sharing_allowed: bool = True
    share_min_users: int = 2
    share_max_users: int = 4
    opening_hours: dict[str, str] = Field(default_factory=lambda: {"start": "06:00", "end": "23:00"})
    distance_minutes: int = 10
    currency: str = "USD"


class BookingCreate(BaseModel):
    layover_id: str
    facility_id: str
    start_time: datetime
    end_time: datetime
    members: list[str] = Field(default_factory=list)
    user_id: Optional[str] = None


class BookingOut(BaseModel):
    id: str
    layover_id: str
    facility_id: str
    status: str
    total_price: Decimal
    per_person_price: Decimal
    currency: Literal["USD"] = "USD"
    price_metadata: dict | None = None
    members: list[str]
    start_time: datetime
    end_time: datetime


class PaymentCreate(BaseModel):
    booking_id: str
    amount: Decimal
    currency: Literal["USD"] = "USD"
    method: str = "demo"


class PaymentOut(BaseModel):
    id: str
    booking_id: str
    status: str
    amount: Decimal
    currency: str
    reference: str


class ItineraryActivity(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    category: str
    duration_minutes: int


class ItineraryOut(BaseModel):
    id: str
    layover_id: str
    start_time: datetime
    end_time: datetime
    activities: list[ItineraryActivity]
    usable_minutes: int
