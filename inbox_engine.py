"""
GrowthOS AI v2.0 — Social Inbox & AI Auto-Reply Engine
========================================================
Feature #100: Unified Social Inbox Manager
Feature #101: AI Smart Auto-Reply (tone-aware, multi-language)
Feature #102: Auto-Reply Rules Engine (keyword triggers)
Feature #103: Reply Templates Library Generator
Feature #104: Message Sentiment & Intent Analyzer
"""
import json
import random
from datetime import datetime, timedelta
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import (
    LLM_CLIENT as _client,
    LLM_MODEL as _model,
    LLM_FAST_MODEL as _fast_model,
    USE_AI,
)


# ─── LLM Helper ──────────────────────────────────────────────────────────────
async def _gpt(prompt: str, system: str = "", fast: bool = True, max_tokens: int = 400) -> str:
    if not _client:
        return ""
    try:
        model = _fast_model if fast else _model
        resp = await _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or "You are a professional social media community manager."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.80,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


def _try_json(raw: str, fallback):
    try:
        s = raw.find("{") if "{" in raw else raw.find("[")
        e = raw.rfind("}") + 1 if "{" in raw else raw.rfind("]") + 1
        if s >= 0 and e > s:
            return json.loads(raw[s:e])
    except Exception:
        pass
    return fallback


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE #101 — AI Smart Reply Generator
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_ai_reply(
    message: str,
    platform: str = "TikTok",
    tone: str = "Friendly & Warm",
    brand_name: str = "",
    niche: str = "General",
    language: str = "English",
    context: str = "",
) -> dict:
    """Generate AI-powered smart reply for a message or comment."""

    brand_ctx = f"Brand name: {brand_name}. " if brand_name else ""
    ctx_str   = f"Prior conversation context: {context}. " if context else ""

    if USE_AI:
        prompt = (
            f"You are a social media community manager for a {niche} brand on {platform}.\n"
            f"{brand_ctx}{ctx_str}"
            f"Tone: {tone}. Language: {language}.\n\n"
            f"Customer/follower message:\n\"{message}\"\n\n"
            f"Write a perfect reply that:\n"
            f"- Matches the specified tone exactly\n"
            f"- Sounds natural and human (not robotic)\n"
            f"- Encourages further engagement\n"
            f"- Is appropriate for {platform}\n"
            f"- Is written in {language}\n"
            f"- Maximum 2-3 sentences\n"
            f"- Includes relevant emoji if appropriate\n"
            f"- Ends with a question or soft CTA when suitable\n\n"
            f"Return ONLY the reply text, no quotes."
        )
        best_reply = await _gpt(prompt, max_tokens=200)

        # Generate 3 variations
        var_prompt = (
            f"Generate 3 alternative replies (different styles) for this {platform} message:\n"
            f"\"{message}\"\n\n"
            f"Tone: {tone}, Language: {language}, Niche: {niche}\n\n"
            f'Return JSON array only: ["reply1", "reply2", "reply3"]'
        )
        var_raw  = await _gpt(var_prompt, max_tokens=350)
        var_list = _try_json(var_raw, [best_reply])
        if not isinstance(var_list, list):
            var_list = [best_reply]

        if not best_reply:
            best_reply = var_list[0] if var_list else _mock_reply(message, tone, niche)
    else:
        best_reply = _mock_reply(message, tone, niche)
        var_list   = _mock_variations(message, tone)

    return {
        "suggested_reply": best_reply,
        "variations":      var_list,
        "platform":        platform,
        "tone":            tone,
        "language":        language,
        "brand_name":      brand_name,
        "original_message": message[:200],
        "char_count":      len(best_reply),
        "source":          "ai" if USE_AI else "mock",
        "generated_at":    datetime.now().isoformat(),
    }


