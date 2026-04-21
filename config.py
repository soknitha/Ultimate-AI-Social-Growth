"""
GrowthOS AI v2.0 — Central Configuration
==========================================
All API keys loaded from environment variables or .env file.
Never hardcode secrets. Use .env file for local development.
"""
import os
from dotenv import load_dotenv

load_dotenv()

_PLACEHOLDERS = {"", "your_key", "YOUR_KEY_HERE", "your_api_key", "your_token",
                 "your_groq_key", "your_supabase_url", "your_supabase_anon_key"}

# ─── Groq API (primary AI — fast, free tier available) ───────────────────────
# Get from: https://console.groq.com/keys
GROQ_API_KEY       = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL         = os.getenv("GROQ_MODEL",      "llama-3.3-70b-versatile")   # ≈ GPT-4o
GROQ_FAST_MODEL    = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")      # ≈ GPT-4o-mini

# ─── OpenAI API (fallback if no Groq key) ────────────────────────────────────
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL       = os.getenv("OPENAI_MODEL",       "gpt-4o")
OPENAI_FAST_MODEL  = os.getenv("OPENAI_FAST_MODEL",  "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# ─── Supabase (database — replaces file-based memory_store) ─────────────────
# Get from: https://supabase.com → Project → Settings → API
SUPABASE_URL       = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY       = os.getenv("SUPABASE_KEY", "")          # anon/public key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "") # service_role key (server-only)

# ─── GitHub (for CI/CD and source control) ───────────────────────────────────
GITHUB_TOKEN       = os.getenv("GITHUB_TOKEN", "")          # PAT with repo scope
GITHUB_REPO        = os.getenv("GITHUB_REPO", "")           # owner/repo-name

# ─── Telegram Bot ────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ─── SMM Panel (generic — works with any SMM panel API v2) ───────────────────
# Set to your own panel URL. Leave empty to use demo/mock data.
SMM_API_KEY        = os.getenv("SMM_API_KEY", "")
SMM_API_URL        = os.getenv("SMM_API_URL", "")

# ─── Backend / Railway ───────────────────────────────────────────────────────
# On Railway: set BACKEND_URL to your Railway public URL
BACKEND_URL        = os.getenv("BACKEND_URL",  "http://127.0.0.1:8000")
BACKEND_HOST       = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT       = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))  # Railway sets PORT

# ─── Feature Flags ───────────────────────────────────────────────────────────
USE_REAL_AI   = (
    (bool(GROQ_API_KEY)   and GROQ_API_KEY   not in _PLACEHOLDERS) or
    (bool(OPENAI_API_KEY) and OPENAI_API_KEY.startswith("sk-"))
)
USE_SUPABASE  = bool(SUPABASE_URL) and SUPABASE_URL not in _PLACEHOLDERS
USE_SMM_PANEL = bool(SMM_API_KEY)  and SMM_API_KEY  not in _PLACEHOLDERS

# Legacy aliases (keep backward compat with any code that imports these)
DEMOSMM_API_KEY = SMM_API_KEY
DEMOSMM_API_URL = SMM_API_URL


# ─── Application ─────────────────────────────────────────────────────────────
APP_NAME     = "GrowthOS AI"
APP_VERSION  = "2.0.0"
APP_TAGLINE  = "AI Social Growth Operating System"

# ─── Safety Rate Limits ──────────────────────────────────────────────────────
MAX_DAILY_GROWTH = {
    "Instagram": 2000,
    "TikTok":    3000,
    "Facebook":  1500,
    "YouTube":   1000,
    "Telegram":  5000,
    "X (Twitter)": 400,
}

RISK_THRESHOLDS = {
    "low":      0.30,
    "medium":   0.60,
    "high":     0.80,
    "critical": 0.95,
}

# ─── Geo / Location Targeting ────────────────────────────────────────────────
DEFAULT_GEO_COUNTRY  = os.getenv("DEFAULT_GEO_COUNTRY",  "KH")              # ISO 3166-1 alpha-2
DEFAULT_GEO_TIMEZONE = os.getenv("DEFAULT_GEO_TIMEZONE", "Asia/Phnom_Penh")
DEFAULT_GEO_LANGUAGE = os.getenv("DEFAULT_GEO_LANGUAGE", "km")              # ISO 639-1
DEFAULT_GEO_REGION   = os.getenv("DEFAULT_GEO_REGION",   "Southeast Asia")

# ─── Platform & Niche Lists ──────────────────────────────────────────────────
SUPPORTED_PLATFORMS = [
    "TikTok", "Instagram", "Facebook",
    "YouTube", "Telegram", "X (Twitter)", "Shopify",
]

CONTENT_TONES = [
    "Viral & Catchy", "Professional", "Funny / Humorous",
    "Educational", "Inspirational", "Storytelling",
    "Premium Brand", "Casual & Friendly",
]

POPULAR_NICHES = [
    "Technology", "Fashion", "Fitness", "Food", "Travel",
    "Business", "Cryptocurrency", "Education", "Entertainment",
    "Gaming", "Beauty", "Real Estate", "Finance", "Health",
    "Khmer Culture", "E-commerce", "Motivation", "Art & Design",
]
