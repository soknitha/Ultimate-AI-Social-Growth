"""
GrowthOS AI — Content Engine
==============================
Feature #4  : AI Content Generator
Feature #7  : Auto Campaign System (content side)
Feature #14 : Cross-Platform Content Transformer
Feature #88 : Micro-Content Generator
Feature #81 : Lifecycle Content Engine
Feature #8  : AI Storytelling Builder
Feature #2  : Creative DNA Engine (advanced)
Feature #7  : Real-time Creative Editor AI (advanced)
Feature #29 : Cross-Language Growth Engine
"""
import json
import random
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL as OPENAI_MODEL, LLM_FAST_MODEL as OPENAI_FAST_MODEL, USE_AI as USE_REAL_AI


async def _gpt(prompt: str, system: str = "", fast: bool = False) -> str:
    if not _client:
        return ""
    try:
        model = OPENAI_FAST_MODEL if fast else OPENAI_MODEL
        resp = await _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or "You are a viral social media content expert."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.85,
            max_tokens=2000,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #4: Viral Hook Generator ────────────────────────────────────────
async def generate_viral_hook(topic: str, platform: str, language: str = "English") -> dict:
    """Generate 5 viral hooks for first 3 seconds of video."""
    if USE_REAL_AI:
        prompt = (
            f"Generate 5 ultra-viral video hooks for:\nTopic: {topic}\nPlatform: {platform}\n"
            f"Language: {language}\n\n"
            "Each hook must grab attention in the first 3 seconds.\n"
            "Return JSON: hooks(list of 5 strings), best_hook(str), hook_type(str), "
            "why_it_works(str)"
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    # Smart multilingual fallback
    hooks_en = [
        f"Nobody tells you this about {topic} (until now)...",
        f"I gained 10,000 followers using this ONE {topic} trick →",
        f"Stop doing {topic} wrong — here's what actually works:",
        f"This {topic} mistake is costing you thousands of followers",
        f"POV: You finally figured out {topic} on {platform} 🤯",
    ]
    hooks_kh = [
        f"មិនដែលមានអ្នកណាប្រាប់អ្នកអំពី {topic} នេះទេ...",
        f"ខ្ញុំបានទទួល Followers ១ម៉ឺននាក់ ដោយប្រើ {topic} trick នេះ →",
        f"បញ្ឈប់ការប្រើ {topic} ខុស — នេះជាវិធីដែលព្ជាក់ផ្ទាល់",
        f"កំហុស {topic} នេះបណ្តាល ឲ្យ Followers អ្នកធ្លាក់ 💀",
        f"POV: ពេលអ្នកដឹងការប្រើ {topic} ត្រូវវិធី 🤯",
    ]
    hooks = hooks_kh if language == "Khmer" else hooks_en
    return {
        "hooks": hooks,
        "best_hook": hooks[0],
        "hook_type": "Pattern Interrupt + Curiosity Gap",
        "why_it_works": "Opens with unexpected revelation — triggers dopamine curiosity loop",
        "delivery_tip": "Say with confident, slightly shocked facial expression. Cut to content immediately.",
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #4: Caption Generator ──────────────────────────────────────────
async def generate_caption(
    topic: str, platform: str, tone: str = "Viral & Catchy", language: str = "English",
) -> dict:
    """Generate optimized caption with CTA for any platform."""
    if USE_REAL_AI:
        prompt = (
            f"Write a high-converting social media caption:\n"
            f"Topic: {topic}\nPlatform: {platform}\nTone: {tone}\nLanguage: {language}\n\n"
            "Include: attention-grabbing opener, value points, emotional hook, strong CTA.\n"
            "Return JSON: caption(str), cta(str), emoji_usage(str), caption_length(str), "
            "engagement_prediction(str)"
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    if language == "Khmer":
        caption = (
            f"📌 {topic} — ដំណឹងសំខាន់ ❗\n\n"
            f"ការបង្រៀន {topic} ត្រឹមត្រូវ អាចជួយឲ្យ Engagement "
            f"របស់អ្នककើនឡើងរហូតដល់ ៣០០% ក្នុងពេលខ្លី! 🚀\n\n"
            f"✅ ចំណុចសំខាន់ #{1}: ផ្តើមដំបូង...\n"
            f"✅ ចំណុចសំខាន់ #{2}: បន្ទាប់មក...\n"
            f"✅ ចំណុចសំខាន់ #{3}: ចុងក្រោយ...\n\n"
            f"💡 Save Post នេះ — អ្នកនឹងត្រូវការវាពេលក្រោយ!"
        )
        cta = "💬 Comment 'YES' ប្រសិនបើអ្នកចង់ដឹងបន្ថែម!"
    else:
        caption = (
            f"🔥 {topic} — The game-changer nobody talks about.\n\n"
            f"Most people struggle with {topic} because they skip these steps:\n\n"
            f"✅ Step 1: Start with the fundamentals...\n"
            f"✅ Step 2: Layer in the advanced technique...\n"
            f"✅ Step 3: Scale what's working...\n\n"
            f"💡 Save this post — you'll need it later.\n"
            f"Follow for more {topic} insights every day 🎯"
        )
        cta = "💬 Comment 'READY' if you want the full guide!"

    return {
        "caption": caption,
        "cta": cta,
        "emoji_usage": "Strategic (3–5 per caption)",
        "caption_length": "Medium (150–300 chars ideal for most platforms)",
        "engagement_prediction": "High — CTA drives comments; save-worthy format",
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #4: Video Script Builder ────────────────────────────────────────
async def generate_video_script(
    topic: str, duration_seconds: int = 60,
    style: str = "Educational", language: str = "English",
) -> dict:
    """Generate full video script with timestamps."""
    if USE_REAL_AI:
        prompt = (
            f"Write a complete {duration_seconds}-second video script:\n"
            f"Topic: {topic}\nStyle: {style}\nLanguage: {language}\n\n"
            "Include timestamps, on-screen text suggestions, and B-roll notes.\n"
            "Return JSON: title(str), script(list of scene objects with "
            "time, action, dialogue, text_overlay, b_roll), cta_scene(dict), "
            "engagement_hooks(list)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    # Calculated scene breakdown
    intro_end    = 5
    body_end     = duration_seconds - 10
    cta_start    = duration_seconds - 10

    script = [
        {
            "time": f"0:00–0:{intro_end:02d}",
            "action": "Open with HOOK — close-up face, confident expression",
            "dialogue": f"Nobody talks about this {topic} secret — until now.",
            "text_overlay": f"THE {topic.upper()} SECRET 🤫",
            "b_roll": "Fast-cut montage of results/transformation",
        },
        {
            "time": f"0:{intro_end:02d}–0:{body_end // 3:02d}",
            "action": "State the problem clearly",
            "dialogue": f"Most people approach {topic} completely wrong. Here's why...",
            "text_overlay": "THE PROBLEM ❌",
            "b_roll": "Screen recording or text animation",
        },
        {
            "time": f"0:{body_end // 3:02d}–0:{body_end * 2 // 3:02d}",
            "action": "Deliver the core value — 3 steps",
            "dialogue": "Step 1... Step 2... Step 3...",
            "text_overlay": "STEP 1 → STEP 2 → STEP 3 ✅",
            "b_roll": "Show each step visually",
        },
        {
            "time": f"0:{body_end * 2 // 3:02d}–0:{cta_start:02d}",
            "action": "Show the result / transformation",
            "dialogue": "After applying this, the results were incredible...",
            "text_overlay": "THE RESULT 🚀",
            "b_roll": "Results screenshot or graph animation",
        },
        {
            "time": f"0:{cta_start:02d}–0:{duration_seconds:02d}",
            "action": "Strong CTA — look directly at camera",
            "dialogue": "Follow for more strategies like this. Save this video now.",
            "text_overlay": "FOLLOW + SAVE 🔔",
            "b_roll": "Brand outro / logo animation",
        },
    ]

    return {
        "title": f"How to Master {topic} in {duration_seconds // 60} Minute",
        "duration": f"{duration_seconds} seconds",
        "style": style,
        "language": language,
        "script": script,
        "cta_scene": script[-1],
        "engagement_hooks": [
            "Pattern interrupt opener (first 3 sec)",
            "Problem identification (builds tension)",
            "Step-by-step solution (builds trust)",
            "Result reveal (emotional payoff)",
            "Direct CTA (converts viewers to followers)",
        ],
        "production_tips": [
            "Use trending audio as background",
            "Add text overlays for silent viewers (80% watch silent)",
            "Keep cuts fast (1 new shot every 2–3 seconds)",
            "Maintain eye contact with camera for authority",
        ],
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #4: Hashtag Clustering ──────────────────────────────────────────
async def generate_hashtags(topic: str, niche: str, platform: str, count: int = 20) -> dict:
    """Generate optimized hashtag clusters for maximum reach."""
    if USE_REAL_AI:
        prompt = (
            f"Generate {count} optimized hashtags for:\nTopic: {topic}\nNiche: {niche}\nPlatform: {platform}\n"
            "Mix small (10K–100K), medium (100K–1M), and large (1M+) hashtags.\n"
            "Return JSON: small_hashtags(list), medium_hashtags(list), large_hashtags(list), "
            "niche_hashtags(list), trending_hashtags(list), recommended_combo(list of 20)"
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    base = topic.lower().replace(" ", "")
    niche_b = niche.lower().replace(" ", "")
    plat_b  = platform.lower().replace(" ", "")
    return {
        "small_hashtags":    [f"#{base}tips", f"#{base}guide", f"#{niche_b}creator", f"#{base}hack"],
        "medium_hashtags":   [f"#{base}", f"#{niche_b}growth", f"#{plat_b}tips", f"#{niche_b}content"],
        "large_hashtags":    ["#viral", "#trending", "#fyp", "#explore", "#foryou"],
        "niche_hashtags":    [f"#{niche_b}", f"#{niche_b}community", f"#{niche_b}life", f"#{niche_b}expert"],
        "trending_hashtags": ["#growthhacks", "#contentcreator", "#socialmedia", "#digitalmarketing"],
        "recommended_combo": [
            f"#{base}tips", f"#{base}guide", f"#{niche_b}creator", f"#{base}hack",
            f"#{base}", f"#{niche_b}growth", f"#{plat_b}tips", f"#{niche_b}content",
            "#viral", "#trending", "#fyp", "#explore",
            f"#{niche_b}", f"#{niche_b}community", "#growthhacks", "#contentcreator",
            f"#{base}strategy", f"#{niche_b}tips", "#socialmediagrowth", f"#{plat_b}growth",
        ],
        "hashtag_strategy": "40% niche-specific, 40% medium-competition, 20% broad trending",
        "optimal_count": {"TikTok": 5, "Instagram": 20, "Facebook": 10, "YouTube": 15}.get(platform, 15),
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #14: Cross-Platform Content Transformer ─────────────────────────
async def repurpose_content(original_content: str, source_platform: str, target_platforms: list) -> dict:
    """Transform one piece of content into multiple platform-optimized formats."""
    if USE_REAL_AI:
        prompt = (
            f"Repurpose this content from {source_platform} to other platforms:\n\n"
            f"Original: {original_content}\n\nTarget platforms: {', '.join(target_platforms)}\n\n"
            "Return JSON with a key per platform, each containing: "
            "format(str), adaptation(str), key_changes(list)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    adaptations = {}
    platform_formats = {
        "TikTok":    "15–60 sec vertical video with trending audio",
        "Instagram": "Reel or 10-slide carousel with cohesive visual theme",
        "YouTube":   "5–10 min long-form video with chapters + SEO title",
        "Facebook":  "2–3 min video or text post with discussion question",
        "Telegram":  "Structured text message with bold headlines and emoji",
        "X (Twitter)": "2–4 tweet thread with cliffhangers between tweets",
    }
    for plat in target_platforms:
        adaptations[plat] = {
            "format": platform_formats.get(plat, "Adapt content for platform norms"),
            "adaptation": f"Reformat '{original_content[:80]}...' for {plat} audience",
            "key_changes": [
                f"Adjust length for {plat} optimal engagement",
                f"Use {plat}-native features (e.g., polls, stickers, chapters)",
                "Re-hook opening since each platform has different scroll speed",
            ],
        }

    return {
        "source": source_platform,
        "original_snippet": original_content[:120] + "...",
        "adaptations": adaptations,
        "time_saved": f"~{len(target_platforms) * 45} minutes of manual work",
        "tip": "Post each platform version 2–4 hours apart for cross-platform momentum",
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #88: Micro-Content Generator ────────────────────────────────────
async def micro_content_generator(idea: str, platform: str) -> dict:
    """Break 1 idea into 20 pieces of micro-content."""
    if USE_REAL_AI:
        prompt = (
            f"Break this content idea into 20 micro-content pieces for {platform}:\n"
            f"Idea: {idea}\n\n"
            "Return JSON: micro_content_list(list of 20 objects with type, title, description)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass

    content_types = [
        "Viral Hook Video", "5-Tip Carousel", "Behind the Scenes",
        "Q&A Story", "Poll", "Quote Graphic", "Mini Tutorial",
        "Myth vs Fact", "Before/After", "Day in My Life",
        "Top 3 Mistakes", "Quick Win Tip", "Testimonial Story",
        "Product/Tool Demo", "Challenge", "Trend Reaction",
        "Educational Infographic", "Personal Story", "Trend Prediction", "Summary Recap",
    ]
    micro_list = [
        {
            "index": i + 1,
            "type": content_types[i],
            "title": f"{content_types[i]}: {idea[:40]}",
            "description": f"Create a {content_types[i].lower()} focusing on the most compelling angle of '{idea}'",
            "estimated_production": "15–30 min",
        }
        for i in range(20)
    ]

    return {
        "source_idea": idea,
        "platform": platform,
        "total_pieces": 20,
        "micro_content_list": micro_list,
        "posting_schedule": "1 piece/day = 20-day content calendar covered",
        "tip": "Start with Hook Video (#1) and Q&A Poll (#4) — fastest engagement starters",
        "generated_at": datetime.now().isoformat(),
    }


# ─── Feature #81: Lifecycle Content Engine ────────────────────────────────────
async def analyze_content_lifecycle(post_age_days: int, engagement_data: dict) -> dict:
    """Detect where content is in its lifecycle and suggest next action."""
    views = engagement_data.get("views", 0)
    likes = engagement_data.get("likes", 0)
    comments = engagement_data.get("comments", 0)
    shares = engagement_data.get("shares", 0)

    engagement = (likes + comments * 3 + shares * 5) / max(views, 1) * 100

    if post_age_days <= 3 and engagement > 5:
        stage = "🚀 Launch — HIGH MOMENTUM"
        action = "Boost immediately with paid promotion for maximum reach"
    elif post_age_days <= 7 and engagement > 3:
        stage = "📈 Growth — SCALING"
        action = "Repurpose into other formats while momentum continues"
    elif post_age_days <= 14 and engagement > 1.5:
        stage = "📊 Peak — OPTIMIZE"
        action = "Pin to profile, add to highlights, cross-post to other platforms"
    elif post_age_days <= 30:
        stage = "📉 Decline — REPURPOSE"
        action = "Refresh with new hook, update text, repost as 'throwback' with new angle"
    else:
        stage = "🔄 Archive — EVERGREEN CANDIDATE"
        action = "If still relevant, repurpose as long-form YouTube video or blog post"

    return {
        "post_age_days": post_age_days,
        "lifecycle_stage": stage,
        "engagement_score": f"{engagement:.2f}%",
        "recommended_action": action,
        "evergreen_potential": engagement > 2 and comments > 5,
        "repurpose_ideas": [
            "YouTube Shorts version",
            "Instagram Carousel with key points",
            "Telegram channel post",
            "Email newsletter snippet",
        ],
        "analyzed_at": datetime.now().isoformat(),
    }


# ─── Feature: Content Calendar Generator ─────────────────────────────────────
async def generate_content_calendar(
    niche: str, platform: str, days: int = 14, language: str = "English",
) -> dict:
    """Generate a complete content calendar for X days."""
    content_pillars = [
        "Educational / How-To",
        "Entertainment / Humor",
        "Inspiration / Motivation",
        "Behind the Scenes",
        "Product / Service Showcase",
        "User Generated Content",
        "Trending / Current Events",
    ]
    calendar = {}
    for d in range(1, days + 1):
        pillar = content_pillars[d % len(content_pillars)]
        post_date = datetime.now() + timedelta(days=d)
        calendar[f"Day {d} ({post_date.strftime('%A, %b %d')})"] = {
            "content_pillar": pillar,
            "suggested_topic": f"{pillar} content about {niche}",
            "format": random.choice(["Short Video", "Carousel", "Story Poll", "Live Stream"]),
            "posting_time": random.choice(["7:00 AM", "12:00 PM", "7:30 PM", "9:00 PM"]),
            "status": "Scheduled",
        }

    return {
        "niche": niche,
        "platform": platform,
        "calendar_days": days,
        "language": language,
        "calendar": calendar,
        "posting_frequency": "1 post/day minimum",
        "variety_score": "High — 7 content pillars rotating",
        "generated_at": datetime.now().isoformat(),
    }
