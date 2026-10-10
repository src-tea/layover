from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.api.routes import matches as matches_route
from app.core.security import create_auth_token
from app.main import app
from app.repositories.memory_store import MemoryStore
from app.repositories import store as app_store
from app.services.auth_service import AuthService


def test_register_and_login_successfully():
    store = MemoryStore()
    auth = AuthService(store)

    user = auth.register_user({
        'full_name': 'Ava Singh',
        'email': 'ava@example.com',
        'password': 'StrongPass123!',
    })

    assert user['email'] == 'ava@example.com'
    assert user['is_email_verified'] is False

    login = auth.login_with_email('ava@example.com', 'StrongPass123!')
    assert 'token' in login
    assert login['user']['email'] == 'ava@example.com'


def test_duplicate_registration_is_rejected():
    store = MemoryStore()
    auth = AuthService(store)

    auth.register_user({'full_name': 'Ava Singh', 'email': 'ava@example.com', 'password': 'StrongPass123!'})

    try:
        auth.register_user({'full_name': 'Ava Singh', 'email': 'ava@example.com', 'password': 'StrongPass123!'})
        assert False, 'duplicate should be rejected'
    except ValueError:
        pass


def test_pending_or_declined_requests_do_not_expose_contact_details():
    store = MemoryStore()
    auth = AuthService(store)

    sender = auth.register_user({'full_name': 'Ava', 'email': 'ava@example.com', 'password': 'StrongPass123!'})
    target = auth.register_user({'full_name': 'Ben', 'email': 'ben@example.com', 'password': 'StrongPass123!'})

    req = auth.create_connection_request(sender['id'], target['id'])
    assert req['status'] == 'pending'

    details = auth.get_shared_contact_details(sender['id'], target['id'])
    assert details == {'email': None, 'phone': None}

    auth.respond_to_connection_request(req['id'], target['id'], 'declined')
    details = auth.get_shared_contact_details(sender['id'], target['id'])
    assert details == {'email': None, 'phone': None}


def test_accepted_connection_exposes_only_opted_in_contact_methods():
    store = MemoryStore()
    auth = AuthService(store)

    sender = auth.register_user({
        'full_name': 'Ava',
        'email': 'ava@example.com',
        'password': 'StrongPass123!',
        'phone': '+12345678900',
        'contact_sharing': {'email': True, 'phone': False},
    })
    target = auth.register_user({
        'full_name': 'Ben',
        'email': 'ben@example.com',
        'password': 'StrongPass123!',
        'phone': '+12345678901',
        'contact_sharing': {'email': False, 'phone': True},
    })

    request = auth.create_connection_request(sender['id'], target['id'])
    auth.respond_to_connection_request(request['id'], target['id'], 'accepted')

    details = auth.get_shared_contact_details(sender['id'], target['id'])
    assert details == {'email': None, 'phone': '+12345678901'}

    details_b = auth.get_shared_contact_details(target['id'], sender['id'])
    assert details_b == {'email': 'ava@example.com', 'phone': None}

    connected = auth.list_connected_users(sender['id'])
    assert connected[0]['user']['email'] is None
    assert connected[0]['user']['phone'] == '+12345678901'


def test_pending_requests_do_not_reserve_users_but_acceptance_cancels_other_pending_requests():
    store = MemoryStore()
    auth = AuthService(store)
    first = auth.register_user({'full_name': 'Ava', 'email': 'ava@example.com', 'password': 'StrongPass123!'})
    second = auth.register_user({'full_name': 'Ben', 'email': 'ben@example.com', 'password': 'StrongPass123!'})
    third = auth.register_user({'full_name': 'Cam', 'email': 'cam@example.com', 'password': 'StrongPass123!'})

    first_request = auth.create_connection_request(first['id'], second['id'])
    other_request = auth.create_connection_request(first['id'], third['id'])
    assert first_request['status'] == other_request['status'] == 'pending'
    assert first['id'] not in store.list_pairing_locked_user_ids()

    auth.respond_to_connection_request(first_request['id'], second['id'], 'accepted')
    assert store.connection_requests[other_request['id']]['status'] == 'cancelled'
    assert store.list_pairing_locked_user_ids() == {first['id'], second['id']}

    with pytest.raises(ValueError, match='already belong to a pair'):
        auth.create_connection_request(third['id'], first['id'])


