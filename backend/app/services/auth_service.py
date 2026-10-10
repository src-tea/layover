from __future__ import annotations

import re
from typing import Any

from app.core.security import create_auth_token, generate_otp, lock_password, verify_password


class AuthService:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        if email is None:
            return None
        value = email.strip().lower()
        return value or None

    @staticmethod
    def _normalize_phone(phone: str | None) -> str | None:
        if phone is None:
            return None
        value = phone.strip()
        return value or None

    @staticmethod
    def _is_valid_phone(phone: str | None) -> bool:
        if not phone:
            return False
        return bool(re.fullmatch(r'\+?[1-9]\d{7,14}', phone.replace(' ', '')))

    @staticmethod
    def _public_user(user: dict[str, Any]) -> dict[str, Any]:
        public = {
            'id': user.get('id'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'full_name': user.get('full_name'),
            'display_name': user.get('display_name') or user.get('full_name'),
            'role': user.get('role', 'traveller'),
            'profile_picture': user.get('profile_picture'),
            'airport_code': user.get('airport_code'),
            'interests': user.get('interests', []),
            'is_email_verified': bool(user.get('is_email_verified')),
            'is_phone_verified': bool(user.get('is_phone_verified')),
            'contact_sharing': user.get('contact_sharing', {'email': False, 'phone': False}),
            'created_at': user.get('created_at'),
            'status': user.get('status', 'active'),
        }
        return public

    def register_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        full_name = (payload.get('full_name') or '').strip()
        email = self._normalize_email(payload.get('email'))
        phone = self._normalize_phone(payload.get('phone'))
        password = payload.get('password')

        if not full_name:
            raise ValueError('Full name is required')
        if not email and not phone:
            raise ValueError('Either an email or phone number is required')
        if email and not re.fullmatch(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            raise ValueError('Email format is invalid')
        if phone and not self._is_valid_phone(phone):
            raise ValueError('Phone number format is invalid')
        if len(password or '') < 8:
            raise ValueError('Password must be at least 8 characters')
        if email and self.store.find_user_by_email(email):
            raise ValueError('An account with this email already exists')
        if phone and self.store.find_user_by_phone(phone):
            raise ValueError('An account with this phone number already exists')

        user_id = f"user-{len(self.store.users) + 1}"
        user = {
            'id': user_id,
            'email': email,
            'phone': phone,
            'full_name': full_name,
            'display_name': payload.get('display_name') or full_name,
            'password_hash': lock_password(password),
            'role': 'traveller',
            'airport_code': payload.get('airport_code'),
            'interests': payload.get('interests', []),
            'profile_picture': payload.get('profile_picture'),
            'is_email_verified': False,
            'is_phone_verified': False,
            'contact_sharing': {'email': bool(payload.get('contact_sharing', {}).get('email', False)), 'phone': bool(payload.get('contact_sharing', {}).get('phone', False))},
            'created_at': self.store.current_timestamp() if hasattr(self.store, 'current_timestamp') else None,
            'status': 'active',
        }

        if email:
            user['is_email_verified'] = False
        if phone:
            user['is_phone_verified'] = False

        record = self.store.register_user(user)
        return self._public_user(record)

    def login_with_email(self, email: str, password: str) -> dict[str, Any]:
        user = self.store.find_user_by_email(email)
        if not user or not verify_password(password, user.get('password_hash') or ''):
            raise ValueError('Invalid email or password')

        return {
            'token': create_auth_token(user),
            'user': self._public_user(user),
        }

    def login_with_phone(self, phone: str, password: str) -> dict[str, Any]:
        user = self.store.find_user_by_phone(phone)
        if not user or not verify_password(password, user.get('password_hash') or ''):
            raise ValueError('Invalid phone number or password')

        return {
            'token': create_auth_token(user),
            'user': self._public_user(user),
        }

    def send_phone_otp(self, phone: str) -> str:
        normalized_phone = self._normalize_phone(phone)
        if not self._is_valid_phone(normalized_phone):
            raise ValueError('Phone number format is invalid')
        user = self.store.find_user_by_phone(normalized_phone)
        if not user:
            raise ValueError('No account found for the provided phone number')
        code = generate_otp(6)
        self.store.create_verification_code(normalized_phone, code, 'phone')
        return code

    def verify_phone_code(self, phone: str, code: str) -> dict[str, Any]:
        user = self.store.find_user_by_phone(self._normalize_phone(phone))
        if not user:
            raise ValueError('Phone number not found')
        record = self.store.get_verification_code(self._normalize_phone(phone), 'phone')
        if not record or record.get('code') != code:
            raise ValueError('Invalid or expired verification code')
        user['is_phone_verified'] = True
        self.store.users[user['id']] = user
        self.store.clear_verification_code(self._normalize_phone(phone), 'phone')
        return self._public_user(user)

    def send_email_verification_code(self, email: str) -> str:
        normalized_email = self._normalize_email(email)
        if not normalized_email:
            raise ValueError('Email is required')
        user = self.store.find_user_by_email(normalized_email)
        if not user:
            raise ValueError('No account found for the provided email')
        code = generate_otp(6)
        self.store.create_verification_code(normalized_email, code, 'email')
        return code

    def verify_email_code(self, email: str, code: str) -> dict[str, Any]:
        normalized_email = self._normalize_email(email)
        user = self.store.find_user_by_email(normalized_email)
        if not user:
            raise ValueError('Email not found')
        record = self.store.get_verification_code(normalized_email, 'email')
        if not record or record.get('code') != code:
            raise ValueError('Invalid or expired verification code')
        user['is_email_verified'] = True
        self.store.users[user['id']] = user
        self.store.clear_verification_code(normalized_email, 'email')
        return self._public_user(user)

    def request_password_reset(self, identifier: str) -> str:
        user = None
        normalized = self._normalize_email(identifier)
        if normalized:
            user = self.store.find_user_by_email(normalized)
        if not user:
            normalized_phone = self._normalize_phone(identifier)
            user = self.store.find_user_by_phone(normalized_phone)
        if not user:
            raise ValueError('No account matches that identifier')
        code = generate_otp(6)
        self.store.create_password_reset_code(user.get('email') or user.get('phone') or identifier, code)
        return code

    def reset_password(self, identifier: str, code: str, new_password: str) -> dict[str, Any]:
        user = None
        normalized = self._normalize_email(identifier)
        if normalized:
            user = self.store.find_user_by_email(normalized)
        if not user:
            normalized_phone = self._normalize_phone(identifier)
            user = self.store.find_user_by_phone(normalized_phone)
        if not user:
            raise ValueError('No account matches that identifier')
        store_key = user.get('email') or user.get('phone') or identifier
        record = self.store.get_password_reset_code(store_key)
        if not record or record.get('code') != code:
            raise ValueError('Invalid or expired reset code')
        if len(new_password or '') < 8:
            raise ValueError('Password must be at least 8 characters')
        user['password_hash'] = lock_password(new_password)
        self.store.users[user['id']] = user
        self.store.clear_password_reset_code(store_key)
        return self._public_user(user)

    def create_connection_request(self, user_a_id: str, user_b_id: str) -> dict[str, Any]:
        if user_a_id == user_b_id:
            raise ValueError('You cannot connect with yourself')
        if not self.store.get_user(user_a_id) or not self.store.get_user(user_b_id):
            raise ValueError('User not found')
        request = self.store.create_connection_request({'user_a_id': user_a_id, 'user_b_id': user_b_id, 'status': 'pending'})
        return request

    def respond_to_connection_request(self, request_id: str, actor_user_id: str, status: str) -> dict[str, Any]:
        if status not in {'accepted', 'declined', 'cancelled'}:
            raise ValueError('Unsupported connection status')
        return self.store.respond_to_connection_request(request_id, actor_user_id, status)

    def list_requests(self, user_id: str, direction: str = 'incoming') -> list[dict[str, Any]]:
        requests = self.store.list_requests_for_user(user_id, direction)
        results = []
        for request in requests:
            other_user_id = request['user_a_id'] if direction == 'incoming' else request['user_b_id']
            other_user = self.store.get_user(other_user_id)
            public_user = self._public_user(other_user) if other_user else None
            if public_user:
                public_user['email'] = None
                public_user['phone'] = None
                public_user['contact_sharing'] = {'email': False, 'phone': False}
            results.append({**request, 'other_user': public_user})
        return results

    def list_connected_users(self, user_id: str) -> list[dict[str, Any]]:
        records = []
        for connection in self.store.list_connections_for_user(user_id):
            other = connection['user_b_id'] if connection['user_a_id'] == user_id else connection['user_a_id']
            user = self.store.get_user(other)
            if user:
                public_user = self._public_user(user)
                shared_contacts = self.get_shared_contact_details(user_id, other)
                public_user['email'] = shared_contacts['email']
                public_user['phone'] = shared_contacts['phone']
                records.append({
                    'connection': connection,
                    'user': public_user,
                })
        return records

    def get_shared_contact_details(self, requester_user_id: str, other_user_id: str) -> dict[str, Any]:
        request = self.store.get_connection_between_users(requester_user_id, other_user_id)
        if not request or request.get('status') != 'active':
            return {'email': None, 'phone': None}

        other_user = self.store.get_user(other_user_id)
        if not other_user:
            return {'email': None, 'phone': None}

        sharing = other_user.get('contact_sharing', {'email': False, 'phone': False})
        return {
            'email': other_user.get('email') if sharing.get('email') else None,
            'phone': other_user.get('phone') if sharing.get('phone') else None,
        }

    def disconnect_connection(self, connection_id: str, actor_user_id: str) -> dict[str, Any]:
        return self.store.disconnect_connection(connection_id, actor_user_id)

    def update_contact_sharing(self, user_id: str, preferences: dict[str, bool]) -> dict[str, Any]:
        user = self.store.get_user(user_id)
        if not user:
            raise ValueError('User not found')
        user['contact_sharing'] = {
            'email': bool(preferences.get('email', False)),
            'phone': bool(preferences.get('phone', False)),
        }
        self.store.users[user_id] = user
        return self._public_user(user)
