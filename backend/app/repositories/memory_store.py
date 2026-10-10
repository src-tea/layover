from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from threading import RLock
from typing import Any

from app.services.airport_service import load_airport_catalog


class MemoryStore:
    def __init__(self):
        self._connection_lock = RLock()
        self.reset()

    def reset(self) -> None:
        self.users = {
            "user-1": {
                "id": "user-1",
                "email": "maya@example.com",
                "phone": None,
                "full_name": "Maya Chen",
                "display_name": "Maya",
                "role": "traveller",
                "password_hash": None,
                "is_email_verified": True,
                "is_phone_verified": False,
                "contact_sharing": {"email": True, "phone": False},
                "profile_picture": None,
                "airport_code": "DXB",
                "interests": ["food", "shopping"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
            },
            "user-2": {
                "id": "user-2",
                "email": "sam@example.com",
                "phone": None,
                "full_name": "Sam Patel",
                "display_name": "Sam",
                "role": "traveller",
                "password_hash": None,
                "is_email_verified": True,
                "is_phone_verified": False,
                "contact_sharing": {"email": False, "phone": True},
                "profile_picture": None,
                "airport_code": "DXB",
                "interests": ["food", "spa"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
            },
            "user-3": {
                "id": "user-3",
                "email": "lina@example.com",
                "phone": None,
                "full_name": "Lina Gomez",
                "display_name": "Lina",
                "role": "traveller",
                "password_hash": None,
                "is_email_verified": True,
                "is_phone_verified": False,
                "contact_sharing": {"email": True, "phone": True},
                "profile_picture": None,
                "airport_code": "LHR",
                "interests": ["coffee", "books"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
            },
        }
        self.layovers = {
            "layover-1": {
                "id": "layover-1",
                "user_id": "user-1",
                "airport_code": "DXB",
                "arrival_time": "2025-01-01T12:00:00+00:00",
                "departure_time": "2025-01-01T18:00:00+00:00",
                "baggage_size": "medium",
                "interests": ["food", "shopping", "spa"],
            },
            "layover-2": {
                "id": "layover-2",
                "user_id": "user-2",
                "airport_code": "DXB",
                "arrival_time": "2025-01-01T15:00:00+00:00",
                "departure_time": "2025-01-01T19:00:00+00:00",
                "baggage_size": "medium",
                "interests": ["food", "shopping", "museum"],
            },
            "layover-3": {
                "id": "layover-3",
                "user_id": "user-3",
                "airport_code": "LHR",
                "arrival_time": "2025-01-02T09:00:00+00:00",
                "departure_time": "2025-01-02T16:00:00+00:00",
                "baggage_size": "light",
                "interests": ["books", "coffee"],
            },
        }
        self.storage_facilities = {
            "facility-1": {
                "id": "facility-1",
                "name": "SkySafe Lockers",
                "airport_code": "DXB",
                "city": "Dubai",
                "base_price": 24.0,
                "price_status": "illustrative_estimate",
                "price_source_name": "Legacy LAYOVER sample data",
                "price_source_url": None,
                "price_verified_at": None,
                "price_assumptions": "Illustrative USD fixture; provider, availability, and current price are not verified.",
                "sharing_allowed": True,
                "share_min_users": 2,
                "share_max_users": 4,
                "opening_hours": {"start": "06:00", "end": "23:00"},
                "distance_minutes": 12,
                "currency": "USD",
            },
            "facility-2": {
                "id": "facility-2",
                "name": "Passport Pods",
                "airport_code": "DXB",
                "city": "Terminal 3",
                "base_price": 18.0,
                "price_status": "illustrative_estimate",
                "price_source_name": "Legacy LAYOVER sample data",
                "price_source_url": None,
                "price_verified_at": None,
                "price_assumptions": "Illustrative USD fixture; provider, availability, and current price are not verified.",
                "sharing_allowed": False,
                "share_min_users": 1,
                "share_max_users": 1,
                "opening_hours": {"start": "07:00", "end": "21:00"},
                "distance_minutes": 8,
                "currency": "USD",
            },
            "facility-3": {
                "id": "facility-3",
                "name": "LHR Lounge Lockers",
                "airport_code": "LHR",
                "city": "London",
                "base_price": 20.0,
                "price_status": "illustrative_estimate",
                "price_source_name": "Legacy LAYOVER sample data",
                "price_source_url": None,
                "price_verified_at": None,
                "price_assumptions": "Illustrative USD fixture; provider, availability, and current price are not verified.",
                "sharing_allowed": True,
                "share_min_users": 2,
                "share_max_users": 3,
                "opening_hours": {"start": "05:00", "end": "22:00"},
                "distance_minutes": 16,
                "currency": "USD",
            },
        }
        self.bookings = {}
        self.payments = {}
        self.itineraries = {}
        self.connection_requests = {}
        self.connections = {}
        self.pairing_locks = set()
        self.verification_codes = {}
        self.password_reset_codes = {}
        self.access_logs = []

    def list_users(self):
        return [deepcopy(user) for user in self.users.values()]

    def list_airports(self):
        return deepcopy(load_airport_catalog()["airports"])

    def get_airport(self, iata_code: str):
        normalized = iata_code.strip().upper()
        return next((airport for airport in self.list_airports() if airport["iata_code"] == normalized), None)

    def get_user(self, user_id: str):
        return deepcopy(self.users.get(user_id))

    def find_user_by_email(self, email: str):
        if not email:
            return None
        normalized_email = email.strip().lower()
        for user in self.users.values():
            if (user.get('email') or '').strip().lower() == normalized_email:
                return deepcopy(user)
        return None

    def find_user_by_phone(self, phone: str):
        if not phone:
            return None
        normalized_phone = phone.strip()
        for user in self.users.values():
            if (user.get('phone') or '').strip() == normalized_phone:
                return deepcopy(user)
        return None

    def register_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        allowed_fields = {'id', 'email', 'phone', 'full_name', 'display_name', 'password_hash', 'role', 'airport_code', 'interests', 'profile_picture', 'is_email_verified', 'is_phone_verified', 'contact_sharing', 'status', 'created_at'}
        user_id = payload.get('id') or f"user-{len(self.users) + 1}"
        record = {key: value for key, value in payload.items() if key in allowed_fields}
        record.setdefault('id', user_id)
        record.setdefault('email', None)
        record.setdefault('phone', None)
        record.setdefault('full_name', record.get('display_name') or 'LAYOVER User')
        record.setdefault('display_name', record.get('full_name') or 'LAYOVER User')
        record.setdefault('role', 'traveller')
        record.setdefault('password_hash', None)
        record.setdefault('is_email_verified', bool(record.get('email') is None))
        record.setdefault('is_phone_verified', bool(record.get('phone') is None))
        record.setdefault('contact_sharing', {'email': True, 'phone': False})
        record.setdefault('status', 'active')
        record.setdefault('created_at', datetime.now(timezone.utc).isoformat())
        self.users[user_id] = record
        return deepcopy(record)

    def create_verification_code(self, identifier: str, code: str, kind: str):
        self.verification_codes[f"{kind}:{identifier.strip().lower()}"] = {'code': code, 'kind': kind, 'created_at': datetime.now(timezone.utc).isoformat()}

    def get_verification_code(self, identifier: str, kind: str):
        return deepcopy(self.verification_codes.get(f"{kind}:{identifier.strip().lower()}"))

    def clear_verification_code(self, identifier: str, kind: str):
        self.verification_codes.pop(f"{kind}:{identifier.strip().lower()}", None)

    def create_password_reset_code(self, identifier: str, code: str):
        self.password_reset_codes[identifier.strip().lower()] = {'code': code, 'created_at': datetime.now(timezone.utc).isoformat()}

    def get_password_reset_code(self, identifier: str):
        return deepcopy(self.password_reset_codes.get(identifier.strip().lower()))

    def clear_password_reset_code(self, identifier: str):
        self.password_reset_codes.pop(identifier.strip().lower(), None)

    def create_connection_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connection_lock:
            sender_id = payload['user_a_id']
            recipient_id = payload['user_b_id']
            if sender_id == recipient_id:
                raise ValueError('You cannot connect with yourself')
            if not self.get_user(sender_id) or not self.get_user(recipient_id):
                raise ValueError('User not found')
            if sender_id in self.pairing_locks or recipient_id in self.pairing_locks:
                raise ValueError('One or both users already belong to a pair')

            for request in self.connection_requests.values():
                if request['status'] == 'pending' and {
                    request['user_a_id'], request['user_b_id'],
                } == {sender_id, recipient_id}:
                    return deepcopy(request)

            request_id = payload.get('id') or f"request-{len(self.connection_requests) + 1}"
            record = {
                'id': request_id,
                'user_a_id': sender_id,
                'user_b_id': recipient_id,
                'status': 'pending',
                'created_at': payload.get('created_at') or datetime.now(timezone.utc).isoformat(),
                'responded_at': None,
                'accepted_at': None,
                'connection_id': None,
            }
            self.connection_requests[request_id] = record
            return deepcopy(record)

    def respond_to_connection_request(self, request_id: str, actor_user_id: str, status: str):
        with self._connection_lock:
            request = self.connection_requests.get(request_id)
            if not request:
                raise ValueError('Connection request not found')

            if request['status'] == 'accepted' and status == 'accepted':
                connection = self.connections.get(request.get('connection_id'))
                if connection and connection['status'] == 'active':
                    return deepcopy(request)
                raise ValueError('This connection request has already been completed')
            if request['status'] != 'pending':
                raise ValueError('This connection request is no longer pending')
            if status == 'accepted' or status == 'declined':
                if request['user_b_id'] != actor_user_id:
                    raise ValueError('Only the recipient can respond to this request')
            elif status == 'cancelled':
                if request['user_a_id'] != actor_user_id:
                    raise ValueError('Only the sender can cancel this request')
            else:
                raise ValueError('Unsupported connection status')

            now = datetime.now(timezone.utc).isoformat()
            if status != 'accepted':
                request['status'] = status
                request['responded_at'] = now
                return deepcopy(request)

            user_a_id = request['user_a_id']
            user_b_id = request['user_b_id']
            if user_a_id in self.pairing_locks or user_b_id in self.pairing_locks:
                raise ValueError('One or both users already belong to a pair')

            connection_id = f"connection-{len(self.connections) + 1}"
            connection = {
                'id': connection_id,
                'user_a_id': user_a_id,
                'user_b_id': user_b_id,
                'status': 'active',
                'created_at': now,
                'accepted_at': now,
                'disconnected_at': None,
            }
            self.connections[connection_id] = connection
            self.pairing_locks.update((user_a_id, user_b_id))
            request['status'] = 'accepted'
            request['responded_at'] = now
            request['accepted_at'] = now
            request['connection_id'] = connection_id

            paired_user_ids = {user_a_id, user_b_id}
            for pending in self.connection_requests.values():
                if pending['id'] != request_id and pending['status'] == 'pending' and paired_user_ids.intersection((pending['user_a_id'], pending['user_b_id'])):
                    pending['status'] = 'cancelled'
                    pending['responded_at'] = now

            return deepcopy(request)

    def disconnect_connection(self, connection_id: str, actor_user_id: str):
        with self._connection_lock:
            connection = self.connections.get(connection_id)
            if not connection:
                raise ValueError('Connection not found')
            if actor_user_id not in {connection['user_a_id'], connection['user_b_id']}:
                raise ValueError('Only a member of this pair can disconnect it')
            if connection['status'] != 'active':
                return deepcopy(connection)
            connection['status'] = 'disconnected'
            connection['disconnected_at'] = datetime.now(timezone.utc).isoformat()
            return deepcopy(connection)

    def list_requests_for_user(self, user_id: str, direction: str = 'incoming'):
        with self._connection_lock:
            results = []
            for request in self.connection_requests.values():
                if direction == 'incoming' and request['user_b_id'] == user_id:
                    results.append(deepcopy(request))
                elif direction == 'outgoing' and request['user_a_id'] == user_id:
                    results.append(deepcopy(request))
            return results

    def list_connections_for_user(self, user_id: str):
        with self._connection_lock:
            return [
                deepcopy(connection)
                for connection in self.connections.values()
                if connection['status'] == 'active' and user_id in {connection['user_a_id'], connection['user_b_id']}
            ]

    def list_pairing_locked_user_ids(self):
        with self._connection_lock:
            return set(self.pairing_locks)

    def get_connection_between_users(self, user_a_id: str, user_b_id: str):
        with self._connection_lock:
            for connection in self.connections.values():
                pair = {connection['user_a_id'], connection['user_b_id']}
                if pair == {user_a_id, user_b_id}:
                    return deepcopy(connection)
            return None

    def create_layover(self, payload: dict[str, Any]) -> dict[str, Any]:
        layover_id = payload.get("id") or f"layover-{len(self.layovers) + 1}"
        record = {
            "id": layover_id,
            "user_id": payload.get("user_id") or "user-1",
            "airport_code": payload["airport_code"],
            "arrival_time": payload["arrival_time"].isoformat() if hasattr(payload["arrival_time"], "isoformat") else payload["arrival_time"],
            "departure_time": payload["departure_time"].isoformat() if hasattr(payload["departure_time"], "isoformat") else payload["departure_time"],
            "baggage_size": payload.get("baggage_size", "medium"),
            "interests": payload.get("interests", []),
            "budget": Decimal(str(payload.get("budget", 0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "budget_currency": payload.get("budget_currency", "USD"),
        }
        self.layovers[layover_id] = record
        self.access_logs.append({
            "id": f"log-{len(self.access_logs) + 1}",
            "event": "layover_created",
            "user_id": record["user_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return deepcopy(record)

    def list_layovers(self, user_id: str | None = None):
        layovers = list(self.layovers.values())
        if user_id:
            return [deepcopy(item) for item in layovers if item["user_id"] == user_id]
        return [deepcopy(item) for item in layovers]

    def get_layover(self, layover_id: str):
        return deepcopy(self.layovers.get(layover_id))

    def list_storage_facilities(self, airport_code: str | None = None):
        facilities = list(self.storage_facilities.values())
        if airport_code:
            return [deepcopy(item) for item in facilities if item["airport_code"] == airport_code]
        return [deepcopy(item) for item in facilities]

    def get_storage_facility(self, facility_id: str):
        return deepcopy(self.storage_facilities.get(facility_id))

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        booking_id = payload.get("id") or f"booking-{len(self.bookings) + 1}"
        record = {
            "id": booking_id,
            "layover_id": payload["layover_id"],
            "facility_id": payload["facility_id"],
            "user_id": payload.get("user_id", "user-1"),
            "members": payload.get("members", []),
            "status": payload.get("status", "confirmed"),
            "start_time": payload["start_time"].isoformat() if hasattr(payload["start_time"], "isoformat") else payload["start_time"],
            "end_time": payload["end_time"].isoformat() if hasattr(payload["end_time"], "isoformat") else payload["end_time"],
            "total_price": Decimal(str(payload.get("total_price", 0.0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "per_person_price": Decimal(str(payload.get("per_person_price", 0.0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "currency": payload.get("currency", "USD"),
            "price_metadata": payload.get("price_metadata"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.bookings[booking_id] = record
        self.access_logs.append({
            "id": f"log-{len(self.access_logs) + 1}",
            "event": "booking_created",
            "user_id": record["user_id"],
            "booking_id": booking_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return deepcopy(record)

    def list_bookings(self, user_id: str | None = None):
        bookings = list(self.bookings.values())
        if user_id:
            return [deepcopy(item) for item in bookings if item["user_id"] == user_id]
        return [deepcopy(item) for item in bookings]

    def get_booking(self, booking_id: str):
        return deepcopy(self.bookings.get(booking_id))

    def cancel_booking(self, booking_id: str, user_id: str):
        booking = self.bookings.get(booking_id)
        if not booking:
            raise KeyError("Booking not found")
        if booking["user_id"] != user_id:
            raise PermissionError("Only the creator can cancel the booking")
        booking["status"] = "cancelled"
        return deepcopy(booking)

    def create_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        payment_id = payload.get("id") or f"payment-{len(self.payments) + 1}"
        reference = payload.get("reference") or f"SIM-{payment_id.upper()}"
        record = {
            "id": payment_id,
            "booking_id": payload["booking_id"],
            "amount": Decimal(str(payload.get("amount", 0.0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "currency": payload.get("currency", "USD"),
            "status": payload.get("status", "authorized"),
            "reference": reference,
            "method": payload.get("method", "demo"),
        }
        self.payments[payment_id] = record
        return deepcopy(record)

    def create_itinerary(self, payload: dict[str, Any]) -> dict[str, Any]:
        itinerary_id = payload.get("id") or f"itinerary-{len(self.itineraries) + 1}"
        record = {
            "id": itinerary_id,
            "layover_id": payload["layover_id"],
            "user_id": payload.get("user_id", "user-1"),
            "start_time": payload["start_time"].isoformat() if hasattr(payload["start_time"], "isoformat") else payload["start_time"],
            "end_time": payload["end_time"].isoformat() if hasattr(payload["end_time"], "isoformat") else payload["end_time"],
            "usable_minutes": int(payload.get("usable_minutes", 0)),
            "activities": payload.get("activities", []),
        }
        self.itineraries[itinerary_id] = record
        return deepcopy(record)

    def list_itineraries(self, user_id: str | None = None):
        itineraries = list(self.itineraries.values())
        if user_id:
            return [deepcopy(item) for item in itineraries if item["user_id"] == user_id]
        return [deepcopy(item) for item in itineraries]


store = MemoryStore()
