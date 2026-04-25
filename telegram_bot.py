# telegram_bot.py  — GrowthOS AI v2.0 — Full Telegram Command Bot
"""
Full aiogram 3.x Telegram Bot for GrowthOS AI.
Commands:
  /start    — Welcome screen with keyboard
  /strategy — Generate 30-day AI growth strategy
  /content  — Generate viral content package
  /audit    — Deep account audit
  /trends   — Trending topics scanner
  /risk     — Content safety checker
  /campaign — Create campaign plan
  /panel    — SMM panel services + balance
  /order    — Place smart SMM order
  /report   — Generate performance report
  /agents   — Run multi-agent AI team analysis
  /balance  — Check SMM panel balance
  /help     — Show all commands
"""
import asyncio
import logging
import sys
import httpx
import json
import aiohttp

# ── Windows DNS fix ──────────────────────────────────────────────────────────
# On Windows, aiodns/c-ares cannot read the system DNS configuration when the
# event loop is ProactorEventLoop (Python 3.8+ default).  This manifests as
# "Could not contact DNS servers" (c-ares error 11 / ARES_ENOSERVERS) every
# time aiohttp tries to resolve api.telegram.org.
#
# Fix A — monkey-patch TCPConnector so every instance (including the one
#          AiohttpSession.close() creates internally) uses Python's built-in
#          socket.getaddrinfo via ThreadedResolver, bypassing aiodns entirely.
# Fix B — fall back to SelectorEventLoop on Windows so aiodns can work even if
#          ThreadedResolver somehow isn't picked up.
if sys.platform == "win32":
    _orig_tcp_connector_init = aiohttp.TCPConnector.__init__

    def _patched_tcp_connector_init(self, *args, **kwargs):
        kwargs.setdefault("resolver", aiohttp.ThreadedResolver())
        _orig_tcp_connector_init(self, *args, **kwargs)

    aiohttp.TCPConnector.__init__ = _patched_tcp_connector_init  # type: ignore[method-assign]
    # Fix B: selector event loop is required by aiodns on Windows (fallback)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ─────────────────────────────────────────────────────────────────────────────

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

try:
    from config import TELEGRAM_BOT_TOKEN, BACKEND_URL
except ImportError:
    import os
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BACKEND_URL        = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── AI Social Platform ───────────────────────────────────────────────────────
try:
    import sys as _sys
    import os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from ai_core.social_platform import (
        is_registered, register_user, get_user_profile, update_profile,
        create_post, get_feed, toggle_like, add_comment, reply_comment,
        get_post, get_platform_stats, ai_enhance_caption, ai_suggest_reply,
    )
    _SOCIAL_OK = True
except Exception as _e:
    _SOCIAL_OK = False
    log.warning("social_platform not available: %s", _e)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

_SETUP_MSG = """
========================================================
   GrowthOS AI -- Telegram Bot Setup
========================================================
  TELEGRAM_BOT_TOKEN is missing or invalid.

  How to get your token:
  1. Open Telegram and search for @BotFather
  2. Send /newbot and follow the prompts
  3. Copy the token (format: 123456789:AAFxxx...)
  4. Add it to your .env file:
     TELEGRAM_BOT_TOKEN=123456789:AAFxxx...

  Backend API is running -- other features work fine.
========================================================
"""

_PLACEHOLDER_VALUES = {"", "your_token", "YOUR_TELEGRAM_BOT_TOKEN_HERE"}

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN in _PLACEHOLDER_VALUES:
    print(_SETUP_MSG)
    raise SystemExit(1)

# Bot is created inside main() so ThreadedResolver has a running event loop
bot: Bot = None  # type: ignore — assigned in main() before polling
dp = Dispatcher(storage=MemoryStorage())

TIMEOUT = httpx.Timeout(30.0)


# ─── HTTP helpers ─────────────────────────────────────────────────────────────
async def _api_post(endpoint: str, payload: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{BACKEND_URL}{endpoint}", json=payload)
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError:
        return {"error": "Cannot connect to backend. Make sure it is running:\n  uvicorn backend_api:app --reload"}
    except Exception as e:
        return {"error": str(e)}


async def _api_get(endpoint: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BACKEND_URL}{endpoint}")
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError:
        return {"error": "Cannot connect to backend."}
    except Exception as e:
        return {"error": str(e)}


# ─── Format helpers ───────────────────────────────────────────────────────────
def _fmt(data, max_chars: int = 3800) -> str:
    if isinstance(data, dict):
        text = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        text = str(data)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[truncated — use Desktop App for full output]"
    return f"<pre>{text}</pre>"


def _err(msg: str) -> str:
    return f"❌ <b>Error:</b>\n<code>{msg}</code>"


# ─── FSM States ──────────────────────────────────────────────────────────────
class StrategyState(StatesGroup):
    waiting_platform  = State()
    waiting_username  = State()
    waiting_followers = State()
    waiting_niche     = State()

class ContentState(StatesGroup):
    waiting_topic    = State()
    waiting_platform = State()

class AuditState(StatesGroup):
    waiting_info = State()

class OmniState(StatesGroup):
    waiting_task = State()
    waiting_input = State()

class RiskState(StatesGroup):
    waiting_content = State()

class OrderState(StatesGroup):
    waiting_details = State()

class GeoOrderState(StatesGroup):
    waiting_link     = State()
    waiting_platform = State()
    waiting_budget   = State()
    waiting_country  = State()

class ViralState(StatesGroup):
    waiting_topic    = State()
    waiting_platform = State()

class AnalyticsState(StatesGroup):
    waiting_platform = State()

class BusinessState(StatesGroup):
    waiting_niche    = State()
    waiting_platform = State()

# ── Registration FSM ─────────────────────────────────────────────────────────
class RegState(StatesGroup):
    waiting_phone = State()
    waiting_sex   = State()
    waiting_dob   = State()

# ── Social Media FSM ─────────────────────────────────────────────────────────
class SocialPostState(StatesGroup):
    waiting_caption = State()
    waiting_media   = State()   # optional photo/video after caption

class SocialPhotoState(StatesGroup):
    waiting_caption = State()
    waiting_photo   = State()

class SocialVideoState(StatesGroup):
    waiting_caption = State()
    waiting_video   = State()

class SocialCommentState(StatesGroup):
    waiting_post_id = State()
    waiting_text    = State()

class SocialReplyState(StatesGroup):
    waiting_post_id    = State()
    waiting_comment_id = State()
    waiting_text       = State()


# ─── Keyboards ────────────────────────────────────────────────────────────────
PLATFORM_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="TikTok",     callback_data="plt_TikTok"),
        InlineKeyboardButton(text="Instagram",  callback_data="plt_Instagram"),
    ],
    [
        InlineKeyboardButton(text="Facebook",   callback_data="plt_Facebook"),
        InlineKeyboardButton(text="YouTube",    callback_data="plt_YouTube"),
    ],
    [
        InlineKeyboardButton(text="Telegram",   callback_data="plt_Telegram"),
        InlineKeyboardButton(text="Twitter/X",  callback_data="plt_Twitter/X"),
    ],
])

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Social Network"), KeyboardButton(text="🌌 Omni Hub")],
        [KeyboardButton(text="Omni Hub"),   KeyboardButton(text="Strategy")],
        [KeyboardButton(text="Content"),    KeyboardButton(text="Audit")],
        [KeyboardButton(text="Trends"),     KeyboardButton(text="Risk")],
        [KeyboardButton(text="Agents"),     KeyboardButton(text="GEO Order")],
        [KeyboardButton(text="Facebook"),   KeyboardButton(text="Viral")],
        [KeyboardButton(text="Business"),   KeyboardButton(text="SMM Panel")],
        [KeyboardButton(text="Help")],
    ],
    resize_keyboard=True,
)

# ── Social Network Keyboards ──────────────────────────────────────────────────
SOCIAL_MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📰 View Feed"),      KeyboardButton(text="✍️ Post Text")],
        [KeyboardButton(text="📸 Post Photo"),     KeyboardButton(text="🎬 Post Video")],
        [KeyboardButton(text="❤️ Like Post"),      KeyboardButton(text="💬 Comment")],
        [KeyboardButton(text="↩️ Reply Comment"),  KeyboardButton(text="👤 My Profile")],
        [KeyboardButton(text="🏠 Main Menu")],
    ],
    resize_keyboard=True,
)

SEX_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👦 Male",   callback_data="reg_sex_male"),
        InlineKeyboardButton(text="👧 Female", callback_data="reg_sex_female"),
        InlineKeyboardButton(text="🌈 Other",  callback_data="reg_sex_other"),
    ]
])

MEDIA_TYPE_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✍️ Text Only",      callback_data="post_type_text"),
        InlineKeyboardButton(text="📸 Add Photo",      callback_data="post_type_photo"),
    ],
    [
        InlineKeyboardButton(text="🎬 Add Video",      callback_data="post_type_video"),
        InlineKeyboardButton(text="❌ Cancel",          callback_data="post_cancel"),
    ],
])


