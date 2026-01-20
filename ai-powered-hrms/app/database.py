from __future__ import annotations

from typing import Any, Dict

from supabase import Client, create_client

from app.config import Settings, get_settings


class SupabaseDatabase:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        url = self.settings.supabase_url
        key = self.settings.supabase_service_key or self.settings.supabase_anon_key
        if not url or not key:
            raise RuntimeError("Supabase credentials are not configured")
        self.client: Client = create_client(url, key)

    def table(self, name: str):
        return self.client.table(name)

    # Convenience helpers
    def insert(self, table: str, data: Dict[str, Any]):
        return self.table(table).insert(data).execute()

    def update(self, table: str, data: Dict[str, Any], eq: tuple[str, Any]):
        column, value = eq
        return self.table(table).update(data).eq(column, value).execute()

    def select_one(self, table: str, eq: tuple[str, Any]):
        column, value = eq
        resp = self.table(table).select("*").eq(column, value).limit(1).single().execute()
        return resp.data

    def select(self, table: str, filters: dict[str, Any] | None = None):
        query = self.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.execute().data


def get_db(settings: Settings | None = None) -> SupabaseDatabase:
    return SupabaseDatabase(settings=settings)


