"""
GrowthOS AI — Social Media OAuth & Account Manager
====================================================
Features #105–#110: Secure Multi-Platform Authentication

  #105 — OAuth 2.0 + PKCE flow for 6 major platforms
  #106 — AES-256 Fernet encrypted local token storage
  #107 — Automatic token refresh (access + refresh tokens)
  #108 — Multi-account support (multiple accounts per platform)
  #109 — Connection health monitoring & status tracking
  #110 — Bot-token connect (Telegram & future platforms)

Supported platforms:
  Facebook  • Instagram • TikTok • YouTube • Twitter/X • LinkedIn • Telegram

Architecture:
  • All tokens encrypted at rest via cryptography.Fernet (AES-128-CBC + HMAC-SHA256)
  • Fallback XOR obfuscation if `cryptography` package not installed
  • OAuth callback captured by FastAPI server at /oauth/callback (port 8000)
  • PKCE S256 for TikTok, YouTube, Twitter/X (RFC 7636)
  • Secrets generated with os.urandom (CSPRNG)
"""

import os
import sys
import json
import base64
import hashlib
import secrets
import asyncio
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cryptography.fernet import Fernet, InvalidToken
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

# ─── Storage paths ────────────────────────────────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AUTH_FILE = os.path.join(_BASE_DIR, "social_accounts.enc")
_KEY_FILE  = os.path.join(_BASE_DIR, ".auth_key")

# ─── Redirect URI (FastAPI captures on port 8000) ─────────────────────────────
_REDIRECT_URI = "http://localhost:8000/oauth/callback"