def _mock_reply(message: str, tone: str, niche: str) -> str:
    msg_lower = message.lower()
    if "?" in message:
        replies = [
            f"Great question! 😊 In the {niche} space, we always recommend doing your research first. Let us know if you need more details!",
            f"That's a really good point! 👍 Feel free to DM us directly and we'll give you a full answer!",
            f"We love answering questions like this! 🙌 Drop us a DM for a more detailed response!",
        ]
    elif any(w in msg_lower for w in ["love", "great", "amazing", "thank", "good", "awesome"]):
        replies = [
            f"Thank you so much! 🙏 Comments like yours keep us motivated every day!",
            f"You're so kind! ❤️ This truly made our day! Stay tuned for more amazing content!",
            f"Aww, thank you! 😊 We're so grateful for your support! Keep being awesome! 🌟",
        ]
    elif any(w in msg_lower for w in ["bad", "hate", "worst", "terrible", "scam", "fake"]):
        replies = [
            f"We're really sorry about your experience 🙏 Please DM us directly so we can make this right.",
            f"Thank you for the feedback. We take this seriously and want to resolve it immediately. Please contact us.",
            f"We sincerely apologize 🙏 This is not our standard. Could you DM us with more details?",
        ]
    else:
        replies = [
            f"Thank you for reaching out! 🙏 We appreciate your engagement and will get back to you soon!",
            f"We saw your message and we're on it! 💪 Stay tuned for our response!",
            f"Thanks for being part of our community! 🌟 We appreciate every interaction!",
        ]
    return random.choice(replies)