# ─── /start ───────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    tid  = user.id

    # ── Auto-registration check ───────────────────────────────────────────────
    if _SOCIAL_OK:
        if not is_registered(tid):
            # Save basic Telegram info immediately
            register_user(
                telegram_id  = tid,
                first_name   = user.first_name or "",
                last_name    = user.last_name  or "",
                username     = user.username   or "",
                language_code= user.language_code or "en",
            )
            # Start registration wizard to collect phone / sex / dob
            await state.set_state(RegState.waiting_phone)
            phone_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Share My Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            await message.answer(
                f"🎉 <b>Welcome, {user.first_name}!</b>\n\n"
                f"🚀 You are joining <b>GrowthOS AI Social Network</b> — "
                f"the most advanced AI-powered social platform!\n\n"
                f"📋 <b>Quick Registration (2 steps):</b>\n"
                f"Please share your phone number to complete sign-up.\n\n"
                f"<i>Your data is secure and private.</i>",
                parse_mode="HTML",
                reply_markup=phone_kb,
            )
            return
        else:
            # Already registered — update last seen
            register_user(
                telegram_id   = tid,
                first_name    = user.first_name or "",
                last_name     = user.last_name  or "",
                username      = user.username   or "",
                language_code = user.language_code or "en",
            )

    name = user.first_name or "there"
    await message.answer(
        f"<b>Welcome back to GrowthOS AI, {name}! 🚀</b>\n\n"
        "Your autonomous AI Social Growth OS — <b>110 features</b> in one bot.\n\n"
        "<b>🌟 AI Social Network:</b>\n"
        "📱 /social  — Open Social Network hub\n"
        "📰 /feed    — Browse latest posts\n"
        "✍️ /post    — Share a text post\n"
        "📸 /photo   — Share a photo post\n"
        "🎬 /video   — Share a short video\n"
        "👤 /profile — View your profile\n\n"
        "<b>Quick Start:</b>\n"
        "🌌 /omni     — Omni AI Hub (150 Features)\n"
        "🧠 /strategy — 30-day AI growth plan\n"
        "✍️ /content  — Viral content package\n"
        "🤖 /agents   — 5-agent AI team analysis\n\n"
        "Type /help for all commands.",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


# ─── Registration: Phone ──────────────────────────────────────────────────────
@dp.message(RegState.waiting_phone)
async def reg_got_phone(message: Message, state: FSMContext):
    tid = message.from_user.id
    phone = ""
    if message.contact:
        phone = message.contact.phone_number or ""
    elif message.text and message.text.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        phone = message.text.strip()

    if _SOCIAL_OK:
        update_profile(tid, phone=phone)

    await state.update_data(phone=phone)
    await state.set_state(RegState.waiting_sex)
    await message.answer(
        "✅ Phone saved!\n\n"
        "👤 What is your <b>gender</b>?",
        parse_mode="HTML",
        reply_markup=SEX_KB,
    )


@dp.callback_query(F.data.startswith("reg_sex_"))
async def reg_got_sex(callback: CallbackQuery, state: FSMContext):
    sex_map = {"reg_sex_male": "Male", "reg_sex_female": "Female", "reg_sex_other": "Other"}
    sex = sex_map.get(callback.data, "")
    tid = callback.from_user.id
    if _SOCIAL_OK:
        update_profile(tid, sex=sex)

    await state.update_data(sex=sex)
    await state.set_state(RegState.waiting_dob)
    await callback.message.answer(
        f"✅ Gender: <b>{sex}</b>\n\n"
        "🎂 Please enter your <b>Date of Birth</b>:\n"
        "<i>Format: DD/MM/YYYY  (e.g. 15/03/2000)</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⏭ Skip")]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await callback.answer()


@dp.message(RegState.waiting_dob)
async def reg_got_dob(message: Message, state: FSMContext):
    tid  = message.from_user.id
    text = message.text.strip() if message.text else ""
    dob  = ""
    if text and text.lower() not in ("skip", "⏭ skip"):
        # Validate simple date format
        import re as _re
        if _re.match(r"^\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}$", text):
            dob = text
        else:
            dob = text  # store as-is

    if _SOCIAL_OK and dob:
        update_profile(tid, date_of_birth=dob)

    await state.clear()

    name = message.from_user.first_name or "Friend"
    await message.answer(
        f"🎉 <b>Registration Complete, {name}!</b>\n\n"
        f"✅ You are now a member of <b>GrowthOS AI Social Network</b>!\n\n"
        f"<b>What you can do:</b>\n"
        f"📰 Browse the community feed\n"
        f"✍️ Post text, photos & short videos\n"
        f"❤️ Like & comment on posts\n"
        f"🤖 Access all AI Growth Tools\n\n"
        f"👇 <b>Tap 📱 Social Network below to get started!</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


# ─── /help ────────────────────────────────────────────────────────────────────
@dp.message(Command("help"))
@dp.message(F.text == "Help")
async def cmd_help(message: Message):
    await message.answer(
        "<b>🚀 GrowthOS AI — All 23 Commands</b>\n\n"
        "<b>── Omni AI Hub ──</b>\n"
        "/omni — Run any of the 150 Advanced AI Features\n\n"
        "<b>── Core AI Brain ──</b>\n"
        "/strategy — 30-day AI growth strategy\n"
        "/content  — Viral content package\n"
        "/audit    — Deep account audit\n"
        "/trends   — Live trending topics\n"
        "/risk     — Content safety check\n"
        "/agents   — 5-agent AI team analysis\n"
        "/report   — Performance report\n"
        "/campaign — Campaign plan builder\n\n"
        "<b>── Growth & Creator ──</b>\n"
        "/viral     — Viral hooks, captions & hashtags\n"
        "/brand     — Brand authority score\n"
        "/creator   — Creator toolkit (scripts, ideas)\n"
        "/community — Community engagement strategies\n"
        "/analytics — Quick analytics dashboard\n"
        "/business  — Business intelligence\n\n"
        "<b>── SMM Panel ──</b>\n"
        "/panel   — SMM services catalog\n"
        "/order   — Place smart SMM order\n"
        "/geo     — 🌍 GEO-targeted Real Human order\n"
        "/balance — Panel balance\n\n"
        "<b>── Management ──</b>\n"
        "/facebook — Facebook page tools & AI content\n"
        "/schedule — Content scheduling & best times\n"
        "/inbox    — Auto-reply templates & tips\n\n"
        "<b>── Other ──</b>\n"
        "/start — Main menu\n"
        "/help  — This help screen\n\n"
        "💡 Set <code>GROQ_API_KEY</code> or <code>OPENAI_API_KEY</code> in .env for real AI",
        parse_mode="HTML",
    )


# ─── /strategy ────────────────────────────────────────────────────────────────
@dp.message(Command("strategy"))
@dp.message(F.text == "Strategy")
async def cmd_strategy(message: Message, state: FSMContext):
    await state.set_state(StrategyState.waiting_platform)
    await message.answer(
        "<b>AI Strategy Brain</b>\n\nSelect your platform:",
        parse_mode="HTML",
        reply_markup=PLATFORM_KB,
    )


@dp.callback_query(F.data.startswith("plt_"), StrategyState.waiting_platform)
async def strategy_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    await state.update_data(platform=platform)
    await state.set_state(StrategyState.waiting_username)
    await callback.message.answer(
        f"Platform: <b>{platform}</b>\n\nNow send your <b>username</b> (e.g. mybrand):",
        parse_mode="HTML",
    )
    await callback.answer()


@dp.message(StrategyState.waiting_username)
async def strategy_got_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip("@"))
    await state.set_state(StrategyState.waiting_followers)
    await message.answer("How many <b>current followers</b>? (send a number)", parse_mode="HTML")


@dp.message(StrategyState.waiting_followers)
async def strategy_got_followers(message: Message, state: FSMContext):
    try:
        followers = int(message.text.replace(",", "").replace("k", "000").strip())
    except ValueError:
        await message.answer("Please send a valid number (e.g. 15000)")
        return
    await state.update_data(followers=followers)
    await state.set_state(StrategyState.waiting_niche)
    await message.answer("What is your <b>niche</b>? (e.g. Fitness, Tech, Food, Business):", parse_mode="HTML")