# ─── Platform Configurations ──────────────────────────────────────────────────
PLATFORM_CONFIGS: dict[str, dict] = {

    "Facebook": {
        "auth_url":      "https://www.facebook.com/v21.0/dialog/oauth",
        "token_url":     "https://graph.facebook.com/v21.0/oauth/access_token",
        "api_base":      "https://graph.facebook.com/v21.0",
        "test_endpoint": "/me?fields=id,name,picture",
        # NOTE: instagram_basic was removed by Facebook in Sept 2020 — do NOT include it.
        # Instagram Graph API scopes (instagram_content_publish etc.) require adding the
        # "Instagram Graph API" product separately in the Facebook Developer Console.
        # Keep scopes to Facebook-only here; Instagram uses its own platform entry below.
        # In Development Mode, no App Review is needed — just add your account as a Developer
        # or Tester under App → Roles → Roles in the Facebook Developer Console.
        # SAFE SCOPES — work on ALL Facebook app types in Development Mode
        # without App Review AND without adding anything in Permissions & Features.
        #
        #   public_profile   → always auto-granted (name, id, picture)
        #   pages_show_list  → list Pages the user admins
        #
        # pages_read_engagement and pages_manage_posts both require the permission
        # to be added under App Review > Permissions & Features in the Facebook
        # Developer Console even in Development Mode — so we omit them here.
        # Use the "Quick Token" flow (Graph API Explorer) to get full Page access.
        "scopes": [
            "public_profile",
            "pages_show_list",
        ],
        "icon": "📘", "color": "#1877F2",
        "auth_type": "oauth2",  "pkce": False,
        "docs_url": "https://developers.facebook.com/apps/",
        "docs_steps": (
            "══════════════════════════════════════════════════════\n"
            "EASIEST: Facebook Quick Token (no App ID/Secret needed)\n"
            "══════════════════════════════════════════════════════\n"
            "1. Go to: https://developers.facebook.com/tools/explorer\n"
            "2. Click 'Generate Access Token' (top right)\n"
            "3. Tick: pages_show_list, pages_read_engagement, pages_manage_posts\n"
            "4. Click 'Generate Token' → copy the token shown\n"
            "5. In GrowthOS → 🔐 Social Accounts → 🚀 Quick Token tab\n"
            "   → select Facebook → paste token → click Connect\n"
            "\n"
            "══════════════════════════════════════════════════════\n"
            "FULL OAuth (long-lived token via your own Facebook App)\n"
            "══════════════════════════════════════════════════════\n"
            "1. https://developers.facebook.com/apps/ → Create App → Consumer\n"
            "2. Add product: Facebook Login → Set Up\n"
            "3. Facebook Login → Settings → Valid OAuth Redirect URIs:\n"
            "       http://localhost:8000/oauth/callback\n"
            "4. Settings → Basic → copy App ID and App Secret\n"
            "5. Left sidebar → Roles → Roles → Add Developers (add yourself)\n"
            "6. Make sure app toggle shows 'In development'\n"
            "7. Paste App ID + App Secret in Connect Platform tab → Start OAuth\n"
            "   ⚠ Only use: public_profile + pages_show_list\n"
            "   Do NOT add pages_manage_posts — it requires App Review."
        ),
    },

    "Instagram": {
        "auth_url":        "https://api.instagram.com/oauth/authorize",
        "token_url":       "https://api.instagram.com/oauth/access_token",
        "long_token_url":  "https://graph.instagram.com/access_token",
        "api_base":        "https://graph.instagram.com/v21.0",
        "test_endpoint":   "/me?fields=id,username,account_type",
        "scopes": ["user_profile", "user_media"],
        "icon": "📸", "color": "#E1306C",
        "auth_type": "oauth2", "pkce": False,
        "docs_url": "https://developers.facebook.com/apps/",
        "docs_steps": (
            "1. Instagram Basic Display API uses the Facebook Developer Console\n"
            "2. Go to https://developers.facebook.com/apps/ → Create App → Consumer\n"
            "3. Add product: 'Instagram Basic Display'\n"
            "4. Instagram Basic Display → Settings → add Redirect URI:\n"
            "       http://localhost:8000/oauth/callback\n"
            "5. Add your Instagram account as a Test User\n"
            "6. Copy 'Instagram App ID' and 'Instagram App Secret'\n"
            "7. Paste both below and click Start OAuth"
        ),
    },

    "TikTok": {
        "auth_url":      "https://www.tiktok.com/v2/auth/authorize/",
        "token_url":     "https://open.tiktokapis.com/v2/oauth/token/",
        "api_base":      "https://open.tiktokapis.com/v2",
        "test_endpoint": "/user/info/?fields=open_id,union_id,avatar_url,display_name",
        "scopes": ["user.info.basic", "video.list", "video.upload", "video.publish"],
        "icon": "🎵", "color": "#FF004F",
        "auth_type": "oauth2_pkce", "pkce": True,
        "docs_url": "https://developers.tiktok.com/",
        "docs_steps": (
            "1. Go to https://developers.tiktok.com/ → Login → My Apps\n"
            "2. Create App → select 'Connect TikTok Accounts and Manage Content'\n"
            "3. Add products: Login Kit + Content Posting API\n"
            "4. Login Kit → Settings → add Redirect URI:\n"
            "       http://localhost:8000/oauth/callback\n"
            "5. Copy 'Client Key' (Client ID) from App Details\n"
            "   (Client Secret optional — TikTok uses PKCE so secret is not required)\n"
            "6. Paste Client Key below and click Start OAuth"
        ),
    },

    "YouTube": {
        "auth_url":      "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url":     "https://oauth2.googleapis.com/token",
        "api_base":      "https://www.googleapis.com/youtube/v3",
        "test_endpoint": "/channels?part=snippet&mine=true",
        "scopes": [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ],
        "icon": "▶️", "color": "#FF0000",
        "auth_type": "oauth2_pkce", "pkce": True,
        "docs_url": "https://console.cloud.google.com/",
        "docs_steps": (
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create Project → APIs & Services → Library → Enable 'YouTube Data API v3'\n"
            "3. APIs & Services → Credentials → Create Credentials → OAuth Client ID\n"
            "4. Application Type: Desktop App\n"
            "5. Authorized Redirect URIs → add:\n"
            "       http://localhost:8000/oauth/callback\n"
            "6. Copy 'Client ID' and 'Client Secret'\n"
            "7. Also go to OAuth Consent Screen → set to External + add your email as test user\n"
            "8. Paste both below and click Start OAuth"
        ),
    },

    "Twitter/X": {
        "auth_url":      "https://twitter.com/i/oauth2/authorize",
        "token_url":     "https://api.twitter.com/2/oauth2/token",
        "api_base":      "https://api.twitter.com/2",
        "test_endpoint": "/users/me",
        "scopes":        ["tweet.read", "tweet.write", "users.read", "offline.access"],
        "icon": "🐦", "color": "#1DA1F2",
        "auth_type": "oauth2_pkce", "pkce": True,
        "docs_url": "https://developer.twitter.com/en/portal/dashboard",
        "docs_steps": (
            "1. Go to https://developer.twitter.com/en/portal/dashboard\n"
            "2. Create Project → Create App (Free Basic tier is enough)\n"
            "3. App Settings → Authentication Settings → Enable OAuth 2.0\n"
            "4. App Type: Native App (uses PKCE — more secure)\n"
            "5. Callback URI → add:\n"
            "       http://localhost:8000/oauth/callback\n"
            "6. Keys and Tokens → OAuth 2.0 → copy 'Client ID'\n"
            "   (No Client Secret needed for Native/PKCE apps)\n"
            "7. Paste Client ID below and click Start OAuth"
        ),
    },

    "LinkedIn": {
        "auth_url":      "https://www.linkedin.com/oauth/v2/authorization",
        "token_url":     "https://www.linkedin.com/oauth/v2/accessToken",
        "api_base":      "https://api.linkedin.com/v2",
        "test_endpoint": "/me",
        "scopes":        ["r_liteprofile", "r_emailaddress", "w_member_social"],
        "icon": "💼", "color": "#0A66C2",
        "auth_type": "oauth2", "pkce": False,
        "docs_url": "https://www.linkedin.com/developers/apps",
        "docs_steps": (
            "1. Go to https://www.linkedin.com/developers/apps\n"
            "2. Create App → fill company name and logo\n"
            "3. Auth tab → Authorized Redirect URLs → add:\n"
            "       http://localhost:8000/oauth/callback\n"
            "4. Products tab → request: 'Sign In with LinkedIn using OpenID Connect'\n"
            "   and 'Share on LinkedIn'\n"
            "5. Auth tab → copy 'Client ID' and 'Client Secret'\n"
            "6. Paste both below and click Start OAuth"
        ),
    },

    "Telegram": {
        "auth_url":      "",
        "token_url":     "",
        "api_base":      "https://api.telegram.org",
        "test_endpoint": "",
        "scopes":        [],
        "icon": "✈️", "color": "#26A5E4",
        "auth_type": "bot_token", "pkce": False,
        "docs_url": "https://t.me/BotFather",
        "docs_steps": (
            "1. Open Telegram on your phone or desktop\n"
            "2. Search for @BotFather → Start\n"
            "3. Send: /newbot\n"
            "4. Follow instructions: give your bot a name and username\n"
            "5. BotFather will send you a token like:\n"
            "       1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ\n"
            "6. Copy that token and paste it in the 'Bot Tokens' tab\n"
            "7. Click 'Connect Bot Token' — GrowthOS will verify it with Telegram API"
        ),
    },
}