def _mock_variations(message: str, tone: str) -> list:
    is_question = "?" in message
    return [
        "Thanks for reaching out! 😊 We'll get back to you shortly!",
        "We appreciate your message! 🙏 Feel free to DM us for more details.",
        "Great to hear from you! 💙 Stay connected for more updates!" if not is_question
        else "That's a great question! DM us for a detailed answer 📩",
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE #104 — Message Sentiment & Intent Analyzer
# ═══════════════════════════════════════════════════════════════════════════════

async def analyze_message_sentiment(message: str, platform: str = "General") -> dict:
    """Analyze sentiment, intent, urgency, and emotion of a message."""

    if USE_AI:
        prompt = (
            f'Analyze this {platform} message and return ONLY valid JSON:\n'
            f'Message: "{message}"\n\n'
            f'Return this exact JSON structure:\n'
            f'{{"sentiment": "Positive|Negative|Neutral|Mixed",'
            f'"sentiment_score": 0.0-1.0,'
            f'"intent": "Question|Complaint|Compliment|Request|Spam|General",'
            f'"urgency": "High|Medium|Low",'
            f'"emotion": "Happy|Angry|Sad|Excited|Curious|Neutral",'
            f'"requires_response": true|false,'
            f'"priority": 1-5,'
            f'"topics": ["topic1"],'
            f'"language_detected": "English|Khmer|Thai|etc",'
            f'"is_spam": true|false,'
            f'"suggested_action": "Reply immediately|Schedule reply|Escalate|Ignore|Auto-reply"}}'
        )
        raw  = await _gpt(prompt, max_tokens=350)
        data = _try_json(raw, None)
        if data and isinstance(data, dict):
            return {**data, "message_preview": message[:100], "analyzed_at": datetime.now().isoformat(), "source": "ai"}

    # Mock fallback
    msg_lower = message.lower()
    sentiment = (
        "Positive" if any(w in msg_lower for w in ["love", "great", "amazing", "thank", "good", "awesome", "wonderful"]) else
        "Negative" if any(w in msg_lower for w in ["bad", "hate", "worst", "terrible", "scam", "fake", "angry", "refund"]) else
        "Neutral"
    )
    intent = (
        "Question"   if "?" in message else
        "Complaint"  if sentiment == "Negative" else
        "Compliment" if sentiment == "Positive" else
        "Spam"       if any(w in msg_lower for w in ["follow me", "check my", "f4f", "buy followers"]) else
        "General"
    )
    return {
        "sentiment":        sentiment,
        "sentiment_score":  0.8 if sentiment == "Positive" else 0.2 if sentiment == "Negative" else 0.5,
        "intent":           intent,
        "urgency":          "High" if sentiment == "Negative" else "Medium",
        "emotion":          "Happy" if sentiment == "Positive" else "Angry" if sentiment == "Negative" else "Curious" if "?" in message else "Neutral",
        "requires_response": intent != "Spam",
        "priority":         1 if sentiment == "Negative" else 3,
        "topics":           [],
        "language_detected": "English",
        "is_spam":          intent == "Spam",
        "suggested_action": "Reply immediately" if sentiment == "Negative" else "Auto-reply" if "?" in message else "Schedule reply",
        "message_preview":  message[:100],
        "analyzed_at":      datetime.now().isoformat(),
        "source":           "mock",
    }


async def batch_analyze_sentiment(messages: List[str], platform: str = "General") -> list:
    """Analyze sentiment for multiple messages at once."""
    results = []
    for i, msg in enumerate(messages[:30]):
        r = await analyze_message_sentiment(msg, platform)
        r["index"] = i + 1
        results.append(r)
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE #103 — Reply Templates Library
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_reply_templates(
    niche: str = "General",
    platform: str = "TikTok",
    tone: str = "Friendly & Warm",
    language: str = "English",
) -> dict:
    """Generate a full reply templates library for common scenarios."""

    if USE_AI:
        prompt = (
            f"Create a complete social media reply template library for a {niche} brand on {platform}.\n"
            f"Tone: {tone}. Language: {language}.\n\n"
            f"Return ONLY valid JSON with exactly these 10 categories (3 templates each):\n"
            f'{{"welcome_follower": ["t1","t2","t3"],'
            f'"thank_compliment": ["t1","t2","t3"],'
            f'"handle_complaint": ["t1","t2","t3"],'
            f'"price_question": ["t1","t2","t3"],'
            f'"product_question": ["t1","t2","t3"],'
            f'"collab_request": ["t1","t2","t3"],'
            f'"encourage_purchase": ["t1","t2","t3"],'
            f'"handle_negative": ["t1","t2","t3"],'
            f'"general_question": ["t1","t2","t3"],'
            f'"handle_spam": ["t1","t2","t3"]}}'
        )
        raw       = await _gpt(prompt, fast=False, max_tokens=1500)
        templates = _try_json(raw, None)
        if templates and isinstance(templates, dict) and len(templates) >= 5:
            return _wrap_templates(templates, niche, platform, tone, language, "ai")

    # Smart mock fallback
    templates = _mock_templates(niche, tone)
    return _wrap_templates(templates, niche, platform, tone, language, "mock")


def _wrap_templates(templates: dict, niche, platform, tone, language, source) -> dict:
    return {
        "templates":        templates,
        "total_categories": len(templates),
        "total_templates":  sum(len(v) for v in templates.values() if isinstance(v, list)),
        "platform":         platform,
        "niche":            niche,
        "tone":             tone,
        "language":         language,
        "source":           source,
        "generated_at":     datetime.now().isoformat(),
    }


def _mock_templates(niche: str, tone: str) -> dict:
    warm = "warm" in tone.lower() or "friendly" in tone.lower()
    emoji = "😊" if warm else ""
    return {
        "welcome_follower": [
            f"Welcome to our {niche} community! {emoji} So glad you're here! Stay tuned for amazing content!",
            f"Hey, welcome! 👋 We share the best {niche} tips daily. Feel free to ask anything!",
            f"You just made a great decision joining us! 🚀 Lots of valuable {niche} content coming your way!",
        ],
        "thank_compliment": [
            f"Thank you so much! 🙏 Comments like yours keep us going every single day!",
            f"Aww, you're so kind! ❤️ This truly made our day! We appreciate you!",
            f"That means the world to us! 🌟 Thank you for the love and support!",
        ],
        "handle_complaint": [
            f"We're really sorry about this 🙏 Please DM us directly so we can resolve it immediately.",
            f"Thank you for letting us know. We take this very seriously and will fix it right away.",
            f"We sincerely apologize. This is not our standard — please contact us directly and we'll make it right.",
        ],
        "price_question": [
            f"Great question! 😊 Please check the link in our bio for full pricing details!",
            f"We have different packages to fit all budgets! DM us and we'll find the perfect option for you!",
            f"Pricing depends on your needs! Let's chat in DMs and we'll customize a plan for you 💬",
        ],
        "product_question": [
            f"That's a great question about our {niche} product! 🙌 DM us for a full detailed answer!",
            f"We'd love to answer that! Check our bio link for full details or DM us directly 📩",
            f"Thanks for asking! Drop us a DM and our team will give you all the info you need!",
        ],
        "collab_request": [
            f"We love collaborating! 🤝 Please send us your media kit via the email in our bio!",
            f"Interested in collabing! Please DM us with your stats and proposal 📊",
            f"We're always open to meaningful collaborations! Reach out via email for details 💼",
        ],
        "encourage_purchase": [
            f"Don't wait — our limited offer ends soon! 🔥 Check the link in bio to grab yours!",
            f"So many happy customers! 🌟 Ready to join them? Click the link in bio to get started!",
            f"This is the perfect time to invest in your {niche} journey! 💪 Link in bio!",
        ],
        "handle_negative": [
            f"We hear you and we're truly sorry 🙏 Please DM us so we can personally address this.",
            f"Your feedback matters to us. We want to make this right — please reach out directly.",
            f"We apologize for falling short of your expectations. DM us and let's resolve this together.",
        ],
        "general_question": [
            f"Great question! 😊 We'll answer this in detail — DM us for a personal response!",
            f"Thanks for asking! Check our highlighted stories for answers or DM us directly 📲",
            f"We love questions! 🙏 For the best answer, drop us a DM and we'll reply ASAP!",
        ],
        "handle_spam": [
            f"Thank you for your message! We only engage with genuine community interactions.",
            f"",  # silent ignore
            f"Our community is focused on valuable {niche} discussions. Please keep it relevant!",
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE #102 — Auto-Reply Rules Engine
# ═══════════════════════════════════════════════════════════════════════════════

def check_auto_reply_rules(message: str, rules: list) -> dict:
    """Check if a message matches any enabled auto-reply rule (keyword-based)."""
    msg_lower = message.lower()

    for rule in rules:
        if not rule.get("enabled", True):
            continue
        keywords = [k.strip().lower() for k in str(rule.get("keywords", "")).split(",")]
        if any(kw and kw in msg_lower for kw in keywords if kw):
            return {
                "matched":    True,
                "rule_id":    rule.get("id", ""),
                "rule_name":  rule.get("name", ""),
                "reply":      rule.get("reply", ""),
                "keywords":   rule.get("keywords", ""),
                "silent":     rule.get("reply", "") == "",   # empty reply = ignore/delete
            }
    return {"matched": False}


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE #100 — Inbox Simulator (demo mode / real API integration)
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_inbox_messages(
    platform: str = "TikTok",
    niche: str = "Fitness",
    count: int = 25,
) -> list:
    """
    Simulate realistic inbox messages for demo.
    In production, replace this with real platform API calls.
    """
    _MESSAGES_BY_NICHE = {
        "Fitness": [
            ("This workout routine changed my life! How many times per week should I do it?", "comment", "question"),
            ("Does this really help with weight loss?", "dm", "question"),
            ("I've been doing this for 2 weeks and already lost 4kg! 🔥🔥🔥", "comment", "compliment"),
            ("What's the best time of day to workout?", "comment", "question"),
            ("Can you make a beginner-friendly version?", "comment", "request"),
            ("This is way too hard for me 😭 Any easier alternative?", "comment", "complaint"),
            ("What protein powder do you personally recommend?", "dm", "question"),
            ("You're the best fitness creator on here! Never stop! 💪🙏", "comment", "compliment"),
            ("Is this safe for people with lower back pain?", "dm", "question"),
            ("How much does your coaching program cost?", "dm", "question"),
            ("Buy real followers cheap! DM me", "comment", "spam"),
            ("My doctor said I should lose weight. Where do I start?", "dm", "question"),
            ("This didn't work for me at all! Complete waste of time!", "comment", "complaint"),
            ("Can I do this while pregnant?", "dm", "question"),
            ("Can you ship to Cambodia?", "dm", "question"),
        ],
        "Tech": [
            ("What are the minimum specs to run this software?", "dm", "question"),
            ("Amazing tutorial! Just subscribed! 🙌🙌", "comment", "compliment"),
            ("This crashes on my MacBook, any fix?", "comment", "complaint"),
            ("How much does the premium version cost?", "dm", "question"),
            ("Can you make a tutorial for complete beginners?", "comment", "request"),
            ("Best tech channel I've found in years! Keep it up 🚀", "comment", "compliment"),
            ("Is there a free trial available?", "dm", "question"),
            ("This app completely crashed my phone, fix it NOW!", "comment", "complaint"),
            ("Do you offer a student discount?", "dm", "question"),
            ("What's the difference between the Basic and Pro plan?", "dm", "question"),
            ("This is so much better than the competitors!", "comment", "compliment"),
            ("I've been waiting for a refund for 2 weeks!", "dm", "complaint"),
        ],
        "Business": [
            ("How do I start a business with only $100?", "dm", "question"),
            ("This strategy literally doubled my income! Thank you so much 🙏🙏", "comment", "compliment"),
            ("Is this legal in Cambodia?", "dm", "question"),
            ("Can you do 1-on-1 coaching sessions?", "comment", "request"),
            ("Amazing content as always! 👏", "comment", "compliment"),
            ("This doesn't work for small businesses in developing countries", "comment", "complaint"),
            ("How long before I see results?", "dm", "question"),
            ("I tried your method and made $500 in one week! INSANE!", "comment", "compliment"),
            ("What's the best platform to sell digital products?", "comment", "question"),
            ("Do you have a course on dropshipping?", "dm", "question"),
        ],
        "Food": [
            ("What brand of flour do you use?", "comment", "question"),
            ("Made this last night and my family loved it! 😍❤️", "comment", "compliment"),
            ("Can I substitute the eggs with something vegan?", "dm", "question"),
            ("How long does this keep in the fridge?", "comment", "question"),
            ("Can you do more Khmer recipes?", "comment", "request"),
            ("I followed this exactly and it was terrible!", "comment", "complaint"),
            ("Where do I buy this ingredient in Cambodia?", "dm", "question"),
            ("You are the best food creator! Love all your videos 🍽️", "comment", "compliment"),
        ],
        "Fashion": [
            ("Where can I buy this outfit?", "comment", "question"),
            ("You look absolutely stunning! 😍🔥", "comment", "compliment"),
            ("Do you ship internationally?", "dm", "question"),
            ("What size are you wearing in this?", "comment", "question"),
            ("Can you do more affordable fashion options?", "comment", "request"),
            ("I ordered and it looks nothing like the photo!", "dm", "complaint"),
            ("What brand is that bag?", "comment", "question"),
            ("Love your style so much! Been following for 2 years! 💕", "comment", "compliment"),
            ("Do you have a discount code?", "dm", "question"),
        ],
    }

    # Default to Business if niche not found, or mix random messages
    niche_key = niche if niche in _MESSAGES_BY_NICHE else "Business"
    message_pool = _MESSAGES_BY_NICHE[niche_key]
    # Add some from other niches for variety
    for other_niche, msgs in _MESSAGES_BY_NICHE.items():
        if other_niche != niche_key:
            message_pool = message_pool + msgs[:2]

    _NAMES = [
        "@alex_user", "@sarah_m", "@john_doe3", "@mia_fan", "@user_kh",
        "@sokha_khmer", "@vanna_ph", "@kevin_sg", "@anna_th", "@mo_id",
        "@lisa_vn", "@david_us", "@cam_user99", "@biz_grinder", "@tech_kh",
        "@fitness_mom", "@daily_learner", "@growth_ph", "@real_user_2", "@loyal_fan",
    ]

    _CHANNELS = {
        "TikTok":    ["TikTok Comment", "TikTok DM"],
        "Instagram": ["Instagram Comment", "Instagram DM", "Instagram Story Reply"],
        "Facebook":  ["Facebook Comment", "Facebook Message", "Facebook Page Comment"],
        "YouTube":   ["YouTube Comment", "YouTube Community"],
        "Telegram":  ["Telegram Message", "Telegram Group"],
        "Twitter/X": ["Twitter/X Reply", "Twitter/X DM", "Twitter/X Mention"],
        "LinkedIn":  ["LinkedIn Message", "LinkedIn Comment"],
    }

    _SENTIMENT_MAP = {
        "question":   "Neutral",
        "compliment": "Positive",
        "complaint":  "Negative",
        "request":    "Neutral",
        "spam":       "Spam",
    }

    channels = _CHANNELS.get(platform, ["Message", "Comment"])
    messages  = []
    used      = set()

    for i in range(min(count, 50)):
        pool_idx = i % len(message_pool)
        text, msg_type, intent = message_pool[pool_idx]

        minutes_ago = random.randint(1, 2880)   # up to 2 days
        ts = (datetime.now() - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M")

        sender = random.choice(_NAMES)
        # ensure some variety
        while sender in used and len(used) < len(_NAMES):
            sender = random.choice(_NAMES)
        used.add(sender)

        sentiment = _SENTIMENT_MAP.get(intent, "Neutral")
        status    = random.choices(
            ["Unread", "Read", "Replied", "Auto-Replied"],
            weights=[45, 25, 20, 10], k=1
        )[0]
        priority  = "🔴 High" if intent == "complaint" else "🟡 Medium" if "?" in text else "🟢 Normal"

        messages.append({
            "id":        i + 1,
            "platform":  platform,
            "channel":   random.choice(channels),
            "from":      sender,
            "message":   text,
            "type":      msg_type,
            "intent":    intent,
            "sentiment": sentiment,
            "priority":  priority,
            "timestamp": ts,
            "status":    status,
        })

    messages.sort(key=lambda x: x["timestamp"], reverse=True)
    return messages
