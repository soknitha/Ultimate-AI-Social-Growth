"""
GrowthOS AI — Business Intelligence Engine
============================================
Features: Crisis Manager, Growth Forecasting, Brand Voice AI,
          YouTube SEO Optimizer, Profile Optimizer, Report Generator
"""
import asyncio
import math
import random
import json
import re

from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str) -> dict | list:
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def detect_crisis(
    comments_text: str, brand: str = "", platform: str = "General",
    language: str = "English"
) -> dict:
    """Detect crisis signals from comments/mentions and assess severity."""
    if not USE_AI or not LLM_CLIENT:
        crisis_words = ["scam", "fraud", "lawsuit", "terrible", "hate", "worst",
                        "disgusting", "avoid", "warning", "fake", "refund now", "liar"]
        text_lower = comments_text.lower()
        score = sum(8 for w in crisis_words if w in text_lower)
        score = min(score, 100)
        level = ("Critical" if score >= 40 else "High" if score >= 25
                 else "Medium" if score >= 10 else "Low")
        return {
            "crisis_level": level,
            "crisis_score": score,
            "detected_issues": (
                [f"{len([w for w in crisis_words if w in text_lower])} negative signal(s) detected"]
                if score > 0 else ["✅ No crisis signals detected"]
            ),
            "affected_platforms": [platform],
            "recommended_actions": [
                "✅ Do NOT delete comments — acknowledge and respond",
                "✅ Reply to every negative comment within 2–4 hours",
                "✅ Pause all promotional scheduled posts immediately" if level in ("Critical", "High") else "⚠️ Monitor closely for 24h",
                "✅ Prepare a public statement if score > 40",
                "✅ Escalate to senior team if score > 60",
            ],
            "response_urgency": ("2 hours" if level == "Critical"
                                 else "4 hours" if level == "High" else "24 hours"),
            "pause_scheduled_posts": level in ("Critical", "High"),
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a PR crisis detection specialist. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze these comments/mentions for brand '{brand}' on {platform}:\n\n"
                f"{comments_text[:1200]}\n\n"
                f"Return JSON only: {{\"crisis_level\":\"None|Low|Medium|High|Critical\","
                f"\"crisis_score\":int,\"detected_issues\":[],\"affected_platforms\":[],"
                f"\"recommended_actions\":[],\"response_urgency\":\"str\","
                f"\"pause_scheduled_posts\":bool}}"
            )},
        ],
        temperature=0.2, max_tokens=500,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"crisis_level": "Unknown", "crisis_score": 0, "detected_issues": [],
                "recommended_actions": [], "response_urgency": "24 hours",
                "pause_scheduled_posts": False}


