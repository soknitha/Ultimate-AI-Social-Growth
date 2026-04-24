"""
GrowthOS AI — Brand Authority Engine
=======================================
P7: Personal Brand Scorecard, Content Audit, Competitor Content Gap,
    Audience Persona Builder, Algorithm Intelligence Tracker
"""
import json, re
from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str):
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def audit_personal_brand(
    platform: str, niche: str, bio: str,
    posting_freq: str = "3x/week",
    engagement_rate: float = 2.5,
    follower_count: int = 5000,
    has_website: bool = False,
    has_email_list: bool = False,
    language: str = "English",
) -> dict:
    """Score a personal brand across 7 dimensions with actionable roadmap."""
    if not USE_AI or not LLM_CLIENT:
        bio_score = min(25, len(bio.split()) * 1.2)
        eng_score = min(25, engagement_rate * 4)
        freq_scores = {"daily": 20, "2x/day": 20, "5x/week": 17, "3x/week": 14, "1x/week": 7, "monthly": 2}
        freq_score = freq_scores.get(posting_freq.lower(), 10)
        follower_score = min(10, follower_count / 10000 * 10)
        bonus = (5 if has_website else 0) + (5 if has_email_list else 0)
        total = round(bio_score + eng_score + freq_score + follower_score + bonus, 1)
        grade = "A+" if total >= 90 else "A" if total >= 80 else "B+" if total >= 75 else "B" if total >= 65 else "C+" if total >= 55 else "C" if total >= 45 else "D"
        return {
            "overall_score": total,
            "overall_grade": grade,
            "dimension_scores": {
                "Profile Optimization": round(bio_score, 1),
                "Engagement Quality": round(eng_score, 1),
                "Posting Consistency": freq_score,
                "Audience Size": round(follower_score, 1),
                "Platform Diversification": bonus,
                "Brand Clarity": 12 if niche else 5,
                "Monetization Readiness": 8 if has_website and has_email_list else 4,
            },
            "strengths": [
                s for s, c in [
                    (f"Strong engagement rate ({engagement_rate}%)", engagement_rate >= 3),
                    (f"Consistent posting frequency ({posting_freq})", "week" in posting_freq),
                    ("Clear niche positioning", bool(niche)),
                    ("Professional website presence", has_website),
                    ("Email list asset (long-term leverage)", has_email_list),
                ] if c
            ] or ["Building foundation — keep going!"],
            "weaknesses": [
                w for w, c in [
                    ("Low engagement rate — prioritize community interaction", engagement_rate < 2),
                    ("Inconsistent posting hurts algorithm reach", "month" in posting_freq),
                    ("No website = no owned audience", not has_website),
                    ("No email list = no safety net if platform changes", not has_email_list),
                    ("Optimize bio with keywords + clear value prop", len(bio.split()) < 10),
                ] if c
            ] or ["Minor optimizations available — see roadmap"],
            "improvement_roadmap": [
                "Week 1–2: Rewrite bio with keyword + clear transformation promise",
                "Week 3–4: Increase posting to minimum 3x/week at peak times",
                "Month 2: Add link-in-bio website (use Linktree or own domain)",
                "Month 2–3: Launch email list with freebie lead magnet",
                "Month 3–6: Build 3 content pillars for brand clarity",
                "Month 6+: Create signature content series + collaboration outreach",
            ],
            "priority_action": "Optimize bio with a keyword + clear result/promise in first line — this affects profile visits, search discovery, and first impressions.",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a personal brand strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Audit this personal brand on {platform}:\n"
                f"Niche: {niche}, Bio: {bio}, Posting: {posting_freq}, "
                f"Engagement: {engagement_rate}%, Followers: {follower_count:,}, "
                f"Has Website: {has_website}, Has Email List: {has_email_list}\n\n"
                f"Return JSON: {{\"overall_score\":float,\"overall_grade\","
                f"\"dimension_scores\":{{}},\"strengths\":[],\"weaknesses\":[],"
                f"\"improvement_roadmap\":[],\"priority_action\"}}"
            )},
        ],
        temperature=0.5, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"overall_score": 0, "overall_grade": "N/A", "dimension_scores": {}}


