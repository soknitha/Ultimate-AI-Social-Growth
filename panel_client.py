"""
GrowthOS AI — SMM Panel Client  (Generic API v2)
=================================================
Feature #2  : Smart Order Auto-Optimization
Feature #8  : Smart Pricing Engine
Feature #10 : White-label AI Panel

Works with ANY SMM panel that uses the standard API v2 format.
Configure via environment variables:
    SMM_API_KEY=your_key
    SMM_API_URL=https://your-panel.com/api/v2

Production-grade implementation:
  • Persistent httpx.AsyncClient connection pool (reused, not per-request)
  • Exponential-backoff retry (3 attempts) for transient errors
  • Services list TTL cache (10 min) to minimise API calls
  • Live order history persisted to Supabase or orders_history.json
  • Bulk order status (up to 100 IDs per request)
  • Graceful demo fallback when key is absent / placeholder
"""
import sys
import os
import json
import asyncio
import time
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SMM_API_KEY, SMM_API_URL, USE_SMM_PANEL
# Legacy aliases
DEMOSMM_API_KEY = SMM_API_KEY
DEMOSMM_API_URL = SMM_API_URL

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False
    try:
        import requests as _requests
    except ImportError:
        _requests = None


# ─── Persistent HTTP Client ───────────────────────────────────────────────────
_client: "httpx.AsyncClient | None" = None

async def _get_client() -> "httpx.AsyncClient":
    """Return (or lazily create) the shared async HTTP client."""
    global _client
    if _HAS_HTTPX:
        if _client is None or _client.is_closed:
            _client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=5.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
                headers={"User-Agent": "GrowthOS-AI/2.0"},
            )
        return _client
    return None  # type: ignore


async def _api_call(action: str, params: dict = None, _retries: int = 3) -> dict:
    """
    Perform authenticated POST to SMM panel API v2.
    Retries up to _retries times with exponential backoff on connection errors.
    """
    if not USE_SMM_PANEL:
        return {"_demo": True}

    payload = {"key": DEMOSMM_API_KEY, "action": action, **(params or {})}

    last_error: str = "Unknown error"
    for attempt in range(_retries):
        try:
            if _HAS_HTTPX:
                client = await _get_client()
                resp = await client.post(DEMOSMM_API_URL, data=payload)
                resp.raise_for_status()
                data = resp.json()
                # API-level error returned as {"error": "..."} with HTTP 200
                if isinstance(data, dict) and "error" in data:
                    return {"error": data["error"]}
                return data
            elif _requests:
                resp = _requests.post(DEMOSMM_API_URL, data=payload, timeout=20)
                resp.raise_for_status()
                return resp.json()
            else:
                return {"error": "No HTTP library available. Install httpx or requests."}
        except Exception as exc:
            last_error = str(exc)
            if attempt < _retries - 1:
                await asyncio.sleep(2 ** attempt)   # 1s, 2s, 4s backoff

    return {"error": f"API unreachable after {_retries} attempts: {last_error}"}


# ─── Services Cache (TTL = 600 s) ─────────────────────────────────────────────
_svc_cache: dict[str, Any] = {}   # key -> (timestamp, data)
_SVC_CACHE_TTL = 600              # 10 minutes


def _svc_cache_get(key: str):
    entry = _svc_cache.get(key)
    if entry and (time.time() - entry[0]) < _SVC_CACHE_TTL:
        return entry[1]
    return None

def _svc_cache_set(key: str, data: Any):
    _svc_cache[key] = (time.time(), data)


# ─── Order History Persistence ────────────────────────────────────────────────
_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "orders_history.json"
)

