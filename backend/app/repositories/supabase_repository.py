from __future__ import annotations

from typing import Any

from supabase import create_client

from app.core.config import settings
from app.repositories.memory_store import store as memory_store


class SupabaseRepository:
    def __init__(self):
        self.enabled = bool(settings.supabase_url and settings.supabase_service_role_key)
        self.client = None

        if self.enabled:
            try:
                self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            except Exception:
                self.enabled = False
                self.client = None

    def available(self) -> bool:
        return bool(self.client)

    def list_storage_facilities(self, airport_code: str | None = None):
        if not self.available():
            return memory_store.list_storage_facilities(airport_code)
        try:
            query = self.client.table("storage_facilities").select("*")
            if airport_code:
                query = query.eq("airport_code", airport_code)
            response = query.execute()
            return list(response.data or [])
        except Exception:
            return memory_store.list_storage_facilities(airport_code)

    def get_storage_facility(self, facility_id: str):
        if not self.available():
            return memory_store.get_storage_facility(facility_id)
        try:
            response = self.client.table("storage_facilities").select("*").eq("id", facility_id).execute()
            items = response.data or []
            return items[0] if items else None
        except Exception:
            return memory_store.get_storage_facility(facility_id)

    def list_layovers(self, user_id: str | None = None):
        if not self.available():
            return memory_store.list_layovers(user_id)
        try:
            query = self.client.table("layovers").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return list(response.data or [])
        except Exception:
            return memory_store.list_layovers(user_id)

    def get_layover(self, layover_id: str):
        if not self.available():
            return memory_store.get_layover(layover_id)
        try:
            response = self.client.table("layovers").select("*").eq("id", layover_id).execute()
            items = response.data or []
            return items[0] if items else None
        except Exception:
            return memory_store.get_layover(layover_id)

    def create_layover(self, payload: dict[str, Any]):
        if not self.available():
            return memory_store.create_layover(payload)
        try:
            response = self.client.table("layovers").insert(payload).execute()
            return response.data[0] if getattr(response, "data", None) else payload
        except Exception:
            return memory_store.create_layover(payload)

    def list_bookings(self, user_id: str | None = None):
        if not self.available():
            return memory_store.list_bookings(user_id)
        try:
            query = self.client.table("bookings").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return list(response.data or [])
        except Exception:
            return memory_store.list_bookings(user_id)

    def create_booking(self, payload: dict[str, Any]):
        if not self.available():
            return memory_store.create_booking(payload)
        try:
            database_payload = dict(payload)
            for field in ("total_price", "per_person_price"):
                if field in database_payload:
                    database_payload[field] = str(database_payload[field])
            response = self.client.table("bookings").insert(database_payload).execute()
            return response.data[0] if getattr(response, "data", None) else payload
        except Exception:
            return memory_store.create_booking(payload)

    def create_payment(self, payload: dict[str, Any]):
        if not self.available():
            return memory_store.create_payment(payload)
        try:
            database_payload = dict(payload)
            if "amount" in database_payload:
                database_payload["amount"] = str(database_payload["amount"])
            response = self.client.table("payments").insert(database_payload).execute()
            return response.data[0] if getattr(response, "data", None) else payload
        except Exception:
            return memory_store.create_payment(payload)

    def create_itinerary(self, payload: dict[str, Any]):
        if not self.available():
            return memory_store.create_itinerary(payload)
        try:
            response = self.client.table("itineraries").insert(payload).execute()
            return response.data[0] if getattr(response, "data", None) else payload
        except Exception:
            return memory_store.create_itinerary(payload)

    def list_itineraries(self, user_id: str | None = None):
        if not self.available():
            return memory_store.list_itineraries(user_id)
        try:
            query = self.client.table("itineraries").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
            return list(response.data or [])
        except Exception:
            return memory_store.list_itineraries(user_id)

    def cancel_booking(self, booking_id: str, user_id: str):
        if not self.available():
            return memory_store.cancel_booking(booking_id, user_id)
        try:
            response = self.client.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).eq("user_id", user_id).execute()
            items = response.data or []
            return items[0] if items else memory_store.cancel_booking(booking_id, user_id)
        except Exception:
            return memory_store.cancel_booking(booking_id, user_id)

    def list_users(self):
        if not self.available():
            return memory_store.list_users()
        try:
            response = self.client.table("users").select("*").execute()
            return list(response.data or [])
        except Exception:
            return memory_store.list_users()

    def get_user(self, user_id: str):
        if not self.available():
            return memory_store.get_user(user_id)
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            items = response.data or []
            return items[0] if items else None
        except Exception as exc:
            raise RuntimeError("Unable to load user profile") from exc

    def list_airports(self):
        if not self.available():
            return memory_store.list_airports()
        try:
            response = self.client.table("airports").select("*").order("city").order("name").execute()
            return list(response.data or [])
        except Exception as exc:
            raise RuntimeError("Unable to load the airport catalog") from exc

    def get_airport(self, iata_code: str):
        if not self.available():
            return memory_store.get_airport(iata_code)
        try:
            response = self.client.table("airports").select("*").eq("iata_code", iata_code.upper()).execute()
            items = response.data or []
            return items[0] if items else None
        except Exception as exc:
            raise RuntimeError("Unable to validate airport code") from exc

    @staticmethod
    def _rpc_record(response):
        data = response.data
        if isinstance(data, list):
            return data[0] if data else None
        return data

    @staticmethod
    def _connection_error(exc: Exception) -> ValueError:
        message = str(exc).lower()
        if "already belong" in message or "pairing lock" in message or "unique constraint" in message:
            return ValueError("One or both users already belong to a pair")
        if "not pending" in message or "already been completed" in message:
            return ValueError("This connection request is no longer pending")
        if "only the" in message or "not a member" in message:
            return ValueError(str(exc))
        if "not found" in message:
            return ValueError("Connection request or user not found")
        return ValueError("Connection could not be completed; refresh and try again")

    def list_pairing_locked_user_ids(self):
        if not self.available():
            return memory_store.list_pairing_locked_user_ids()
        try:
            response = self.client.table("pairing_locks").select("user_id").execute()
            return {row["user_id"] for row in response.data or []}
        except Exception as exc:
            raise RuntimeError("Unable to verify match eligibility") from exc

    def create_connection_request(self, payload: dict[str, Any]):
        if not self.available():
            return memory_store.create_connection_request(payload)
        try:
            response = self.client.rpc("create_connection_request", {
                "p_sender_user_id": payload["user_a_id"],
                "p_recipient_user_id": payload["user_b_id"],
            }).execute()
            record = self._rpc_record(response)
            if not record:
                raise ValueError("Connection request was not created")
            return record
        except Exception as exc:
            raise self._connection_error(exc) from exc

    def respond_to_connection_request(self, request_id: str, actor_user_id: str, status: str):
        if not self.available():
            return memory_store.respond_to_connection_request(request_id, actor_user_id, status)
        try:
            response = self.client.rpc("respond_to_connection_request", {
                "p_request_id": request_id,
                "p_actor_user_id": actor_user_id,
                "p_response": status,
            }).execute()
            record = self._rpc_record(response)
            if not record:
                raise ValueError("Connection request was not updated")
            return record
        except Exception as exc:
            raise self._connection_error(exc) from exc

    def disconnect_connection(self, connection_id: str, actor_user_id: str):
        if not self.available():
            return memory_store.disconnect_connection(connection_id, actor_user_id)
        try:
            response = self.client.rpc("disconnect_connection", {
                "p_connection_id": connection_id,
                "p_actor_user_id": actor_user_id,
            }).execute()
            record = self._rpc_record(response)
            if not record:
                raise ValueError("Connection was not updated")
            return record
        except Exception as exc:
            raise self._connection_error(exc) from exc

    def list_requests_for_user(self, user_id: str, direction: str = "incoming"):
        if not self.available():
            return memory_store.list_requests_for_user(user_id, direction)
        column = "user_b_id" if direction == "incoming" else "user_a_id"
        response = self.client.table("connection_requests").select("*").eq(column, user_id).execute()
        return list(response.data or [])

    def list_connections_for_user(self, user_id: str):
        if not self.available():
            return memory_store.list_connections_for_user(user_id)
        response = self.client.table("confirmed_pairs").select("*").eq("status", "active").or_(
            f"user_a_id.eq.{user_id},user_b_id.eq.{user_id}"
        ).execute()
        return list(response.data or [])

    def get_connection_between_users(self, user_a_id: str, user_b_id: str):
        if not self.available():
            return memory_store.get_connection_between_users(user_a_id, user_b_id)
        first, second = sorted((user_a_id, user_b_id))
        response = self.client.table("confirmed_pairs").select("*").eq("user_a_id", first).eq("user_b_id", second).execute()
        items = response.data or []
        return items[0] if items else None


STORE = SupabaseRepository()