async def audit_content_performance(
    posts_summary: str, platform: str = "Instagram",
    niche: str = "General", language: str = "English"
) -> dict:
    """Analyze content patterns to identify what to replicate vs kill."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "analysis_platform": platform,
            "top_performing_patterns": [
                "How-to/tutorial posts with numbered steps",
                "Personal story + lesson + takeaway structure",
                "Contrarian takes ('Stop doing X')",
                "Before/after transformations",
                "Data-backed insights ('X% of people don't know…')",
            ],
            "underperforming_patterns": [
                "Generic motivational quotes without personal angle",
                "Promotional posts without value upfront",
                "Long paragraphs without white space or bullets",
                "Posts without a clear CTA",
                "Reposts without original commentary",
            ],
            "content_to_kill": [
                "Motivational quotes with no personal story",
                "Stock image posts",
                "Self-promotional posts (>1 per 10 posts max)",
            ],
            "content_to_replicate": [
                "Step-by-step tutorials in your niche",
                "Personal failure/learning stories",
                "Controversial takes on common {niche} advice",
            ],
            "content_mix_recommendation": {
                "Educational (How-to, Tips)": "40%",
                "Personal Story / Behind-the-Scenes": "25%",
                "Entertaining / Relatable": "20%",
                "Promotional / CTA": "10%",
                "Community / UGC / Re-share": "5%",
            },
            "insight": f"Based on {platform} algorithm patterns for {niche} — educational + personal content gets 2–3x organic reach vs pure promotional.",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a content performance analyst for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze this content performance data for a {niche} creator on {platform}:\n{posts_summary}\n\n"
                f"Return JSON: {{\"analysis_platform\",\"top_performing_patterns\":[],\"underperforming_patterns\":[],"
                f"\"content_to_kill\":[],\"content_to_replicate\":[],\"content_mix_recommendation\":{{}},\"insight\"}}"
            )},
        ],
        temperature=0.5, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"top_performing_patterns": [], "content_to_kill": [], "content_mix_recommendation": {}}


async def find_competitor_content_gap(
    your_niche: str, competitor_info: str,
    platform: str = "Instagram", language: str = "English"
) -> dict:
    """Identify untapped content gaps competitors are missing."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "platform": platform,
            "niche": your_niche,
            "gap_opportunities": [
                {
                    "topic": f"Beginner mistakes in {your_niche}",
                    "why_it_works": "High search intent, low competition in direct how-to format",
                    "difficulty": "Easy",
                    "potential_reach": "High",
                    "content_angle": "First-person mistake story → solution reveal",
                    "urgency": "Evergreen",
                },
                {
                    "topic": f"Advanced {your_niche} strategies (not basic tips)",
                    "why_it_works": "Most creators only cover beginner content — advanced gap is wide",
                    "difficulty": "Medium",
                    "potential_reach": "Medium-High",
                    "content_angle": "Series: 'Level Up Your {niche}' for established creators",
                    "urgency": "Evergreen",
                },
                {
                    "topic": f"{your_niche} tools & resources roundup",
                    "why_it_works": "High save rate + SEO value + can monetize with affiliate",
                    "difficulty": "Easy",
                    "potential_reach": "Medium",
                    "content_angle": "'My exact {niche} toolkit' with pros/cons",
                    "urgency": "Update quarterly",
                },
                {
                    "topic": f"Controversial/contrarian take on {your_niche} advice",
                    "why_it_works": "Debate = comments = algorithm boost",
                    "difficulty": "Medium",
                    "potential_reach": "Very High (viral potential)",
                    "content_angle": "'Unpopular opinion: [Common advice] is WRONG' → explain why",
                    "urgency": "Do within 1 week",
                },
                {
                    "topic": f"{your_niche} trends for [current year]",
                    "why_it_works": "Search spike at year-start + journalists quote it + backlink potential",
                    "difficulty": "Medium",
                    "potential_reach": "Very High",
                    "content_angle": "Annual 'State of {niche}' post — be the source",
                    "urgency": "Time-sensitive",
                },
            ],
            "quick_wins": [
                f"Post a '{your_niche} for beginners' guide — most competitors skip this",
                f"Create comparison posts: '[Tool A] vs [Tool B] for {your_niche}'",
                f"Document your own {your_niche} journey — competitors show results, not the process",
                "Answer the 5 most-Googled questions in your niche (check Google autocomplete)",
            ],
            "content_calendar_tip": "Fill 3 gap topics per month — measure which gets highest saves to double-down",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a competitive content strategist for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Find content gaps for a {your_niche} creator on {platform}.\n"
                f"Competitor info: {competitor_info}\n\n"
                f"Return JSON: {{\"platform\",\"niche\",\"gap_opportunities\":[{{\"topic\",\"why_it_works\","
                f"\"difficulty\",\"potential_reach\",\"content_angle\",\"urgency\"}}],"
                f"\"quick_wins\":[],\"content_calendar_tip\"}}"
            )},
        ],
        temperature=0.65, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"gap_opportunities": [], "quick_wins": []}