def _load_history() -> dict:
    try:
        with open(_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_history(history: dict) -> None:
    try:
        os.makedirs(os.path.dirname(_HISTORY_FILE), exist_ok=True)
        with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ─── Demo data store ──────────────────────────────────────────────────────────
_DEMO_SERVICES = [
    {"service": 1001, "name": "Facebook Live Stream Views [15 min]",  "type": "Default", "category": "Facebook Live Stream", "rate": "0.50", "min": 10,   "max": 5000,   "refill": False},
    {"service": 1002, "name": "Facebook Live Stream Views [60 min]",  "type": "Default", "category": "Facebook Live Stream", "rate": "1.20", "min": 10,   "max": 50000,  "refill": False},
    {"service": 1003, "name": "Facebook Followers [Real Mix]",         "type": "Default", "category": "Facebook",            "rate": "0.80", "min": 100,  "max": 100000, "refill": True},
    {"service": 1004, "name": "TikTok Followers [HQ]",                 "type": "Default", "category": "TikTok",              "rate": "1.50", "min": 50,   "max": 50000,  "refill": True},
    {"service": 1005, "name": "TikTok Views [Fast]",                   "type": "Default", "category": "TikTok",              "rate": "0.15", "min": 100,  "max": 1000000,"refill": False},
    {"service": 1006, "name": "TikTok Likes [HQ]",                     "type": "Default", "category": "TikTok",              "rate": "0.60", "min": 50,   "max": 100000, "refill": True},
    {"service": 1007, "name": "Instagram Followers [Real]",            "type": "Default", "category": "Instagram",           "rate": "2.50", "min": 100,  "max": 50000,  "refill": True},
    {"service": 1008, "name": "Instagram Likes [HQ]",                  "type": "Default", "category": "Instagram",           "rate": "0.40", "min": 50,   "max": 50000,  "refill": False},
    {"service": 1009, "name": "Instagram Views [Reels]",               "type": "Default", "category": "Instagram",           "rate": "0.10", "min": 100,  "max": 1000000,"refill": False},
    {"service": 1010, "name": "YouTube Views [HQ Retention]",          "type": "Default", "category": "YouTube",             "rate": "3.50", "min": 500,  "max": 100000, "refill": False},
    {"service": 1011, "name": "YouTube Subscribers [Real]",            "type": "Default", "category": "YouTube",             "rate": "5.00", "min": 100,  "max": 10000,  "refill": True},
    {"service": 1012, "name": "Telegram Members [Real]",               "type": "Default", "category": "Telegram",            "rate": "1.20", "min": 100,  "max": 100000, "refill": True},
    {"service": 1013, "name": "Telegram Post Views",                   "type": "Default", "category": "Telegram",            "rate": "0.30", "min": 100,  "max": 500000, "refill": False},
]

_order_counter = 90000
_demo_orders: dict = {}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def get_panel_info() -> dict:
    """Return panel connection status, mode, and API URL."""
    return {
        "mode":         "live" if USE_SMM_PANEL else "demo",
        "api_url":      DEMOSMM_API_URL,
        "key_set":      bool(DEMOSMM_API_KEY),
        "http_library": "httpx" if _HAS_HTTPX else ("requests" if _requests else "none"),
        "cache_ttl_s":  _SVC_CACHE_TTL,
        "checked_at":   datetime.now().isoformat(),
    }


async def get_services(category: str = None) -> dict:
    """
    List all available SMM services, optionally filtered by category.
    Live results are cached for _SVC_CACHE_TTL seconds.
    """
    cache_key = f"services:{(category or '').lower()}"

    if USE_SMM_PANEL:
        cached = _svc_cache_get(cache_key)
        if cached:
            return {**cached, "cached": True}

        data = await _api_call("services")
        if "error" not in data and not data.get("_demo"):
            svc_list = data if isinstance(data, list) else data.get("services", [])
            if category:
                svc_list = [s for s in svc_list if category.lower() in str(s.get("category", "")).lower()]
            result = {
                "source": "live",
                "services": svc_list,
                "total": len(svc_list),
                "categories": list({s.get("category", "") for s in svc_list}),
                "cached": False,
                "fetched_at": datetime.now().isoformat(),
            }
            _svc_cache_set(cache_key, result)
            return result
        # Fall through to demo on API error
        return {"source": "live_error", "error": data.get("error", "Unknown"), "services": []}

    services = _DEMO_SERVICES
    if category:
        services = [s for s in services if category.lower() in s["category"].lower()]

    return {
        "source": "demo",
        "services": services,
        "total": len(services),
        "categories": list({s["category"] for s in _DEMO_SERVICES}),
    }


async def check_balance() -> dict:
    """Check account balance and currency."""
    if USE_SMM_PANEL:
        data = await _api_call("balance")
        if "error" not in data and not data.get("_demo"):
            return {
                "source":        "live",
                "balance":       data.get("balance", "0.00"),
                "currency":      data.get("currency", "USD"),
                "checked_at":    datetime.now().isoformat(),
            }
        if "error" in data:
            return {"source": "live_error", "error": data["error"]}

    return {
        "source":       "demo",
        "balance":      "125.50",
        "currency":     "USD",
        "account_type": "Reseller",
        "status":       "Active",
        "note":         "Set SMM_API_KEY and SMM_API_URL in .env to see your real balance",
    }


async def place_order(service_id: int, link: str, quantity: int) -> dict:
    """Place a new SMM order with live API; falls back to demo simulation."""
    global _order_counter

    # Input validation against known demo services (also applies to live mode for safety)
    service = next((s for s in _DEMO_SERVICES if s["service"] == service_id), None)
    if service:
        if quantity < service["min"]:
            return {"error": f"Minimum quantity for service #{service_id} is {service['min']}"}
        if quantity > service["max"]:
            return {"error": f"Maximum quantity for service #{service_id} is {service['max']}"}

    if not link or not link.strip():
        return {"error": "Link / URL cannot be empty"}

    if USE_SMM_PANEL:
        data = await _api_call("add", {
            "service":  service_id,
            "link":     link.strip(),
            "quantity": quantity,
        })
        if "error" not in data and not data.get("_demo"):
            order_id = data.get("order")
            # Persist to live order history
            if order_id:
                history = _load_history()
                history[str(order_id)] = {
                    "order":      order_id,
                    "service":    service_id,
                    "link":       link,
                    "quantity":   quantity,
                    "source":     "live",
                    "placed_at":  datetime.now().isoformat(),
                }
                _save_history(history)
            return {"source": "live", **data}
        if "error" in data:
            return {"source": "live_error", "error": data["error"]}

    # Demo simulation
    _order_counter += 1
    order_id = _order_counter
    charge = f"${float(service['rate']) * quantity / 1000:.4f}" if service else "$0.0000"
    _demo_orders[str(order_id)] = {
        "order":      order_id,
        "service":    service_id,
        "link":       link,
        "quantity":   quantity,
        "start_count": 0,
        "status":     "Pending",
        "remains":    quantity,
        "charge":     charge,
        "currency":   "USD",
        "created_at": datetime.now().isoformat(),
    }
    return {
        "source":       "demo",
        "order":        order_id,
        "status":       "Order placed successfully",
        "service_name": service["name"] if service else f"Service #{service_id}",
        "link":         link,
        "quantity":     quantity,
        "charge":       charge,
    }


async def check_order_status(order_ids) -> dict:
    """
    Check status of one or multiple orders (max 100 IDs).
    For live mode uses multi-status bulk endpoint when >1 ID.
    """
    import random
    if isinstance(order_ids, int):
        order_ids = [order_ids]
    order_ids = list(order_ids)[:100]

    if USE_SMM_PANEL:
        ids_str = ",".join(str(i) for i in order_ids)
        params  = {"orders": ids_str} if len(order_ids) > 1 else {"order": order_ids[0]}
        data    = await _api_call("status", params)
        if "error" not in data and not data.get("_demo"):
            # Normalise: single-order API returns flat dict, multi returns nested
            if len(order_ids) == 1 and isinstance(data, dict) and "status" in data:
                orders = {str(order_ids[0]): data}
            else:
                orders = data
            return {"source": "live", "orders": orders, "queried": len(order_ids)}
        if "error" in data:
            return {"source": "live_error", "error": data["error"]}

    # Demo simulation with realistic progression
    results = {}
    for oid in order_ids:
        stored = _demo_orders.get(str(oid))
        if stored:
            qty = stored["quantity"]
            completed = random.randint(int(qty * 0.3), qty)
            stored["status"]  = "Completed" if completed >= qty else "In Progress"
            stored["remains"] = max(0, qty - completed)
            results[str(oid)] = {
                "charge":      stored["charge"],
                "start_count": stored.get("start_count", 0),
                "status":      stored["status"],
                "remains":     stored["remains"],
                "currency":    "USD",
            }
        else:
            results[str(oid)] = {"status": "Not Found", "error": f"Order {oid} not found in demo store"}

    return {"source": "demo", "orders": results, "queried": len(order_ids)}


async def request_refill(order_id: int) -> dict:
    """Request a refill for a completed order (service must support refill)."""
    if USE_SMM_PANEL:
        data = await _api_call("refill", {"order": order_id})
        if "error" not in data and not data.get("_demo"):
            return {"source": "live", **data}
        if "error" in data:
            return {"source": "live_error", "error": data["error"]}

    stored = _demo_orders.get(str(order_id))
    if not stored:
        return {"error": f"Order {order_id} not found"}

    service = next((s for s in _DEMO_SERVICES if s["service"] == stored.get("service")), None)
    if service and not service.get("refill"):
        return {"error": f"Service '{service['name']}' does not support refill"}

    refill_id = f"REFILL_{order_id}_{datetime.now().strftime('%H%M%S')}"
    return {
        "source":   "demo",
        "refill":   refill_id,
        "order_id": order_id,
        "status":   "Refill request submitted successfully",
    }


async def cancel_orders(order_ids: list) -> dict:
    """Cancel one or more pending orders (max 100 IDs)."""
    order_ids = list(order_ids)[:100]

    if USE_SMM_PANEL:
        data = await _api_call("cancel", {"orders": ",".join(str(i) for i in order_ids)})
        if "error" not in data and not data.get("_demo"):
            return {"source": "live", **data}
        if "error" in data:
            return {"source": "live_error", "error": data["error"]}

    results = {}
    for oid in order_ids:
        key = str(oid)
        if key in _demo_orders:
            status = _demo_orders[key]["status"]
            if status == "Pending":
                _demo_orders[key]["status"] = "Cancelled"
                results[key] = {"cancel_id": oid, "status": "Cancelled"}
            else:
                results[key] = {"error": f"Cannot cancel — order status is '{status}'"}
        else:
            results[key] = {"error": f"Order {oid} not found"}

    return {"source": "demo", "cancelled": results, "total_cancelled": sum(1 for v in results.values() if "cancel_id" in v)}


async def get_order_history(limit: int = 50) -> dict:
    """Return order history (live orders from JSON + demo in-memory orders)."""
    orders = []

    if USE_SMM_PANEL:
        history = _load_history()
        for oid, rec in list(history.items())[-limit:]:
            orders.append({**rec, "source": "live"})
    else:
        for oid, rec in list(_demo_orders.items())[-limit:]:
            orders.append({**rec, "source": "demo"})

    return {
        "source":  "live" if USE_SMM_PANEL else "demo",
        "orders":  orders,
        "total":   len(orders),
    }


# ─── Feature #2: Smart Order (AI-Optimized) ──────────────────────────────────
async def smart_order(link: str, goal: str, budget_usd: float, platform: str) -> dict:
    """
    Feature #2: Smart Order Auto-Optimization.
    AI selects the best service and quantity based on goal and budget.
    Works in both live and demo mode.
    """
    if budget_usd <= 0:
        return {"error": "Budget must be greater than $0"}
    if not link:
        return {"error": "Link cannot be empty"}

    services_data = await get_services()
    all_services  = services_data.get("services", [])

    if not all_services:
        return {"error": f"No services available (panel source: {services_data.get('source', 'unknown')})"}

    # Filter by platform
    platform_services = [
        s for s in all_services
        if platform.lower() in str(s.get("category", "")).lower()
    ]
    if not platform_services:
        return {"error": f"No services found for platform: {platform}"}

    # AI-style goal matching
    goal_lower = goal.lower()
    if any(kw in goal_lower for kw in ("follower", "subscriber", "growth", "member")):
        candidates = [s for s in platform_services if any(kw in s["name"].lower() for kw in ("follower", "subscriber", "member"))]
    elif any(kw in goal_lower for kw in ("view", "reach", "impression")):
        candidates = [s for s in platform_services if "view" in s["name"].lower()]
    elif any(kw in goal_lower for kw in ("like", "engage", "reaction")):
        candidates = [s for s in platform_services if "like" in s["name"].lower()]
    elif "comment" in goal_lower:
        candidates = [s for s in platform_services if "comment" in s["name"].lower()]
    else:
        candidates = platform_services

    if not candidates:
        candidates = platform_services

    # Rank: best-value (lowest cost per 1000, refill preferred)
    def _score(s):
        rate     = float(s.get("rate", 999))
        has_refill = 1 if s.get("refill") else 0
        return rate - has_refill * 0.1   # small bonus for refillable

    best_service = min(candidates, key=_score)

    rate        = float(best_service.get("rate", 1.0))
    max_qty     = int(best_service.get("max", 1000))
    min_qty     = int(best_service.get("min", 10))
    optimal_qty = min(max_qty, max(min_qty, int((budget_usd / rate) * 1000)))
    actual_cost = rate * optimal_qty / 1000

    return {
        "ai_recommendation":     f"Best service for '{goal}' within ${budget_usd:.2f} budget",
        "selected_service":      best_service,
        "recommended_quantity":  optimal_qty,
        "estimated_cost":        f"${actual_cost:.4f}",
        "remaining_budget":      f"${budget_usd - actual_cost:.4f}",
        "optimization_reason":   (
            f"Lowest cost-per-1000 for {platform} {goal}"
            + (" + refill supported" if best_service.get("refill") else "")
        ),
        "alternatives":          sorted(candidates, key=_score)[:3],
        "place_order_ready":     True,
        "link":                  link,
        "panel_source":          services_data.get("source", "unknown"),
        "analyzed_at":           datetime.now().isoformat(),
    }
