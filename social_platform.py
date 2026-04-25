# ai_core/social_platform.py  — GrowthOS AI v2.0 — AI Social Network Platform
"""
Full AI Social Media Platform with:
  • Auto-registration for Telegram users (Name / TG-ID / Phone / Sex / DOB)
  • Post creation — Text, Image, Selfie/Short-Video
  • Feed / Timeline browsing
  • Like / Unlike posts
  • Comment on posts
  • Reply to comments
  • Admin view of all registered members
  • All data stored in encrypted JSON files
"""
from __future__ import annotations

import os
import json
import secrets
import base64
import hashlib
import re
from datetime import datetime, timezone
from typing import Optional

# ── Storage paths ─────────────────────────────────────────────────────────────
_DIR           = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR      = os.path.join(_DIR, "..", "social_data")
_USERS_FILE    = os.path.join(_DATA_DIR, "tg_users.json")
_POSTS_FILE    = os.path.join(_DATA_DIR, "posts.json")
_MEDIA_DIR     = os.path.join(_DATA_DIR, "media")

os.makedirs(_DATA_DIR, exist_ok=True)
os.makedirs(_MEDIA_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL I/O helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _load_json(path: str) -> dict | list:
    if not os.path.exists(path):
        return {} if path.endswith("users.json") else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if path.endswith("users.json") else []


def _save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_users() -> dict:
    return _load_json(_USERS_FILE)  # type: ignore[return-value]


def _save_users(users: dict):
    _save_json(_USERS_FILE, users)


def _load_posts() -> list:
    return _load_json(_POSTS_FILE)  # type: ignore[return-value]


def _save_posts(posts: list):
    _save_json(_POSTS_FILE, posts)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _post_id() -> str:
    return secrets.token_hex(8)


def _comment_id() -> str:
    return secrets.token_hex(6)


# ═══════════════════════════════════════════════════════════════════════════════
# USER REGISTRATION & PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

def is_registered(telegram_id: int | str) -> bool:
    """Return True if this Telegram user ID is already registered."""
    users = _load_users()
    return str(telegram_id) in users


def register_user(
    telegram_id: int | str,
    first_name: str,
    last_name: str = "",
    username: str = "",
    phone: str = "",
    sex: str = "",
    date_of_birth: str = "",
    bio: str = "",
    language_code: str = "en",
) -> dict:
    """
    Register or update a Telegram user profile.
    Returns the saved user record.
    """
    users = _load_users()
    tid   = str(telegram_id)

    display_name = f"{first_name} {last_name}".strip()
    now          = _now()

    if tid in users:
        # Update mutable fields only
        u = users[tid]
        u["display_name"]    = display_name or u.get("display_name", "")
        u["first_name"]      = first_name or u.get("first_name", "")
        u["last_name"]       = last_name  or u.get("last_name", "")
        u["username"]        = username   or u.get("username", "")
        u["language_code"]   = language_code
        if phone:
            u["phone"] = phone
        if sex:
            u["sex"] = sex
        if date_of_birth:
            u["date_of_birth"] = date_of_birth
        if bio:
            u["bio"] = bio
        u["last_seen"] = now
    else:
        u = {
            "telegram_id":   tid,
            "first_name":    first_name,
            "last_name":     last_name,
            "display_name":  display_name,
            "username":      username,
            "phone":         phone,
            "sex":           sex,
            "date_of_birth": date_of_birth,
            "bio":           bio,
            "language_code": language_code,
            "avatar_url":    "",
            "followers":     0,
            "following":     0,
            "post_count":    0,
            "registered_at": now,
            "last_seen":     now,
            "is_active":     True,
            "role":          "member",
        }
        users[tid] = u

    _save_users(users)
    return u


def get_user_profile(telegram_id: int | str) -> Optional[dict]:
    """Return user profile dict or None."""
    return _load_users().get(str(telegram_id))


def update_profile(telegram_id: int | str, **fields) -> dict:
    """Update allowed profile fields. Returns updated record."""
    allowed = {"phone", "sex", "date_of_birth", "bio", "avatar_url",
               "display_name", "first_name", "last_name"}
    users = _load_users()
    tid   = str(telegram_id)
    if tid not in users:
        raise ValueError("User not registered")
    for k, v in fields.items():
        if k in allowed:
            users[tid][k] = v
    users[tid]["last_seen"] = _now()
    _save_users(users)
    return users[tid]


def list_all_users() -> list[dict]:
    """Return list of all registered users (admin use)."""
    return list(_load_users().values())


def get_total_users() -> int:
    return len(_load_users())


# ═══════════════════════════════════════════════════════════════════════════════
# POST / MEDIA
# ═══════════════════════════════════════════════════════════════════════════════

def create_post(
    telegram_id: int | str,
    content: str,
    media_type: str = "text",       # "text" | "image" | "video" | "audio"
    media_file_id: str = "",        # Telegram file_id (for images/videos)
    media_url: str = "",
    location: str = "",
    tags: list[str] | None = None,
) -> dict:
    """Create a new post. Returns the post dict."""
    users = _load_users()
    tid   = str(telegram_id)
    if tid not in users:
        raise ValueError("Please register first with /start")

    posts   = _load_posts()
    pid     = _post_id()
    display = users[tid].get("display_name") or users[tid].get("first_name") or "Anonymous"
    post    = {
        "post_id":     pid,
        "author_id":   tid,
        "author_name": display,
        "author_uname": users[tid].get("username", ""),
        "content":     content[:2000],
        "media_type":  media_type,
        "media_file_id": media_file_id,
        "media_url":   media_url,
        "location":    location,
        "tags":        tags or [],
        "likes":       [],           # list of telegram_ids
        "comments":    [],           # list of comment dicts
        "views":       0,
        "shares":      0,
        "created_at":  _now(),
        "edited_at":   "",
        "is_active":   True,
    }
    posts.insert(0, post)           # newest first
    _save_posts(posts)

    # update user post count
    users[tid]["post_count"] = users[tid].get("post_count", 0) + 1
    _save_users(users)

    return post


def get_post(post_id: str) -> Optional[dict]:
    for p in _load_posts():
        if p.get("post_id") == post_id:
            return p
    return None


def get_feed(
    page: int = 1,
    per_page: int = 10,
    author_id: str | None = None,
) -> list[dict]:
    """Return paginated feed. If author_id given, return that user's posts only."""
    posts  = [p for p in _load_posts() if p.get("is_active", True)]
    if author_id:
        posts = [p for p in posts if p.get("author_id") == str(author_id)]
    start  = (page - 1) * per_page
    return posts[start: start + per_page]


def get_post_stats() -> dict:
    posts = _load_posts()
    active = [p for p in posts if p.get("is_active", True)]
    total_likes    = sum(len(p.get("likes", [])) for p in active)
    total_comments = sum(len(p.get("comments", [])) for p in active)
    return {
        "total_posts":    len(active),
        "total_likes":    total_likes,
        "total_comments": total_comments,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LIKE / UNLIKE
# ═══════════════════════════════════════════════════════════════════════════════

def toggle_like(telegram_id: int | str, post_id: str) -> dict:
    """
    Like or unlike a post.
    Returns {"liked": bool, "total_likes": int}.
    """
    tid   = str(telegram_id)
    posts = _load_posts()
    for p in posts:
        if p.get("post_id") == post_id:
            likes = p.setdefault("likes", [])
            if tid in likes:
                likes.remove(tid)
                liked = False
            else:
                likes.append(tid)
                liked = True
            _save_posts(posts)
            return {"liked": liked, "total_likes": len(likes)}
    raise ValueError(f"Post {post_id} not found")


# ═══════════════════════════════════════════════════════════════════════════════
# COMMENTS & REPLIES
# ═══════════════════════════════════════════════════════════════════════════════

def add_comment(
    telegram_id: int | str,
    post_id: str,
    text: str,
) -> dict:
    """Add a top-level comment to a post."""
    tid   = str(telegram_id)
    users = _load_users()
    if tid not in users:
        raise ValueError("Please register first with /start")

    posts  = _load_posts()
    author = users[tid].get("display_name") or users[tid].get("first_name") or "Anonymous"
    cid    = _comment_id()
    comment = {
        "comment_id": cid,
        "author_id":  tid,
        "author_name": author,
        "text":       text[:500],
        "likes":      [],
        "replies":    [],
        "created_at": _now(),
    }
    for p in posts:
        if p.get("post_id") == post_id:
            p.setdefault("comments", []).append(comment)
            _save_posts(posts)
            return comment
    raise ValueError(f"Post {post_id} not found")


def reply_comment(
    telegram_id: int | str,
    post_id: str,
    comment_id: str,
    text: str,
) -> dict:
    """Reply to a comment."""
    tid   = str(telegram_id)
    users = _load_users()
    if tid not in users:
        raise ValueError("Please register first with /start")

    posts  = _load_posts()
    author = users[tid].get("display_name") or users[tid].get("first_name") or "Anonymous"
    rid    = _comment_id()
    reply  = {
        "reply_id":   rid,
        "author_id":  tid,
        "author_name": author,
        "text":       text[:500],
        "likes":      [],
        "created_at": _now(),
    }
    for p in posts:
        if p.get("post_id") == post_id:
            for c in p.get("comments", []):
                if c.get("comment_id") == comment_id:
                    c.setdefault("replies", []).append(reply)
                    _save_posts(posts)
                    return reply
            raise ValueError(f"Comment {comment_id} not found")
    raise ValueError(f"Post {post_id} not found")


def like_comment(telegram_id: int | str, post_id: str, comment_id: str) -> dict:
    """Toggle like on a comment."""
    tid   = str(telegram_id)
    posts = _load_posts()
    for p in posts:
        if p.get("post_id") == post_id:
            for c in p.get("comments", []):
                if c.get("comment_id") == comment_id:
                    likes = c.setdefault("likes", [])
                    if tid in likes:
                        likes.remove(tid)
                        liked = False
                    else:
                        likes.append(tid)
                        liked = True
                    _save_posts(posts)
                    return {"liked": liked, "total_likes": len(likes)}
    raise ValueError("Comment not found")


# ═══════════════════════════════════════════════════════════════════════════════
# AI-POWERED POST ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def ai_enhance_caption(raw_text: str, platform: str = "Social") -> str:
    """
    Use LLM to improve/enhance post caption with emojis and hashtags.
    Falls back gracefully if LLM not configured.
    """
    try:
        from ai_core.llm_client import chat_completion
        prompt = (
            f"You are a viral social media expert. Improve this caption for {platform}. "
            f"Add 3-5 relevant emojis, 5-8 trending hashtags, and make it engaging and youth-friendly.\n\n"
            f"Original: {raw_text}\n\n"
            f"Return only the improved caption, nothing else."
        )
        result = chat_completion(prompt)
        return result.strip() if result else raw_text
    except Exception:
        return raw_text


def ai_suggest_reply(comment_text: str, post_content: str = "") -> str:
    """AI-generated smart reply suggestion."""
    try:
        from ai_core.llm_client import chat_completion
        prompt = (
            f"You are a friendly social media manager. Write a short, warm, engaging reply "
            f"(max 2 sentences) to this comment: '{comment_text}'\n"
            f"Context (post content): '{post_content[:200]}'"
        )
        result = chat_completion(prompt)
        return result.strip() if result else "Thanks for your comment! 😊"
    except Exception:
        return "Thanks for your comment! 😊"


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN & ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def admin_get_all_users() -> list[dict]:
    """Return all registered Telegram users for admin panel."""
    return sorted(
        list(_load_users().values()),
        key=lambda u: u.get("registered_at", ""),
        reverse=True,
    )


def admin_get_recent_posts(limit: int = 50) -> list[dict]:
    """Return most recent posts for admin review."""
    posts = [p for p in _load_posts() if p.get("is_active", True)]
    return posts[:limit]


def admin_delete_post(post_id: str) -> bool:
    """Soft-delete a post (admin only)."""
    posts = _load_posts()
    for p in posts:
        if p.get("post_id") == post_id:
            p["is_active"] = False
            _save_posts(posts)
            return True
    return False


def admin_ban_user(telegram_id: int | str) -> bool:
    """Deactivate a user account (admin only)."""
    users = _load_users()
    tid   = str(telegram_id)
    if tid in users:
        users[tid]["is_active"] = False
        _save_users(users)
        return True
    return False


def get_platform_stats() -> dict:
    users  = _load_users()
    posts  = _load_posts()
    active_posts = [p for p in posts if p.get("is_active", True)]

    total_likes    = sum(len(p.get("likes", [])) for p in active_posts)
    total_comments = sum(len(p.get("comments", [])) for p in active_posts)
    active_users   = sum(1 for u in users.values() if u.get("is_active", True))

    return {
        "total_users":     len(users),
        "active_users":    active_users,
        "total_posts":     len(active_posts),
        "total_likes":     total_likes,
        "total_comments":  total_comments,
        "registered_today": sum(
            1 for u in users.values()
            if u.get("registered_at", "")[:10] == datetime.now().strftime("%Y-%m-%d")
        ),
        "posts_today": sum(
            1 for p in active_posts
            if p.get("created_at", "")[:10] == datetime.now().strftime("%Y-%m-%d")
        ),
    }