@dp.message(StrategyState.waiting_niche)
async def strategy_got_niche(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.answer("Generating your 30-day strategy...")

    result = await _api_post("/api/v1/ai/strategy", {
        "username": data["username"],
        "platform": data["platform"],
        "current_followers": data["followers"],
        "niche": message.text.strip(),
        "goal_followers": data["followers"] * 3,
        "duration_days": 30,
    })

    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await message.answer(
            f"<b>30-Day Strategy Ready!</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )


# ─── /content ─────────────────────────────────────────────────────────────────
@dp.message(Command("content"))
@dp.message(F.text == "Content")
async def cmd_content(message: Message, state: FSMContext):
    await state.set_state(ContentState.waiting_topic)
    await message.answer(
        "<b>AI Content Studio</b>\n\nSend your content <b>topic or keyword</b>:\n"
        "(e.g. Weight Loss, AI Tools, Business Tips)",
        parse_mode="HTML",
    )


@dp.message(ContentState.waiting_topic)
async def content_got_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text.strip())
    await state.set_state(ContentState.waiting_platform)
    await message.answer("Select your platform:", reply_markup=PLATFORM_KB)


@dp.callback_query(F.data.startswith("plt_"), ContentState.waiting_platform)
async def content_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    data = await state.get_data()
    await state.clear()
    await callback.message.answer("Generating viral content package...")

    result = await _api_post("/api/v1/ai/content", {
        "topic": data["topic"],
        "platform": platform,
        "tone": "Viral and Catchy",
        "language": "English",
    })

    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        text = (
            f"<b>Content Package Ready!</b>\n\n"
            f"<b>Hook:</b>\n{d.get('hook', 'N/A')}\n\n"
            f"<b>Caption:</b>\n{d.get('caption', 'N/A')}\n\n"
            f"<b>Hashtags:</b>\n{d.get('hashtags', 'N/A')}\n\n"
            f"<b>Script preview:</b>\n{str(d.get('video_script', ''))[:300]}..."
        )
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# ─── /audit ───────────────────────────────────────────────────────────────────
@dp.message(Command("audit"))
@dp.message(F.text == "Audit")
async def cmd_audit(message: Message, state: FSMContext):
    await state.set_state(AuditState.waiting_info)
    await message.answer(
        "<b>Account Audit</b>\n\nSend info in this format:\n"
        "<code>username platform followers niche</code>\n\n"
        "Example:\n<code>mybrand TikTok 15000 Fitness</code>",
        parse_mode="HTML",
    )


@dp.message(AuditState.waiting_info)
async def audit_got_info(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) < 4:
        await message.answer("Please send: username platform followers niche\nExample: mybrand TikTok 15000 Fitness")
        return
    await state.clear()
    try:
        followers = int(parts[2])
    except ValueError:
        followers = 10000

    await message.answer("Running deep account audit...")
    result = await _api_post("/api/v1/ai/audit", {
        "username": parts[0], "platform": parts[1],
        "followers": followers, "niche": " ".join(parts[3:]),
    })
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await message.answer(
            f"<b>Audit Complete!</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )


# ─── /trends ─────────────────────────────────────────────────────────────────
@dp.message(Command("trends"))
@dp.message(F.text == "Trends")
async def cmd_trends(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="TikTok Trends",    callback_data="trend_TikTok"),
            InlineKeyboardButton(text="Instagram Trends", callback_data="trend_Instagram"),
        ],
        [
            InlineKeyboardButton(text="Facebook Trends",  callback_data="trend_Facebook"),
            InlineKeyboardButton(text="YouTube Trends",   callback_data="trend_YouTube"),
        ],
    ])
    await message.answer("<b>Trend Radar</b>\n\nSelect a platform to scan:", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("trend_"))
async def trends_handler(callback: CallbackQuery):
    platform = callback.data.replace("trend_", "")
    await callback.message.answer(f"Scanning {platform} trends...")
    result = await _api_post("/api/v1/ai/trends", {"platform": platform, "niche": "General", "region": "Global"})
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await callback.message.answer(
            f"<b>{platform} Trends Now!</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )
    await callback.answer()


# ─── /risk ────────────────────────────────────────────────────────────────────
@dp.message(Command("risk"))
@dp.message(F.text == "Risk")
async def cmd_risk(message: Message, state: FSMContext):
    await state.set_state(RiskState.waiting_content)
    await message.answer(
        "<b>Content Safety Checker</b>\n\nPaste your caption, post text, or script to check:",
        parse_mode="HTML",
    )


@dp.message(RiskState.waiting_content)
async def risk_got_content(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Scanning content for risks...")
    result = await _api_post("/api/v1/ai/risk", {"content": message.text, "platform": "General"})
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        status = "SAFE" if d.get("is_safe", True) else "RISKY"
        await message.answer(
            f"<b>Safety Check: {status}</b>\n\n{_fmt(d)}",
            parse_mode="HTML",
        )


# ─── /campaign ────────────────────────────────────────────────────────────────
@dp.message(Command("campaign"))
async def cmd_campaign(message: Message):
    await message.answer("Creating sample campaign plan...")
    result = await _api_post("/api/v1/ai/campaign", {
        "name": "Quick Growth Campaign",
        "platform": "TikTok",
        "niche": "General",
        "goal": "Grow Followers",
        "budget_usd": 500.0,
        "duration_days": 30,
    })
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await message.answer(
            f"<b>Campaign Plan Ready!</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )


# ─── /panel ───────────────────────────────────────────────────────────────────
@dp.message(Command("panel"))
@dp.message(F.text == "SMM Panel")
async def cmd_panel(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="View Services", callback_data="smm_services"),
            InlineKeyboardButton(text="Check Balance", callback_data="smm_balance"),
        ],
        [
            InlineKeyboardButton(text="TikTok Services",    callback_data="smm_cat_TikTok"),
            InlineKeyboardButton(text="Instagram Services", callback_data="smm_cat_Instagram"),
        ],
    ])
    await message.answer("<b>SMM Panel</b>\n\nWhat would you like to do?", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data == "smm_services")
async def smm_services_cb(callback: CallbackQuery):
    await callback.message.answer("Loading services...")
    result = await _api_get("/api/v1/smm/services")
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        services = d.get("services", [])[:8]
        text = "<b>SMM Services (top 8):</b>\n\n"
        for s in services:
            text += f"#{s['service']} {s['name']}\n  ${s['rate']}/1000  |  Min: {s['min']}\n\n"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data.startswith("smm_cat_"))
async def smm_cat_cb(callback: CallbackQuery):
    cat = callback.data.replace("smm_cat_", "")
    await callback.message.answer(f"Loading {cat} services...")
    result = await _api_get(f"/api/v1/smm/services?category={cat}")
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        services = d.get("services", [])
        text = f"<b>{cat} Services:</b>\n\n"
        for s in services:
            text += f"#{s['service']} {s['name']}\n  ${s['rate']}/1000  |  {s['min']}-{s['max']}\n\n"
        await callback.message.answer(text or "No services found.", parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "smm_balance")
async def smm_balance_cb(callback: CallbackQuery):
    result = await _api_get("/api/v1/smm/balance")
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        await callback.message.answer(
            f"<b>Panel Balance</b>\n\n"
            f"Balance: <b>${d.get('balance', 'N/A')}</b> {d.get('currency', 'USD')}\n"
            f"Account: {d.get('account_type', 'N/A')}\n"
            f"Status: {d.get('status', 'N/A')}",
            parse_mode="HTML",
        )
    await callback.answer()


# ─── /balance ─────────────────────────────────────────────────────────────────
@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    result = await _api_get("/api/v1/smm/balance")
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        await message.answer(
            f"<b>SMM Panel Balance</b>\n"
            f"${d.get('balance', 'N/A')} {d.get('currency', 'USD')}\n"
            f"Status: {d.get('status', 'N/A')}",
            parse_mode="HTML",
        )


# ─── /order ───────────────────────────────────────────────────────────────────
@dp.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.set_state(OrderState.waiting_details)
    await message.answer(
        "<b>Place Smart SMM Order</b>\n\n"
        "Send your order in this format:\n"
        "<code>link goal budget platform</code>\n\n"
        "Example:\n"
        "<code>https://tiktok.com/@mybrand followers 50 TikTok</code>",
        parse_mode="HTML",
    )


@dp.message(OrderState.waiting_details)
async def order_got_details(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) < 4:
        await message.answer("Please send: link goal budget platform")
        return
    await state.clear()
    try:
        budget = float(parts[2])
    except ValueError:
        budget = 20.0

    await message.answer("AI selecting best service for your budget...")
    result = await _api_post("/api/v1/smm/smart-order", {
        "link": parts[0],
        "goal": parts[1],
        "budget_usd": budget,
        "platform": parts[3],
    })
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        svc = d.get("selected_service", {})
        await message.answer(
            f"<b>AI Smart Order Recommendation:</b>\n\n"
            f"Service: <b>{svc.get('name', 'N/A')}</b>\n"
            f"Quantity: <b>{d.get('recommended_quantity', 'N/A')}</b>\n"
            f"Cost: <b>{d.get('estimated_cost', 'N/A')}</b>\n\n"
            f"Reason: {d.get('optimization_reason', '')}",
            parse_mode="HTML",
        )


