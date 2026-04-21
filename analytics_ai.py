"""
GrowthOS AI — Analytics AI Copilot
=====================================
Feature #3  : Real Analytics Dashboard
Feature #6  : Deep Analytics + Insight AI
Feature #11 : Smart Report Generator
Feature #9  : Smart Budget Optimization AI
Feature #83 : Trust & Authenticity Score
Feature #96 : Cross-Channel Attribution Engine
Feature #92 : Audience Fatigue Detector
Feature #89 : AI Timing Precision Engine
"""
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL as OPENAI_MODEL, LLM_FAST_MODEL as OPENAI_FAST_MODEL, USE_AI as USE_REAL_AI


async def _gpt(prompt: str, fast: bool = True) -> str:
    if not _client:
        return ""
    try:
        resp = await _client.chat.completions.create(
            model=OPENAI_FAST_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert social media analytics AI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1500,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #6: Performance Analysis ────────────────────────────────────────
async def analyze_performance(metrics: dict, platform: str) -> dict:
    """Analyze post/account performance with AI insights."""
    views    = metrics.get("views", 0)
    likes    = metrics.get("likes", 0)
    comments = metrics.get("comments", 0)
    shares   = metrics.get("shares", 0)
    saves    = metrics.get("saves", 0)
    follows  = metrics.get("follows", 0)

    # Computed rates
    eng_rate     = round((likes + comments + shares + saves) / max(views, 1) * 100, 2)
    save_rate    = round(saves / max(views, 1) * 100, 2)
    share_rate   = round(shares / max(views, 1) * 100, 2)
    follow_rate  = round(follows / max(views, 1) * 100, 2)
    comment_rate = round(comments / max(views, 1) * 100, 2)

    benchmarks = {
        "TikTok":    {"eng_rate": 5.0, "save_rate": 2.0},
        "Instagram": {"eng_rate": 3.5, "save_rate": 1.5},
        "Facebook":  {"eng_rate": 1.5, "save_rate": 0.5},
        "YouTube":   {"eng_rate": 4.0, "save_rate": 3.0},
    }
    bench = benchmarks.get(platform, {"eng_rate": 3.0, "save_rate": 1.5})

    performance_vs_avg = "Above Average ✅" if eng_rate > bench["eng_rate"] else "Below Average ⚠️"

    if USE_REAL_AI:
        prompt = (
            f"Analyze these social media metrics:\nPlatform: {platform}\n"
            f"Views: {views:,}, Likes: {likes:,}, Comments: {comments:,}, "
            f"Shares: {shares:,}, Saves: {saves:,}\n"
            f"Engagement Rate: {eng_rate}% (Platform avg: {bench['eng_rate']}%)\n\n"
            "Explain: what worked, what didn't, and 3 specific improvement recommendations. "
            "Return JSON: what_worked(str), what_failed(str), recommendations(list), "
            "performance_grade(A/B/C/D/F), viral_potential(str)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                ai = json.loads(raw)
                ai.update({
                    "engagement_rate": f"{eng_rate}%",
                    "save_rate": f"{save_rate}%",
                    "share_rate": f"{share_rate}%",
                    "follow_rate": f"{follow_rate}%",
                    "performance_vs_benchmark": performance_vs_avg,
                })
                return ai
            except Exception:
                pass

    grade = "A" if eng_rate > 7 else "B" if eng_rate > 4 else "C" if eng_rate > 2 else "D"
    return {
        "platform": platform,
        "metrics_summary": {
            "views": f"{views:,}",
            "engagement_rate": f"{eng_rate}%",
            "save_rate": f"{save_rate}%",
            "share_rate": f"{share_rate}%",
            "comment_rate": f"{comment_rate}%",
            "follow_rate": f"{follow_rate}%",
        },
        "performance_vs_benchmark": performance_vs_avg,
        "performance_grade": grade,
        "what_worked": "Strong hook likely drove initial views. Save rate indicates valuable content.",
        "what_failed": "Low share rate suggests content wasn't 'pass-it-on' worthy. Comments indicate room for controversy/question.",
        "recommendations": [
            "Add a direct question at the end to spark comments",
            "Include more share-worthy statistics or controversial opinion",
            f"Re-post at peak hour with A/B test caption for {platform}",
        ],
        "viral_potential": "Medium — needs stronger share trigger",
        "analyzed_at": datetime.now().isoformat(),
    }


# ─── Feature #6: Performance Explainer ───────────────────────────────────────
async def explain_performance(
    post_topic: str, platform: str, outcome: str, metrics: dict,
) -> str:
    """Plain-language explanation of WHY a post performed as it did."""
    if USE_REAL_AI:
        prompt = (
            f"Explain in plain, conversational language why this post performed this way:\n"
            f"Topic: {post_topic}\nPlatform: {platform}\nOutcome: {outcome}\n"
            f"Metrics: {json.dumps(metrics)}\n\n"
            "Be specific. Give 3 reasons with actionable fixes. Keep it under 200 words."
        )
        raw = await _gpt(prompt)
        if raw:
            return raw

    outcomes = {
        "viral": f"This post likely went viral because the hook matched a trending topic in {post_topic}, "
                 f"the first 3 seconds had a strong pattern interrupt, and the save-worthy content drove "
                 f"algorithm amplification. Keep replicating this format!",
        "flop": f"This post underperformed likely because: (1) the hook wasn't strong enough to stop the scroll, "
                f"(2) posting time may have missed peak audience hours on {platform}, or "
                f"(3) the topic wasn't specific enough to a core audience pain point. "
                f"Try testing a more provocative opening line next time.",
        "average": f"Average performance suggests decent content but missing a viral multiplier. "
                   f"Add a stronger CTA, a controversial opinion, or a share-worthy statistic to push it further.",
    }
    key = "viral" if "good" in outcome.lower() or "viral" in outcome.lower() \
          else "flop" if "bad" in outcome.lower() or "flop" in outcome.lower() \
          else "average"
    return outcomes[key]


# ─── Feature #9: ROI Calculator ──────────────────────────────────────────────
def calculate_roi(ad_spend: float, revenue_generated: float, new_followers: int, platform: str) -> dict:
    """Calculate comprehensive ROI for a paid campaign."""
    if ad_spend <= 0:
        return {"error": "Ad spend must be greater than 0"}

    roi_pct = round((revenue_generated - ad_spend) / ad_spend * 100, 1)
    cost_per_follower = round(ad_spend / max(new_followers, 1), 3)
    roas = round(revenue_generated / ad_spend, 2)

    return {
        "ad_spend": f"${ad_spend:,.2f}",
        "revenue_generated": f"${revenue_generated:,.2f}",
        "net_profit": f"${revenue_generated - ad_spend:,.2f}",
        "roi_percentage": f"{roi_pct}%",
        "roas": f"{roas}x",
        "new_followers": f"{new_followers:,}",
        "cost_per_follower": f"${cost_per_follower:.3f}",
        "performance_rating": "Excellent 🏆" if roi_pct > 200 else "Good ✅" if roi_pct > 100 else "Average ⚠️" if roi_pct > 0 else "Loss ❌",
        "platform": platform,
        "recommendation": (
            "Scale this campaign immediately — high ROAS" if roas > 3
            else "Optimize creatives before scaling" if roas > 1
            else "Pause and revise targeting strategy"
        ),
        "calculated_at": datetime.now().isoformat(),
    }


# ─── Feature #83: Trust & Authenticity Score ─────────────────────────────────
def calculate_trust_score(
    follower_count: int,
    avg_engagement_rate: float,
    account_age_months: int,
    post_consistency_score: float,
    verified: bool = False,
) -> dict:
    """Score account credibility and audience authenticity."""
    # Score components
    eng_score = min(30, avg_engagement_rate * 4)
    age_score = min(20, account_age_months * 0.5)
    consistency_score = post_consistency_score * 20  # 0-1 scale
    size_score = min(20, follower_count / 5000)
    verify_score = 10 if verified else 0

    total = round(eng_score + age_score + consistency_score + size_score + verify_score, 1)
    total = min(100, total)

    level = (
        "Platinum 💎" if total >= 85
        else "Gold 🥇" if total >= 70
        else "Silver 🥈" if total >= 55
        else "Bronze 🥉" if total >= 40
        else "Building 🌱"
    )

    return {
        "trust_score": total,
        "trust_level": level,
        "breakdown": {
            "engagement_quality": f"{eng_score:.1f}/30",
            "account_maturity":   f"{age_score:.1f}/20",
            "posting_consistency": f"{consistency_score:.1f}/20",
            "audience_size":      f"{size_score:.1f}/20",
            "verification_bonus": f"{verify_score}/10",
        },
        "interpretation": (
            "Highly authentic account — brands will trust this profile" if total >= 70
            else "Growing trust — focus on consistency and engagement" if total >= 50
            else "Early stage — build consistency and genuine interactions"
        ),
        "improvement_tips": [
            "Post consistently (same days/times each week)",
            "Reply to every comment within 1 hour",
            "Avoid buying fake engagement — it destroys trust score",
            "Collaborate with verified accounts in your niche",
        ],
        "calculated_at": datetime.now().isoformat(),
    }


# ─── Feature #11: Smart Report Generator ─────────────────────────────────────
async def generate_report(
    account_name: str, platform: str, period: str,
    metrics: dict, goals_achieved: list,
) -> dict:
    """Generate a comprehensive performance report."""
    views    = metrics.get("total_views", 0)
    followers_gained = metrics.get("followers_gained", 0)
    avg_eng  = metrics.get("avg_engagement_rate", 0)
    top_post = metrics.get("top_post", "N/A")
    ad_spend = metrics.get("ad_spend", 0)
    revenue  = metrics.get("revenue", 0)

    if USE_REAL_AI:
        prompt = (
            f"Write an executive summary for a social media performance report:\n"
            f"Account: {account_name} on {platform}\nPeriod: {period}\n"
            f"Total Views: {views:,}, Followers Gained: {followers_gained:,}, "
            f"Avg Engagement: {avg_eng}%\n"
            f"Goals Achieved: {', '.join(goals_achieved) if goals_achieved else 'None set'}\n\n"
            "Write 3 paragraphs: Performance Summary, Key Wins, Next Steps. Keep professional."
        )
        raw = await _gpt(prompt)
        exec_summary = raw if raw else f"Account {account_name} achieved {followers_gained:,} new followers in {period}."
    else:
        exec_summary = (
            f"{account_name} delivered strong performance on {platform} during {period}. "
            f"Total reach of {views:,} impressions with {avg_eng}% average engagement rate. "
            f"The top-performing content was '{top_post}' demonstrating audience resonance with this format. "
            f"Growth strategy is working — recommend continuing current content cadence with expanded ad investment."
        )

    roi_data = calculate_roi(ad_spend, revenue, followers_gained, platform) if ad_spend > 0 else {}

    return {
        "report_title": f"Performance Report — {account_name} on {platform}",
        "period": period,
        "generated_at": datetime.now().isoformat(),
        "executive_summary": exec_summary,
        "key_metrics": {
            "Total Views / Impressions": f"{views:,}",
            "New Followers":              f"{followers_gained:,}",
            "Avg Engagement Rate":        f"{avg_eng}%",
            "Top Performing Content":     top_post,
        },
        "goals_report": {
            goal: "✅ Achieved" for goal in goals_achieved
        } if goals_achieved else {"No goals set": "—"},
        "roi_analysis": roi_data,
        "grade": "A" if avg_eng > 5 and followers_gained > 1000 else "B" if avg_eng > 2 else "C",
        "next_month_recommendations": [
            "Double down on top-performing content format",
            "A/B test 3 new hook styles",
            "Increase posting frequency by 20%",
            "Launch one collaboration with complementary creator",
        ],
    }


# ─── Feature #89: Timing Precision Engine ────────────────────────────────────
def predict_best_posting_time(platform: str, timezone: str = "Asia/Phnom_Penh", niche: str = "") -> dict:
    """Ultra-accurate posting time recommendations based on platform data."""
    schedules = {
        "TikTok": {
            "peak_hours": ["6:00 AM", "10:00 AM", "7:00 PM", "9:00 PM", "11:00 PM"],
            "peak_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
            "avoid": ["3–5 AM", "Midday weekdays"],
        },
        "Instagram": {
            "peak_hours": ["6:00 AM", "11:00 AM", "1:00 PM", "7:00 PM", "9:00 PM"],
            "peak_days": ["Monday", "Wednesday", "Thursday"],
            "avoid": ["Sundays 11 PM–7 AM"],
        },
        "Facebook": {
            "peak_hours": ["9:00 AM", "1:00 PM", "3:00 PM", "8:00 PM"],
            "peak_days": ["Wednesday", "Thursday", "Friday"],
            "avoid": ["Weekends before 8 AM"],
        },
        "YouTube": {
            "peak_hours": ["2:00 PM", "3:00 PM", "4:00 PM", "9:00 PM"],
            "peak_days": ["Friday", "Saturday", "Sunday"],
            "avoid": ["Monday–Tuesday before noon"],
        },
    }
    schedule = schedules.get(platform, schedules["Instagram"])
    return {
        "platform": platform,
        "timezone": timezone,
        "niche_modifier": f"For {niche} audience, shift times 30 min earlier on weekdays" if niche else None,
        "recommended_times": schedule["peak_hours"],
        "best_days": schedule["peak_days"],
        "avoid_times": schedule["avoid"],
        "optimal_frequency": {
            "TikTok": "3–5 posts/day",
            "Instagram": "1–3 posts/day",
            "Facebook": "1–2 posts/day",
            "YouTube": "2–3 videos/week",
        }.get(platform, "1–2 posts/day"),
        "power_tip": f"On {platform}, the first 30 minutes after posting are critical. Engage actively during this window.",
    }


# ─── Feature #92: Audience Fatigue Detector ──────────────────────────────────
def detect_audience_fatigue(engagement_history: list) -> dict:
    """Detect declining engagement patterns indicating audience fatigue."""
    if len(engagement_history) < 3:
        return {"status": "Insufficient data", "fatigue_detected": False}

    # Calculate trend
    recent_avg = sum(engagement_history[-3:]) / 3
    earlier_avg = sum(engagement_history[:3]) / 3 if len(engagement_history) >= 6 else recent_avg * 1.2
    decline_pct = round((earlier_avg - recent_avg) / max(earlier_avg, 0.01) * 100, 1)

    fatigue_detected = decline_pct > 20
    severity = (
        "Critical 🔴" if decline_pct > 50
        else "High ⚠️" if decline_pct > 30
        else "Medium 🟡" if decline_pct > 20
        else "None 🟢"
    )

    return {
        "fatigue_detected": fatigue_detected,
        "severity": severity,
        "engagement_decline": f"{decline_pct:.1f}%",
        "recent_avg_engagement": f"{recent_avg:.2f}%",
        "earlier_avg_engagement": f"{earlier_avg:.2f}%",
        "recommendations": [
            "Introduce a new content format immediately",
            "Take a 2-day break then return with a 'comeback' post",
            "Poll your audience — ask what they want to see",
            "Collaborate with another creator to inject fresh energy",
            "Try a controversial or vulnerable personal story post",
        ] if fatigue_detected else ["Engagement is healthy — maintain current strategy"],
        "analyzed_at": datetime.now().isoformat(),
    }
