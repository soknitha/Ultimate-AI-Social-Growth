"""
GrowthOS AI v2.0 — Admin & Member Management System
=====================================================
Secure authentication, role management, and member lifecycle.

Security:
  • PBKDF2-SHA256 password hashing (260,000 iterations, random 32-byte salt)
  • AES-256 Fernet-encrypted user database  (users.enc)
  • XOR fallback encryption if `cryptography` not installed
  • 256-bit cryptographically random session tokens (timing-safe compare)
  • Role-based access control: admin | member | viewer

Usage:
    import admin
    user = admin.login("admin", "admin123")   # {token, role, display_name, ...}
    admin.verify_session(token)               # session info or None
    admin.list_users(token)                   # admin only
    admin.create_user(token, "bob", "pw", role="member")
    admin.logout(token)

Default first-run account:
    username: admin   password: admin123   (force_pw_change=True)
"""

import os
import json
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional

# ── File paths ────────────────────────────────────────────────────────────────
_DIR        = os.path.dirname(os.path.abspath(__file__))
_KEY_FILE   = os.path.join(_DIR, ".admin_key")
_USERS_FILE = os.path.join(_DIR, "users.enc")
_LOG_FILE   = os.path.join(_DIR, "activity_log.json")

# ── Public constants ──────────────────────────────────────────────────────────
ROLES            = ("admin", "member", "viewer")
SESSION_TTL_HOURS = 24

# ── Encryption ────────────────────────────────────────────────────────────────
try:
    from cryptography.fernet import Fernet
    _CRYPTO_OK = True
except ImportError:
    _CRYPTO_OK = False


def _get_key() -> bytes:
    """Load or create the encryption key file."""
    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read().strip()
    if _CRYPTO_OK:
        key = Fernet.generate_key()
    else:
        key = base64.urlsafe_b64encode(secrets.token_bytes(32))
    with open(_KEY_FILE, "wb") as f:
        f.write(key)
    try:
        os.chmod(_KEY_FILE, 0o600)
    except OSError:
        pass
    return key


def _xor_stretch(length: int) -> bytes:
    """Stretch key material for XOR fallback."""
    seed = _get_key()
    result, block = b"", seed
    while len(result) < length:
        block = hashlib.sha256(block).digest()
        result += block
    return result[:length]


def _encrypt(plaintext: str) -> str:
    if _CRYPTO_OK:
        return Fernet(_get_key()).encrypt(plaintext.encode()).decode()
    raw = plaintext.encode("utf-8")
    return base64.urlsafe_b64encode(bytes(a ^ b for a, b in zip(raw, _xor_stretch(len(raw))))).decode()


def _decrypt(ciphertext: str) -> str:
    if _CRYPTO_OK:
        return Fernet(_get_key()).decrypt(ciphertext.encode()).decode()
    raw = base64.urlsafe_b64decode(ciphertext)
    return bytes(a ^ b for a, b in zip(raw, _xor_stretch(len(raw)))).decode("utf-8")


# ── User storage ──────────────────────────────────────────────────────────────
def _load_users() -> dict:
    if not os.path.exists(_USERS_FILE):
        return {}
    try:
        data = open(_USERS_FILE, "r", encoding="utf-8").read().strip()
        return json.loads(_decrypt(data)) if data else {}
    except Exception:
        return {}


def _save_users(users: dict):
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        f.write(_encrypt(json.dumps(users, ensure_ascii=False)))


# ── Password hashing (OWASP 2024: ≥260,000 iterations for PBKDF2-SHA256) ─────
_PBKDF2_ITERS = 260_000


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(32)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERS
    )
    return base64.b64encode(dk).decode(), salt


def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    computed, _ = _hash_password(password, salt)
    return secrets.compare_digest(computed, stored_hash)


# ── Session management (in-memory) ────────────────────────────────────────────
_sessions: dict[str, dict] = {}


def _new_session(username: str, role: str) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "username":   username,
        "role":       role,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)).isoformat(),
    }
    return token


def verify_session(token: str) -> Optional[dict]:
    """Return session dict if valid, else None."""
    s = _sessions.get(token)
    if not s:
        return None
    if datetime.utcnow() > datetime.fromisoformat(s["expires_at"]):
        _sessions.pop(token, None)
        return None
    return dict(s)


def get_current_user(token: str) -> Optional[dict]:
    """Return full user record (no password fields) for a valid session."""
    sess = verify_session(token)
    if not sess:
        return None
    user = _load_users().get(sess["username"])
    if not user:
        return None
    safe = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
    safe["session_token"] = token
    return safe


