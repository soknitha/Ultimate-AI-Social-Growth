"""
GrowthOS AI — Risk & Compliance Engine
========================================
Feature #6  : Risk Detection & Safety AI
Feature #5  : Anti-Ban Intelligence AI (advanced)
Feature #86 : Shadowban Detection AI
Feature #97 : AI Content Risk Scanner
Feature #9  : Advanced Compliance AI (advanced)
Feature #11 : Zero-Trust Security AI (advanced)
Feature #17 : Self-Healing System (retry/recovery)
"""
import re
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MAX_DAILY_GROWTH, RISK_THRESHOLDS

# ─── Banned / High-risk keyword patterns ─────────────────────────────────────
_POLICY_PATTERNS = [
    r"\bfake\s+followers?\b",
    r"\bbuy\s+followers?\b",
    r"\bbot\s+engagement\b",
    r"\bspam\b",
    r"\bhate\s+speech\b",
    r"\bviolence\b",
    r"\bself[- ]harm\b",
    r"\bterror\b",
    r"\bscam\b",
    r"\bphishing\b",
    r"\bclick\s*bait\b",
    r"\bmanipulat\w+\b",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _POLICY_PATTERNS]


# ─── Feature #97: Content Risk Scanner ───────────────────────────────────────
def check_content_safety(content: str, platform: str = "General") -> dict:
    """Scan content for policy violations before posting."""
    violations = []
    for pattern in _COMPILED_PATTERNS:
        match = pattern.search(content)
        if match:
            violations.append({
                "pattern": match.group(),
                "type": "Policy Violation",
                "severity": "High",
            })

    # Length checks
    length_warnings = []
    if len(content) > 2200 and platform == "Instagram":
        length_warnings.append("Caption exceeds Instagram's 2,200 character limit")
    if len(content) > 500 and platform == "TikTok":
        length_warnings.append("Caption may be too long for TikTok's optimal display (150 chars recommended)")

    # Hashtag density check
    hashtag_count = content.count("#")
    if hashtag_count > 30:
        length_warnings.append(f"⚠️ {hashtag_count} hashtags detected — over 30 may trigger spam filters")

    risk_score = min(1.0, len(violations) * 0.3 + len(length_warnings) * 0.1)
    is_safe = risk_score < RISK_THRESHOLDS["medium"] and not violations

    return {
        "is_safe": is_safe,
        "risk_score": round(risk_score, 2),
        "risk_level": (
            "Critical 🔴" if risk_score >= RISK_THRESHOLDS["critical"]
            else "High ⚠️"    if risk_score >= RISK_THRESHOLDS["high"]
            else "Medium 🟡"  if risk_score >= RISK_THRESHOLDS["medium"]
            else "Low 🟢"
        ),
        "policy_violations": violations,
        "length_warnings": length_warnings,
        "platform": platform,
        "suggestion": (
            "✅ Content is safe to post"
            if is_safe
            else "❌ Remove flagged terms before posting. See violations above."
        ),
        "scanned_at": datetime.now().isoformat(),
    }


