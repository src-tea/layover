from app.repositories.memory_store import store as memory_store
from app.repositories.supabase_repository import STORE as supabase_store

store = supabase_store if supabase_store.available() else memory_store

__all__ = ["store"]

