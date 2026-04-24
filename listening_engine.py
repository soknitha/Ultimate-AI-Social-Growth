"""
GrowthOS AI — Social Listening & Competitor Intelligence Engine
================================================================
Features: Brand Monitoring, Competitor Analysis, Ad Intelligence
"""
import asyncio
import random
import json
import re

from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str) -> dict | list:
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def simulate_brand_listening(
    brand: str, platform: str = "All Platforms",
    period: str = "Last 7 days", niche: str = "General",
    language: str = "English"
) -> dict:
    """Generate a social listening report for brand mentions."""
    if not USE_AI or not LLM_CLIENT:
        total = random.randint(150, 4200)
        pos = int(total * random.uniform(0.55, 0.70))
        neg = int(total * random.uniform(0.10, 0.22))
        neu = total - pos - neg
        return {
            "summary": f"Found {total:,} mentions of '{brand}' in the {period}",
            "total_mentions": total, "positive": pos, "negative": neg, "neutral": neu,
            "sentiment_score": int(pos / total * 100),
            "trending_keywords": [brand, niche, "review", "recommend", "quality",
                                   "delivery", "support", "price", "worth it"],
            "top_platforms": ["Instagram", "Twitter/X", "TikTok", "Facebook", "YouTube"],
            "influencer_mentions": random.randint(2, 18),
            "viral_mentions": random.randint(0, 3),
            "urgent_alerts": (
                ["⚠️ 2 viral negative posts require response within 4h"]
                if neg > 40 else ["✅ No urgent issues detected"]
            ),
            "top_topics": ["Customer service", "Product quality", "Price value",
                           "Shipping speed", "User experience"],
            "competitors_mentioned": ["Competitor A", "Competitor B", "Competitor C"],
            "share_of_voice": f"{random.randint(15, 45)}%",
            "recommendations": [
                "Reply to all negative reviews within 4 hours to show responsiveness",
                "Amplify the top 3 positive influencer mentions with paid boost",
                "Address price-related comments with a value comparison post",
                "Create a response template for common complaint themes",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social media brand monitoring specialist. Language: {language}."},
            {"role": "user", "content": (
                f"Generate a social listening report for brand '{brand}' on {platform}, {period}. Niche: {niche}.\n"
                f"Return JSON only: {{\"summary\",\"total_mentions\":int,\"positive\":int,\"negative\":int,"
                f"\"neutral\":int,\"sentiment_score\":int,\"trending_keywords\":[],\"top_platforms\":[],"
                f"\"influencer_mentions\":int,\"viral_mentions\":int,\"urgent_alerts\":[],"
                f"\"top_topics\":[],\"competitors_mentioned\":[],\"share_of_voice\":\"str\","
                f"\"recommendations\":[]}}"
            )},
        ],
        temperature=0.5, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"summary": f"Report for {brand}", "total_mentions": 0,
                "positive": 0, "negative": 0, "neutral": 0,
                "sentiment_score": 50, "recommendations": []}