# ─── In-memory OAuth state + PKCE store ──────────────────────────────────────
# state → {verifier, platform, client_id, client_secret}
_pkce_store: dict[str, dict] = {}

# In-memory callback capture (state → {code, captured_at}) — written by FastAPI /oauth/callback
_oauth_callbacks: dict[str, dict] = {}


# ──────────────────────────────────────────────────────────────────────────────
# Encryption helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_or_create_key() -> bytes:
    """Load or generate the Fernet encryption key saved in .auth_key."""
    if os.path.exists(_KEY_FILE):
        try:
            with open(_KEY_FILE, "rb") as f:
                raw = f.read().strip()
            if len(raw) >= 44:
                return raw[:44]
        except Exception:
            pass
    key = Fernet.generate_key() if _HAS_CRYPTO else base64.urlsafe_b64encode(os.urandom(32))
    try:
        with open(_KEY_FILE, "wb") as f:
            f.write(key)
        try:
            import stat
            os.chmod(_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
    except Exception:
        pass
    return key


def _encrypt(plaintext: str) -> str:
    """Return AES-encrypted (Fernet) or XOR-obfuscated base64 string."""
    if not plaintext:
        return ""
    if _HAS_CRYPTO:
        try:
            f = Fernet(_get_or_create_key())
            return f.encrypt(plaintext.encode()).decode()
        except Exception:
            pass
    # Fallback: XOR with key bytes + base64
    key_b  = _get_or_create_key()[:32]
    data_b = plaintext.encode()
    xored  = bytes(b ^ key_b[i % 32] for i, b in enumerate(data_b))
    return base64.urlsafe_b64encode(xored).decode()


def _decrypt(ciphertext: str) -> str:
    """Decrypt a string previously encrypted by _encrypt()."""
    if not ciphertext:
        return ""
    if _HAS_CRYPTO:
        try:
            f = Fernet(_get_or_create_key())
            return f.decrypt(ciphertext.encode()).decode()
        except Exception:
            pass
    # Fallback: XOR
    try:
        key_b  = _get_or_create_key()[:32]
        data_b = base64.urlsafe_b64decode(ciphertext.encode() + b"==")
        return bytes(b ^ key_b[i % 32] for i, b in enumerate(data_b)).decode()
    except Exception:
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# Account storage (encrypted at rest)
# ──────────────────────────────────────────────────────────────────────────────

_SENSITIVE = ("access_token", "refresh_token", "client_secret")


def _load_accounts() -> list:
    """Load all accounts from disk, decrypting sensitive fields."""
    if not os.path.exists(_AUTH_FILE):
        return []
    try:
        with open(_AUTH_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        result = []
        for acc in raw:
            acc = dict(acc)
            for field in _SENSITIVE:
                val = acc.get(field, "")
                if val and val.startswith("ENC:"):
                    acc[field] = _decrypt(val[4:])
            result.append(acc)
        return result
    except Exception:
        return []


def _save_accounts(accounts: list) -> None:
    """Save accounts to disk, encrypting sensitive fields."""
    try:
        to_save = []
        for acc in accounts:
            acc = dict(acc)
            for field in _SENSITIVE:
                val = acc.get(field, "")
                if val and not val.startswith("ENC:"):
                    acc[field] = "ENC:" + _encrypt(val)
            to_save.append(acc)
        with open(_AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# PKCE helpers (RFC 7636)
# ──────────────────────────────────────────────────────────────────────────────

def _pkce_pair() -> tuple:
    """Return (code_verifier, code_challenge_S256)."""
    verifier  = base64.urlsafe_b64encode(os.urandom(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


# ──────────────────────────────────────────────────────────────────────────────
# Feature #105 — Generate OAuth URL
# ──────────────────────────────────────────────────────────────────────────────

def generate_oauth_url(platform: str, client_id: str, client_secret: str = "") -> dict:
    """
    Build the OAuth 2.0 authorization URL for a platform.
    Returns {url, state, redirect_uri, platform, pkce, scopes}
    or {error: "..."} on failure.
    """
    cfg = PLATFORM_CONFIGS.get(platform)
    if not cfg:
        return {"error": f"Unknown platform: {platform}"}
    if cfg["auth_type"] == "bot_token":
        return {"error": "Telegram uses bot token authentication, not OAuth. Use the Bot Tokens tab."}
    if not client_id.strip():
        return {"error": "Client ID is required"}

    state     = secrets.token_urlsafe(20)
    verifier  = ""
    challenge = ""

    if cfg.get("pkce"):
        verifier, challenge = _pkce_pair()

    params: dict = {
        "client_id":     client_id.strip(),
        "redirect_uri":  _REDIRECT_URI,
        "response_type": "code",
        "scope":         " ".join(cfg["scopes"]),
        "state":         state,
    }

    if challenge:
        params["code_challenge"]        = challenge
        params["code_challenge_method"] = "S256"

    # Platform-specific extras
    if platform == "YouTube":
        params["access_type"] = "offline"
        params["prompt"]      = "consent"

    url = cfg["auth_url"] + "?" + urllib.parse.urlencode(params)

    # Persist PKCE state for code exchange
    _pkce_store[state] = {
        "verifier":      verifier,
        "platform":      platform,
        "client_id":     client_id.strip(),
        "client_secret": client_secret.strip(),
        "redirect_uri":  _REDIRECT_URI,
    }

    return {
        "url":          url,
        "state":        state,
        "redirect_uri": _REDIRECT_URI,
        "platform":     platform,
        "pkce":         bool(verifier),
        "scopes":       cfg["scopes"],
        "instructions": (
            f"1. Click the URL or copy it to your browser\n"
            f"2. Log in and authorize GrowthOS\n"
            f"3. You will be redirected to: {_REDIRECT_URI}\n"
            f"   → GrowthOS auto-captures the code via the backend server\n"
            f"4. Click 'Complete Connection' to finish"
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Feature #105 — Exchange code for token
# ──────────────────────────────────────────────────────────────────────────────

async def exchange_code_for_token(
    platform: str,
    code: str,
    state: str,
    client_id: str = "",
    client_secret: str = "",
) -> dict:
    """
    Exchange the OAuth authorization code for access + refresh tokens,
    fetch account info, and persist the account to encrypted storage.
    """
    cfg = PLATFORM_CONFIGS.get(platform)
    if not cfg:
        return {"error": f"Unknown platform: {platform}"}
    if not code.strip():
        return {"error": "Authorization code is required"}

    # Retrieve PKCE state
    pkce_data = _pkce_store.pop(state, {})
    if pkce_data:
        client_id     = pkce_data.get("client_id",     client_id)
        client_secret = pkce_data.get("client_secret", client_secret)
        verifier      = pkce_data.get("verifier",      "")
        redirect_uri  = pkce_data.get("redirect_uri",  _REDIRECT_URI)
    else:
        verifier     = ""
        redirect_uri = _REDIRECT_URI

    if not _HAS_HTTPX:
        return {"error": "httpx is not installed. Run: pip install httpx"}

    payload: dict = {
        "grant_type":   "authorization_code",
        "code":         code.strip(),
        "redirect_uri": redirect_uri,
        "client_id":    client_id,
    }
    if client_secret:
        payload["client_secret"] = client_secret
    if verifier:
        payload["code_verifier"] = verifier

    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth    = None
        if platform == "Twitter/X" and client_secret:
            auth = (client_id, client_secret)

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(cfg["token_url"], data=payload, headers=headers, auth=auth)
            try:
                data: dict = r.json()
            except Exception:
                return {"error": f"Platform returned non-JSON response (HTTP {r.status_code}): {r.text[:300]}"}

        if not r.is_success or "error" in data:
            fb_desc  = data.get("error_description", "")
            fb_msg   = data.get("error", "")
            fb_code  = data.get("error_subcode", "") or data.get("code", "")
            fb_user  = data.get("error_user_msg", "")
            # Build a human-readable message
            detail = fb_desc or fb_user or fb_msg or f"HTTP {r.status_code}"
            hint = ""
            if "redirect_uri" in str(fb_desc).lower() or fb_code in (191,):
                hint = "\n\nHint: The redirect URI in your Facebook app settings does not match.\nAdd exactly: http://localhost:8000/oauth/callback"
            elif "code" in str(fb_desc).lower() and "expired" in str(fb_desc).lower():
                hint = "\n\nHint: Authorization codes expire in ~10 minutes.\nClick 'Start OAuth' again to get a fresh code."
            elif "invalid_client" in fb_msg or r.status_code == 401:
                hint = "\n\nHint: App ID or App Secret is wrong. Double-check Settings → Basic in your Facebook Developer Console."
            return {"error": f"{detail}{hint}"}

        access_token  = data.get("access_token", "")
        refresh_token = data.get("refresh_token", "")
        expires_in    = int(data.get("expires_in", 0))

        # Instagram: upgrade short-lived → long-lived token (~60 days)
        if platform == "Instagram" and access_token and "long_token_url" in cfg:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    lr = await client.get(cfg["long_token_url"], params={
                        "grant_type":    "ig_exchange_token",
                        "client_secret": client_secret,
                        "access_token":  access_token,
                    })
                    ld = lr.json()
                if "access_token" in ld:
                    access_token = ld["access_token"]
                    expires_in   = ld.get("expires_in", 5183944)
            except Exception:
                pass  # use short-lived token

        if not access_token:
            return {"error": "No access token received from platform API"}

        # Fetch account info
        profile = await _fetch_account_info(platform, access_token, cfg)

        account = {
            "id":            secrets.token_hex(8),
            "platform":      platform,
            "display_name":  (
                profile.get("name")
                or profile.get("username")
                or profile.get("display_name")
                or platform
            ),
            "account_id":    str(profile.get("id") or profile.get("open_id") or ""),
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "client_id":     client_id,
            "client_secret": client_secret,
            "expires_in":    expires_in,
            "connected_at":  datetime.now(timezone.utc).isoformat(),
            "last_tested":   datetime.now(timezone.utc).isoformat(),
            "status":        "connected",
            "profile_info":  profile,
            "icon":          cfg["icon"],
            "color":         cfg["color"],
        }

        # Upsert (replace existing account with same platform + account_id)
        accounts = _load_accounts()
        accounts = [
            a for a in accounts
            if not (a["platform"] == platform and a.get("account_id") == account["account_id"])
        ]
        accounts.append(account)
        _save_accounts(accounts)

        return {
            "success":      True,
            "display_name": account["display_name"],
            "account_id":   account["account_id"],
            "platform":     platform,
            "account": {k: v for k, v in account.items() if k not in _SENSITIVE},
        }

    except httpx.TimeoutException:
        return {"error": "Request timed out. Check your internet connection."}
    except Exception as e:
        return {"error": str(e)}


async def _fetch_account_info(platform: str, access_token: str, cfg: dict) -> dict:
    """Fetch basic profile info after token exchange to name the account."""
    endpoint = cfg.get("test_endpoint", "")
    if not endpoint or not _HAS_HTTPX:
        return {}
    try:
        url     = cfg["api_base"] + endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        params  = {}
        # Facebook / Instagram use query-param auth
        if platform in ("Facebook", "Instagram"):
            headers = {}
            params  = {"access_token": access_token}

        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url, headers=headers, params=params)
        data = r.json()

        # Normalize platform-specific response shapes
        if platform == "TikTok":
            return data.get("data", {}).get("user", data)
        if platform == "YouTube":
            items = data.get("items", [])
            if items:
                snip = items[0].get("snippet", {})
                return {"id": items[0]["id"], "name": snip.get("title", "")}
        return data
    except Exception:
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# Feature #110 — Bot / API-key token connect (Telegram, etc.)
# ──────────────────────────────────────────────────────────────────────────────

async def connect_bot_token(platform: str, token: str) -> dict:
    """Verify and store a bot/API token (e.g. Telegram bot token)."""
    cfg = PLATFORM_CONFIGS.get(platform)
    if not cfg:
        return {"error": f"Unknown platform: {platform}"}
    if not token.strip():
        return {"error": "Token cannot be empty"}

    if platform == "Telegram":
        if not _HAS_HTTPX:
            return {"error": "httpx not installed. Run: pip install httpx"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.telegram.org/bot{token.strip()}/getMe",
                    timeout=10,
                )
            data = r.json()
        except Exception as e:
            return {"error": f"Network error: {e}"}

        if not data.get("ok"):
            return {"error": data.get("description", "Invalid bot token — check with @BotFather")}

        bot   = data["result"]
        uname = bot.get("username", "")
        fname = bot.get("first_name", "Bot")

        account = {
            "id":            secrets.token_hex(8),
            "platform":      "Telegram",
            "display_name":  f"@{uname} • {fname}",
            "account_id":    str(bot.get("id", "")),
            "access_token":  token.strip(),
            "refresh_token": "",
            "client_id":     "",
            "client_secret": "",
            "connected_at":  datetime.now(timezone.utc).isoformat(),
            "last_tested":   datetime.now(timezone.utc).isoformat(),
            "status":        "connected",
            "profile_info":  bot,
            "icon":          cfg["icon"],
            "color":         cfg["color"],
        }
        accounts = _load_accounts()
        accounts = [
            a for a in accounts
            if not (a["platform"] == "Telegram" and a.get("account_id") == account["account_id"])
        ]
        accounts.append(account)
        _save_accounts(accounts)

        return {
            "success":      True,
            "display_name": account["display_name"],
            "platform":     "Telegram",
            "account_id":   account["account_id"],
            "account": {k: v for k, v in account.items() if k not in _SENSITIVE},
        }

    return {"error": f"Bot token authentication not yet supported for {platform}"}


# ──────────────────────────────────────────────────────────────────────────────
# Feature #106b — Direct / Quick Token Connect
# Lets users paste a token obtained from Graph API Explorer or any other source
# without going through the full OAuth flow.  Validates the token immediately.
# ──────────────────────────────────────────────────────────────────────────────

async def connect_direct_token(platform: str, token: str) -> dict:
    """
    Validate and store a pre-obtained access token for any supported platform.
    Works great with Facebook/Instagram tokens from Graph API Explorer, YouTube
    tokens from OAuth Playground, etc.
    """
    cfg = PLATFORM_CONFIGS.get(platform)
    if not cfg:
        return {"error": f"Unknown platform: {platform}"}
    if not token.strip():
        return {"error": "Token cannot be empty"}
    if not _HAS_HTTPX:
        return {"error": "httpx not installed. Run: pip install httpx"}

    token = token.strip()

    # Verify the token by fetching the profile
    profile = await _fetch_account_info(platform, token, cfg)

    if not profile or "error" in profile:
        err_msg = profile.get("error", "Token validation failed") if profile else "Token validation failed"
        # Give a friendlier message for common Facebook errors
        if "OAuthException" in str(err_msg) or "invalid" in str(err_msg).lower():
            return {
                "error": (
                    f"Token rejected by {platform}: {err_msg}\n\n"
                    "Make sure the token is fresh (tokens from Graph API Explorer expire in ~1 hour).\n"
                    "Go to https://developers.facebook.com/tools/explorer and generate a new one."
                )
            }
        return {"error": f"Token validation failed: {err_msg}"}

    account = {
        "id":            secrets.token_hex(8),
        "platform":      platform,
        "display_name":  (
            profile.get("name") or profile.get("username") or
            profile.get("display_name") or platform
        ),
        "account_id":    str(profile.get("id") or profile.get("open_id") or ""),
        "access_token":  token,
        "refresh_token": "",
        "client_id":     "",
        "client_secret": "",
        "connected_at":  datetime.now(timezone.utc).isoformat(),
        "last_tested":   datetime.now(timezone.utc).isoformat(),
        "status":        "connected",
        "profile_info":  profile,
        "icon":          cfg["icon"],
        "color":         cfg["color"],
    }

    accounts = _load_accounts()
    # Upsert — replace if same platform + account_id
    accounts = [
        a for a in accounts
        if not (a["platform"] == platform and a.get("account_id") == account["account_id"])
    ]
    accounts.append(account)
    _save_accounts(accounts)

    return {
        "success":      True,
        "display_name": account["display_name"],
        "platform":     platform,
        "account_id":   account["account_id"],
        "account": {k: v for k, v in account.items() if k not in _SENSITIVE},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Feature #109 — Connection health monitoring
# ──────────────────────────────────────────────────────────────────────────────

async def test_account_connection(account_id: str) -> dict:
    """Test whether an account's token is still valid. Returns {status, ...}."""
    accounts = _load_accounts()
    acc = next((a for a in accounts if a["id"] == account_id), None)
    if not acc:
        return {"error": "Account not found"}

    platform     = acc["platform"]
    access_token = acc.get("access_token", "")
    cfg          = PLATFORM_CONFIGS.get(platform, {})

    if not access_token:
        return {"status": "no_token", "error": "No access token stored"}
    if not _HAS_HTTPX:
        return {"status": "unknown", "error": "httpx not installed"}

    try:
        if platform == "Telegram":
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"https://api.telegram.org/bot{access_token}/getMe")
            data = r.json()
            ok   = data.get("ok", False)
            _update_status(accounts, account_id, "connected" if ok else "error")
            _save_accounts(accounts)
            return {
                "status":   "connected" if ok else "error",
                "platform": platform,
                "info":     data.get("result", {}),
                "error":    "" if ok else data.get("description", ""),
            }

        endpoint = cfg.get("test_endpoint", "")
        if not endpoint:
            return {"status": "unknown", "note": "No test endpoint for this platform"}

        url     = cfg["api_base"] + endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        params  = {}
        if platform in ("Facebook", "Instagram"):
            headers = {}
            params  = {"access_token": access_token}

        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url, headers=headers, params=params)

        if r.status_code == 200:
            _update_status(accounts, account_id, "connected")
            _save_accounts(accounts)
            return {"status": "connected", "platform": platform, "http_status": 200}
        elif r.status_code in (401, 403):
            _update_status(accounts, account_id, "expired")
            _save_accounts(accounts)
            return {"status": "expired", "error": "Token expired — please reconnect or refresh", "http_status": r.status_code}
        else:
            return {"status": "error", "http_status": r.status_code, "platform": platform}

    except httpx.TimeoutException:
        return {"status": "timeout", "error": "Request timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _update_status(accounts: list, account_id: str, status: str) -> None:
    for a in accounts:
        if a["id"] == account_id:
            a["status"]      = status
            a["last_tested"] = datetime.now(timezone.utc).isoformat()
            break


async def test_all_accounts() -> list:
    """Test all stored accounts concurrently. Returns list of results."""
    accounts = _load_accounts()
    results  = []
    for acc in accounts:
        r = await test_account_connection(acc["id"])
        r["display_name"] = acc.get("display_name", acc["platform"])
        r["account_id"]   = acc["id"]
        results.append(r)
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Feature #107 — Automatic token refresh
# ──────────────────────────────────────────────────────────────────────────────

async def refresh_account_token(account_id: str) -> dict:
    """Refresh the access token for an account using its refresh token."""
    accounts = _load_accounts()
    acc = next((a for a in accounts if a["id"] == account_id), None)
    if not acc:
        return {"error": "Account not found"}

    platform      = acc["platform"]
    refresh_token = acc.get("refresh_token", "")
    client_id     = acc.get("client_id", "")
    client_secret = acc.get("client_secret", "")
    cfg           = PLATFORM_CONFIGS.get(platform, {})

    if not refresh_token:
        return {"error": "No refresh token stored — please reconnect the account"}
    if not cfg.get("token_url"):
        return {"error": f"Token refresh not supported for {platform}"}
    if not _HAS_HTTPX:
        return {"error": "httpx not installed"}

    try:
        payload = {
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
        }
        if client_secret:
            payload["client_secret"] = client_secret

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                cfg["token_url"], data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        data = r.json()

        if "error" in data:
            return {"error": data.get("error_description", data["error"])}

        new_access  = data.get("access_token", "")
        new_refresh = data.get("refresh_token", refresh_token)

        for a in accounts:
            if a["id"] == account_id:
                a["access_token"]  = new_access
                a["refresh_token"] = new_refresh
                a["status"]        = "connected"
                a["last_tested"]   = datetime.now(timezone.utc).isoformat()
                break
        _save_accounts(accounts)

        return {
            "success":      True,
            "platform":     platform,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# Feature #108 — Multi-account management
# ──────────────────────────────────────────────────────────────────────────────

def list_accounts(platform: str = "") -> list:
    """List all accounts (tokens masked). Optionally filter by platform."""
    accounts = _load_accounts()
    result   = []
    for acc in accounts:
        if platform and acc.get("platform") != platform:
            continue
        safe = {k: v for k, v in acc.items() if k not in _SENSITIVE}
        safe["has_token"]         = bool(acc.get("access_token"))
        safe["has_refresh_token"] = bool(acc.get("refresh_token"))
        result.append(safe)
    return result


def delete_account(account_id: str) -> dict:
    """Permanently remove an account and its tokens."""
    accounts = _load_accounts()
    before   = len(accounts)
    accounts = [a for a in accounts if a["id"] != account_id]
    if len(accounts) == before:
        return {"error": "Account not found"}
    _save_accounts(accounts)
    return {"success": True, "deleted_id": account_id}


def get_platform_configs_public() -> dict:
    """Return safe (no internal) platform configs for the UI."""
    result = {}
    for name, cfg in PLATFORM_CONFIGS.items():
        result[name] = {
            "icon":       cfg["icon"],
            "color":      cfg["color"],
            "auth_type":  cfg["auth_type"],
            "scopes":     cfg["scopes"],
            "docs_url":   cfg.get("docs_url", ""),
            "docs_steps": cfg.get("docs_steps", ""),
            "pkce":       cfg.get("pkce", False),
        }
    return result