async def generate_crisis_response(
    brand: str, crisis_description: str, tone: str = "Empathetic & Professional",
    platform: str = "General", language: str = "English"
) -> dict:
    """Generate complete crisis response kit for multiple channels."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "public_comment_response": (
                f"We at {brand} take this matter seriously and sincerely apologize. "
                f"We are investigating immediately and will provide a full update within 24 hours. "
                f"Our customers are our #1 priority. Thank you for bringing this to our attention. 🙏"
            ),
            "story_response": f"We hear you. 🙏 We're on it. Full update in 24h. — Team {brand}",
            "dm_response": (
                f"Hi, thank you for reaching out. We're deeply sorry about your experience. "
                f"Please DM us your order/account details and we'll resolve this immediately — "
                f"full refund or replacement, no questions asked."
            ),
            "press_statement": (
                f"{brand} acknowledges the recent concerns raised by our community. "
                f"We are conducting a thorough investigation with full transparency. "
                f"A detailed update will be shared within 48 hours."
            ),
            "what_not_to_say": [
                "No comment", "You misunderstood us", "It's not our fault",
                "Other brands do this too", "We disagree with your assessment",
            ],
            "action_checklist": [
                "✅ Post acknowledgment within 2 hours",
                "✅ Reply personally to every negative comment",
                "✅ Pause all promotional/scheduled posts immediately",
                "✅ Brief customer service team on standard responses",
                "✅ Document all complaints for internal review",
                "✅ Issue follow-up update in 24–48 hours",
                "✅ Monitor for 72h post-response for sentiment shift",
            ],
            "recovery_plan": (
                "Week 1: Transparency + fixes. Week 2: Customer success stories. "
                "Week 3: Return to normal content with proof of improvement."
            ),
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a PR crisis communications expert. Tone: {tone}. Language: {language}."
            )},
            {"role": "user", "content": (
                f"Brand: {brand}\nCrisis: {crisis_description}\nPlatform: {platform}\n\n"
                f"Return JSON only: {{\"public_comment_response\",\"story_response\","
                f"\"dm_response\",\"press_statement\",\"what_not_to_say\":[],"
                f"\"action_checklist\":[],\"recovery_plan\"}}"
            )},
        ],
        temperature=0.3, max_tokens=1000,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"public_comment_response": resp.choices[0].message.content[:400],
                "action_checklist": [], "what_not_to_say": []}


def forecast_growth_ml(
    current_followers: int, platform: str = "Instagram",
    monthly_growth_rate: float = 5.0, posting_freq: int = 7,
    engagement_rate: float = 3.5, months: int = 6
) -> dict:
    """Mathematical ML-style growth forecasting with 3 scenarios (no LLM needed)."""
    benchmarks = {
        "Instagram": {"avg_monthly_growth": "3–8%", "good_engagement": ">3%"},
        "TikTok":    {"avg_monthly_growth": "10–25%", "good_engagement": ">5%"},
        "YouTube":   {"avg_monthly_growth": "5–15%",  "good_engagement": ">4%"},
        "LinkedIn":  {"avg_monthly_growth": "2–5%",   "good_engagement": ">2%"},
        "Facebook":  {"avg_monthly_growth": "1–3%",   "good_engagement": ">1%"},
        "Twitter/X": {"avg_monthly_growth": "2–6%",   "good_engagement": ">1%"},
    }
    scenarios = {}
    for label, mult in [("Conservative", 0.65), ("Realistic", 1.0), ("Optimistic", 1.55)]:
        rate = (monthly_growth_rate / 100) * mult
        projections = []
        f = current_followers
        for m in range(1, months + 1):
            f = int(f * (1 + rate))
            projections.append({
                "month": m,
                "followers": f,
                "net_gain": int(f - current_followers),
                "monthly_gain": int(f - (projections[-1]["followers"] if projections else current_followers)),
            })
        scenarios[label] = projections

    realistic_final = scenarios["Realistic"][-1]["followers"]

    # Next milestone calculation
    milestones = {}
    for ms in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
        if ms > current_followers:
            rate = monthly_growth_rate / 100
            if rate > 0:
                months_to = math.log(ms / max(current_followers, 1)) / math.log(1 + rate)
                milestones[f"{ms:,}"] = f"{months_to:.1f} months"
            break

    return {
        "current_followers": current_followers,
        "platform": platform,
        "input_monthly_growth_rate": f"{monthly_growth_rate:.1f}%",
        "forecast_months": months,
        "scenarios": scenarios,
        "in_{}_months_realistic".format(months): realistic_final,
        "platform_benchmark": benchmarks.get(platform, {"avg_monthly_growth": "3–8%", "good_engagement": ">3%"}),
        "next_milestone": milestones,
        "growth_tips": [
            f"{'✅' if 5 <= posting_freq <= 14 else '⚠️'} Posting {posting_freq}x/week — {'ideal range' if 5 <= posting_freq <= 14 else 'consider 5–14x/week for best growth'}",
            f"{'✅' if engagement_rate >= 3 else '⚠️'} Engagement {engagement_rate:.1f}% — {'above average' if engagement_rate >= 3 else 'below avg — focus on interactive posts (polls, Q&A, saves)'}",
            "Reels/Shorts boost reach 3–5x vs static posts — prioritize video",
            "Collaborate with 2–3 creators/month for audience sharing",
            "Reply to every comment in first 60 minutes — signals algorithm to boost post",
        ],
    }


async def analyze_brand_voice(
    samples: str, brand_name: str = "", language: str = "English"
) -> dict:
    """Analyze and codify brand voice from content samples."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "brand_voice_profile": "Friendly, Professional, Empowering",
            "tone_attributes": ["Conversational", "Positive", "Expert", "Relatable", "Motivational"],
            "vocabulary_style": "Simple everyday language, action verbs, inclusive pronouns (we/you/us)",
            "sentence_style": "Short punchy sentences (5–12 words). Occasional longer ones for depth.",
            "emoji_usage": "Moderate (2–4 per post), purposeful — never decorative",
            "punctuation_style": "Exclamation marks for enthusiasm. Ellipses for curiosity…",
            "taboo_words": ["cheap", "problem", "difficult", "never", "can't", "impossible"],
            "preferred_words": ["discover", "achieve", "transform", "effortless", "unlock",
                                 "community", "growth", "proven", "simple"],
            "writing_rules": [
                "Always start with a hook — question, stat, or bold statement",
                "Use 'you' 3x more than 'we'",
                "End every post with a question or action CTA",
                "Keep paragraphs under 3 lines on mobile",
                "Numbers get attention — use them (3 tips, 5x faster, 10K results)",
            ],
            "brand_personality": "Like a smart, encouraging mentor — not a salesperson",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a brand voice analyst and copywriting expert. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze the brand voice from these {brand_name} content samples:\n\n"
                f"{samples[:1400]}\n\n"
                f"Return JSON only: {{\"brand_voice_profile\",\"tone_attributes\":[],"
                f"\"vocabulary_style\",\"sentence_style\",\"emoji_usage\","
                f"\"punctuation_style\",\"taboo_words\":[],\"preferred_words\":[],"
                f"\"writing_rules\":[],\"brand_personality\"}}"
            )},
        ],
        temperature=0.3, max_tokens=700,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"brand_voice_profile": "Analysis unavailable", "writing_rules": []}