# ── Activity log ──────────────────────────────────────────────────────────────
_MAX_LOG = 500


def _log(action: str, actor: str, target: str = "", detail: str = ""):
    entry = {
        "ts":     datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "actor":  actor,
        "target": target,
        "detail": detail,
    }
    log = []
    if os.path.exists(_LOG_FILE):
        try:
            log = json.loads(open(_LOG_FILE, "r", encoding="utf-8").read())
        except Exception:
            pass
    log.insert(0, entry)
    try:
        with open(_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log[:_MAX_LOG], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_activity_log(token: str) -> list:
    """Admin-only: return activity log list."""
    _require_admin(token)
    if not os.path.exists(_LOG_FILE):
        return []
    try:
        return json.loads(open(_LOG_FILE, "r", encoding="utf-8").read())
    except Exception:
        return []


# ── Internal helpers ──────────────────────────────────────────────────────────
def _require_admin(token: str) -> str:
    s = verify_session(token)
    if not s or s["role"] != "admin":
        raise PermissionError("Admin access required.")
    return s["username"]


# ── Bootstrap ─────────────────────────────────────────────────────────────────
def _bootstrap_admin():
    """Create default admin/admin123 account if no users exist."""
    if _load_users():
        return False
    pw_hash, salt = _hash_password("admin123")
    users = {
        "admin": {
            "username":        "admin",
            "password_hash":   pw_hash,
            "salt":            salt,
            "role":            "admin",
            "display_name":    "Administrator",
            "email":           "",
            "active":          True,
            "force_pw_change": True,
            "created_at":      datetime.utcnow().isoformat(),
            "created_by":      "system",
            "last_login":      None,
            "login_count":     0,
            "expiry":          None,
        }
    }
    _save_users(users)
    _log("BOOTSTRAP", "system", "admin", "Default admin created — login: admin / admin123")
    return True


# ── Auth ──────────────────────────────────────────────────────────────────────
def login(username: str, password: str) -> dict:
    """
    Authenticate user.
    Returns: {token, username, role, display_name, force_pw_change, email, active}
    Raises ValueError with a safe message on failure.
    """
    _bootstrap_admin()
    users  = _load_users()
    uname  = username.strip().lower()
    user   = users.get(uname)

    # Use same error for not-found vs wrong password (prevents enumeration)
    if not user or not _verify_password(password, user["password_hash"], user["salt"]):
        _log("LOGIN_FAIL", uname, detail="bad credentials")
        raise ValueError("Invalid username or password.")

    if not user.get("active", True):
        _log("LOGIN_FAIL", uname, detail="suspended")
        raise ValueError("Account is suspended. Contact your administrator.")

    if user.get("expiry"):
        if datetime.utcnow() > datetime.fromisoformat(user["expiry"]):
            _log("LOGIN_FAIL", uname, detail="expired")
            raise ValueError("Account license has expired. Contact your administrator.")

    user["last_login"]  = datetime.utcnow().isoformat()
    user["login_count"] = user.get("login_count", 0) + 1
    users[uname] = user
    _save_users(users)

    token = _new_session(uname, user["role"])
    _log("LOGIN", uname, detail=f"role={user['role']}")
    return {
        "token":           token,
        "username":        uname,
        "role":            user["role"],
        "display_name":    user.get("display_name", uname),
        "force_pw_change": user.get("force_pw_change", False),
        "email":           user.get("email", ""),
        "active":          user.get("active", True),
    }


def logout(token: str):
    """Invalidate a session token."""
    s = _sessions.pop(token, None)
    if s:
        _log("LOGOUT", s["username"])


def change_password(token: str, old_password: str, new_password: str):
    """Change password for the session owner."""
    sess = verify_session(token)
    if not sess:
        raise ValueError("Session expired. Please log in again.")
    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters.")
    users = _load_users()
    user  = users[sess["username"]]
    if not _verify_password(old_password, user["password_hash"], user["salt"]):
        raise ValueError("Current password is incorrect.")
    pw_hash, salt = _hash_password(new_password)
    user["password_hash"]   = pw_hash
    user["salt"]            = salt
    user["force_pw_change"] = False
    users[sess["username"]] = user
    _save_users(users)
    _log("PW_CHANGE", sess["username"])


# ── Admin-only user management ────────────────────────────────────────────────
def list_users(token: str) -> list:
    """Admin-only: return all users (no password fields)."""
    _require_admin(token)
    users = _load_users()
    safe  = [{k: v for k, v in u.items() if k not in ("password_hash", "salt")}
             for u in users.values()]
    return sorted(safe, key=lambda x: x.get("created_at", ""))


def create_user(
    token: str,
    username: str,
    password: str,
    role: str = "member",
    display_name: str = "",
    email: str = "",
    expiry_days: Optional[int] = None,
) -> dict:
    """Admin-only: create a new user account."""
    actor    = _require_admin(token)
    username = username.strip().lower()
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if role not in ROLES:
        raise ValueError(f"Role must be one of: {', '.join(ROLES)}")
    users = _load_users()
    if username in users:
        raise ValueError(f"Username '{username}' already exists.")
    pw_hash, salt = _hash_password(password)
    expiry = (
        (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
        if expiry_days else None
    )
    users[username] = {
        "username":        username,
        "password_hash":   pw_hash,
        "salt":            salt,
        "role":            role,
        "display_name":    display_name.strip() or username,
        "email":           email.strip(),
        "active":          True,
        "force_pw_change": True,
        "created_at":      datetime.utcnow().isoformat(),
        "created_by":      actor,
        "last_login":      None,
        "login_count":     0,
        "expiry":          expiry,
    }
    _save_users(users)
    _log("CREATE_USER", actor, username, f"role={role}")
    return {k: v for k, v in users[username].items() if k not in ("password_hash", "salt")}


def delete_user(token: str, username: str):
    """Admin-only: permanently delete a user. Cannot delete yourself."""
    actor = _require_admin(token)
    if username == actor:
        raise ValueError("You cannot delete your own account.")
    users = _load_users()
    if username not in users:
        raise ValueError(f"User '{username}' not found.")
    del users[username]
    _save_users(users)
    for tok, s in list(_sessions.items()):
        if s["username"] == username:
            del _sessions[tok]
    _log("DELETE_USER", actor, username)


def toggle_active(token: str, username: str) -> bool:
    """Admin-only: toggle user active/suspended. Returns new active state."""
    actor = _require_admin(token)
    if username == actor:
        raise ValueError("You cannot suspend your own account.")
    users = _load_users()
    if username not in users:
        raise ValueError(f"User '{username}' not found.")
    new_state = not users[username].get("active", True)
    users[username]["active"] = new_state
    _save_users(users)
    if not new_state:
        for tok, s in list(_sessions.items()):
            if s["username"] == username:
                del _sessions[tok]
    _log("TOGGLE_ACTIVE", actor, username, f"active={new_state}")
    return new_state


def reset_password(token: str, username: str, new_password: str):
    """Admin-only: force-reset a user's password and flag force_pw_change."""
    actor = _require_admin(token)
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    users = _load_users()
    if username not in users:
        raise ValueError(f"User '{username}' not found.")
    pw_hash, salt = _hash_password(new_password)
    users[username]["password_hash"]   = pw_hash
    users[username]["salt"]            = salt
    users[username]["force_pw_change"] = True
    _save_users(users)
    _log("RESET_PW", actor, username)


def update_user_info(
    token: str,
    username: str,
    display_name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
    expiry_days: Optional[int] = None,
) -> dict:
    """Admin-only: update user metadata fields."""
    actor = _require_admin(token)
    users = _load_users()
    if username not in users:
        raise ValueError(f"User '{username}' not found.")
    user = users[username]
    if display_name is not None:
        user["display_name"] = display_name.strip()
    if email is not None:
        user["email"] = email.strip()
    if role is not None:
        if role not in ROLES:
            raise ValueError(f"Invalid role: {role}")
        user["role"] = role
    if expiry_days is not None:
        user["expiry"] = (
            (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()
            if expiry_days > 0 else None
        )
    users[username] = user
    _save_users(users)
    _log("UPDATE_USER", actor, username, "info updated")
    return {k: v for k, v in user.items() if k not in ("password_hash", "salt")}


def get_stats() -> dict:
    """Return user statistics — no auth required (used on login screen)."""
    users = _load_users()
    if not users:
        _bootstrap_admin()
        users = _load_users()
    total   = len(users)
    active  = sum(1 for u in users.values() if u.get("active", True))
    admins  = sum(1 for u in users.values() if u.get("role") == "admin")
    members = sum(1 for u in users.values() if u.get("role") == "member")
    viewers = sum(1 for u in users.values() if u.get("role") == "viewer")
    return {
        "total": total, "active": active,
        "admins": admins, "members": members, "viewers": viewers,
    }