# ─── /report ─────────────────────────────────────────────────────────────────
@dp.message(Command("report"))
async def cmd_report(message: Message):
    await message.answer("Generating performance report...")
    result = await _api_post("/api/v1/ai/report", {
        "account_name": "MyBrand",
        "platform": "TikTok",
        "period": "Last 30 Days",
        "metrics": {
            "views": 250000, "likes": 18500,
            "comments": 2100, "shares": 980, "follows": 4200,
        },
        "goals_achieved": ["Gained 4,200 new followers", "2 viral posts"],
    })
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await message.answer(
            f"<b>Performance Report Ready!</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )


# ─── /agents ─────────────────────────────────────────────────────────────────
@dp.message(Command("agents"))
@dp.message(F.text == "Agents")
async def cmd_agents(message: Message, state: FSMContext):
    await state.set_state(AuditState.waiting_info)
    await message.answer(
        "<b>Multi-Agent AI Team</b>\n\n"
        "Send account info for full analysis:\n"
        "<code>username platform followers niche</code>\n\n"
        "Example: <code>mybrand TikTok 15000 Fitness</code>",
        parse_mode="HTML",
    )


@dp.message(AuditState.waiting_info)
async def agents_got_info(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) < 4:
        await message.answer("Please send: username platform followers niche")
        return
    await state.clear()
    try:
        followers = int(parts[2])
    except ValueError:
        followers = 10000

    await message.answer(
        "<b>Launching all 5 AI Agents in parallel...</b>\nThis may take 30 seconds with real AI.",
        parse_mode="HTML",
    )
    result = await _api_post("/api/v1/ai/orchestrate", {
        "username": parts[0],
        "platform": parts[1],
        "followers": followers,
        "niche": " ".join(parts[3:]),
        "metrics": {},
    })
    if "error" in result:
        await message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        decision = d.get("final_decision", {})
        text = (
            f"<b>Multi-Agent Analysis Complete!</b>\n\n"
            f"Status: <b>{decision.get('overall_status', 'N/A')}</b>\n"
            f"Est. 30-day growth: <b>{decision.get('estimated_30day_growth', 'N/A')}</b>\n"
            f"Risk: <b>{decision.get('key_risk', 'N/A')}</b>\n"
            f"Next step: {decision.get('next_step', 'N/A')}\n\n"
            f"<b>Priority Actions:</b>\n"
        )
        for action in decision.get("priority_actions", [])[:4]:
            text += f"- {action}\n"
        await message.answer(text, parse_mode="HTML")


# ─── Helper: API GET ──────────────────────────────────────────────────────────
async def _api_get(path: str) -> dict:
    import aiohttp, os
    base = os.environ.get("BACKEND_URL", "http://localhost:8000")
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{base}{path}", timeout=aiohttp.ClientTimeout(total=25)) as r:
                return await r.json()
    except Exception as e:
        return {"error": str(e)}


# ─── Helper: format nested dict for Telegram ─────────────────────────────────
def _fmt(data, depth=0) -> str:
    if isinstance(data, str):
        return data[:1800]
    if isinstance(data, list):
        return "\n".join(f"• {_fmt(i, depth+1)}" for i in data[:6])
    if isinstance(data, dict):
        lines = []
        for k, v in list(data.items())[:10]:
            key = str(k).replace("_", " ").title()
            val = _fmt(v, depth+1) if isinstance(v, (dict, list)) else str(v)[:200]
            lines.append(f"<b>{key}:</b> {val}")
        return "\n".join(lines)
    return str(data)[:400]


# ─── /geo — AI GEO Smart Order ───────────────────────────────────────────────
_GEO_COUNTRIES = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇺🇸 USA",         callback_data="geo_US"),
        InlineKeyboardButton(text="🇬🇧 UK",           callback_data="geo_GB"),
        InlineKeyboardButton(text="🇰🇭 Cambodia",     callback_data="geo_KH"),
    ],
    [
        InlineKeyboardButton(text="🇯🇵 Japan",        callback_data="geo_JP"),
        InlineKeyboardButton(text="🇦🇺 Australia",    callback_data="geo_AU"),
        InlineKeyboardButton(text="🇩🇪 Germany",      callback_data="geo_DE"),
    ],
    [
        InlineKeyboardButton(text="🇮🇳 India",        callback_data="geo_IN"),
        InlineKeyboardButton(text="🇧🇷 Brazil",       callback_data="geo_BR"),
        InlineKeyboardButton(text="🇸🇬 Singapore",    callback_data="geo_SG"),
    ],
    [
        InlineKeyboardButton(text="🌏 Southeast Asia", callback_data="geo_SEA"),
        InlineKeyboardButton(text="🌍 Global",          callback_data="geo_GLOBAL"),
    ],
])

_GEO_COUNTRY_NAMES = {
    "US": "United States", "GB": "United Kingdom", "KH": "Cambodia",
    "JP": "Japan", "AU": "Australia", "DE": "Germany",
    "IN": "India", "BR": "Brazil", "SG": "Singapore",
    "SEA": "Southeast Asia", "GLOBAL": "Global",
}


@dp.message(Command("geo"))
@dp.message(F.text == "GEO Order")
async def cmd_geo(message: Message, state: FSMContext):
    await state.set_state(GeoOrderState.waiting_link)
    await message.answer(
        "<b>🌍 AI GEO Smart Order</b>\n\n"
        "Target <b>Real Human</b> followers, views or likes to a specific country, state, or city.\n\n"
        "📎 Step 1 — Send your <b>profile or post link</b>:",
        parse_mode="HTML",
    )


@dp.message(GeoOrderState.waiting_link)
async def geo_got_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await state.set_state(GeoOrderState.waiting_platform)
    await message.answer("📱 Step 2 — Select your <b>platform</b>:", parse_mode="HTML", reply_markup=PLATFORM_KB)


@dp.callback_query(F.data.startswith("plt_"), GeoOrderState.waiting_platform)
async def geo_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    await state.update_data(platform=platform)
    await state.set_state(GeoOrderState.waiting_budget)
    await callback.message.answer(
        f"Platform: <b>{platform}</b>\n\n💵 Step 3 — Your <b>budget in USD</b>? (e.g. <code>20</code>)",
        parse_mode="HTML",
    )
    await callback.answer()


@dp.message(GeoOrderState.waiting_budget)
async def geo_got_budget(message: Message, state: FSMContext):
    try:
        budget = float(message.text.replace("$", "").strip())
    except ValueError:
        await message.answer("⚠️ Please send a valid amount (e.g. <code>20</code>)", parse_mode="HTML")
        return
    await state.update_data(budget=budget)
    await state.set_state(GeoOrderState.waiting_country)
    await message.answer("🗺 Step 4 — Select your <b>target location</b>:", parse_mode="HTML", reply_markup=_GEO_COUNTRIES)


