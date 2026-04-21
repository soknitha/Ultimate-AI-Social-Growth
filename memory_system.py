"""
GrowthOS AI — Memory & Knowledge System
=========================================
Feature #9  (advanced): Memory-based Personalization AI
Feature #10 (Module 10): Knowledge & Memory
Feature #16 (advanced): AI Memory Timeline
Feature #19 (advanced): Narrative Consistency Engine

Storage priority:
  1. Supabase (cloud, persistent across devices) — when SUPABASE_URL is set
  2. Local file-based (memory_store/*.json)       — always works offline
"""
import json
import os
import sys
from datetime import datetime

# ─── Storage backend ─────────────────────────────────────────────────────────
_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_store")
os.makedirs(_BASE_DIR, exist_ok=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from supabase_client import db as _supabase
    _USE_SUPABASE = _supabase.available
except Exception:
    _supabase = None
    _USE_SUPABASE = False


def _path(brand_id: str, store_type: str) -> str:
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in brand_id)
    return os.path.join(_BASE_DIR, f"{safe_id}_{store_type}.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Brand Memory ─────────────────────────────────────────────────────────────
def store_brand_memory(brand_id: str, brand_data: dict) -> dict:
    """Store brand voice, style, and preferences."""
    brand_data["last_updated"] = datetime.now().isoformat()
    if _USE_SUPABASE:
        existing = _supabase.get_brand(brand_id)
        existing.update(brand_data)
        _supabase.save_brand(brand_id, existing)
        return {"status": "saved", "brand_id": brand_id, "storage": "supabase", "keys_stored": list(brand_data.keys())}
    # File fallback
    p = _path(brand_id, "brand")
    existing = _load(p)
    existing.update(brand_data)
    _save(p, existing)
    return {"status": "saved", "brand_id": brand_id, "storage": "file", "keys_stored": list(brand_data.keys())}


def retrieve_brand_context(brand_id: str) -> dict:
    """Retrieve all stored brand context."""
    if _USE_SUPABASE:
        data = _supabase.get_brand(brand_id)
        if data:
            return {"status": "found", "brand_id": brand_id, "storage": "supabase", "context": data}
        return {"status": "no_memory", "message": f"No brand memory found for '{brand_id}'"}
    # File fallback
    p = _path(brand_id, "brand")
    data = _load(p)
    if not data:
        return {"status": "no_memory", "message": f"No brand memory found for '{brand_id}'"}
    return {"status": "found", "brand_id": brand_id, "storage": "file", "context": data}


# ─── Campaign History ─────────────────────────────────────────────────────────
def store_campaign_result(brand_id: str, campaign_data: dict) -> dict:
    """Store completed campaign results for learning."""
    p = _path(brand_id, "campaigns")
    history = _load(p)
    campaign_id = f"camp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    history[campaign_id] = {
        **campaign_data,
        "stored_at": datetime.now().isoformat(),
    }
    _save(p, history)
    return {"status": "saved", "campaign_id": campaign_id}


def get_campaign_history(brand_id: str, limit: int = 10) -> dict:
    """Retrieve past campaign performance data."""
    p = _path(brand_id, "campaigns")
    history = _load(p)
    items = list(history.items())[-limit:]
    return {
        "brand_id": brand_id,
        "total_campaigns": len(history),
        "recent_campaigns": dict(items),
    }


# ─── Content Performance Memory ───────────────────────────────────────────────
def store_post_result(brand_id: str, post_data: dict) -> dict:
    """Remember what content worked and what didn't."""
    p = _path(brand_id, "posts")
    posts = _load(p)
    post_id = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    posts[post_id] = {
        **post_data,
        "stored_at": datetime.now().isoformat(),
    }
    _save(p, posts)
    return {"status": "saved", "post_id": post_id}