def test_concurrent_acceptance_creates_at_most_one_active_pair():
    store = MemoryStore()
    auth = AuthService(store)
    first = auth.register_user({'full_name': 'Ava', 'email': 'ava@example.com', 'password': 'StrongPass123!'})
    second = auth.register_user({'full_name': 'Ben', 'email': 'ben@example.com', 'password': 'StrongPass123!'})
    third = auth.register_user({'full_name': 'Cam', 'email': 'cam@example.com', 'password': 'StrongPass123!'})

    request_one = auth.create_connection_request(first['id'], second['id'])
    request_two = auth.create_connection_request(third['id'], first['id'])

    def accept(request_id, recipient_id):
        try:
            auth.respond_to_connection_request(request_id, recipient_id, 'accepted')
            return 'accepted'
        except ValueError:
            return 'rejected'

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda args: accept(*args),
            [(request_one['id'], second['id']), (request_two['id'], first['id'])],
        ))

    assert results.count('accepted') == 1
    active_connections = [connection for connection in store.connections.values() if connection['status'] == 'active']
    assert len(active_connections) == 1
    active_users = [active_connections[0]['user_a_id'], active_connections[0]['user_b_id']]
    assert len(set(active_users)) == 2
    assert len(store.pairing_locks) == 2
    assert any(request['status'] == 'cancelled' for request in store.connection_requests.values())


def test_disconnection_revokes_contacts_without_automatically_reenabling_matching():
    store = MemoryStore()
    auth = AuthService(store)
    first = auth.register_user({
        'full_name': 'Ava', 'email': 'ava@example.com', 'password': 'StrongPass123!',
        'contact_sharing': {'email': True, 'phone': False},
    })
    second = auth.register_user({
        'full_name': 'Ben', 'email': 'ben@example.com', 'password': 'StrongPass123!',
        'contact_sharing': {'email': True, 'phone': False},
    })
    request = auth.create_connection_request(first['id'], second['id'])
    accepted = auth.respond_to_connection_request(request['id'], second['id'], 'accepted')
    connection = store.connections[accepted['connection_id']]

    assert auth.get_shared_contact_details(first['id'], second['id'])['email'] == 'ben@example.com'
    disconnected = auth.disconnect_connection(connection['id'], first['id'])

    assert disconnected['status'] == 'disconnected'
    assert disconnected['disconnected_at']
    assert auth.get_shared_contact_details(first['id'], second['id']) == {'email': None, 'phone': None}
    assert store.list_pairing_locked_user_ids() == {first['id'], second['id']}
    assert store.list_connections_for_user(first['id']) == []


def test_match_discovery_hides_both_members_of_a_confirmed_pair(monkeypatch):
    store = MemoryStore()
    auth = AuthService(store)
    first = auth.register_user({'full_name': 'Ava', 'email': 'ava@example.com', 'password': 'StrongPass123!'})
    second = auth.register_user({'full_name': 'Ben', 'email': 'ben@example.com', 'password': 'StrongPass123!'})
    third = auth.register_user({'full_name': 'Cam', 'email': 'cam@example.com', 'password': 'StrongPass123!'})
    fourth = auth.register_user({'full_name': 'Dee', 'email': 'dee@example.com', 'password': 'StrongPass123!'})
    request = auth.create_connection_request(first['id'], second['id'])
    auth.respond_to_connection_request(request['id'], second['id'], 'accepted')

    store.layovers = {
        user['id']: {
            'id': f"layover-{user['id']}", 'user_id': user['id'], 'airport_code': 'DXB',
            'arrival_time': '2026-10-11T08:00:00+00:00',
            'departure_time': '2026-10-11T14:00:00+00:00',
            'baggage_size': 'medium', 'interests': ['food'],
        }
        for user in (first, second, third, fourth)
    }
    monkeypatch.setattr(matches_route, 'store', store)

    results = matches_route.find_matches(airport_code='DXB')['items']

    assert results
    assert {item['user_id'] for item in results} == {fourth['id']}
    assert first['id'] in store.list_pairing_locked_user_ids()
    assert second['id'] not in {item['user_id'] for item in results}


def test_authenticated_api_hides_pair_and_rejects_stale_connection_attempts():
    assert isinstance(app_store, MemoryStore)
    app_store.reset()
    first = app_store.get_user('user-1')
    second = app_store.get_user('user-2')
    third = app_store.get_user('user-3')
    client = TestClient(app)
    first_headers = {'Authorization': f"Bearer {create_auth_token(first)}"}
    second_headers = {'Authorization': f"Bearer {create_auth_token(second)}"}
    third_headers = {'Authorization': f"Bearer {create_auth_token(third)}"}

    created = client.post('/api/auth/connections/request', json={'target_user_id': second['id']}, headers=first_headers)
    assert created.status_code == 200
    request_id = created.json()['request']['id']
    accepted = client.patch(
        f'/api/auth/connections/{request_id}',
        json={'status': 'accepted'},
        headers=second_headers,
    )
    assert accepted.status_code == 200

    visible_layovers = client.get('/api/layovers').json()['items']
    assert {item['user_id'] for item in visible_layovers}.isdisjoint({first['id'], second['id']})
    stale_request = client.post(
        '/api/auth/connections/request',
        json={'target_user_id': first['id']},
        headers=third_headers,
    )
    assert stale_request.status_code == 409
    assert 'already belong to a pair' in stale_request.json()['detail']

    app_store.reset()
