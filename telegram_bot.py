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
import httpx
import json
from aiogram import Bot, Dispatcher, F
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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

_SETUP_MSG = """
╔══════════════════════════════════════════════════════╗
║        GrowthOS AI — Telegram Bot Setup              ║
╠══════════════════════════════════════════════════════╣
║  TELEGRAM_BOT_TOKEN is missing or invalid.           ║
║                                                      ║
║  How to get your token:                              ║
║  1. Open Telegram and search for @BotFather          ║
║  2. Send /newbot and follow the prompts              ║
║  3. Copy the token (format: 123456789:AAFxxx...)     ║
║  4. Add it to your .env file:                        ║
║     TELEGRAM_BOT_TOKEN=123456789:AAFxxx...           ║
║                                                      ║
║  Backend API is running — other features work fine.  ║
╚══════════════════════════════════════════════════════╝
"""

_PLACEHOLDER_VALUES = {"", "your_token", "YOUR_TELEGRAM_BOT_TOKEN_HERE"}

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN in _PLACEHOLDER_VALUES:
    print(_SETUP_MSG)
    raise SystemExit(1)

try:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
except Exception as e:
    print(_SETUP_MSG)
    print(f"Token error: {e}")
    raise SystemExit(1)

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

class RiskState(StatesGroup):
    waiting_content = State()

class OrderState(StatesGroup):
    waiting_details = State()


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
        [KeyboardButton(text="Strategy"),  KeyboardButton(text="Content")],
        [KeyboardButton(text="Audit"),     KeyboardButton(text="Trends")],
        [KeyboardButton(text="Risk"),      KeyboardButton(text="Agents")],
        [KeyboardButton(text="SMM Panel"), KeyboardButton(text="Help")],
    ],
    resize_keyboard=True,
)


# ─── /start ───────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.first_name or "there"
    await message.answer(
        f"<b>Welcome to GrowthOS AI, {name}!</b>\n\n"
        "Your autonomous AI Social Growth OS with <b>99 features</b>.\n\n"
        "<b>What I can do:</b>\n"
        "- Generate full 30-day AI growth strategies\n"
        "- Create viral hooks, captions and video scripts\n"
        "- Scan trending topics in real-time\n"
        "- Check content policy compliance\n"
        "- Manage SMM panel orders intelligently\n"
        "- Run a full 5-agent AI team analysis\n\n"
        "Use the menu below or type <b>/help</b> for all commands.",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


# ─── /help ────────────────────────────────────────────────────────────────────
@dp.message(Command("help"))
@dp.message(F.text == "Help")
async def cmd_help(message: Message):
    await message.answer(
        "<b>GrowthOS AI — All Commands</b>\n\n"
        "/strategy — 30-day AI growth strategy\n"
        "/content  — Viral content package\n"
        "/audit    — Deep account audit\n"
        "/trends   — Trending topics now\n"
        "/risk     — Content safety checker\n"
        "/campaign — Campaign plan builder\n"
        "/panel    — SMM panel services\n"
        "/order    — Smart order placement\n"
        "/balance  — SMM panel balance\n"
        "/report   — Performance report\n"
        "/agents   — Multi-agent AI team\n"
        "/help     — Show this help\n\n"
        "Tip: Set <code>OPENAI_API_KEY</code> in .env for real GPT-4o AI",
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


# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    log.info("GrowthOS AI Telegram Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())