def get_top_performing_posts(brand_id: str, metric: str = "engagement_rate", limit: int = 5) -> dict:
    """Retrieve historically best-performing content patterns."""
    p = _path(brand_id, "posts")
    posts = _load(p)
    if not posts:
        return {"status": "no_data", "message": "No post history found"}

    sorted_posts = sorted(
        posts.items(),
        key=lambda x: x[1].get(metric, 0),
        reverse=True,
    )[:limit]

    return {
        "brand_id": brand_id,
        "metric": metric,
        "top_posts": dict(sorted_posts),
        "patterns": _extract_patterns(dict(sorted_posts)),
    }


def _extract_patterns(top_posts: dict) -> list:
    """Extract winning patterns from top posts."""
    patterns = []
    for post_id, data in top_posts.items():
        if data.get("content_type"):
            patterns.append(f"✅ {data['content_type']} format shows high {data.get('engagement_rate', 0):.1f}% engagement")
        if data.get("posting_time"):
            patterns.append(f"⏰ Posts at {data['posting_time']} outperform average")
    return patterns or ["No patterns extracted yet — need more post history"]


# ─── AI Memory Timeline ───────────────────────────────────────────────────────
def get_memory_timeline(brand_id: str) -> dict:
    """Full chronological history of all AI decisions and results."""
    timeline_p = _path(brand_id, "timeline")
    timeline = _load(timeline_p)
    return {
        "brand_id": brand_id,
        "total_events": len(timeline),
        "timeline": dict(sorted(timeline.items(), reverse=True)),
        "memory_tip": "Use this timeline to identify what strategies consistently produce results",
    }


def log_ai_decision(brand_id: str, decision: str, context: dict, outcome: str = "pending") -> dict:
    """Log every AI decision for accountability and learning."""
    timeline_p = _path(brand_id, "timeline")
    timeline = _load(timeline_p)
    event_id = f"ev_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timeline[event_id] = {
        "decision": decision,
        "context": context,
        "outcome": outcome,
        "timestamp": datetime.now().isoformat(),
    }
    _save(timeline_p, timeline)
    return {"logged": True, "event_id": event_id}


# ─── Knowledge Base / Brand SOP ──────────────────────────────────────────────
def store_knowledge(brand_id: str, topic: str, content: str) -> dict:
    """Store brand SOPs, guidelines, and knowledge."""
    kb_p = _path(brand_id, "knowledge")
    kb = _load(kb_p)
    kb[topic] = {
        "content": content,
        "updated": datetime.now().isoformat(),
    }
    _save(kb_p, kb)
    return {"status": "stored", "topic": topic}


def search_knowledge(brand_id: str, query: str) -> dict:
    """Simple keyword search across brand knowledge base."""
    kb_p = _path(brand_id, "knowledge")
    kb = _load(kb_p)
    query_lower = query.lower()
    results = {
        topic: data for topic, data in kb.items()
        if query_lower in topic.lower() or query_lower in data.get("content", "").lower()
    }
    return {
        "query": query,
        "results_found": len(results),
        "results": results,
    }


# ─── Brand Summary for AI context ────────────────────────────────────────────
def build_ai_context_summary(brand_id: str) -> str:
    """Build a compact summary of brand memory for AI prompts."""
    brand = retrieve_brand_context(brand_id).get("context", {})
    if not brand:
        return "No brand memory found. Operating in generic mode."

    summary_parts = []
    if brand.get("name"):
        summary_parts.append(f"Brand: {brand['name']}")
    if brand.get("niche"):
        summary_parts.append(f"Niche: {brand['niche']}")
    if brand.get("tone"):
        summary_parts.append(f"Voice: {brand['tone']}")
    if brand.get("target_audience"):
        summary_parts.append(f"Audience: {brand['target_audience']}")
    if brand.get("banned_words"):
        summary_parts.append(f"Avoid: {', '.join(brand['banned_words'])}")

    return " | ".join(summary_parts) if summary_parts else "Basic brand profile stored."