# ─── Feature #86: Shadowban Detection ────────────────────────────────────────
def detect_shadowban_signals(metrics_history: list, platform: str) -> dict:
    """
    Detect shadowban signals from declining reach metrics.
    metrics_history: list of dicts with 'date', 'reach', 'impressions', 'hashtag_reach'
    """
    if len(metrics_history) < 5:
        return {
            "shadowban_risk": "Unknown",
            "reason": "Need at least 5 data points for analysis",
            "action": "Keep posting consistently and check back",
        }

    recent_reach = [m.get("reach", 0) for m in metrics_history[-3:]]
    earlier_reach = [m.get("reach", 0) for m in metrics_history[:3]]
    recent_hashtag = [m.get("hashtag_reach", 0) for m in metrics_history[-3:]]
    earlier_hashtag = [m.get("hashtag_reach", 0) for m in metrics_history[:3]]

    avg_recent   = sum(recent_reach) / max(len(recent_reach), 1)
    avg_earlier  = sum(earlier_reach) / max(len(earlier_reach), 1)
    reach_drop   = (avg_earlier - avg_recent) / max(avg_earlier, 1) * 100

    avg_h_recent  = sum(recent_hashtag) / max(len(recent_hashtag), 1)
    avg_h_earlier = sum(earlier_hashtag) / max(len(earlier_hashtag), 1)
    hashtag_drop  = (avg_h_earlier - avg_h_recent) / max(avg_h_earlier, 1) * 100

    shadowban_risk = "High 🔴" if reach_drop > 40 and hashtag_drop > 50 \
                     else "Medium 🟡" if reach_drop > 20 \
                     else "Low 🟢"

    signals = []
    if reach_drop > 20:
        signals.append(f"Overall reach dropped {reach_drop:.0f}%")
    if hashtag_drop > 30:
        signals.append(f"Hashtag reach dropped {hashtag_drop:.0f}% — strong shadowban signal")

    recovery_steps = [
        f"Stop posting for 24–48 hours on {platform}",
        "Remove all hashtags from recent posts temporarily",
        "Post only original, high-quality content (no reposts)",
        "Report the issue through the platform's official support",
        "Avoid third-party automation tools for 2 weeks",
        "Engage manually (comments, DMs) to restore account trust",
    ]

    return {
        "shadowban_risk": shadowban_risk,
        "platform": platform,
        "signals_detected": signals if signals else ["No shadowban signals detected"],
        "reach_trend": f"{reach_drop:.0f}% decline" if reach_drop > 0 else f"{abs(reach_drop):.0f}% growth",
        "hashtag_reach_trend": f"{hashtag_drop:.0f}% decline" if hashtag_drop > 0 else "Stable",
        "recovery_steps": recovery_steps if shadowban_risk != "Low 🟢" else ["No action needed — account is healthy"],
        "estimated_recovery_time": "5–14 days if recovery steps are followed" if shadowban_risk != "Low 🟢" else "N/A",
        "analyzed_at": datetime.now().isoformat(),
    }


# ─── Feature #6: Safe Growth Rate Calculator ─────────────────────────────────
def calculate_safe_limits(current_followers: int, platform: str, days: int = 1) -> dict:
    """Calculate safe daily growth limits to avoid platform flags."""
    platform_max = MAX_DAILY_GROWTH.get(platform, 1000)
    # Scale limit proportionally to account size
    size_factor = min(1.5, max(0.3, current_followers / 50000))
    safe_daily = int(platform_max * size_factor)
    safe_weekly = safe_daily * 7

    # Warning thresholds
    warning_level = int(safe_daily * 0.7)
    danger_level  = int(safe_daily * 0.9)

    return {
        "platform": platform,
        "current_followers": f"{current_followers:,}",
        "safe_daily_growth": f"{safe_daily:,}",
        "safe_weekly_growth": f"{safe_weekly:,}",
        "warning_threshold": f"{warning_level:,}/day (70% of safe max)",
        "danger_threshold": f"{danger_level:,}/day (90% of safe max — slow down)",
        "anti_ban_tips": [
            f"Never add more than {danger_level:,} followers in a single day on {platform}",
            "Spread growth evenly across 24 hours, not in bursts",
            "Mix organic engagement actions between automated tasks",
            "Take 1–2 rest days per week to appear natural",
            "Monitor reach metrics — a sudden drop signals algorithmic penalty",
        ],
        "calculated_at": datetime.now().isoformat(),
    }


