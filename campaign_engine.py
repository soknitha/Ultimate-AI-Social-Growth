"""
GrowthOS AI — Campaign Engine
================================
Feature #7  : Auto Campaign System (Set & Forget)
Feature #4  : Autonomous Campaign Engine (advanced)
Feature #20 : Autonomous Scaling Engine
Feature #98 : Autonomous Scaling Intelligence
Feature #9  : Smart Budget Optimization AI
Feature #93 : AI Revenue Funnel Designer
Feature #90 : Content Velocity Controller
"""
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL as OPENAI_MODEL, LLM_FAST_MODEL as OPENAI_FAST_MODEL, USE_AI as USE_REAL_AI


async def _gpt(prompt: str) -> str:
    if not _client:
        return ""
    try:
        resp = await _client.chat.completions.create(
            model=OPENAI_FAST_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert digital marketing campaign strategist."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #7: Create Campaign ─────────────────────────────────────────────
async def create_campaign(
    name: str,
    platform: str,
    niche: str,
    goal: str,
    budget_usd: float,
    duration_days: int,
) -> dict:
    """Create a fully structured AI-driven campaign plan."""
    if USE_REAL_AI:
        prompt = (
            f"Create a detailed social media campaign:\n"
            f"Name: {name}\nPlatform: {platform}\nNiche: {niche}\n"
            f"Goal: {goal}\nBudget: ${budget_usd}\nDuration: {duration_days} days\n\n"
            "Return JSON: campaign_overview(dict), phase_plan(list of phases with name, days, tasks, kpis), "
            "budget_allocation(dict), content_schedule(dict), success_metrics(list), "
            "risk_mitigation(list)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                data = json.loads(raw)
                data["campaign_id"] = f"CAMP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                return data
            except Exception:
                pass

    daily_budget = budget_usd / duration_days
    phases = []
    phase_size = max(1, duration_days // 3)
    for p, (phase_name, focus) in enumerate([
        ("Launch Phase", "Build awareness and initial engagement"),
        ("Growth Phase", "Scale top performers and expand reach"),
        ("Conversion Phase", "Convert audience to followers/buyers"),
    ]):
        start_day = p * phase_size + 1
        end_day   = min((p + 1) * phase_size, duration_days)
        phases.append({
            "phase": p + 1,
            "name": phase_name,
            "days": f"Day {start_day}–{end_day}",
            "focus": focus,
            "tasks": [
                f"Create {3 + p} content pieces daily",
                "Engage with 50+ targeted accounts",
                "A/B test 2 different content formats",
            ],
            "budget_allocation": f"${daily_budget * (end_day - start_day + 1):.0f}",
            "kpis": ["Reach", "Engagement Rate", "Follower Growth"],
        })

    return {
        "campaign_id": f"CAMP_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "campaign_name": name,
        "platform": platform,
        "niche": niche,
        "goal": goal,
        "total_budget": f"${budget_usd:.2f}",
        "daily_budget": f"${daily_budget:.2f}",
        "duration_days": duration_days,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d"),
        "status": "Ready to Launch",
        "phase_plan": phases,
        "budget_allocation": {
            "Content Creation": "40%",
            "Paid Promotion": "35%",
            "Tools & Software": "15%",
            "Contingency":     "10%",
        },
        "content_schedule": {
            "daily_posts":  3,
            "weekly_reels": 5,
            "stories_daily": 3,
            "live_streams": "1 per week",
        },
        "success_metrics": [
            f"Reach {int(budget_usd * 100):,} impressions",
            f"Gain {int(budget_usd * 10):,} new followers",
            f"Achieve {3 + duration_days // 10:.1f}%+ engagement rate",
            f"Generate {int(budget_usd * 2):.0f}+ profile visits",
        ],
        "risk_mitigation": [
            "Monitor shadowban signals weekly",
            "Keep daily growth within safe limits",
            "A/B test before scaling any single format",
            "Maintain content quality over quantity",
        ],
        "created_at": datetime.now().isoformat(),
    }


# ─── Feature #7 + #4: Post Scheduler ─────────────────────────────────────────
def schedule_posts(
    content_list: list,
    platform: str,
    start_date: str = None,
    posts_per_day: int = 3,
) -> dict:
    """Create an optimized posting schedule for a content list."""
    optimal_times = {
        "TikTok":    ["7:00 AM", "12:00 PM", "7:30 PM", "9:00 PM"],
        "Instagram": ["6:30 AM", "11:30 AM", "7:00 PM", "9:00 PM"],
        "Facebook":  ["9:00 AM",  "1:00 PM", "3:00 PM", "8:00 PM"],
        "YouTube":   ["2:00 PM",  "4:00 PM", "8:00 PM"],
    }
    times = optimal_times.get(platform, optimal_times["Instagram"])[:posts_per_day]

    base_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
    schedule = []
    day = 0
    for i, content in enumerate(content_list):
        slot_time = times[i % len(times)]
        post_date = base_date + timedelta(days=day)
        schedule.append({
            "post_number": i + 1,
            "content": content if isinstance(content, str) else content.get("title", f"Post #{i+1}"),
            "scheduled_date": post_date.strftime("%Y-%m-%d"),
            "scheduled_time": slot_time,
            "platform": platform,
            "status": "Scheduled",
        })
        if (i + 1) % posts_per_day == 0:
            day += 1

    return {
        "platform": platform,
        "total_posts": len(content_list),
        "posts_per_day": posts_per_day,
        "schedule_duration_days": day + 1,
        "schedule": schedule,
        "optimal_times_used": times,
        "tip": "These times are proven peak engagement windows — post within 30 min of scheduled time for best results",
        "created_at": datetime.now().isoformat(),
    }


# ─── Feature #20 + #98: Auto Scaling Intelligence ────────────────────────────
async def auto_optimize_campaign(campaign_metrics: dict, budget_remaining: float) -> dict:
    """AI auto-optimizes running campaign based on performance."""
    top_performers    = campaign_metrics.get("top_performers", [])
    low_performers    = campaign_metrics.get("low_performers", [])
    avg_engagement    = campaign_metrics.get("avg_engagement_rate", 2.0)
    total_reach       = campaign_metrics.get("total_reach", 0)
    conversion_rate   = campaign_metrics.get("conversion_rate", 0.5)

    actions = []

    # Scale winners
    if top_performers:
        actions.append({
            "action": "SCALE UP",
            "target": f"Top {len(top_performers)} performing posts",
            "recommendation": f"Boost these posts with ${budget_remaining * 0.6:.0f} for maximum ROI",
            "expected_impact": f"+{int(total_reach * 0.5):,} additional reach",
            "priority": "HIGH",
        })

    # Kill losers
    if low_performers:
        actions.append({
            "action": "PAUSE",
            "target": f"Bottom {len(low_performers)} performing posts",
            "recommendation": "Reallocate budget from these underperformers",
            "expected_savings": f"${budget_remaining * 0.2:.0f}",
            "priority": "HIGH",
        })

    # Engagement optimization
    if avg_engagement < 3.0:
        actions.append({
            "action": "OPTIMIZE",
            "target": "Content strategy",
            "recommendation": "Switch to story-based format — current content lacks emotional connection",
            "priority": "MEDIUM",
        })

    # Budget reallocation
    budget_plan = {
        "scale_winners":     f"${budget_remaining * 0.60:.2f}",
        "test_new_formats":  f"${budget_remaining * 0.25:.2f}",
        "contingency":       f"${budget_remaining * 0.15:.2f}",
    }

    return {
        "campaign_health": "Needs Optimization" if avg_engagement < 3 else "On Track",
        "auto_actions": actions,
        "budget_reallocation": budget_plan,
        "performance_insight": (
            f"Campaign reaching {total_reach:,} people at {avg_engagement:.1f}% engagement. "
            f"{'Scale immediately — strong performance!' if avg_engagement > 5 else 'Optimize content format before scaling more budget.'}"
        ),
        "ai_confidence": "87%",
        "optimized_at": datetime.now().isoformat(),
    }


# ─── Feature #9: Budget Optimization ─────────────────────────────────────────
def optimize_budget(total_budget: float, goals: list, platform: str) -> dict:
    """AI allocates budget optimally across campaign objectives."""
    allocations = {
        "follower_growth": {
            "Paid Promotion (Reels/Shorts boost)": 0.45,
            "Influencer Micro-Collab":              0.25,
            "Content Production":                  0.20,
            "Tools":                               0.10,
        },
        "sales_conversion": {
            "Direct Response Ads":   0.50,
            "Retargeting Campaign":  0.25,
            "Lead Magnet Content":   0.15,
            "Tools & Analytics":     0.10,
        },
        "brand_awareness": {
            "Wide Reach Promotion":  0.55,
            "Collaboration/UGC":     0.20,
            "Content Production":   0.15,
            "Brand Monitoring":     0.10,
        },
    }

    goal_key = "follower_growth"
    for goal in goals:
        if "sales" in goal.lower() or "convert" in goal.lower():
            goal_key = "sales_conversion"
            break
        elif "brand" in goal.lower() or "awareness" in goal.lower():
            goal_key = "brand_awareness"
            break

    chosen_alloc = allocations[goal_key]
    dollar_alloc = {k: f"${total_budget * v:.2f}" for k, v in chosen_alloc.items()}

    return {
        "total_budget": f"${total_budget:.2f}",
        "optimization_strategy": goal_key.replace("_", " ").title(),
        "platform": platform,
        "dollar_allocation": dollar_alloc,
        "percentage_allocation": {k: f"{v*100:.0f}%" for k, v in chosen_alloc.items()},
        "expected_roi": f"{int(150 + total_budget * 0.5)}%",
        "tip": f"For {platform}, paid promotion on your top organic post typically delivers 3–5x better ROI than cold ad campaigns.",
        "calculated_at": datetime.now().isoformat(),
    }


# ─── Feature #90: Content Velocity Controller ────────────────────────────────
def control_content_velocity(
    current_posts_per_day: float,
    engagement_trend: str,
    account_age_months: int,
    platform: str,
) -> dict:
    """Manage posting speed to avoid burnout and algorithm penalties."""
    recommended_limits = {
        "TikTok":    {"min": 1, "max": 5, "sweet_spot": 3},
        "Instagram": {"min": 1, "max": 3, "sweet_spot": 2},
        "Facebook":  {"min": 1, "max": 2, "sweet_spot": 1},
        "YouTube":   {"min": 0.3, "max": 1, "sweet_spot": 0.5},  # per day (2-4/week)
    }
    limits = recommended_limits.get(platform, {"min": 1, "max": 3, "sweet_spot": 2})

    adjustment = "MAINTAIN"
    if engagement_trend == "declining" and current_posts_per_day > limits["sweet_spot"]:
        adjustment = "REDUCE"
        new_velocity = max(limits["min"], current_posts_per_day - 1)
        reason = "Declining engagement suggests content fatigue — reduce frequency, increase quality"
    elif engagement_trend == "growing" and current_posts_per_day < limits["sweet_spot"]:
        adjustment = "INCREASE"
        new_velocity = min(limits["max"], current_posts_per_day + 1)
        reason = "Growing engagement — algorithm is rewarding you, post more to maximize momentum"
    else:
        new_velocity = current_posts_per_day
        reason = "Current velocity is optimal — maintain consistency"

    return {
        "platform": platform,
        "current_velocity": f"{current_posts_per_day} posts/day",
        "recommended_velocity": f"{new_velocity} posts/day",
        "adjustment": adjustment,
        "reason": reason,
        "platform_limits": limits,
        "sustainability_score": "High" if current_posts_per_day <= limits["sweet_spot"] else "Medium",
        "burnout_risk": "Low" if current_posts_per_day <= limits["max"] else "High — reduce immediately",
        "analyzed_at": datetime.now().isoformat(),
    }