async def analyze_competitor_profile(
    competitor: str, platform: str = "Instagram",
    niche: str = "General", language: str = "English"
) -> dict:
    """Deep competitor profile analysis with content strategy and growth insights."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "overview": (
                f"{competitor} on {platform}: Est. {random.randint(10, 500)}K followers, "
                f"{random.uniform(2.5, 7.2):.1f}% engagement rate, "
                f"posts {random.randint(1, 3)}x/day"
            ),
            "content_strategy": (
                "80% educational + 15% promotional + 5% personal. "
                "Heavy use of Reels/Shorts. Strong Story engagement."
            ),
            "top_post_types": ["Tutorial videos", "Before/After", "Quick-tip carousels",
                               "Polls & Questions", "User-generated content"],
            "posting_schedule": "Mon/Wed/Fri 6–8 PM. Stories daily 8–9 AM.",
            "best_hashtags": [f"#{niche.lower()}tips", f"#{platform.lower()}growth",
                               "#contentcreator", f"#{niche.lower()}hack"],
            "weaknesses": ["No video testimonials", "Inconsistent Stories",
                           "Rarely replies to comments", "No DM engagement strategy"],
            "opportunities": [
                f"Target their audience with better quality {niche} content",
                "Offer video tutorials they lack",
                "Engage their comment sections with value",
                "Outperform with faster response times",
            ],
            "threat_level": random.choice(["Low", "Medium", "Medium", "High"]),
            "estimated_monthly_growth": f"+{random.randint(500, 5000):,} followers/month",
            "estimated_posting_frequency": f"{random.randint(5, 21)} posts/week",
            "top_content_niches": [niche, f"{niche} tips", f"{niche} for beginners"],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a competitive intelligence analyst for social media. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze competitor '{competitor}' on {platform} in the {niche} niche.\n"
                f"Return JSON only: {{\"overview\",\"content_strategy\",\"top_post_types\":[],"
                f"\"posting_schedule\",\"best_hashtags\":[],\"weaknesses\":[],\"opportunities\":[],"
                f"\"threat_level\",\"estimated_monthly_growth\",\"estimated_posting_frequency\","
                f"\"top_content_niches\":[]}}"
            )},
        ],
        temperature=0.5, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"overview": f"Analysis of {competitor}", "content_strategy": "",
                "top_post_types": [], "weaknesses": [], "opportunities": [], "threat_level": "Unknown"}


async def get_competitor_ad_intelligence(
    competitor: str, platform: str = "Facebook",
    niche: str = "General", language: str = "English"
) -> dict:
    """Analyze competitor advertising strategy and creative patterns."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "competitor": competitor, "platform": platform,
            "active_ads_estimate": f"{random.randint(3, 28)} active ads",
            "ad_formats": [
                f"Video ({random.randint(50, 70)}%)",
                f"Image carousel ({random.randint(20, 30)}%)",
                f"Single image ({random.randint(10, 20)}%)",
            ],
            "messaging_themes": ["Value proposition", "Social proof",
                                  "Urgency/scarcity", "Problem → Solution"],
            "cta_buttons": ["Shop Now", "Learn More", "Sign Up", "Get Offer"],
            "estimated_monthly_spend": f"${random.randint(1000, 15000):,} – ${random.randint(5000, 30000):,}",
            "targeting_clues": [
                "Retargeting website visitors (30 days)",
                "Lookalike audiences from customer list",
                f"Interest: {niche}",
                f"Age: {random.randint(18, 25)}–{random.randint(35, 55)}",
            ],
            "ad_copy_patterns": [
                "Uses emojis heavily in headlines",
                "Short punchy hooks (under 10 words)",
                "Numbers and percentages in titles",
                "Questions as ad hooks",
                "Testimonial quotes in body text",
            ],
            "creative_weaknesses": [
                "No video testimonials — opportunity to differentiate",
                "Generic CTAs — personalized CTAs convert 2x better",
                "No limited-time offers visible — urgency drives conversions",
            ],
            "counter_strategies": [
                "Use video testimonials to build trust",
                "Add countdown timers or limited offers",
                "Personalize CTAs to specific audience segments",
                "Test longer-form video vs their short clips",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a competitive ad intelligence expert. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze the advertising strategy of '{competitor}' on {platform}, niche: {niche}.\n"
                f"Return JSON only: {{\"competitor\",\"platform\",\"active_ads_estimate\","
                f"\"ad_formats\":[],\"messaging_themes\":[],\"cta_buttons\":[],"
                f"\"estimated_monthly_spend\",\"targeting_clues\":[],\"ad_copy_patterns\":[],"
                f"\"creative_weaknesses\":[],\"counter_strategies\":[]}}"
            )},
        ],
        temperature=0.6, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"competitor": competitor, "active_ads_estimate": "Unknown",
                "counter_strategies": [], "ad_copy_patterns": []}