# ─── Feature #9 Advanced: Account Health Monitor ─────────────────────────────
def audit_account_health(
    account_age_months: int,
    follower_count: int,
    avg_engagement_rate: float,
    posting_frequency_week: int,
    spam_reports: int = 0,
    policy_violations: int = 0,
) -> dict:
    """Comprehensive account health assessment."""
    # Scoring
    age_score         = min(25, account_age_months * 1.5)
    eng_score         = min(30, avg_engagement_rate * 5)
    freq_score        = min(20, posting_frequency_week * 3)
    size_score        = min(15, follower_count / 10000)
    penalty_deduction = (spam_reports * 10) + (policy_violations * 15)

    health_score = max(0, min(100, age_score + eng_score + freq_score + size_score - penalty_deduction))

    status = (
        "Excellent 🏆" if health_score >= 80
        else "Good ✅"     if health_score >= 60
        else "Fair ⚠️"     if health_score >= 40
        else "Poor 🔴"
    )

    risks = []
    if avg_engagement_rate < 1.5:
        risks.append("Engagement rate critically low — algorithm may deprioritize")
    if spam_reports > 0:
        risks.append(f"{spam_reports} spam report(s) detected — review content strategy")
    if policy_violations > 0:
        risks.append(f"{policy_violations} policy violation(s) — fix immediately")
    if posting_frequency_week < 3:
        risks.append("Low posting frequency — algorithm rewards consistency")

    return {
        "health_score": round(health_score, 1),
        "status": status,
        "score_breakdown": {
            "account_age":        f"{age_score:.1f}/25",
            "engagement_quality": f"{eng_score:.1f}/30",
            "posting_frequency":  f"{freq_score:.1f}/20",
            "audience_size":      f"{size_score:.1f}/15",
            "penalties":          f"-{penalty_deduction}",
        },
        "risks_identified": risks if risks else ["No significant risks identified ✅"],
        "action_items": [
            "Maintain posting at 3–5x/week minimum",
            "Focus on Saves and Shares > Likes for algorithm boost",
            "Never use fake engagement services — permanent account risk",
            "Review platform community guidelines quarterly",
        ],
        "policy_compliance": "✅ Compliant" if policy_violations == 0 else "❌ Violations Found",
        "assessed_at": datetime.now().isoformat(),
    }


# ─── Feature #17: Self-Healing Retry System ──────────────────────────────────
async def self_heal_failed_action(action_type: str, error_code: int, context: dict) -> dict:
    """Auto-diagnose and suggest recovery for failed platform actions."""
    recovery_map = {
        429: {
            "diagnosis": "Rate limit exceeded",
            "auto_action": "Wait 15 minutes then retry with reduced frequency",
            "prevention": "Implement exponential backoff — wait 1s, 2s, 4s, 8s between retries",
        },
        401: {
            "diagnosis": "Authentication token expired",
            "auto_action": "Refresh OAuth token immediately",
            "prevention": "Set token refresh 5 minutes before expiry",
        },
        403: {
            "diagnosis": "Insufficient permissions or account restriction",
            "auto_action": "Check API scopes and re-authorize with correct permissions",
            "prevention": "Audit required scopes before deployment",
        },
        500: {
            "diagnosis": "Platform server error (not your fault)",
            "auto_action": "Retry after 5 minutes with same payload",
            "prevention": "Implement webhook status check — retry on platform recovery",
        },
        400: {
            "diagnosis": "Invalid request payload",
            "auto_action": "Validate payload against current API schema",
            "prevention": "Add schema validation layer before every API call",
        },
    }

    recovery = recovery_map.get(error_code, {
        "diagnosis": f"Unknown error (code {error_code})",
        "auto_action": "Log full error, retry once, escalate if persists",
        "prevention": "Add comprehensive error logging for pattern analysis",
    })

    return {
        "action_type": action_type,
        "error_code": error_code,
        "context": context,
        "diagnosis": recovery["diagnosis"],
        "auto_recovery_action": recovery["auto_action"],
        "prevention_strategy": recovery["prevention"],
        "retry_recommended": error_code in [429, 500],
        "escalate_to_human": error_code in [401, 403],
        "timestamp": datetime.now().isoformat(),
    }
