"""
GrowthOS AI — Viral Engine
===========================
Features: Viral Score Predictor, Influencer Finder, Hashtag Research Engine, A/B Testing
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


async def predict_viral_score(
    content: str, platform: str = "TikTok", post_type: str = "Video",
    followers: int = 10000, niche: str = "General", language: str = "English"
) -> dict:
    """Predict virality score (0-100) with factor breakdown and improvement tips."""
    if not USE_AI or not LLM_CLIENT:
        base = min(98, (len(content) % 38) + 48 + random.randint(0, 18))
        return {
            "score": base,
            "grade": "A" if base >= 80 else "B" if base >= 60 else "C" if base >= 40 else "D",
            "verdict": ("🔥 High viral potential" if base >= 75
                        else "⚡ Moderate potential" if base >= 55 else "⚠️ Needs improvement"),
            "breakdown": {
                "Hook Strength": min(100, base + 5),
                "Emotional Trigger": min(100, base - 4),
                "Shareability": min(100, base + 8),
                "Trend Alignment": min(100, base),
                "Hashtag Power": min(100, base + 3),
                "CTA Effectiveness": min(100, base - 6),
            },
            "improvements": [
                f"Open with a bold question or shocking stat in the first 3 seconds",
                f"Add an emotional trigger — surprise, inspiration, or humor",
                f"Include 1 trending {platform} sound or challenge reference",
                "End with a strong CTA: 'Save this' / 'Share with someone who needs it'",
            ],
            "best_post_time": "Tue–Thu, 6–9 PM local time",
            "estimated_reach": f"{int(followers * (base / 100) * 15):,}",
        }
    system = (
        f"You are an elite viral content analyst specializing in {platform}. Language for output: {language}."
    )
    prompt = (
        f"Analyze this {platform} {post_type} content for viral potential.\n"
        f"Niche: {niche} | Followers: {followers:,}\n\nContent:\n{content[:1000]}\n\n"
        f"Return ONLY a JSON object:\n"
        f'{{"score":int,"grade":"A/B/C/D","verdict":"one line",'
        f'"breakdown":{{"Hook Strength":int,"Emotional Trigger":int,"Shareability":int,'
        f'"Trend Alignment":int,"Hashtag Power":int,"CTA Effectiveness":int}},'
        f'"improvements":["4 specific tips"],'
        f'"best_post_time":"string","estimated_reach":"string"}}'
    )
    try:
        resp = await LLM_CLIENT.chat.completions.create(
            model=LLM_FAST_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=600,
        )
        return _parse_json(resp.choices[0].message.content)
    except Exception as e:
        return {"score": 65, "grade": "B", "verdict": "AI analysis unavailable",
                "breakdown": {}, "improvements": [str(e)],
                "best_post_time": "6–9 PM", "estimated_reach": "10,000+"}


async def find_influencers(
    niche: str, platform: str = "Instagram", follower_range: str = "10K–100K",
    country: str = "Global", language: str = "English"
) -> dict:
    """Find relevant influencers with AI-generated realistic profiles."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "influencers": [
                {
                    "username": f"@{niche.lower().replace(' ', '_')}_creator{i}",
                    "platform": platform,
                    "followers": f"{random.randint(10, 999)}K",
                    "engagement_rate": f"{random.uniform(2.1, 8.5):.1f}%",
                    "niche": niche, "country": country,
                    "fake_follower_risk": random.choice(["Low", "Low", "Medium"]),
                    "contact": f"DM or email in bio",
                    "estimated_rate": f"${random.randint(50, 2500)}/post",
                    "content_quality": random.choice(["High", "High", "Medium"]),
                }
                for i in range(1, 9)
            ],
            "total_found": random.randint(200, 1500),
            "avg_engagement": f"{random.uniform(3.5, 6.2):.1f}%",
            "recommendation": (
                f"Focus on 5–8 micro-influencers (10K–50K) in {niche} for best ROI. "
                f"Micro-influencers have 60% higher engagement than macro on {platform}."
            ),
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are an influencer marketing expert. Language: {language}."},
            {"role": "user", "content": (
                f"Generate 8 realistic {platform} influencer profiles for {niche} niche, "
                f"follower range {follower_range}, country: {country}.\n"
                f"Return JSON only: {{\"influencers\":[{{\"username\",\"platform\",\"followers\","
                f"\"engagement_rate\",\"niche\",\"country\",\"fake_follower_risk\","
                f"\"contact\",\"estimated_rate\",\"content_quality\"}}],"
                f"\"total_found\":int,\"avg_engagement\":\"str\",\"recommendation\":\"str\"}}"
            )},
        ],
        temperature=0.7, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"influencers": [], "total_found": 0, "avg_engagement": "N/A",
                "recommendation": resp.choices[0].message.content[:300]}


