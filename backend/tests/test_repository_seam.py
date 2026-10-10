from app.repositories import store
from app.repositories.memory_store import store as memory_store


def test_repository_defaults_to_memory_store_when_supabase_is_unconfigured():
    assert store is memory_store