async def build_audience_persona(
    niche: str, platform: str = "Instagram",
    product_or_service: str = "Coaching Program",
    language: str = "English"
) -> dict:
    """Build detailed buyer/follower personas for hyper-targeted content."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "niche": niche,
            "personas": [
                {
                    "persona_name": "The Ambitious Starter",
                    "age_range": "22–32",
                    "gender_split": "55% Female, 45% Male",
                    "income": "$35,000–$60,000",
                    "occupation": "Employee wanting side income / freelancer",
                    "top_pain_points": [
                        f"Doesn't know where to start with {niche}",
                        "Afraid of wasting time on wrong strategies",
                        "Overwhelmed by too much conflicting advice online",
                    ],
                    "core_desires": [
                        "Clear step-by-step system that actually works",
                        "Visible results within 30–90 days",
                        "A supportive community to learn from",
                    ],
                    "buying_triggers": [
                        "Social proof from people like them",
                        "Risk-free trial or money-back guarantee",
                        "Before/after story with specific numbers",
                    ],
                    "content_preferences": [
                        "Step-by-step tutorials (How-to)",
                        "Quick wins and tips",
                        "Real talk / no-fluff advice",
                    ],
                    "platforms": ["Instagram", "TikTok", "YouTube"],
                    "objections": [
                        "Is this legit / will this really work for me?",
                        f"I don't have time to learn {niche} right now",
                        "I've tried things before and failed",
                    ],
                    "messaging_angle": f"You don't need more information about {niche} — you need a SYSTEM. Here's the one I used.",
                },
                {
                    "persona_name": "The Scaling Professional",
                    "age_range": "30–45",
                    "gender_split": "50% / 50%",
                    "income": "$60,000–$120,000",
                    "occupation": "Small business owner / established freelancer",
                    "top_pain_points": [
                        "Plateaued growth — stuck at same level for months",
                        "Too busy to learn new strategies",
                        "Want to delegate but don't know how",
                    ],
                    "core_desires": [
                        "Systems that save time and scale revenue",
                        "Authority positioning in their market",
                        "A done-for-you or shortcut solution",
                    ],
                    "buying_triggers": [
                        "ROI calculator / case study with numbers",
                        "Expert authority signals (press, certifications)",
                        "Done-for-you or fast implementation",
                    ],
                    "content_preferences": [
                        "Strategy deep-dives",
                        "Industry data and trends",
                        "Case studies from peers at their level",
                    ],
                    "platforms": ["LinkedIn", "Twitter/X", "YouTube"],
                    "objections": [
                        "I don't have time to implement this",
                        "Too expensive for uncertain ROI",
                        "I've already tried similar things",
                    ],
                    "messaging_angle": f"You've already proven you can do {niche}. Now let's build the system that scales it without working more hours.",
                },
            ],
            "best_persona_to_target": "The Ambitious Starter",
            "targeting_reason": "Larger audience size, higher emotional urgency, and more responsive to content → direct sales conversion",
            "content_strategy_per_persona": {
                "The Ambitious Starter": "How-to content, quick wins, relatable beginner stories, strong CTAs",
                "The Scaling Professional": "ROI-focused case studies, advanced strategy, premium positioning content",
            },
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a market research specialist. Language: {language}."},
            {"role": "user", "content": (
                f"Build 2 detailed audience personas for a {niche} creator on {platform} selling '{product_or_service}'.\n\n"
                f"Return JSON: {{\"niche\",\"personas\":[{{\"persona_name\",\"age_range\","
                f"\"gender_split\",\"income\",\"occupation\",\"top_pain_points\":[],\"core_desires\":[],"
                f"\"buying_triggers\":[],\"content_preferences\":[],\"platforms\":[],"
                f"\"objections\":[],\"messaging_angle\"}}],"
                f"\"best_persona_to_target\",\"targeting_reason\",\"content_strategy_per_persona\":{{}}}}"
            )},
        ],
        temperature=0.55, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"personas": [], "best_persona_to_target": ""}


async def get_algorithm_strategy(
    platform: str, content_type: str = "Short Video",
    niche: str = "General", language: str = "English"
) -> dict:
    """Get current algorithm intelligence + strategy to maximize organic reach."""
    if not USE_AI or not LLM_CLIENT:
        strategies = {
            "TikTok": {
                "algorithm_name": "TikTok For You Page (FYP) Algorithm",
                "key_ranking_factors": [
                    "Watch-through rate (% of video watched) — most important signal",
                    "Re-watches — viewers looping = strong quality signal",
                    "Shares — fastest way to trigger viral distribution",
                    "Comments engagement (especially comments you reply to)",
                    "Profile follows from the post",
                ],
                "content_boosts": [
                    "Videos 21–34 seconds often outperform longer ones",
                    "Trending audio adds discoverability bonus",
                    "Text overlays increase watch time by ~15%",
                    "Consistent niche posting trains algorithm to classify your account",
                    "First 48h posting window is critical — don't delete and repost",
                ],
                "content_kills": [
                    "Watermarks from other platforms (Instagram, YouTube)",
                    "Low-quality, blurry video",
                    "Using hashtags you're not relevant to",
                    "Posting then immediately closing the app (breaks distribution)",
                    "Buying fake followers — suppresses organic reach",
                ],
                "optimal_post_times": "7–9am, 12–3pm, 7–9pm in audience timezone",
                "posting_frequency": "1–3 times/day for growth phase",
                "engagement_signals_to_prioritize": ["Shares > Comments > Likes > Follows"],
                "current_algorithm_insight": "TikTok now weights 'shares to external platforms' heavily — content that makes people share to WhatsApp/DMs gets massive FYP push.",
            },
            "Instagram": {
                "algorithm_name": "Instagram Ranking System (Reels, Feed, Explore)",
                "key_ranking_factors": [
                    "Saves — strongest signal for Explore reach",
                    "Shares (especially to Stories/DMs)",
                    "Comments (especially back-and-forth conversations)",
                    "Watch time on Reels",
                    "Profile relationship history (do they interact with you?)",
                ],
                "content_boosts": [
                    "Reels get 2–3x more reach than static posts",
                    "Carousel posts get 3x more reach than single images (people swipe = time on post)",
                    "Using 3–5 targeted hashtags outperforms 30 generic ones",
                    "Posting consistently at same times trains follower habit",
                    "Responding to comments within first hour boosts distribution",
                ],
                "content_kills": [
                    "TikTok watermarks (Meta actively suppresses these)",
                    "Posting link in caption (use link in bio instead)",
                    "Engagement pod-style fake activity",
                    "Posting frequency drops signal inconsistency",
                    "Stories that only show external links with no value",
                ],
                "optimal_post_times": "8–9am, 12–2pm, 5–7pm on weekdays",
                "posting_frequency": "Reels: 3–5/week | Feed: 3–4/week | Stories: Daily",
                "engagement_signals_to_prioritize": ["Saves > Shares to DM > Comments > Likes"],
                "current_algorithm_insight": "Instagram is prioritizing original Reels content and penalizing TikTok reposts. Aim for 90%+ saves + shares ratio vs likes for Explore placement.",
            },
        }
        default_strategy = strategies.get(platform, {
            "algorithm_name": f"{platform} Content Algorithm",
            "key_ranking_factors": ["Watch/dwell time", "Shares", "Comments", "Saves", "Profile follows"],
            "content_boosts": ["Consistency", "Relevant hashtags", "High-quality visuals", "Strong hook first 3 seconds"],
            "content_kills": ["Inconsistent posting", "Irrelevant hashtags", "Low-quality media"],
            "optimal_post_times": "Check your analytics for peak audience times",
            "posting_frequency": "3–5 posts/week recommended",
            "engagement_signals_to_prioritize": ["Shares > Comments > Saves > Likes"],
            "current_algorithm_insight": "Consistently good content wins long-term over viral one-offs.",
        })
        default_strategy.update({"platform": platform, "content_type": content_type, "niche": niche})
        return default_strategy
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a {platform} algorithm expert with up-to-date knowledge. Language: {language}."},
            {"role": "user", "content": (
                f"Provide the current {platform} algorithm strategy for {content_type} content in {niche} niche.\n\n"
                f"Return JSON: {{\"platform\",\"algorithm_name\",\"key_ranking_factors\":[],\"content_boosts\":[],"
                f"\"content_kills\":[],\"optimal_post_times\",\"posting_frequency\","
                f"\"engagement_signals_to_prioritize\":[],\"current_algorithm_insight\"}}"
            )},
        ],
        temperature=0.4, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"platform": platform, "key_ranking_factors": [], "content_boosts": []}