@dp.callback_query(F.data.startswith("geo_"), GeoOrderState.waiting_country)
async def geo_got_country(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("geo_", "")
    data = await state.get_data()
    await state.clear()
    name = _GEO_COUNTRY_NAMES.get(code, code)
    geo_scope = "Global" if code == "GLOBAL" else ("Continent" if code == "SEA" else "Country")
    continent = "Asia" if code == "SEA" else ""
    country   = code if code not in ("SEA", "GLOBAL") else ""

    await callback.message.answer(
        f"🌍 <b>GEO Smart Order</b>\n"
        f"📍 Location: <b>{name}</b>  |  Platform: <b>{data['platform']}</b>  |  Budget: <b>${data['budget']}</b>\n\n"
        f"🤖 AI is analysing best geo-targeted services…",
        parse_mode="HTML",
    )
    result = await _api_post("/api/v1/smm/geo-smart-order", {
        "link": data["link"], "goal": "followers",
        "budget_usd": data["budget"], "platform": data["platform"],
        "geo_scope": geo_scope, "continent": continent, "country": country,
        "state": "", "city": "", "language": "",
        "quality_tier": "Premium Real Human", "real_human_only": True, "device": "All",
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", result)
        top  = d.get("top_recommendation", {})
        recs = d.get("recommendations", [])
        text = (
            f"✅ <b>GEO Smart Order — Top Pick</b>\n\n"
            f"🏆 <b>{top.get('service_name', 'N/A')}</b>\n"
            f"💰 Rate: <b>${top.get('rate_per_1k', 'N/A')}/1K</b>\n"
            f"📦 Qty: <b>{top.get('recommended_qty', 'N/A')}</b>\n"
            f"💵 Est. Cost: <b>${top.get('estimated_cost', 'N/A')}</b>\n"
            f"👤 Real Human: <b>{top.get('human_score', 'N/A')}%</b>\n"
            f"🌍 Geo Match: <b>{top.get('geo_match_score', 'N/A')}%</b>\n"
            f"🤖 AI Score: <b>{top.get('ai_confidence', 'N/A')}%</b>\n"
            f"📍 Target: <b>{name}</b>\n"
        )
        if len(recs) > 1:
            text += "\n<b>Alternatives:</b>\n"
            for rec in recs[1:3]:
                text += f"  • {rec.get('service_name', '?')} — ${rec.get('estimated_cost', '?')}\n"
        text += "\n<i>Use Desktop App → 🌍 Geo Intelligence for more options.</i>"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# ─── /viral — Viral Content Tools ────────────────────────────────────────────
@dp.message(Command("viral"))
@dp.message(F.text == "Viral")
async def cmd_viral(message: Message, state: FSMContext):
    await state.set_state(ViralState.waiting_topic)
    await message.answer(
        "<b>🔥 Viral Growth Tools</b>\n\n"
        "I'll generate viral hooks, captions, trending hashtags and growth tips.\n\n"
        "Send your <b>topic or keyword</b>:\n"
        "<i>e.g. Weight Loss, AI Tools, Business, Crypto</i>",
        parse_mode="HTML",
    )


@dp.message(ViralState.waiting_topic)
async def viral_got_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text.strip())
    await state.set_state(ViralState.waiting_platform)
    await message.answer("Select your <b>platform</b>:", parse_mode="HTML", reply_markup=PLATFORM_KB)


@dp.callback_query(F.data.startswith("plt_"), ViralState.waiting_platform)
async def viral_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(f"🔥 Generating viral package for <b>{platform}</b>…", parse_mode="HTML")
    result = await _api_post("/api/v1/ai/content", {
        "topic": data["topic"], "platform": platform,
        "tone": "Viral and Catchy", "language": "English",
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", {})
        text = (
            f"<b>🔥 Viral Package — {platform}</b>\n\n"
            f"<b>Hook:</b>\n{d.get('hook', 'N/A')}\n\n"
            f"<b>Caption:</b>\n{d.get('caption', 'N/A')}\n\n"
            f"<b>Hashtags:</b>\n{d.get('hashtags', 'N/A')}\n\n"
            f"<b>Best time to post:</b> {d.get('best_time', '7–9 PM weekdays')}"
        )
        await callback.message.answer(text[:4000], parse_mode="HTML")
    await callback.answer()


# ─── /analytics — Quick Analytics ────────────────────────────────────────────
@dp.message(Command("analytics"))
async def cmd_analytics(message: Message, state: FSMContext):
    await state.set_state(AnalyticsState.waiting_platform)
    await message.answer(
        "<b>📊 Quick Analytics Dashboard</b>\n\nSelect platform:",
        parse_mode="HTML", reply_markup=PLATFORM_KB,
    )


@dp.callback_query(F.data.startswith("plt_"), AnalyticsState.waiting_platform)
async def analytics_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    await state.clear()
    await callback.message.answer(f"📊 Generating {platform} analytics insights…")
    result = await _api_post("/api/v1/ai/report", {
        "account_name": "Your Account", "platform": platform, "period": "Last 30 Days",
        "metrics": {"views": 50000, "likes": 3500, "comments": 420, "shares": 210, "follows": 800},
        "goals_achieved": ["Growing engagement"],
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await callback.message.answer(
            f"<b>📊 Analytics — {platform}</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )
    await callback.answer()


# ─── /brand — Brand Authority Check ─────────────────────────────────────────
@dp.message(Command("brand"))
async def cmd_brand(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="TikTok",    callback_data="brand_TikTok"),
         InlineKeyboardButton(text="Instagram", callback_data="brand_Instagram")],
        [InlineKeyboardButton(text="Facebook",  callback_data="brand_Facebook"),
         InlineKeyboardButton(text="YouTube",   callback_data="brand_YouTube")],
    ])
    await message.answer("<b>🏆 Brand Authority Check</b>\n\nSelect your main platform:", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("brand_"))
async def brand_handler(callback: CallbackQuery):
    platform = callback.data.replace("brand_", "")
    await callback.message.answer(f"Analysing brand authority for <b>{platform}</b>…", parse_mode="HTML")
    result = await _api_post("/api/v1/ai/audit", {
        "username": "yourbrand", "platform": platform,
        "followers": 10000, "niche": "General",
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await callback.message.answer(
            f"<b>🏆 Brand Authority — {platform}</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )
    await callback.answer()


# ─── /business — Business Intelligence ───────────────────────────────────────
@dp.message(Command("business"))
@dp.message(F.text == "Business")
async def cmd_business(message: Message, state: FSMContext):
    await state.set_state(BusinessState.waiting_niche)
    await message.answer(
        "<b>💼 Business Intelligence</b>\n\n"
        "Send your <b>niche or industry</b>:\n"
        "<i>e.g. E-commerce, SaaS, Fashion, Food, Crypto, Real Estate</i>",
        parse_mode="HTML",
    )


@dp.message(BusinessState.waiting_niche)
async def business_got_niche(message: Message, state: FSMContext):
    await state.update_data(niche=message.text.strip())
    await state.set_state(BusinessState.waiting_platform)
    await message.answer("Select your main platform:", reply_markup=PLATFORM_KB)


@dp.callback_query(F.data.startswith("plt_"), BusinessState.waiting_platform)
async def business_got_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("plt_", "")
    data = await state.get_data()
    await state.clear()
    await callback.message.answer(f"💼 Generating business intelligence for <b>{data['niche']}</b>…", parse_mode="HTML")
    result = await _api_post("/api/v1/ai/strategy", {
        "username": "brand", "platform": platform,
        "current_followers": 5000, "niche": data["niche"],
        "goal_followers": 50000, "duration_days": 90,
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        await callback.message.answer(
            f"<b>💼 Business Intelligence — {data['niche']}</b>\n\n{_fmt(result.get('data', result))}",
            parse_mode="HTML",
        )
    await callback.answer()


# ─── /creator — Creator Toolkit ──────────────────────────────────────────────
@dp.message(Command("creator"))
async def cmd_creator(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Video Script",     callback_data="creator_script"),
         InlineKeyboardButton(text="💡 Content Ideas",   callback_data="creator_ideas")],
        [InlineKeyboardButton(text="♻️ Repurpose Plan",  callback_data="creator_repurpose"),
         InlineKeyboardButton(text="🖼 Thumbnail Ideas",  callback_data="creator_thumb")],
    ])
    await message.answer("<b>🎨 Creator Toolkit</b>\n\nWhat do you need to create?", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("creator_"))
async def creator_handler(callback: CallbackQuery):
    action = callback.data.replace("creator_", "")
    labels = {
        "script": "viral video script",
        "ideas": "20 content ideas",
        "repurpose": "content repurpose plan",
        "thumb": "thumbnail + title ideas",
    }
    label = labels.get(action, "creator content")
    await callback.message.answer(f"🎨 Generating {label}…")
    result = await _api_post("/api/v1/ai/content", {
        "topic": label, "platform": "TikTok", "tone": "Viral and Catchy", "language": "English",
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", result)
        await callback.message.answer(f"<b>🎨 {label.title()}</b>\n\n{_fmt(d)}", parse_mode="HTML")
    await callback.answer()


# ─── /community — Community Hub ──────────────────────────────────────────────
@dp.message(Command("community"))
async def cmd_community(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Engagement Tips",  callback_data="comm_engage"),
         InlineKeyboardButton(text="📈 Growth Strategy",  callback_data="comm_growth")],
        [InlineKeyboardButton(text="📅 Content Calendar", callback_data="comm_calendar"),
         InlineKeyboardButton(text="❤️ Loyalty Program",  callback_data="comm_loyalty")],
    ])
    await message.answer("<b>🤝 Community Hub</b>\n\nWhat community strategy do you need?", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("comm_"))
async def community_handler(callback: CallbackQuery):
    labels = {
        "engage": "engagement tips",
        "growth": "community growth strategy",
        "calendar": "content calendar plan",
        "loyalty": "loyalty program design",
    }
    label = labels.get(callback.data.replace("comm_", ""), "community strategy")
    await callback.message.answer(f"🤝 Generating {label}…")
    result = await _api_post("/api/v1/ai/content", {
        "topic": label, "platform": "Instagram", "tone": "Engaging", "language": "English",
    })
    if "error" in result:
        await callback.message.answer(_err(result["error"]), parse_mode="HTML")
    else:
        d = result.get("data", result)
        await callback.message.answer(f"<b>🤝 {label.title()}</b>\n\n{_fmt(d)}", parse_mode="HTML")
    await callback.answer()


# ─── /facebook — Facebook Manager ────────────────────────────────────────────
@dp.message(Command("facebook"))
@dp.message(F.text == "Facebook")
async def cmd_facebook(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 List Pages",       callback_data="fb_pages"),
         InlineKeyboardButton(text="✍️ AI Generate Post", callback_data="fb_genpost")],
        [InlineKeyboardButton(text="📅 Bulk Schedule",    callback_data="fb_schedule"),
         InlineKeyboardButton(text="💬 AI Reply Tips",    callback_data="fb_reply")],
    ])
    await message.answer("<b>📘 Facebook Manager</b>\n\nWhat would you like to do?", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("fb_"))
async def facebook_handler(callback: CallbackQuery):
    action = callback.data.replace("fb_", "")

    if action == "pages":
        await callback.message.answer("Loading your Facebook pages…")
        result = await _api_get("/api/v1/facebook/pages")
        if result.get("status") == "error":
            await callback.message.answer(_err(result.get("message", "Error loading pages")), parse_mode="HTML")
        else:
            pages = result.get("pages", [])
            if not pages:
                text = "No pages found. Connect your account in Desktop App → 🔐 Social Accounts."
            else:
                text = "<b>📘 Your Facebook Pages:</b>\n\n"
                for p in pages[:5]:
                    text += f"• <b>{p.get('name', '?')}</b>  (ID: <code>{p.get('id', '')}</code>)\n  Fans: {p.get('fan_count', 'N/A')}\n\n"
            await callback.message.answer(text, parse_mode="HTML")

    elif action == "genpost":
        await callback.message.answer("✍️ Generating AI Facebook post…")
        result = await _api_post("/api/v1/facebook/ai/generate-post", {
            "page_name": "Your Brand", "tone": "engaging",
            "goal": "grow followers", "audience": "general",
        })
        if result.get("status") == "error":
            await callback.message.answer(_err(result.get("message", "Error")), parse_mode="HTML")
        else:
            await callback.message.answer(
                f"<b>✍️ AI Generated Post:</b>\n\n{result.get('post', '')}", parse_mode="HTML",
            )

    elif action == "reply":
        await callback.message.answer("💬 Generating AI reply example…")
        result = await _api_post("/api/v1/facebook/ai/suggest-reply", {
            "original_text": "How much does this cost?",
            "context": "Facebook page comment", "tone": "friendly",
        })
        if result.get("status") == "error":
            await callback.message.answer(_err(result.get("message", "Error")), parse_mode="HTML")
        else:
            await callback.message.answer(
                f"<b>💬 AI Reply Example:</b>\n\n{result.get('reply', '')}\n\n"
                f"<i>For full comment management: Desktop App → 📘 Facebook Manager</i>",
                parse_mode="HTML",
            )

    elif action == "schedule":
        await callback.message.answer("📅 Generating 5-post bulk schedule…")
        result = await _api_post("/api/v1/facebook/ai/bulk-schedule", {
            "page_name": "Your Brand", "topic": "Social Media Growth",
            "num_posts": 5, "tone": "engaging", "goal": "grow followers",
        })
        if result.get("status") == "error":
            await callback.message.answer(_err(result.get("message", "Error")), parse_mode="HTML")
        else:
            posts = result.get("posts", [])
            text = "<b>📅 5-Post Schedule Ready!</b>\n\n"
            for i, p in enumerate(posts[:3], 1):
                text += f"<b>Post {i}:</b>\n{str(p)[:250]}\n\n"
            text += "<i>See Desktop App → 📘 Facebook Manager for full schedule.</i>"
            await callback.message.answer(text[:4000], parse_mode="HTML")

    await callback.answer()


# ─── /schedule — Content Scheduling ─────────────────────────────────────────
@dp.message(Command("schedule"))
async def cmd_schedule(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 This Week Plan",  callback_data="sched_week"),
         InlineKeyboardButton(text="📆 30-Day Calendar", callback_data="sched_month")],
        [InlineKeyboardButton(text="⏰ Best Post Times", callback_data="sched_times")],
    ])
    await message.answer("<b>📅 Content Scheduler</b>\n\nWhat do you need?", parse_mode="HTML", reply_markup=kb)


@dp.callback_query(F.data.startswith("sched_"))
async def schedule_handler(callback: CallbackQuery):
    action = callback.data.replace("sched_", "")
    if action == "times":
        await callback.message.answer(
            "<b>⏰ Best Posting Times</b>\n\n"
            "🎵 <b>TikTok:</b> 6–9 PM weekdays, 10 AM–12 PM weekends\n"
            "📸 <b>Instagram:</b> 11 AM–1 PM &amp; 7–9 PM\n"
            "📘 <b>Facebook:</b> 1–4 PM weekdays\n"
            "▶️ <b>YouTube:</b> 2–4 PM Fri–Sun\n"
            "✈️ <b>Telegram:</b> 8–10 PM daily\n\n"
            "💡 <i>Use Desktop App → 📅 Auto-Scheduler for AI-powered scheduling.</i>",
            parse_mode="HTML",
        )
    else:
        label = "weekly content plan" if action == "week" else "30-day content calendar"
        await callback.message.answer(f"📅 Generating {label}…")
        result = await _api_post("/api/v1/ai/campaign", {
            "name": label.title(), "platform": "TikTok",
            "niche": "General", "goal": "Grow Followers",
            "budget_usd": 0, "duration_days": 7 if action == "week" else 30,
        })
        if "error" in result:
            await callback.message.answer(_err(result["error"]), parse_mode="HTML")
        else:
            await callback.message.answer(
                f"<b>📅 {label.title()}</b>\n\n{_fmt(result.get('data', result))}",
                parse_mode="HTML",
            )
    await callback.answer()


# ─── /inbox — Inbox Management Tips ─────────────────────────────────────────
@dp.message(Command("inbox"))
async def cmd_inbox(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Reply Templates",    callback_data="inbox_templates"),
         InlineKeyboardButton(text="📊 Engagement Tips",   callback_data="inbox_engage")],
        [InlineKeyboardButton(text="💌 DM Best Practices", callback_data="inbox_dm")],
    ])
    await message.answer(
        "<b>💬 Social Inbox Manager</b>\n\n"
        "Full management is in Desktop App → 💬 Social Inbox\n\nQuick help:",
        parse_mode="HTML", reply_markup=kb,
    )


@dp.callback_query(F.data.startswith("inbox_"))
async def inbox_handler(callback: CallbackQuery):
    action = callback.data.replace("inbox_", "")
    replies = {
        "templates": (
            "<b>💬 Auto-Reply Templates</b>\n\n"
            "📌 <b>Price Inquiry:</b>\nThank you! 😊 Check the link in bio for full pricing!\n\n"
            "📌 <b>Collab Request:</b>\nWe love collabs! 🤝 Send your media kit to our email in bio!\n\n"
            "📌 <b>Thank You:</b>\nYou're amazing! 🙏 Thank you so much for the support!\n\n"
            "📌 <b>Complaint:</b>\nSo sorry to hear this! 💙 Please DM us so we can fix this right away!"
        ),
        "engage": (
            "<b>📊 Comment Engagement Strategy</b>\n\n"
            "1️⃣ Reply within <b>1 hour</b> — algorithm boost\n"
            "2️⃣ Always ask a <b>follow-up question</b>\n"
            "3️⃣ Use the <b>commenter's name</b>\n"
            "4️⃣ Pin the <b>most valuable comment</b>\n"
            "5️⃣ React to ALL comments in first <b>30 minutes</b>\n\n"
            "🔥 <b>Pro Tip:</b> Reply with a question = 3× more replies!"
        ),
        "dm": (
            "<b>💌 DM Best Practices</b>\n\n"
            "✅ Respond within <b>4 hours</b> on weekdays\n"
            "✅ Use their <b>name</b> in your first reply\n"
            "✅ Offer <b>value immediately</b> — no pitch first\n"
            "✅ End with a <b>clear next step</b>\n\n"
            "❌ Never send <b>generic copy-paste</b> DMs\n"
            "❌ Don't push to <b>buy immediately</b>"
        ),
    }
    await callback.message.answer(replies.get(action, ""), parse_mode="HTML")
    await callback.answer()


# ═══════════════════════════════════════════════════════════════════════════════
# AI SOCIAL NETWORK — Full Social Media Platform
# ═══════════════════════════════════════════════════════════════════════════════

# ─── /social — Social Network Hub ────────────────────────────────────────────
@dp.message(Command("social"))
@dp.message(F.text == "📱 Social Network")
@dp.message(F.text == "🌌 Omni Hub")
async def cmd_social(message: Message):
    tid  = message.from_user.id
    name = message.from_user.first_name or "Friend"

    if _SOCIAL_OK:
        stats = get_platform_stats()
        profile = get_user_profile(tid)
        member_since = ""
        if profile:
            member_since = profile.get("registered_at", "")[:10]
        post_count = profile.get("post_count", 0) if profile else 0

        await message.answer(
            f"📱 <b>GrowthOS AI Social Network</b>\n\n"
            f"👋 Hey <b>{name}</b>!\n"
            f"📅 Member since: <b>{member_since or 'Today'}</b>\n"
            f"📝 Your posts: <b>{post_count}</b>\n\n"
            f"<b>🌐 Platform Stats:</b>\n"
            f"👥 Members: <b>{stats['total_users']}</b>\n"
            f"📝 Posts: <b>{stats['total_posts']}</b>\n"
            f"❤️ Likes: <b>{stats['total_likes']}</b>\n"
            f"💬 Comments: <b>{stats['total_comments']}</b>\n"
            f"🆕 New today: <b>{stats['registered_today']}</b> members  |  <b>{stats['posts_today']}</b> posts\n\n"
            f"<b>What do you want to do?</b>",
            parse_mode="HTML",
            reply_markup=SOCIAL_MAIN_KB,
        )
    else:
        await message.answer(
            f"📱 <b>GrowthOS AI Social Network</b>\n\n"
            f"👋 Hey <b>{name}</b>!\n\n"
            f"Choose an action below:",
            parse_mode="HTML",
            reply_markup=SOCIAL_MAIN_KB,
        )


# ─── /feed — Browse Feed ─────────────────────────────────────────────────────
@dp.message(Command("feed"))
@dp.message(F.text == "📰 View Feed")
async def cmd_feed(message: Message):
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    posts = get_feed(page=1, per_page=5)
    if not posts:
        await message.answer(
            "📭 <b>The feed is empty!</b>\n\n"
            "Be the first to post!\n"
            "Use /post to share something amazing 🚀",
            parse_mode="HTML",
        )
        return

    for p in posts:
        media_icon = {"image": "📸", "video": "🎬", "audio": "🎵"}.get(p.get("media_type", "text"), "📝")
        likes_count    = len(p.get("likes", []))
        comments_count = len(p.get("comments", []))
        content        = p.get("content", "")[:800]
        author         = p.get("author_name", "Unknown")
        uname          = p.get("author_uname", "")
        uname_str      = f"@{uname}" if uname else ""
        created        = p.get("created_at", "")[:16]
        pid            = p.get("post_id", "")

        text = (
            f"{media_icon} <b>{author}</b> {uname_str}\n"
            f"<i>{created}</i>\n\n"
            f"{content}\n\n"
            f"❤️ <b>{likes_count}</b>  💬 <b>{comments_count}</b>  🆔 <code>{pid}</code>"
        )

        feed_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"❤️ Like ({likes_count})", callback_data=f"like_{pid}"),
                InlineKeyboardButton(text=f"💬 Comment ({comments_count})", callback_data=f"comment_{pid}"),
            ],
            [
                InlineKeyboardButton(text="👁 View Comments", callback_data=f"view_comments_{pid}"),
            ],
        ])
        await message.answer(text, parse_mode="HTML", reply_markup=feed_kb)


