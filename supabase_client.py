"""
GrowthOS AI — Supabase Client
================================
Wraps supabase-py for all database operations.
Falls back to file-based storage when Supabase is not configured.

Tables created automatically on first use (via create_tables_sql below):
  - brand_memory      : brand profiles + AI memory
  - content_history   : generated content log
  - analytics_events  : performance metrics
  - scheduler_jobs    : scheduled post queue
  - smm_orders        : SMM panel order history

Usage:
    from supabase_client import db
    db.upsert("brand_memory", {"brand_id": "my_brand", "data": {...}})
    rows = db.select("brand_memory", filters={"brand_id": "my_brand"})
"""
import sys
import os
import json
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE

# ─── SQL to create tables (run once in Supabase SQL editor) ──────────────────
CREATE_TABLES_SQL = """
-- Brand memory (replaces memory_store/*.json files)
CREATE TABLE IF NOT EXISTS brand_memory (
    id          BIGSERIAL PRIMARY KEY,
    brand_id    TEXT NOT NULL UNIQUE,
    data        JSONB NOT NULL DEFAULT '{}',
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Content generation history
CREATE TABLE IF NOT EXISTS content_history (
    id          BIGSERIAL PRIMARY KEY,
    brand_id    TEXT NOT NULL,
    platform    TEXT,
    content_type TEXT,
    content     TEXT,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics events
CREATE TABLE IF NOT EXISTS analytics_events (
    id          BIGSERIAL PRIMARY KEY,
    brand_id    TEXT NOT NULL,
    platform    TEXT,
    metric_type TEXT,
    value       FLOAT,
    metadata    JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scheduler jobs
CREATE TABLE IF NOT EXISTS scheduler_jobs (
    id          BIGSERIAL PRIMARY KEY,
    brand_id    TEXT NOT NULL,
    platform    TEXT,
    content     TEXT,
    scheduled_at TIMESTAMPTZ,
    status      TEXT DEFAULT 'pending',
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- SMM order history (replaces orders_history.json)
CREATE TABLE IF NOT EXISTS smm_orders (
    id          BIGSERIAL PRIMARY KEY,
    order_id    TEXT UNIQUE,
    service_id  TEXT,
    platform    TEXT,
    link        TEXT,
    quantity    INT,
    price       FLOAT,
    status      TEXT DEFAULT 'pending',
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
"""


# ─── Supabase wrapper ─────────────────────────────────────────────────────────
class _SupabaseDB:
    def __init__(self):
        self._client = None
        self._available = False
        if USE_SUPABASE:
            try:
                # Use postgrest directly to avoid storage3/pyiceberg build issues on Python 3.14
                from postgrest import SyncPostgrestClient
                rest_url = SUPABASE_URL.rstrip("/") + "/rest/v1"
                self._client = SyncPostgrestClient(
                    rest_url,
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",
                    },
                )
                self._available = True
            except Exception as e:
                print(f"[Supabase] Connection failed: {e} — using file fallback")

    @property
    def available(self) -> bool:
        return self._available

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def select(self, table: str, filters: dict = None, limit: int = 100) -> list[dict]:
        """Select rows. Returns list of dicts."""
        if not self._available:
            return []
        try:
            q = self._client.from_(table).select("*")
            if filters:
                for k, v in filters.items():
                    q = q.eq(k, v)
            q = q.limit(limit)
            result = q.execute()
            return result.data or []
        except Exception as e:
            print(f"[Supabase] select {table}: {e}")
            return []

    def insert(self, table: str, row: dict) -> dict | None:
        """Insert a row, return inserted record."""
        if not self._available:
            return None
        try:
            result = self._client.from_(table).insert(row).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] insert {table}: {e}")
            return None

    def upsert(self, table: str, row: dict, on_conflict: str = "") -> dict | None:
        """Upsert (insert or update on conflict)."""
        if not self._available:
            return None
        try:
            result = self._client.from_(table).upsert(row).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Supabase] upsert {table}: {e}")
            return None

    def update(self, table: str, filters: dict, values: dict) -> list[dict]:
        """Update matching rows."""
        if not self._available:
            return []
        try:
            q = self._client.from_(table).update(values)
            for k, v in filters.items():
                q = q.eq(k, v)
            return q.execute().data or []
        except Exception as e:
            print(f"[Supabase] update {table}: {e}")
            return []

    def delete(self, table: str, filters: dict) -> list[dict]:
        """Delete matching rows."""
        if not self._available:
            return []
        try:
            q = self._client.from_(table).delete()
            for k, v in filters.items():
                q = q.eq(k, v)
            return q.execute().data or []
        except Exception as e:
            print(f"[Supabase] delete {table}: {e}")
            return []

    # ── Convenience helpers ───────────────────────────────────────────────────

    def get_brand(self, brand_id: str) -> dict:
        """Load brand memory record. Returns {} if not found."""
        rows = self.select("brand_memory", {"brand_id": brand_id}, limit=1)
        if rows:
            return rows[0].get("data", {})
        return {}

    def save_brand(self, brand_id: str, data: dict) -> bool:
        """Save/update brand memory."""
        result = self.upsert("brand_memory", {
            "brand_id": brand_id,
            "data": data,
            "updated_at": datetime.utcnow().isoformat(),
        })
        return result is not None

    def log_content(self, brand_id: str, platform: str, content_type: str,
                    content: str, metadata: dict = None) -> bool:
        """Log a generated content piece."""
        result = self.insert("content_history", {
            "brand_id": brand_id,
            "platform": platform,
            "content_type": content_type,
            "content": content,
            "metadata": metadata or {},
        })
        return result is not None

    def log_smm_order(self, order: dict) -> bool:
        """Persist an SMM order."""
        result = self.upsert("smm_orders", {
            "order_id": str(order.get("order", order.get("order_id", ""))),
            "service_id": str(order.get("service", "")),
            "platform": order.get("platform", ""),
            "link": order.get("link", ""),
            "quantity": int(order.get("quantity", 0)),
            "price": float(order.get("charge", order.get("price", 0))),
            "status": order.get("status", "pending"),
            "metadata": order,
        })
        return result is not None


# ─── Singleton ────────────────────────────────────────────────────────────────
db = _SupabaseDB()