async def optimize_youtube_seo(
    title: str, description: str, tags: str,
    target_keyword: str, niche: str = "General",
    language: str = "English"
) -> dict:
    """Optimize YouTube video metadata for maximum search visibility."""
    year = 2026
    if not USE_AI or not LLM_CLIENT:
        kw = target_keyword.strip()
        return {
            "optimized_title": f"{kw}: {title} ({year})" if kw else f"{title} | Complete Guide {year}",
            "optimized_description": (
                f"{description[:200].strip()}\n\n"
                f"🔔 SUBSCRIBE for more {niche} content!\n\n"
                f"📌 CHAPTERS:\n0:00 Introduction\n1:30 Main content\n5:00 Key tips\n8:00 Summary\n\n"
                f"🔗 Links:\n\n"
                f"🏷 Tags: {kw}, {niche}, tutorial, guide, how to\n\n"
                f"#{kw.replace(' ', '')} #{niche.replace(' ', '')} #youtube"
            ),
            "optimized_tags": [
                kw, f"{kw} tutorial", f"{kw} guide {year}", f"how to {kw}",
                f"best {niche}", f"{niche} tips", "tutorial", "beginners",
                f"{niche} for beginners", f"{kw} {niche}",
            ],
            "scores": {"title": 78, "description": 65, "tags": 72, "overall": 72},
            "improvements": [
                f"Put '{kw}' in the first 3 words of the title",
                f"Add year {year} to title for freshness signal",
                "Add timestamps/chapters in first 200 chars of description",
                "Use exact match keyword naturally in first 2 lines",
                "Add 15–20 relevant tags — mix broad + specific",
            ],
            "thumbnail_tips": (
                "Bright colors + readable text (max 5 words) + "
                "human face with strong emotion + high contrast background"
            ),
            "estimated_ctr_boost": "+25–45% with optimized title+thumbnail",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a YouTube SEO expert. Language: {language}."},
            {"role": "user", "content": (
                f"Optimize YouTube metadata for keyword: '{target_keyword}'\n"
                f"Niche: {niche}\nTitle: {title}\nDescription: {description[:400]}\nTags: {tags[:200]}\n\n"
                f"Return JSON only: {{\"optimized_title\",\"optimized_description\","
                f"\"optimized_tags\":[],\"scores\":{{\"title\":int,\"description\":int,"
                f"\"tags\":int,\"overall\":int}},\"improvements\":[],"
                f"\"thumbnail_tips\",\"estimated_ctr_boost\"}}"
            )},
        ],
        temperature=0.4, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"optimized_title": title, "optimized_description": description,
                "improvements": [], "scores": {}}


async def optimize_profile(
    platform: str, current_bio: str, niche: str,
    goals: str, username: str = "", language: str = "English"
) -> dict:
    """AI-powered social media profile optimization."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "bio_score": 58, "bio_grade": "C+",
            "optimized_bio": (
                f"🏆 {niche} Expert  •  "
                f"{goals[:50].rstrip('.')}  •  "
                f"📩 DM for collabs  •  👇 Free guide below"
            ),
            "username_tips": (
                "Include a niche keyword if available. Keep under 20 chars. "
                "No dots/underscores if avoidable. Make it memorable."
            ),
            "profile_photo_tips": (
                "Professional headshot or brand logo. Bright high-contrast background. "
                "No text overlay. Smile or confident expression. Fill the frame."
            ),
            "link_in_bio_strategy": (
                "Use Linktree or Beacons. Link to: "
                "Website → Lead magnet / free resource → Latest post → DM link"
            ),
            "highlights_strategy": ["FAQ", "Testimonials", "Products/Services",
                                     "Behind the Scenes", "Tutorials", "Reviews"],
            "improvements": [
                "Add a clear value proposition in line 1 (who you help + how)",
                "Include a CTA: DM / Click link / Subscribe",
                "Add 1–2 relevant emojis as visual anchors",
                "Mention your #1 result or achievement with a number",
                "Add niche keywords for discoverability",
            ],
            "keywords_to_add": [niche, goals[:25], f"{platform} creator"],
            "bio_formula": "Who you help + How you help + Proof/Result + CTA",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social media profile optimization expert. Language: {language}."},
            {"role": "user", "content": (
                f"Optimize this {platform} profile:\nUsername: {username or 'N/A'}\n"
                f"Current bio: {current_bio}\nNiche: {niche}\nGoals: {goals}\n\n"
                f"Return JSON only: {{\"bio_score\":int,\"bio_grade\":\"str\","
                f"\"optimized_bio\",\"username_tips\",\"profile_photo_tips\","
                f"\"link_in_bio_strategy\",\"highlights_strategy\":[],"
                f"\"improvements\":[],\"keywords_to_add\":[],\"bio_formula\"}}"
            )},
        ],
        temperature=0.5, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"bio_score": 50, "bio_grade": "C", "optimized_bio": current_bio,
                "improvements": [], "bio_formula": ""}