# ─── /post — Text Post ───────────────────────────────────────────────────────
@dp.message(Command("post"))
@dp.message(F.text == "✍️ Post Text")
async def cmd_post(message: Message, state: FSMContext):
    tid = message.from_user.id
    if _SOCIAL_OK and not is_registered(tid):
        await message.answer("❗ Please send /start to register first.", parse_mode="HTML")
        return

    await state.set_state(SocialPostState.waiting_caption)
    await message.answer(
        "✍️ <b>Create a Text Post</b>\n\n"
        "Write your post below. You can include hashtags, emojis, and links.\n\n"
        "<i>💡 Tip: AI will automatically enhance your caption with emojis and hashtags!</i>\n\n"
        "📝 <b>Type your post now:</b>",
        parse_mode="HTML",
    )


@dp.message(SocialPostState.waiting_caption)
async def social_post_caption(message: Message, state: FSMContext):
    await state.clear()
    tid     = message.from_user.id
    raw     = message.text or ""

    if not raw.strip():
        await message.answer("❌ Post cannot be empty. Try again with /post", parse_mode="HTML")
        return

    # AI enhance the caption
    enhanced = ai_enhance_caption(raw) if _SOCIAL_OK else raw

    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    post = create_post(telegram_id=tid, content=enhanced, media_type="text")
    pid  = post.get("post_id", "")
    await message.answer(
        f"✅ <b>Post Published!</b>\n\n"
        f"{enhanced}\n\n"
        f"🆔 Post ID: <code>{pid}</code>\n"
        f"📅 Posted at: <code>{post.get('created_at', '')[:16]}</code>\n\n"
        f"🔔 Your post is now live in the feed!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📰 View Feed", callback_data="goto_feed"),
        ]]),
    )