async def research_hashtags(
    niche: str, platform: str = "Instagram", goal: str = "Reach",
    language: str = "English"
) -> dict:
    """Research best hashtags with difficulty scores and banned hashtag detection."""
    if not USE_AI or not LLM_CLIENT:
        cats = [("mega", 5_000_000), ("large", 800_000), ("medium", 200_000),
                ("small", 40_000), ("niche", 5_000)]
        hashtags = []
        for i in range(20):
            cat, posts = cats[i % 5]
            hashtags.append({
                "hashtag": f"#{niche.lower().replace(' ', '')}{['tips', 'life', 'growth', 'daily', 'pro'][i % 5]}{'' if i < 5 else i}",
                "posts": f"{posts // 1000}K", "difficulty": cat,
                "banned": False, "avg_likes": f"{random.randint(200, 8000):,}",
                "recommendation": "Use" if cat in ("medium", "small", "niche") else "Mix sparingly",
            })
        return {
            "hashtags": hashtags,
            "banned_found": ["#followforfollow", "#f4f", "#likeforlike"],
            "strategy": (
                f"Use 3 large + 7 medium + 7 small + 3 niche hashtags on {platform}. "
                f"Rotate sets every 3–5 posts to avoid shadow-ban."
            ),
            "best_set": [h["hashtag"] for h in hashtags if h["difficulty"] in ("medium", "small", "niche")][:12],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a hashtag strategy expert for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Research 20 hashtags for {niche} niche on {platform}, goal: {goal}.\n"
                f"Return JSON only: {{\"hashtags\":[{{\"hashtag\",\"posts\","
                f"\"difficulty\":\"mega|large|medium|small|niche\","
                f"\"banned\":bool,\"avg_likes\",\"recommendation\"}}],"
                f"\"banned_found\":[],\"strategy\":\"str\",\"best_set\":[]}}"
            )},
        ],
        temperature=0.4, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"hashtags": [], "banned_found": [], "strategy": "AI unavailable", "best_set": []}


async def generate_ab_variants(
    content: str, platform: str = "Instagram",
    objective: str = "Engagement", language: str = "English"
) -> dict:
    """Generate 3 A/B test variants with predicted performance winner."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "variant_a": {
                "label": "Variant A — Original (Control)", "content": content[:300],
                "hook_type": "Direct", "predicted_ctr": "2.1%", "predicted_engagement": "4.3%",
            },
            "variant_b": {
                "label": "Variant B — Curiosity Hook",
                "content": f"🔥 Wait... THIS changed everything about {platform}...\n\n{content[:200]}\n\n👇 Save this for later!",
                "hook_type": "Curiosity Gap", "predicted_ctr": "3.8%", "predicted_engagement": "6.2%",
            },
            "variant_c": {
                "label": "Variant C — Social Proof",
                "content": f"✅ {random.randint(2000, 50000):,} people loved this:\n\n{content[:200]}\n\n🔁 Share if this helped!",
                "hook_type": "Social Proof", "predicted_ctr": "3.3%", "predicted_engagement": "5.7%",
            },
            "predicted_winner": "Variant B",
            "reasoning": f"Curiosity-gap hooks average 80% higher CTR on {platform} vs direct openers.",
            "test_duration": "3–5 days",
            "minimum_sample": "1,000 impressions per variant",
            "ab_tips": [
                "Change only ONE element at a time for clean results",
                "Use same posting time for all variants",
                "Let the test run minimum 72h before declaring winner",
                "Scale winner budget 2x once CTR difference > 30%",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are an A/B testing expert for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Create 3 A/B test variants of this content. Platform: {platform}, Objective: {objective}.\n\n"
                f"Original:\n{content[:600]}\n\n"
                f"Return JSON only: {{\"variant_a\":{{\"label\",\"content\",\"hook_type\","
                f"\"predicted_ctr\",\"predicted_engagement\"}},"
                f"\"variant_b\":{{...}},\"variant_c\":{{...}},"
                f"\"predicted_winner\":\"str\",\"reasoning\":\"str\","
                f"\"test_duration\":\"str\",\"minimum_sample\":\"str\",\"ab_tips\":[]}}"
            )},
        ],
        temperature=0.8, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"variant_a": {}, "variant_b": {}, "variant_c": {},
                "predicted_winner": "B", "reasoning": "AI unavailable", "ab_tips": []}