# ─── /photo — Photo Post ─────────────────────────────────────────────────────
@dp.message(Command("photo"))
@dp.message(F.text == "📸 Post Photo")
async def cmd_photo(message: Message, state: FSMContext):
    tid = message.from_user.id
    if _SOCIAL_OK and not is_registered(tid):
        await message.answer("❗ Please send /start to register first.", parse_mode="HTML")
        return

    await state.set_state(SocialPhotoState.waiting_caption)
    await message.answer(
        "📸 <b>Share a Photo Post</b>\n\n"
        "Step 1: Write your caption first.\n\n"
        "✏️ <b>Type your caption now:</b>",
        parse_mode="HTML",
    )


@dp.message(SocialPhotoState.waiting_caption)
async def social_photo_caption(message: Message, state: FSMContext):
    caption = message.text or ""
    enhanced = ai_enhance_caption(caption, "Social") if _SOCIAL_OK else caption
    await state.update_data(caption=enhanced)
    await state.set_state(SocialPhotoState.waiting_photo)
    await message.answer(
        f"✅ Caption ready!\n\n"
        f"📸 <b>Now send your photo:</b>",
        parse_mode="HTML",
    )


@dp.message(SocialPhotoState.waiting_photo, F.photo)
async def social_photo_upload(message: Message, state: FSMContext):
    data    = await state.get_data()
    caption = data.get("caption", "")
    await state.clear()
    tid     = message.from_user.id

    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    # Get highest resolution photo
    file_id = message.photo[-1].file_id if message.photo else ""
    post = create_post(
        telegram_id  = tid,
        content      = caption,
        media_type   = "image",
        media_file_id= file_id,
    )
    pid = post.get("post_id", "")
    await message.answer(
        f"📸 <b>Photo Posted Successfully!</b>\n\n"
        f"{caption}\n\n"
        f"🆔 Post ID: <code>{pid}</code>\n"
        f"🔔 Your photo is now live in the feed!",
        parse_mode="HTML",
    )


@dp.message(SocialPhotoState.waiting_photo)
async def social_photo_no_photo(message: Message, state: FSMContext):
    await message.answer("❌ Please send a photo image, not text. Or /start to cancel.", parse_mode="HTML")


# ─── /video — Short Video Post ───────────────────────────────────────────────
@dp.message(Command("video"))
@dp.message(F.text == "🎬 Post Video")
async def cmd_video(message: Message, state: FSMContext):
    tid = message.from_user.id
    if _SOCIAL_OK and not is_registered(tid):
        await message.answer("❗ Please send /start to register first.", parse_mode="HTML")
        return

    await state.set_state(SocialVideoState.waiting_caption)
    await message.answer(
        "🎬 <b>Share a Short Video / Selfie Video</b>\n\n"
        "Step 1: Write your caption first.\n\n"
        "✏️ <b>Type your caption now:</b>",
        parse_mode="HTML",
    )


@dp.message(SocialVideoState.waiting_caption)
async def social_video_caption(message: Message, state: FSMContext):
    caption  = message.text or ""
    enhanced = ai_enhance_caption(caption, "Social") if _SOCIAL_OK else caption
    await state.update_data(caption=enhanced)
    await state.set_state(SocialVideoState.waiting_video)
    await message.answer(
        f"✅ Caption ready!\n\n"
        f"🎬 <b>Now send your video</b> (selfie video, short clip, etc.):",
        parse_mode="HTML",
    )


@dp.message(SocialVideoState.waiting_video, F.video | F.video_note)
async def social_video_upload(message: Message, state: FSMContext):
    data    = await state.get_data()
    caption = data.get("caption", "")
    await state.clear()
    tid = message.from_user.id

    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    file_id = ""
    if message.video:
        file_id = message.video.file_id
    elif message.video_note:
        file_id = message.video_note.file_id

    post = create_post(
        telegram_id  = tid,
        content      = caption,
        media_type   = "video",
        media_file_id= file_id,
    )
    pid = post.get("post_id", "")
    await message.answer(
        f"🎬 <b>Video Posted Successfully!</b>\n\n"
        f"{caption}\n\n"
        f"🆔 Post ID: <code>{pid}</code>\n"
        f"🔔 Your video is now live in the feed!",
        parse_mode="HTML",
    )


@dp.message(SocialVideoState.waiting_video)
async def social_video_no_video(message: Message, state: FSMContext):
    await message.answer("❌ Please send a video file. Or /start to cancel.", parse_mode="HTML")


# ─── Like Callback ────────────────────────────────────────────────────────────
@dp.callback_query(F.data.startswith("like_"))
async def cb_like(callback: CallbackQuery):
    if not _SOCIAL_OK:
        await callback.answer("Social platform unavailable.", show_alert=True)
        return
    pid = callback.data.replace("like_", "")
    tid = callback.from_user.id
    try:
        result = toggle_like(tid, pid)
        liked  = result.get("liked", False)
        total  = result.get("total_likes", 0)
        icon   = "❤️" if liked else "🤍"
        await callback.answer(
            f"{icon} {'Liked!' if liked else 'Unliked'} — {total} like{'s' if total != 1 else ''}",
            show_alert=False,
        )
        # Update button label
        new_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{icon} Like ({total})", callback_data=f"like_{pid}"),
                InlineKeyboardButton(text="💬 Comment",             callback_data=f"comment_{pid}"),
            ],
            [
                InlineKeyboardButton(text="👁 View Comments", callback_data=f"view_comments_{pid}"),
            ],
        ])
        await callback.message.edit_reply_markup(reply_markup=new_kb)
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)


# ─── Feed goto callback ───────────────────────────────────────────────────────
@dp.callback_query(F.data == "goto_feed")
async def cb_goto_feed(callback: CallbackQuery):
    await callback.answer()
    await cmd_feed(callback.message)


# ─── Comment Callback ─────────────────────────────────────────────────────────
@dp.callback_query(F.data.startswith("comment_"))
async def cb_comment_start(callback: CallbackQuery, state: FSMContext):
    pid = callback.data.replace("comment_", "")
    tid = callback.from_user.id
    if _SOCIAL_OK and not is_registered(tid):
        await callback.answer("Please /start to register first.", show_alert=True)
        return

    await state.set_state(SocialCommentState.waiting_text)
    await state.update_data(post_id=pid)
    await callback.message.answer(
        f"💬 <b>Write your comment</b> for post <code>{pid}</code>:\n\n"
        f"<i>Just type your comment below:</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@dp.message(SocialCommentState.waiting_text)
async def social_comment_text(message: Message, state: FSMContext):
    data = await state.get_data()
    pid  = data.get("post_id", "")
    await state.clear()
    tid  = message.from_user.id
    text = message.text or ""

    if not text.strip():
        await message.answer("❌ Comment cannot be empty.", parse_mode="HTML")
        return
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    try:
        comment = add_comment(tid, pid, text)
        cid     = comment.get("comment_id", "")
        await message.answer(
            f"✅ <b>Comment Posted!</b>\n\n"
            f"💬 <i>{text}</i>\n\n"
            f"🆔 Comment ID: <code>{cid}</code>\n"
            f"Use /reply to reply to this comment.",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Error: {e}", parse_mode="HTML")


# ─── View Comments Callback ───────────────────────────────────────────────────
@dp.callback_query(F.data.startswith("view_comments_"))
async def cb_view_comments(callback: CallbackQuery):
    if not _SOCIAL_OK:
        await callback.answer("Social platform unavailable.", show_alert=True)
        return
    pid  = callback.data.replace("view_comments_", "")
    post = get_post(pid)
    if not post:
        await callback.answer("Post not found.", show_alert=True)
        return

    comments = post.get("comments", [])
    if not comments:
        await callback.message.answer(
            f"💬 No comments yet on post <code>{pid}</code>.\nBe the first to comment!",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = f"💬 <b>Comments on post <code>{pid}</code></b>\n\n"
    for c in comments[:10]:
        author  = c.get("author_name", "Unknown")
        c_text  = c.get("text", "")[:200]
        cid     = c.get("comment_id", "")
        created = c.get("created_at", "")[:16]
        c_likes = len(c.get("likes", []))
        replies = len(c.get("replies", []))
        text += (
            f"👤 <b>{author}</b>  <i>{created}</i>\n"
            f"   {c_text}\n"
            f"   ❤️ {c_likes}  ↩️ {replies} replies  🆔 <code>{cid}</code>\n\n"
        )

    text += f"<i>To reply: /reply → enter post ID → enter comment ID → type reply</i>"
    await callback.message.answer(text[:4000], parse_mode="HTML")
    await callback.answer()


# ─── /reply — Reply to Comment ───────────────────────────────────────────────
@dp.message(Command("reply"))
@dp.message(F.text == "↩️ Reply Comment")
async def cmd_reply(message: Message, state: FSMContext):
    tid = message.from_user.id
    if _SOCIAL_OK and not is_registered(tid):
        await message.answer("❗ Please send /start to register first.", parse_mode="HTML")
        return

    await state.set_state(SocialReplyState.waiting_post_id)
    await message.answer(
        "↩️ <b>Reply to a Comment</b>\n\n"
        "Step 1: Enter the <b>Post ID</b> (shown under each post as 🆔):",
        parse_mode="HTML",
    )


@dp.message(SocialReplyState.waiting_post_id)
async def reply_got_post_id(message: Message, state: FSMContext):
    pid = (message.text or "").strip()
    post = get_post(pid) if _SOCIAL_OK else None
    if not post:
        await message.answer(
            "❌ Post not found. Check the Post ID and try again.\n\n"
            "Use /feed to browse posts and find their IDs.",
            parse_mode="HTML",
        )
        return
    await state.update_data(post_id=pid)
    await state.set_state(SocialReplyState.waiting_comment_id)
    comments = post.get("comments", [])
    c_info = ""
    for c in comments[:5]:
        cid  = c.get("comment_id", "")
        auth = c.get("author_name", "?")
        txt  = c.get("text", "")[:80]
        c_info += f"  <code>{cid}</code> — <b>{auth}</b>: {txt}\n"
    await message.answer(
        f"✅ Post found!\n\n"
        f"<b>Comments:</b>\n{c_info or '(No comments yet)'}\n\n"
        f"Step 2: Enter the <b>Comment ID</b> to reply to:",
        parse_mode="HTML",
    )


@dp.message(SocialReplyState.waiting_comment_id)
async def reply_got_comment_id(message: Message, state: FSMContext):
    cid = (message.text or "").strip()
    await state.update_data(comment_id=cid)
    await state.set_state(SocialReplyState.waiting_text)
    await message.answer(
        f"✅ Comment ID: <code>{cid}</code>\n\n"
        f"Step 3: Type your <b>reply</b>:",
        parse_mode="HTML",
    )


@dp.message(SocialReplyState.waiting_text)
async def reply_got_text(message: Message, state: FSMContext):
    data = await state.get_data()
    pid  = data.get("post_id", "")
    cid  = data.get("comment_id", "")
    text = (message.text or "").strip()
    await state.clear()
    tid  = message.from_user.id

    if not text:
        await message.answer("❌ Reply cannot be empty.", parse_mode="HTML")
        return
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    try:
        rep = reply_comment(tid, pid, cid, text)
        # AI-suggested response for the author
        post = get_post(pid)
        post_content = post.get("content", "") if post else ""
        ai_tip = ai_suggest_reply(text, post_content)
        await message.answer(
            f"✅ <b>Reply Posted!</b>\n\n"
            f"↩️ <i>{text}</i>\n\n"
            f"💡 <b>AI Smart Reply tip:</b>\n<i>{ai_tip}</i>",
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Error: {e}", parse_mode="HTML")


# ─── /profile — My Profile ───────────────────────────────────────────────────
@dp.message(Command("profile"))
@dp.message(F.text == "👤 My Profile")
async def cmd_profile(message: Message):
    tid = message.from_user.id
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    profile = get_user_profile(tid)
    if not profile:
        await message.answer(
            "❗ Profile not found. Please send /start to register.",
            parse_mode="HTML",
        )
        return

    name       = profile.get("display_name") or profile.get("first_name") or "Unknown"
    username   = profile.get("username", "")
    phone      = profile.get("phone", "")
    sex        = profile.get("sex", "")
    dob        = profile.get("date_of_birth", "")
    bio        = profile.get("bio", "")
    posts      = profile.get("post_count", 0)
    joined     = profile.get("registered_at", "")[:10]
    last_seen  = profile.get("last_seen", "")[:16]
    role       = profile.get("role", "member")
    lang       = profile.get("language_code", "")

    uname_str  = f"@{username}" if username else "(not set)"
    phone_str  = f"{phone}" if phone else "(not set)"
    sex_str    = f"{sex}"   if sex   else "(not set)"
    dob_str    = f"{dob}"   if dob   else "(not set)"
    bio_str    = f"{bio}"   if bio   else "(no bio)"

    await message.answer(
        f"👤 <b>My Profile</b>\n\n"
        f"📛 Name:         <b>{name}</b>\n"
        f"🔗 Username:     {uname_str}\n"
        f"🆔 Telegram ID:  <code>{tid}</code>\n"
        f"📱 Phone:        {phone_str}\n"
        f"⚧ Gender:       {sex_str}\n"
        f"🎂 Date of Birth:{dob_str}\n"
        f"🌐 Language:     {lang}\n"
        f"📝 Posts:        <b>{posts}</b>\n"
        f"📅 Joined:       {joined}\n"
        f"👁 Last seen:    {last_seen}\n"
        f"🏷 Role:         {role}\n\n"
        f"💬 Bio: <i>{bio_str}</i>",
        parse_mode="HTML",
    )


# ─── 🏠 Main Menu button ─────────────────────────────────────────────────────
@dp.message(F.text == "🏠 Main Menu")
async def cmd_main_menu(message: Message, state: FSMContext):
    await state.clear()
    name = message.from_user.first_name or "Friend"
    await message.answer(
        f"🏠 <b>Main Menu</b> — Welcome back, {name}!",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


# ─── /like — Quick Like Command ──────────────────────────────────────────────
@dp.message(Command("like"))
@dp.message(F.text == "❤️ Like Post")
async def cmd_like(message: Message):
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    posts = get_feed(page=1, per_page=5)
    if not posts:
        await message.answer(
            "📭 No posts to like yet. Use /post to create one!",
            parse_mode="HTML",
        )
        return

    kb_rows = []
    for p in posts[:5]:
        pid    = p.get("post_id", "")
        author = p.get("author_name", "Unknown")[:20]
        likes  = len(p.get("likes", []))
        content = p.get("content", "")[:30]
        kb_rows.append([
            InlineKeyboardButton(
                text=f"❤️ {author}: {content}... ({likes})",
                callback_data=f"like_{pid}",
            )
        ])

    await message.answer(
        "❤️ <b>Like a Post</b>\n\n"
        "Select which post to like/unlike:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
    )


# ─── /comment quick command ───────────────────────────────────────────────────
@dp.message(F.text == "💬 Comment")
async def cmd_comment_quick(message: Message, state: FSMContext):
    if not _SOCIAL_OK:
        await message.answer("❌ Social platform unavailable.", parse_mode="HTML")
        return

    posts = get_feed(page=1, per_page=5)
    if not posts:
        await message.answer("📭 No posts to comment on yet. Use /post to create one!", parse_mode="HTML")
        return

    kb_rows = []
    for p in posts[:5]:
        pid    = p.get("post_id", "")
        author = p.get("author_name", "Unknown")[:20]
        comments = len(p.get("comments", []))
        content  = p.get("content", "")[:30]
        kb_rows.append([
            InlineKeyboardButton(
                text=f"💬 {author}: {content}... ({comments})",
                callback_data=f"comment_{pid}",
            )
        ])

    await message.answer(
        "💬 <b>Comment on a Post</b>\n\n"
        "Select which post to comment on:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    global bot
    # The Windows DNS fix (ThreadedResolver monkey-patch + SelectorEventLoop)
    # is applied at module import time above, so a plain AiohttpSession() is
    # sufficient — every TCPConnector() it creates internally will already use
    # the patched resolver.
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
    except Exception as e:
        log.error("Bot token error: %s", e)
        raise SystemExit(1)

    log.info("GrowthOS AI Telegram Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())