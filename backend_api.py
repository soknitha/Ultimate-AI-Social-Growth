"""
GrowthOS AI v2.0 — Backend API
================================
FastAPI server exposing all 99 AI features as REST endpoints.
Run: uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import httpx
from datetime import datetime

# ─── AI Core Imports ─────────────────────────────────────────────────────────
from ai_core.strategy_agent  import (
    audit_account, generate_growth_strategy,
    build_audience_persona, forecast_growth, analyze_competitor, simulate_scenario,
)
from ai_core.content_engine  import (
    generate_viral_hook, generate_caption, generate_video_script,
    generate_hashtags, repurpose_content, micro_content_generator,
    analyze_content_lifecycle, generate_content_calendar,
)
from ai_core.analytics_ai    import (
    analyze_performance, explain_performance, calculate_roi,
    calculate_trust_score, generate_report, predict_best_posting_time,
    detect_audience_fatigue,
)
from ai_core.risk_engine      import (
    check_content_safety, detect_shadowban_signals,
    calculate_safe_limits, audit_account_health, self_heal_failed_action,
)
from ai_core.trend_radar      import (
    get_trending_topics, predict_upcoming_trends,
    fuse_cross_platform_signals, scan_opportunities, get_time_aware_strategy,
)
from ai_core.campaign_engine  import (
    create_campaign, schedule_posts, auto_optimize_campaign,
    optimize_budget, control_content_velocity,
)
from ai_core.multi_agent      import OrchestratorAgent
from ai_core.memory_system    import (
    store_brand_memory, retrieve_brand_context, store_campaign_result,
    get_campaign_history, store_post_result, get_top_performing_posts,
    get_memory_timeline, log_ai_decision, store_knowledge, search_knowledge,
)
from smm_panel.panel_client   import (
    get_services, check_balance, place_order, check_order_status,
    request_refill, cancel_orders, smart_order, geo_smart_order,
    get_panel_info, get_order_history,
)
from ai_core.geo_engine       import (
    list_all_countries, get_country_detail, search_locations,
    get_local_time, get_geo_strategy, get_best_times_by_timezone,
    get_regional_trends, get_cultural_content_guide,
    get_platform_availability, get_geo_audience_insights,
    get_multi_country_comparison,
)
from ai_core.inbox_engine     import (
    generate_ai_reply, analyze_message_sentiment, batch_analyze_sentiment,
    generate_reply_templates, simulate_inbox_messages, check_auto_reply_rules,
)
from ai_core.social_auth import (
    generate_oauth_url, exchange_code_for_token,
    connect_bot_token, connect_direct_token,
    test_account_connection, test_all_accounts,
    refresh_account_token, list_accounts, delete_account,
    get_platform_configs_public, _oauth_callbacks,
)
from ai_core.viral_engine import (
    predict_viral_score, find_influencers, research_hashtags, generate_ab_variants,
)
from ai_core.listening_engine import (
    simulate_brand_listening, analyze_competitor_profile, get_competitor_ad_intelligence,
)
from ai_core.automation_engine import (
    bulk_reply_comments, repurpose_content, generate_video_storyboard, generate_dm_templates,
)
from ai_core.business_intel import (
    detect_crisis, generate_crisis_response, forecast_growth_ml,
    analyze_brand_voice, optimize_youtube_seo, optimize_profile,
)
from ai_core.sales_engine import (
    map_sales_funnel, build_lead_magnet, generate_product_descriptions,
    generate_email_sequence, generate_ctas,
)
from ai_core.content_domination import (
    generate_viral_hooks, generate_short_script, plan_content_series,
    generate_thumbnail_concepts, generate_emotional_captions,
)
from ai_core.brand_authority import (
    audit_personal_brand, audit_content_performance, find_competitor_content_gap,
    build_audience_persona, get_algorithm_strategy,
)
from ai_core.community_engine import (
    plan_influencer_collab, plan_ugc_campaign, transform_testimonial_to_post,
    generate_community_playbook, plan_live_stream,
    hijack_trend, clone_viral_content, get_optimal_posting_times, scan_niche_opportunity,
)
from config import APP_NAME, APP_VERSION, APP_TAGLINE, USE_REAL_AI, USE_SMM_PANEL

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=f"{APP_NAME} Backend",
    version=APP_VERSION,
    description=APP_TAGLINE,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrator = OrchestratorAgent()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AccountData(BaseModel):
    username: str
    platform: str
    current_followers: int = Field(ge=0)
    niche: str
    goal_followers: Optional[int] = 0
    duration_days: Optional[int] = 30

class ContentData(BaseModel):
    topic: str
    platform: str
    tone: str = "Viral & Catchy"
    language: str = "English"
    duration_seconds: Optional[int] = 60

class AuditData(BaseModel):
    username: str
    platform: str
    followers: int = Field(ge=0)
    niche: str

class ForecastData(BaseModel):
    current_followers: int = Field(ge=0)
    engagement_rate: float = Field(ge=0.0, le=100.0)
    posting_frequency: int = Field(ge=1)
    platform: str
    months: Optional[int] = 3

class CompetitorData(BaseModel):
    competitor_username: str
    platform: str
    your_niche: str

class RiskCheckData(BaseModel):
    content: str
    platform: str = "General"

class PerformanceData(BaseModel):
    platform: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    follows: int = 0

class TrendData(BaseModel):
    platform: str
    niche: str
    region: Optional[str] = "Global"

class CampaignData(BaseModel):
    name: str
    platform: str
    niche: str
    goal: str
    budget_usd: float = Field(gt=0)
    duration_days: int = Field(ge=1)

class SMM_OrderData(BaseModel):
    service_id: int
    link: str
    quantity: int = Field(ge=1)

class SmartOrderData(BaseModel):
    link: str
    goal: str
    budget_usd: float = Field(gt=0)
    platform: str

class GeoSmartOrderData(BaseModel):
    link: str
    goal: str
    budget_usd: float        = Field(gt=0)
    platform: str
    geo_scope: str           = Field(default="Global")
    continent: str           = Field(default="")
    country: str             = Field(default="", max_length=5)
    state: str               = Field(default="", max_length=100)
    city: str                = Field(default="", max_length=100)
    language: str            = Field(default="")
    quality_tier: str        = Field(default="High Quality")
    real_human_only: bool    = Field(default=True)
    device: str              = Field(default="All")

class SMM_RefillData(BaseModel):
    order_id: int

class SMM_CancelData(BaseModel):
    order_ids: List[int]

class SMM_BulkStatusData(BaseModel):
    order_ids: List[int] = Field(max_length=100)

class GeoStrategyData(BaseModel):
    country_code: str = Field(default="KH", description="ISO 3166-1 alpha-2 country code")
    platform: str     = Field(default="TikTok")
    niche: str        = Field(default="General")

class GeoAudienceData(BaseModel):
    country_code: str = Field(default="KH")
    platform: str     = Field(default="TikTok")
    niche: str        = Field(default="General")

class GeoSearchData(BaseModel):
    query: str = Field(description="Country name, ISO code, or region")

class GeoCompareData(BaseModel):
    country_codes: List[str] = Field(description="Up to 10 ISO country codes", max_length=10)
    platform: str            = Field(default="TikTok")

class MemoryStoreData(BaseModel):
    brand_id: str
    data: dict

class MemoryQueryData(BaseModel):
    brand_id: str
    query: str

class ReportData(BaseModel):
    account_name: str
    platform: str
    period: str
    metrics: dict
    goals_achieved: Optional[List[str]] = []

class OrchestrateData(BaseModel):
    username: str
    platform: str
    followers: int = 0
    niche: str
    metrics: Optional[dict] = {}

# ─── Social Inbox Models ─────────────────────────────────────────────────────
class InboxSimulateData(BaseModel):
    platform: str = Field(default="TikTok")
    niche: str    = Field(default="Fitness")
    count: int    = Field(default=25, ge=1, le=50)

class InboxReplyData(BaseModel):
    message:    str
    platform:   str = "TikTok"
    tone:       str = "Friendly & Warm"
    brand_name: str = ""
    niche:      str = "General"
    language:   str = "English"
    context:    str = ""

class InboxSentimentData(BaseModel):
    message:  str
    platform: str = "General"

class InboxBatchSentimentData(BaseModel):
    messages: List[str] = Field(max_length=30)
    platform: str = "General"

class InboxTemplateData(BaseModel):
    niche:    str = "General"
    platform: str = "TikTok"
    tone:     str = "Friendly & Warm"
    language: str = "English"

class InboxRulesCheckData(BaseModel):
    message: str
    rules:   List[dict]


# ── Social Auth models ────────────────────────────────────────────────────────

class AuthGenerateURLData(BaseModel):
    platform:      str
    client_id:     str
    client_secret: Optional[str] = ""

class AuthExchangeData(BaseModel):
    platform:      str
    code:          str
    state:         str
    client_id:     Optional[str] = ""
    client_secret: Optional[str] = ""

class AuthBotTokenData(BaseModel):
    platform: str
    token:    str

class AuthTestData(BaseModel):
    account_id: str

class AuthRefreshData(BaseModel):
    account_id: str


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["System"])
def read_root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "tagline": APP_TAGLINE,
        "status": "🚀 All systems operational",
        "ai_enabled": USE_REAL_AI,
        "smm_panel_enabled": USE_SMM_PANEL,
        "features_count": 99,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "ai_mode": "OpenAI GPT-4o" if USE_REAL_AI else "Smart Mock AI",
        "smm_panel": "Live API" if USE_SMM_PANEL else "Demo Mode",
        "endpoints_available": 30,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/v1/dashboard", tags=["System"])
async def get_dashboard():
    """Returns summary dashboard data."""
    return {
        "status": "success",
        "data": {
            "quick_stats": {
                "total_features": 99,
                "ai_models_active": 1 if USE_REAL_AI else 0,
                "smm_services": 13,
                "platforms_supported": 7,
            },
            "recent_activity": [
                {"action": "AI Strategy Generated", "time": "2 min ago"},
                {"action": "Content Calendar Created", "time": "5 min ago"},
                {"action": "Trend Scan Completed",    "time": "12 min ago"},
            ],
            "system_tips": [
                "Set OPENAI_API_KEY in .env to activate real AI",
                "Set DEMOSMM_API_KEY to connect live SMM panel",
                "Set TELEGRAM_BOT_TOKEN to activate Telegram bot",
            ],
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1: AI STRATEGY BRAIN
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/audit", tags=["Strategy"])
async def api_audit_account(data: AuditData):
    """Feature #1: Deep account audit with AI health scoring."""
    try:
        result = await audit_account(data.username, data.platform, data.followers, data.niche)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/strategy", tags=["Strategy"])
async def api_create_strategy(data: AccountData):
    """Feature #1 + #80: Generate 30/60/90-day AI growth strategy."""
    try:
        result = await generate_growth_strategy(
            data.username, data.platform, data.current_followers,
            data.niche, data.goal_followers, data.duration_days,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/persona", tags=["Strategy"])
async def api_build_persona(data: AuditData):
    """Feature #5: Build Audience DNA persona."""
    try:
        result = await build_audience_persona(data.niche, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/forecast", tags=["Strategy"])
async def api_forecast_growth(data: ForecastData):
    """Feature #80: Predict 3-6 month growth trajectory."""
    try:
        result = await forecast_growth(
            data.current_followers, data.engagement_rate,
            data.posting_frequency, data.platform, data.months,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/competitor", tags=["Strategy"])
async def api_analyze_competitor(data: CompetitorData):
    """Feature #18 + #91: Competitor intelligence analysis."""
    try:
        result = await analyze_competitor(data.competitor_username, data.platform, data.your_niche)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2: AI CONTENT STUDIO
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/content", tags=["Content"])
async def api_generate_content(data: ContentData):
    """Feature #4: Full content package — hook + caption + hashtags + script."""
    try:
        hook_data    = await generate_viral_hook(data.topic, data.platform, data.language)
        caption_data = await generate_caption(data.topic, data.platform, data.tone, data.language)
        hashtag_data = await generate_hashtags(data.topic, data.topic, data.platform)
        script_data  = await generate_video_script(data.topic, data.duration_seconds or 60, data.tone, data.language)

        return {
            "status": "success",
            "data": {
                "hook":         hook_data.get("best_hook", ""),
                "all_hooks":    hook_data.get("hooks", []),
                "caption":      caption_data.get("caption", ""),
                "cta":          caption_data.get("cta", ""),
                "hashtags":     " ".join(hashtag_data.get("recommended_combo", [])[:20]),
                "video_script": "\n".join(
                    f"[{s['time']}] {s['dialogue']}" for s in script_data.get("script", [])
                ),
                "full_script":  script_data,
                "generated_at": datetime.now().isoformat(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/hook", tags=["Content"])
async def api_generate_hook(data: ContentData):
    """Feature #4: Generate 5 viral hooks."""
    try:
        result = await generate_viral_hook(data.topic, data.platform, data.language)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/script", tags=["Content"])
async def api_generate_script(data: ContentData):
    """Feature #4: Full video script with timestamps."""
    try:
        result = await generate_video_script(
            data.topic, data.duration_seconds or 60, data.tone, data.language,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/hashtags", tags=["Content"])
async def api_generate_hashtags(data: ContentData):
    """Feature #4: Smart hashtag clustering (20 optimized hashtags)."""
    try:
        result = await generate_hashtags(data.topic, data.topic, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/micro-content", tags=["Content"])
async def api_micro_content(data: ContentData):
    """Feature #88: Break 1 idea into 20 micro-content pieces."""
    try:
        result = await micro_content_generator(data.topic, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/calendar", tags=["Content"])
async def api_content_calendar(data: ContentData):
    """Generate 14-day content calendar."""
    try:
        result = await generate_content_calendar(data.topic, data.platform, 14, data.language)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 3: ANALYTICS COPILOT
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/performance", tags=["Analytics"])
async def api_analyze_performance(data: PerformanceData):
    """Feature #3 + #6: Deep performance analysis with AI insights."""
    try:
        metrics = data.model_dump()
        platform = metrics.pop("platform")
        result = await analyze_performance(metrics, platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/report", tags=["Analytics"])
async def api_generate_report(data: ReportData):
    """Feature #11: Generate comprehensive performance report."""
    try:
        result = await generate_report(
            data.account_name, data.platform, data.period,
            data.metrics, data.goals_achieved,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/timing/{platform}", tags=["Analytics"])
def api_best_posting_time(platform: str, niche: str = ""):
    """Feature #89: Predict optimal posting times."""
    result = predict_best_posting_time(platform, niche=niche)
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 4: RISK & COMPLIANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/risk", tags=["Risk"])
async def api_risk_check(data: RiskCheckData):
    """Feature #97 + #6: Scan content for policy violations & safety risks."""
    try:
        result = check_content_safety(data.content, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/safe-limits/{platform}/{followers}", tags=["Risk"])
def api_safe_limits(platform: str, followers: int):
    """Feature #6: Calculate safe daily growth limits."""
    result = calculate_safe_limits(followers, platform)
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 5: TREND RADAR
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/trends", tags=["Trends"])
async def api_trending_topics(data: TrendData):
    """Feature #12: Detect trending topics in real-time."""
    try:
        result = await get_trending_topics(data.platform, data.niche, data.region)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/predict-trends", tags=["Trends"])
async def api_predict_trends(data: TrendData):
    """Feature #8 advanced: Predict upcoming trends."""
    try:
        result = await predict_upcoming_trends(data.platform, data.niche)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/opportunities/{platform}/{niche}", tags=["Trends"])
async def api_opportunities(platform: str, niche: str):
    """Feature #20: Scan for immediate growth opportunities."""
    try:
        result = await scan_opportunities(platform, niche)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/time-strategy/{platform}", tags=["Trends"])
def api_time_strategy(platform: str, niche: str = ""):
    """Feature #25: Get time-aware posting strategy for RIGHT NOW."""
    result = get_time_aware_strategy(platform, niche)
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 6: CAMPAIGN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/campaign", tags=["Campaign"])
async def api_create_campaign(data: CampaignData):
    """Feature #7: Create full autonomous campaign plan."""
    try:
        result = await create_campaign(
            data.name, data.platform, data.niche,
            data.goal, data.budget_usd, data.duration_days,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 7: MULTI-AGENT ORCHESTRATION (Feature #99)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/orchestrate", tags=["MultiAgent"])
async def api_orchestrate(data: OrchestrateData):
    """Feature #99: Run full multi-agent AI team analysis."""
    try:
        account_data = {
            "username": data.username,
            "platform": data.platform,
            "current_followers": data.followers,
            "niche": data.niche,
        }
        result = await _orchestrator.run_full_analysis(account_data, data.metrics)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 8: SMM PANEL
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/smm/services", tags=["SMM Panel"])
async def api_smm_services(category: str = None):
    """List all SMM services from demosmm.com."""
    try:
        result = await get_services(category)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/smm/balance", tags=["SMM Panel"])
async def api_smm_balance():
    """Check SMM panel account balance."""
    try:
        result = await check_balance()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/order", tags=["SMM Panel"])
async def api_smm_place_order(data: SMM_OrderData):
    """Place a new SMM order."""
    try:
        result = await place_order(data.service_id, data.link, data.quantity)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/smart-order", tags=["SMM Panel"])
async def api_smm_smart_order(data: SmartOrderData):
    """Feature #2: AI-optimized order selection."""
    try:
        result = await smart_order(data.link, data.goal, data.budget_usd, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/geo-smart-order", tags=["SMM Panel"])
async def api_smm_geo_smart_order(data: GeoSmartOrderData):
    """AI Geo-Targeted Smart Order — finds highest-quality real-human service matching exact location."""
    try:
        result = await geo_smart_order(
            link=data.link,
            goal=data.goal,
            budget_usd=data.budget_usd,
            platform=data.platform,
            geo_scope=data.geo_scope,
            continent=data.continent,
            country=data.country,
            state=data.state,
            city=data.city,
            language=data.language,
            quality_tier=data.quality_tier,
            real_human_only=data.real_human_only,
            device=data.device,
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/smm/order/{order_id}", tags=["SMM Panel"])
async def api_smm_order_status(order_id: int):
    """Check SMM order status."""
    try:
        result = await check_order_status([order_id])
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/bulk-status", tags=["SMM Panel"])
async def api_smm_bulk_status(data: SMM_BulkStatusData):
    """Check status of multiple orders at once (max 100)."""
    try:
        result = await check_order_status(data.order_ids)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/refill", tags=["SMM Panel"])
async def api_smm_refill(data: SMM_RefillData):
    """Request refill for a completed order."""
    try:
        result = await request_refill(data.order_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/smm/cancel", tags=["SMM Panel"])
async def api_smm_cancel(data: SMM_CancelData):
    """Cancel one or more pending SMM orders."""
    try:
        result = await cancel_orders(data.order_ids)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/smm/history", tags=["SMM Panel"])
async def api_smm_history(limit: int = 50):
    """Return order history (live or demo)."""
    try:
        result = await get_order_history(limit)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/smm/panel-info", tags=["SMM Panel"])
async def api_smm_panel_info():
    """Return panel connection status (live vs demo, API URL, library)."""
    try:
        result = await get_panel_info()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 9: MEMORY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/memory/store-brand", tags=["Memory"])
def api_store_brand(data: MemoryStoreData):
    """Store brand memory (voice, niche, style, audience)."""
    result = store_brand_memory(data.brand_id, data.data)
    return {"status": "success", "data": result}

@app.get("/api/v1/memory/brand/{brand_id}", tags=["Memory"])
def api_get_brand(brand_id: str):
    """Retrieve brand memory context."""
    result = retrieve_brand_context(brand_id)
    return {"status": "success", "data": result}

@app.post("/api/v1/memory/search", tags=["Memory"])
def api_search_memory(data: MemoryQueryData):
    """Search brand knowledge base."""
    result = search_knowledge(data.brand_id, data.query)
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 10: GEO INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/geo/countries", tags=["Geo Intelligence"])
async def api_geo_countries():
    """List all 60+ supported countries with market stats."""
    return {"status": "success", "data": list_all_countries()}

@app.get("/api/v1/geo/country/{country_code}", tags=["Geo Intelligence"])
async def api_geo_country(country_code: str):
    """Full country detail: timezone, languages, platforms, cultural tips, local time."""
    result = get_country_detail(country_code.upper())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.get("/api/v1/geo/local-time/{country_code}", tags=["Geo Intelligence"])
async def api_geo_local_time(country_code: str):
    """Get exact current local time in a target country."""
    result = get_local_time(country_code.upper())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.post("/api/v1/geo/search", tags=["Geo Intelligence"])
async def api_geo_search(data: GeoSearchData):
    """Search for countries by name, ISO code, or region."""
    results = search_locations(data.query)
    return {"status": "success", "data": results, "count": len(results)}

@app.post("/api/v1/geo/strategy", tags=["Geo Intelligence"])
async def api_geo_strategy(data: GeoStrategyData):
    """
    Feature #26: AI-powered geo-targeted growth strategy.
    Returns platform-specific strategy tailored to the target country.
    """
    result = await get_geo_strategy(data.country_code, data.platform, data.niche)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.get("/api/v1/geo/best-times/{country_code}/{platform}", tags=["Geo Intelligence"])
async def api_geo_best_times(country_code: str, platform: str):
    """
    Feature #28: Timezone-aware best posting times for a country + platform.
    Returns local times AND UTC equivalents.
    """
    result = await get_best_times_by_timezone(country_code.upper(), platform)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.get("/api/v1/geo/trends/{country_code}", tags=["Geo Intelligence"])
async def api_geo_trends(country_code: str, niche: str = "General"):
    """
    Feature #27: Regional trend intelligence for a specific country.
    Returns country-specific trending topics, local events, and content angles.
    """
    result = await get_regional_trends(country_code.upper(), niche)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.get("/api/v1/geo/cultural-guide/{country_code}", tags=["Geo Intelligence"])
async def api_geo_cultural_guide(country_code: str, niche: str = "General"):
    """
    Feature #29: Cultural content guide — what to say, how, and what to avoid.
    """
    result = await get_cultural_content_guide(country_code.upper(), niche)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.get("/api/v1/geo/platforms/{country_code}", tags=["Geo Intelligence"])
async def api_geo_platforms(country_code: str):
    """
    Feature #30: Platform availability and dominance map for a country.
    Shows which platforms are blocked, dominant, or growing.
    """
    result = await get_platform_availability(country_code.upper())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.post("/api/v1/geo/audience", tags=["Geo Intelligence"])
async def api_geo_audience(data: GeoAudienceData):
    """
    Feature #31: Regional audience demographics and psychographics.
    """
    result = await get_geo_audience_insights(data.country_code, data.platform, data.niche)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}

@app.post("/api/v1/geo/compare", tags=["Geo Intelligence"])
async def api_geo_compare(data: GeoCompareData):
    """Compare multiple countries side-by-side for a specific platform."""
    result = await get_multi_country_comparison(data.country_codes, data.platform)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 11: SOCIAL INBOX & AI AUTO-REPLY
# Feature #100: Unified Inbox  #101: AI Smart Reply  #102: Auto-Reply Rules
# Feature #103: Reply Templates  #104: Sentiment Analyzer
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/inbox/messages", tags=["Social Inbox"])
async def api_inbox_messages(data: InboxSimulateData):
    """Feature #100: Load/simulate inbox messages from a social platform."""
    try:
        messages = simulate_inbox_messages(data.platform, data.niche, data.count)
        unread   = sum(1 for m in messages if m["status"] == "Unread")
        high_pri = sum(1 for m in messages if "High" in m.get("priority", ""))
        return {
            "status": "success",
            "data": {
                "messages":     messages,
                "total":        len(messages),
                "unread":       unread,
                "high_priority": high_pri,
                "platform":     data.platform,
                "source":       "demo",
                "note":         "Connect real platform APIs via webhooks for live data.",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inbox/ai-reply", tags=["Social Inbox"])
async def api_inbox_ai_reply(data: InboxReplyData):
    """Feature #101: Generate AI smart reply for a message/comment."""
    try:
        result = await generate_ai_reply(
            data.message, data.platform, data.tone,
            data.brand_name, data.niche, data.language, data.context,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inbox/sentiment", tags=["Social Inbox"])
async def api_inbox_sentiment(data: InboxSentimentData):
    """Feature #104: Analyze sentiment, intent, urgency of a single message."""
    try:
        result = await analyze_message_sentiment(data.message, data.platform)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inbox/sentiment-batch", tags=["Social Inbox"])
async def api_inbox_sentiment_batch(data: InboxBatchSentimentData):
    """Feature #104: Batch sentiment analysis for up to 30 messages at once."""
    try:
        results = await batch_analyze_sentiment(data.messages, data.platform)
        positives = sum(1 for r in results if r.get("sentiment") == "Positive")
        negatives = sum(1 for r in results if r.get("sentiment") == "Negative")
        return {
            "status": "success",
            "data": {
                "results":    results,
                "total":      len(results),
                "positives":  positives,
                "negatives":  negatives,
                "neutrals":   len(results) - positives - negatives,
                "summary":    f"{positives} positive, {negatives} negative, {len(results)-positives-negatives} neutral",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inbox/templates", tags=["Social Inbox"])
async def api_inbox_templates(data: InboxTemplateData):
    """Feature #103: Generate full reply templates library (10 categories × 3 templates)."""
    try:
        result = await generate_reply_templates(
            data.niche, data.platform, data.tone, data.language,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inbox/check-rules", tags=["Social Inbox"])
def api_inbox_check_rules(data: InboxRulesCheckData):
    """Feature #102: Check if a message matches any auto-reply rule."""
    result = check_auto_reply_rules(data.message, data.rules)
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# SOCIAL AUTH ENDPOINTS   (Features #105–#110)
# ═══════════════════════════════════════════════════════════════════════════════

# OAuth 2.0 callback capture — browser redirects here after user authorizes
@app.get("/oauth/callback", response_class=HTMLResponse, tags=["Social Auth"])
async def oauth_callback(code: str = "", state: str = "", error: str = ""):
    """Capture OAuth authorization code from browser redirect."""
    if error:
        _oauth_callbacks[state] = {"error": error, "captured_at": datetime.now().isoformat()}
        return HTMLResponse(
            "<html><body style='font-family:sans-serif;text-align:center;padding:60px;"
            "background:#1E1E2E;color:#CDD6F4'>"
            "<h2 style='color:#F38BA8'>❌ Authorization Failed</h2>"
            f"<p>Error: {error}</p><p>You can close this window and return to GrowthOS.</p>"
            "</body></html>"
        )
    if code and state:
        _oauth_callbacks[state] = {"code": code, "captured_at": datetime.now().isoformat()}
        return HTMLResponse(
            "<html><body style='font-family:sans-serif;text-align:center;padding:60px;"
            "background:#1E1E2E;color:#CDD6F4'>"
            "<h2 style='color:#A6E3A1'>✅ Authorization Successful!</h2>"
            "<p>Return to <strong>GrowthOS AI</strong> and click <strong>Complete Connection</strong>.</p>"
            "<p style='color:#6C7086;font-size:12px'>This window will close automatically…</p>"
            "<script>setTimeout(() => window.close(), 4000);</script>"
            "</body></html>"
        )
    return HTMLResponse("<html><body><h2>⚠ No authorization code received</h2></body></html>")


@app.get("/api/v1/auth/poll-callback/{state}", tags=["Social Auth"])
async def poll_oauth_callback(state: str):
    """Poll for a captured OAuth callback code (called by desktop after browser redirect)."""
    data = _oauth_callbacks.get(state)
    if data:
        if "error" in data:
            del _oauth_callbacks[state]
            return {"captured": False, "error": data["error"]}
        return {"captured": True, "code": data.get("code", ""), "state": state}
    return {"captured": False}


@app.get("/api/v1/auth/platforms", tags=["Social Auth"])
def api_auth_platforms():
    """Feature #105: Return all supported platform configs for the UI."""
    return {"status": "success", "data": get_platform_configs_public()}


@app.get("/api/v1/auth/accounts", tags=["Social Auth"])
def api_auth_list_accounts(platform: str = Query(default="")):
    """Feature #108: List all connected social accounts (tokens masked)."""
    accounts = list_accounts(platform)
    return {"status": "success", "data": accounts, "total": len(accounts)}


@app.post("/api/v1/auth/generate-url", tags=["Social Auth"])
def api_auth_generate_url(data: AuthGenerateURLData):
    """Feature #105: Generate OAuth 2.0 authorization URL for a platform."""
    result = generate_oauth_url(data.platform, data.client_id, data.client_secret or "")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


@app.post("/api/v1/auth/exchange", tags=["Social Auth"])
async def api_auth_exchange(data: AuthExchangeData):
    """Feature #105: Exchange OAuth code for access token and store account."""
    result = await exchange_code_for_token(
        data.platform, data.code, data.state,
        data.client_id or "", data.client_secret or "",
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


@app.post("/api/v1/auth/connect-bot", tags=["Social Auth"])
async def api_auth_connect_bot(data: AuthBotTokenData):
    """Feature #110: Connect a Telegram bot token or similar API key."""
    result = await connect_bot_token(data.platform, data.token)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


@app.post("/api/v1/auth/connect-token", tags=["Social Auth"])
async def api_auth_connect_token(data: AuthBotTokenData):
    """
    Feature #106b: Connect any platform using a pre-obtained access token.
    Works with Facebook/Instagram tokens from Graph API Explorer, YouTube tokens
    from OAuth Playground, etc.  No App ID or App Secret required.
    """
    result = await connect_direct_token(data.platform, data.token)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


@app.post("/api/v1/auth/test", tags=["Social Auth"])
async def api_auth_test(data: AuthTestData):
    """Feature #109: Test whether a stored account token is still valid."""
    result = await test_account_connection(data.account_id)
    return {"status": "success", "data": result}


@app.post("/api/v1/auth/test-all", tags=["Social Auth"])
async def api_auth_test_all():
    """Feature #109: Test all stored accounts concurrently."""
    results = await test_all_accounts()
    connected = sum(1 for r in results if r.get("status") == "connected")
    return {"status": "success", "data": results, "connected": connected, "total": len(results)}


@app.post("/api/v1/auth/refresh", tags=["Social Auth"])
async def api_auth_refresh(data: AuthRefreshData):
    """Feature #107: Refresh an expired access token using stored refresh token."""
    result = await refresh_account_token(data.account_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "data": result}


@app.delete("/api/v1/auth/account/{account_id}", tags=["Social Auth"])
def api_auth_delete(account_id: str):
    """Feature #108: Permanently delete a connected account and its tokens."""
    result = delete_account(account_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# SOCIAL MEDIA MANAGER — Features #111–#120
# ═══════════════════════════════════════════════════════════════════════════════

class SocialAdExpertData(BaseModel):
    question:      str
    platform:      str = "General"
    niche:         str = "General"
    budget_usd:    float = 0.0
    objective:     str = "Awareness"
    language:      str = "English"

class SocialAdCopyData(BaseModel):
    product:       str
    platform:      str = "Facebook"
    objective:     str = "Conversions"
    target_audience: str = ""
    tone:          str = "Professional"
    language:      str = "English"
    variants:      int = Field(default=3, ge=1, le=6)

class SocialPostData(BaseModel):
    topic:         str
    platform:      str = "Instagram"
    tone:          str = "Engaging"
    language:      str = "English"
    include_hashtags: bool = True
    include_cta:   bool = True
    post_type:     str = "Standard"   # Standard | Reel | Story | Carousel

class SocialCampaignPlanData(BaseModel):
    brand:         str
    platform:      str = "Facebook"
    objective:     str = "Lead Generation"
    budget_usd:    float = Field(default=500.0, gt=0)
    duration_days: int   = Field(default=30, ge=1)
    target_audience: str = ""
    niche:         str = "General"
    language:      str = "English"

class SocialAudienceData(BaseModel):
    platform:      str = "Facebook"
    niche:         str = "E-commerce"
    country:       str = "Global"
    age_range:     str = "18-35"
    language:      str = "English"

class SocialInsightsData(BaseModel):
    platform:      str = "Instagram"
    account_name:  str = ""
    followers:     int = Field(default=0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0.0)
    impressions:   int = Field(default=0, ge=0)
    reach:         int = Field(default=0, ge=0)
    clicks:        int = Field(default=0, ge=0)
    spend_usd:     float = Field(default=0.0, ge=0.0)


@app.post("/api/v1/social/ai-ads-expert", tags=["Social Manager"])
async def api_social_ads_expert(data: SocialAdExpertData):
    """Feature #111: AI Ads Expert — ask any advertising question and get expert-level guidance."""
    import asyncio
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    if not USE_AI or not LLM_CLIENT:
        return {"status": "ok", "answer": (
            f"[AI Ads Expert – Demo Mode]\n\n"
            f"Platform: {data.platform} | Objective: {data.objective} | Budget: ${data.budget_usd}\n\n"
            f"Question: {data.question}\n\n"
            f"Answer: For {data.platform} with a ${data.budget_usd} budget targeting {data.niche}, "
            f"focus on {data.objective.lower()} campaigns. Start with broad audience testing, "
            f"allocate 20% for A/B testing creatives, and optimize CPM before scaling. "
            f"Use retargeting for warm audiences once you have 1,000+ impressions. "
            f"Monitor frequency — keep it under 3x per week. Rotate ad creatives every 7–10 days."
        )}
    system = (
        "You are an elite social media advertising expert with 15+ years of experience managing "
        "multi-million dollar campaigns across Facebook, Instagram, TikTok, YouTube, LinkedIn, and Twitter/X. "
        "You specialize in performance marketing, audience targeting, creative strategy, budget optimization, "
        "retargeting funnels, and ROAS maximization. Provide concise, actionable, expert advice. "
        "When relevant, include platform-specific tips, benchmarks, and best practices. "
        f"The user's language preference: {data.language}. Always answer in that language."
    )
    user_msg = (
        f"Platform: {data.platform}\nObjective: {data.objective}\n"
        f"Budget: ${data.budget_usd}\nNiche: {data.niche}\n\n"
        f"Question: {data.question}"
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
        temperature=0.6, max_tokens=1200,
    )
    return {"status": "ok", "answer": resp.choices[0].message.content}


@app.post("/api/v1/social/generate-ad-copy", tags=["Social Manager"])
async def api_social_ad_copy(data: SocialAdCopyData):
    """Feature #112: Generate high-converting ad copy variants for any platform."""
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    if not USE_AI or not LLM_CLIENT:
        variants = [
            f"Variant {i+1}: 🔥 {'[Product]'.replace('[Product]', data.product)} — "
            f"Transform your results today! {data.target_audience or 'Perfect for everyone'}. "
            f"Limited offer — Act now! [CTA: {'Shop Now' if data.objective=='Conversions' else 'Learn More'}]"
            for i in range(data.variants)
        ]
        return {"status": "ok", "variants": variants, "platform_tips": f"Optimal for {data.platform}: Use visuals with text overlay under 20%."}
    system = (
        f"You are an expert copywriter specializing in high-converting {data.platform} ad copy. "
        f"Write {data.variants} distinct ad copy variants for the given product. "
        f"Each variant must have: Headline (max 40 chars), Primary Text (max 125 chars), Description (max 30 chars), CTA. "
        f"Format each as: VARIANT N:\\nHeadline: ...\\nPrimary Text: ...\\nDescription: ...\\nCTA: ...\\n "
        f"Tone: {data.tone}. Objective: {data.objective}. Language: {data.language}."
    )
    prompt = (
        f"Product/Service: {data.product}\nTarget Audience: {data.target_audience or 'General'}\n"
        f"Platform: {data.platform}\nObjective: {data.objective}\nVariants needed: {data.variants}"
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.8, max_tokens=900,
    )
    raw = resp.choices[0].message.content
    platform_tips = {
        "Facebook": "Use 1200×628px images. Keep text under 20% of image area. Best CTRs: 0.9–1.5%.",
        "Instagram": "Square (1080×1080) or vertical (1080×1350). Stories: 1080×1920. Avg CPC: $0.50–$1.00.",
        "TikTok":    "Vertical 9:16 video only. First 3 seconds are critical. Hook fast, CTA at end.",
        "YouTube":   "Skippable ads: 15–20s. Non-skippable: 15s max. Bumpers: 6s. High brand recall.",
        "LinkedIn":  "Text ads work well for B2B. Sponsored content: 1200×627px. CPC avg $5–$12.",
        "Twitter/X": "Promoted tweets. Image: 800×418px. Video: up to 2m20s. Best for engagement.",
    }.get(data.platform, "Follow platform creative guidelines for best results.")
    return {"status": "ok", "copy": raw, "platform_tips": platform_tips}


@app.post("/api/v1/social/generate-post", tags=["Social Manager"])
async def api_social_generate_post(data: SocialPostData):
    """Feature #113: Generate optimized social media post content for any platform."""
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    if not USE_AI or not LLM_CLIENT:
        hashtags = "#viral #trending #fyp #growth #socialmedia" if data.include_hashtags else ""
        cta = "\n\n👇 What do you think? Drop a comment below!" if data.include_cta else ""
        return {"status": "ok", "post": f"🔥 {data.topic}\n\nCaption text here for {data.platform}...{cta}\n{hashtags}"}
    char_limits = {"Twitter/X": "280 chars", "Instagram": "2200 chars", "Facebook": "63206 chars",
                   "TikTok": "2200 chars", "LinkedIn": "3000 chars", "YouTube": "5000 chars"}
    char_note = char_limits.get(data.platform, "no strict limit")
    system = (
        f"You are an expert {data.platform} content creator. Write a {data.tone.lower()} "
        f"{data.post_type} post. Platform character limit: {char_note}. "
        f"{'Include 5–10 relevant hashtags.' if data.include_hashtags else 'No hashtags.'} "
        f"{'End with a compelling CTA.' if data.include_cta else ''} "
        f"Language: {data.language}. Format perfectly for {data.platform}."
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": f"Topic: {data.topic}"}],
        temperature=0.85, max_tokens=600,
    )
    return {"status": "ok", "post": resp.choices[0].message.content}


@app.post("/api/v1/social/plan-campaign", tags=["Social Manager"])
async def api_social_plan_campaign(data: SocialCampaignPlanData):
    """Feature #114: Generate a full AI-powered advertising campaign plan with targeting, budget allocation, and timeline."""
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    if not USE_AI or not LLM_CLIENT:
        return {"status": "ok", "plan": (
            f"CAMPAIGN PLAN: {data.brand} on {data.platform}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Objective: {data.objective}\nBudget: ${data.budget_usd} / {data.duration_days} days\n"
            f"Daily budget: ${data.budget_usd/data.duration_days:.2f}\n\n"
            f"PHASE 1 (Days 1-7): Awareness & Testing — 30% budget\n"
            f"  • A/B test 2-3 ad creatives with broad audience\n"
            f"  • Target: {data.target_audience or 'Broad demographic'}\n\n"
            f"PHASE 2 (Days 8-21): Optimization — 40% budget\n"
            f"  • Scale winning creatives, pause underperformers\n"
            f"  • Add lookalike audiences from engaged users\n\n"
            f"PHASE 3 (Days 22-{data.duration_days}): Scaling — 30% budget\n"
            f"  • Retargeting + lookalike at 2x-3x scale\n"
            f"  • Dynamic ads for personalization\n\n"
            f"KPIs: CTR > 1.5%, CPC < $1.20, ROAS > 3x\nExpected reach: ~{int(data.budget_usd*850):,}"
        )}
    system = (
        "You are a senior performance marketing strategist. Create a detailed, actionable paid advertising "
        "campaign plan. Include: campaign structure, targeting strategy, audience segmentation, creative guidelines, "
        "budget allocation by phase, bidding strategy, KPIs, optimization schedule, expected results, and scaling triggers. "
        f"Language: {data.language}. Be specific and data-driven."
    )
    prompt = (
        f"Brand: {data.brand}\nPlatform: {data.platform}\nObjective: {data.objective}\n"
        f"Total Budget: ${data.budget_usd}\nDuration: {data.duration_days} days\n"
        f"Daily Budget: ${data.budget_usd/data.duration_days:.2f}\n"
        f"Target Audience: {data.target_audience or 'To be determined'}\nNiche: {data.niche}"
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.5, max_tokens=1500,
    )
    return {"status": "ok", "plan": resp.choices[0].message.content}


@app.post("/api/v1/social/audience-targeting", tags=["Social Manager"])
async def api_social_audience(data: SocialAudienceData):
    """Feature #115: AI-powered audience targeting recommendations with interest/behavior/demographic breakdown."""
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    if not USE_AI or not LLM_CLIENT:
        return {"status": "ok", "targeting": (
            f"AUDIENCE TARGETING: {data.niche} on {data.platform}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Demographics: Age {data.age_range}, {data.country}\n"
            f"Core Interests: Online shopping, {data.niche}, Mobile apps\n"
            f"Behaviors: Online buyers, Engaged shoppers, Tech-savvy users\n"
            f"Lookalike: 1-2% of your customer list\nRetargeting: Website visitors (30d), Video viewers (75%)\n"
            f"Exclusions: Existing customers, Recent converters\nEstimated CPM: $8-15 | CPC: $0.50-1.50"
        )}
    system = (
        f"You are an expert {data.platform} ads targeting specialist. Provide highly specific audience targeting "
        f"recommendations including: core interests, behaviors, demographics, lookalike audiences, retargeting layers, "
        f"negative audiences, and estimated CPM/CPC ranges. Use {data.platform}-specific targeting options. "
        f"Language: {data.language}."
    )
    prompt = (
        f"Platform: {data.platform}\nNiche: {data.niche}\nCountry: {data.country}\n"
        f"Age Range: {data.age_range}\nProvide complete targeting strategy."
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.5, max_tokens=1000,
    )
    return {"status": "ok", "targeting": resp.choices[0].message.content}


@app.post("/api/v1/social/analyze-insights", tags=["Social Manager"])
async def api_social_insights(data: SocialInsightsData):
    """Feature #116: AI analysis of social media/ad performance with optimization recommendations."""
    from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
    ctr   = round((data.clicks / data.impressions * 100) if data.impressions > 0 else 0, 2)
    cpc   = round((data.spend_usd / data.clicks) if data.clicks > 0 else 0, 2)
    er    = data.engagement_rate
    roas  = round((data.impressions * 0.02 * 15 / data.spend_usd) if data.spend_usd > 0 else 0, 2)
    if not USE_AI or not LLM_CLIENT:
        return {"status": "ok", "analysis": (
            f"PERFORMANCE ANALYSIS — {data.platform}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Followers: {data.followers:,} | Engagement Rate: {er:.1f}%\n"
            f"Impressions: {data.impressions:,} | Reach: {data.reach:,}\n"
            f"Clicks: {data.clicks:,} | CTR: {ctr}% | CPC: ${cpc:.2f}\n"
            f"Ad Spend: ${data.spend_usd:.2f} | Est. ROAS: {roas:.1f}x\n\n"
            f"ASSESSMENT: {'Excellent' if er > 4 else 'Good' if er > 2 else 'Needs improvement'}\n"
            f"RECOMMENDATION: {'Scale budget by 20%' if ctr > 1.5 else 'Refresh creatives and test new audiences'}"
        )}
    system = (
        f"You are an expert {data.platform} performance marketing analyst. "
        f"Analyze the metrics provided and give: (1) performance assessment, (2) what's working, "
        f"(3) what needs improvement, (4) specific actionable recommendations, (5) next steps to optimize."
    )
    prompt = (
        f"Platform: {data.platform} | Account: {data.account_name or 'N/A'}\n"
        f"Followers: {data.followers:,} | Engagement Rate: {er:.2f}%\n"
        f"Impressions: {data.impressions:,} | Reach: {data.reach:,}\n"
        f"Clicks: {data.clicks:,} | CTR: {ctr}% | CPC: ${cpc:.2f}\n"
        f"Ad Spend: ${data.spend_usd:.2f} | Estimated ROAS: {roas:.1f}x"
    )
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.4, max_tokens=900,
    )
    return {"status": "ok", "analysis": resp.choices[0].message.content}


# ═══════════════════════════════════════════════════════════════════════════════
# PRIORITY 1–4 FEATURES  (#121–#140)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Pydantic Models ──────────────────────────────────────────────────────────

class ViralScoreData(BaseModel):
    content:     str
    platform:    str = "TikTok"
    post_type:   str = "Video"
    followers:   int = Field(default=10000, ge=0)
    niche:       str = "General"
    language:    str = "English"

class InfluencerData(BaseModel):
    niche:          str
    platform:       str = "Instagram"
    follower_range: str = "10K–100K"
    country:        str = "Global"
    language:       str = "English"

class HashtagData(BaseModel):
    niche:    str
    platform: str = "Instagram"
    goal:     str = "Reach"
    language: str = "English"

class ABTestData(BaseModel):
    content:   str
    platform:  str = "Instagram"
    objective: str = "Engagement"
    language:  str = "English"

class BrandListeningData(BaseModel):
    brand:    str
    platform: str = "All Platforms"
    period:   str = "Last 7 days"
    niche:    str = "General"
    language: str = "English"

class CompetitorProfileData(BaseModel):
    competitor: str
    platform:   str = "Instagram"
    niche:      str = "General"
    language:   str = "English"

class CompetitorAdsData(BaseModel):
    competitor: str
    platform:   str = "Facebook"
    niche:      str = "General"
    language:   str = "English"

class CommentReplyData(BaseModel):
    comments:   List[str] = Field(max_length=25)
    tone:       str = "Friendly & Warm"
    brand_name: str = ""
    platform:   str = "Instagram"
    language:   str = "English"

class RepurposeData(BaseModel):
    original:       str
    source_format:  str = "Blog Post"
    target_formats: Optional[List[str]] = None
    brand_name:     str = ""
    niche:          str = "General"
    language:       str = "English"

class StoryboardData(BaseModel):
    topic:            str
    platform:         str = "TikTok"
    duration_seconds: int = Field(default=60, ge=15, le=600)
    style:            str = "Educational"
    niche:            str = "General"
    language:         str = "English"

class DMTemplateData(BaseModel):
    purpose:    str = "Influencer Outreach"
    platform:   str = "Instagram"
    brand_name: str = ""
    niche:      str = "General"
    tone:       str = "Professional"
    count:      int = Field(default=5, ge=1, le=10)
    language:   str = "English"

class CrisisDetectData(BaseModel):
    comments_text: str
    brand:         str = ""
    platform:      str = "General"
    language:      str = "English"

class CrisisResponseData(BaseModel):
    brand:              str
    crisis_description: str
    tone:               str = "Empathetic & Professional"
    platform:           str = "General"
    language:           str = "English"

class GrowthForecastData(BaseModel):
    current_followers:    int   = Field(default=1000, ge=0)
    platform:             str   = "Instagram"
    monthly_growth_rate:  float = Field(default=5.0, ge=0.1, le=100.0)
    posting_freq:         int   = Field(default=7, ge=1)
    engagement_rate:      float = Field(default=3.5, ge=0.0)
    months:               int   = Field(default=6, ge=1, le=24)

class BrandVoiceData(BaseModel):
    samples:    str
    brand_name: str = ""
    language:   str = "English"

class YouTubeSEOData(BaseModel):
    title:          str
    description:    str = ""
    tags:           str = ""
    target_keyword: str
    niche:          str = "General"
    language:       str = "English"

class ProfileOptData(BaseModel):
    platform:    str
    current_bio: str
    niche:       str
    goals:       str
    username:    str = ""
    language:    str = "English"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/v1/viral/score", tags=["Viral & Growth"])
async def api_viral_score(data: ViralScoreData):
    """Feature #121: AI Viral Score Predictor — predict virality before posting."""
    result = await predict_viral_score(
        data.content, data.platform, data.post_type,
        data.followers, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/viral/influencers", tags=["Viral & Growth"])
async def api_find_influencers(data: InfluencerData):
    """Feature #122: Influencer Finder — discover relevant influencers for any niche."""
    result = await find_influencers(
        data.niche, data.platform, data.follower_range, data.country, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/viral/hashtags", tags=["Viral & Growth"])
async def api_hashtag_research(data: HashtagData):
    """Feature #123: Hashtag Research Engine with difficulty scores and banned detection."""
    result = await research_hashtags(data.niche, data.platform, data.goal, data.language)
    return {"status": "ok", "data": result}


@app.post("/api/v1/viral/ab-test", tags=["Viral & Growth"])
async def api_ab_test(data: ABTestData):
    """Feature #124: A/B Test Generator — 3 variants with predicted winner."""
    result = await generate_ab_variants(data.content, data.platform, data.objective, data.language)
    return {"status": "ok", "data": result}


@app.post("/api/v1/intel/brand-listening", tags=["Intelligence"])
async def api_brand_listening(data: BrandListeningData):
    """Feature #125: Social Listening — brand mention monitoring and sentiment analysis."""
    result = await simulate_brand_listening(
        data.brand, data.platform, data.period, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/intel/competitor-profile", tags=["Intelligence"])
async def api_competitor_profile(data: CompetitorProfileData):
    """Feature #126: Competitor Intelligence — deep profile analysis and strategy."""
    result = await analyze_competitor_profile(
        data.competitor, data.platform, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/intel/competitor-ads", tags=["Intelligence"])
async def api_competitor_ads(data: CompetitorAdsData):
    """Feature #127: Ad Intelligence — analyze competitor advertising strategy."""
    result = await get_competitor_ad_intelligence(
        data.competitor, data.platform, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/automation/comment-replies", tags=["Automation"])
async def api_comment_replies(data: CommentReplyData):
    """Feature #128: AI Comment Manager — bulk smart replies with sentiment detection."""
    result = await bulk_reply_comments(
        data.comments, data.tone, data.brand_name, data.platform, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/automation/repurpose", tags=["Automation"])
async def api_repurpose(data: RepurposeData):
    """Feature #129: Content Repurposer — 1 piece → multiple platform formats."""
    result = await repurpose_content(
        data.original, data.source_format, data.target_formats,
        data.brand_name, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/automation/storyboard", tags=["Automation"])
async def api_storyboard(data: StoryboardData):
    """Feature #130: Video Storyboard Generator — shot-by-shot TikTok/Reel plan."""
    result = await generate_video_storyboard(
        data.topic, data.platform, data.duration_seconds,
        data.style, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/automation/dm-templates", tags=["Automation"])
async def api_dm_templates(data: DMTemplateData):
    """Feature #131: DM Campaign Templates — personalized outreach scripts."""
    result = await generate_dm_templates(
        data.purpose, data.platform, data.brand_name,
        data.niche, data.tone, data.count, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/biz/crisis-detect", tags=["Business Intel"])
async def api_crisis_detect(data: CrisisDetectData):
    """Feature #132: Crisis Detection — analyze comments for PR crisis signals."""
    result = await detect_crisis(
        data.comments_text, data.brand, data.platform, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/biz/crisis-response", tags=["Business Intel"])
async def api_crisis_response(data: CrisisResponseData):
    """Feature #133: Crisis Response Generator — full PR crisis response kit."""
    result = await generate_crisis_response(
        data.brand, data.crisis_description, data.tone, data.platform, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/biz/growth-forecast", tags=["Business Intel"])
async def api_growth_forecast(data: GrowthForecastData):
    """Feature #134: Growth Forecasting — ML-style 3-scenario follower projections."""
    result = forecast_growth_ml(
        data.current_followers, data.platform, data.monthly_growth_rate,
        data.posting_freq, data.engagement_rate, data.months,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/biz/brand-voice", tags=["Business Intel"])
async def api_brand_voice(data: BrandVoiceData):
    """Feature #135: Brand Voice AI — analyze and codify brand writing style."""
    result = await analyze_brand_voice(data.samples, data.brand_name, data.language)
    return {"status": "ok", "data": result}


@app.post("/api/v1/creator/youtube-seo", tags=["Creator Tools"])
async def api_youtube_seo(data: YouTubeSEOData):
    """Feature #136: YouTube SEO Optimizer — title, description, tags, scoring."""
    result = await optimize_youtube_seo(
        data.title, data.description, data.tags,
        data.target_keyword, data.niche, data.language,
    )
    return {"status": "ok", "data": result}


@app.post("/api/v1/creator/profile-optimizer", tags=["Creator Tools"])
async def api_profile_optimizer(data: ProfileOptData):
    """Feature #137: AI Profile Optimizer — bio rewrite with scoring and keywords."""
    result = await optimize_profile(
        data.platform, data.current_bio, data.niche,
        data.goals, data.username, data.language,
    )
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# P5 — SALES ENGINE ENDPOINTS (#138–#142)
# ═══════════════════════════════════════════════════════════════════════════════

class SalesFunnelData(BaseModel):
    niche: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    platform: str = "Instagram"
    audience: str = "General"
    language: str = "English"

class LeadMagnetData(BaseModel):
    niche: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    format_type: str = "PDF Checklist"
    audience: str = "General"
    language: str = "English"

class ProductDescData(BaseModel):
    product_name: str = Field(..., min_length=1)
    product_type: str = "Digital Product"
    niche: str = Field(..., min_length=1)
    price: str = "$97"
    platform: str = "Instagram"
    language: str = "English"

class EmailSeqData(BaseModel):
    topic: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    product: str = ""
    num_emails: int = Field(5, ge=1, le=10)
    tone: str = "Conversational"
    language: str = "English"

class CTAData(BaseModel):
    niche: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    platform: str = "Instagram"
    goal: str = "Sales"
    count: int = Field(10, ge=1, le=20)
    language: str = "English"

@app.post("/api/v1/sales/funnel-map", tags=["Sales Engine"])
async def api_sales_funnel(data: SalesFunnelData):
    """Feature #138: Sales Funnel Mapper."""
    result = await map_sales_funnel(data.niche, data.product, data.platform, data.audience, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/sales/lead-magnet", tags=["Sales Engine"])
async def api_lead_magnet(data: LeadMagnetData):
    """Feature #139: Lead Magnet Builder."""
    result = await build_lead_magnet(data.niche, data.topic, data.format_type, data.audience, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/sales/product-description", tags=["Sales Engine"])
async def api_product_description(data: ProductDescData):
    """Feature #140: Social Commerce Product Descriptions."""
    result = await generate_product_descriptions(data.product_name, data.product_type, data.niche, data.price, data.platform, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/sales/email-sequence", tags=["Sales Engine"])
async def api_email_sequence(data: EmailSeqData):
    """Feature #141: Email Sequence Generator."""
    result = await generate_email_sequence(data.topic, data.niche, data.product, data.num_emails, data.tone, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/sales/ctas", tags=["Sales Engine"])
async def api_ctas(data: CTAData):
    """Feature #142: CTA Generator."""
    result = await generate_ctas(data.niche, data.product, data.platform, data.goal, data.count, data.language)
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# P6 — CONTENT DOMINATION ENDPOINTS (#143–#147)
# ═══════════════════════════════════════════════════════════════════════════════

class ViralHooksData(BaseModel):
    niche: str = Field(..., min_length=1)
    platform: str = "TikTok"
    content_type: str = "Video"
    count: int = Field(20, ge=5, le=30)
    language: str = "English"

class ReelScriptData(BaseModel):
    topic: str = Field(..., min_length=1)
    platform: str = "TikTok"
    duration: str = "60s"
    style: str = "Educational"
    niche: str = "General"
    language: str = "English"

class ContentSeriesData(BaseModel):
    theme: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    series_type: str = "7-Day Challenge"
    language: str = "English"

class ThumbnailData(BaseModel):
    title: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    platform: str = "YouTube"
    style: str = "Bold & Dramatic"
    count: int = Field(5, ge=1, le=5)
    language: str = "English"

class EmotionCaptionData(BaseModel):
    topic: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    emotion: str = "Curiosity"
    count: int = Field(5, ge=1, le=10)
    language: str = "English"

@app.post("/api/v1/content/viral-hooks", tags=["Content Domination"])
async def api_viral_hooks(data: ViralHooksData):
    """Feature #143: Viral Hook Library."""
    result = await generate_viral_hooks(data.niche, data.platform, data.content_type, data.count, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/content/reel-script", tags=["Content Domination"])
async def api_reel_script(data: ReelScriptData):
    """Feature #144: Reel/Short Script Engine."""
    result = await generate_short_script(data.topic, data.platform, data.duration, data.style, data.niche, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/content/series-plan", tags=["Content Domination"])
async def api_content_series(data: ContentSeriesData):
    """Feature #145: Content Series Planner."""
    result = await plan_content_series(data.theme, data.niche, data.platform, data.series_type, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/content/thumbnail", tags=["Content Domination"])
async def api_thumbnail(data: ThumbnailData):
    """Feature #146: Thumbnail Concept Generator."""
    result = await generate_thumbnail_concepts(data.title, data.niche, data.platform, data.style, data.count, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/content/emotional-caption", tags=["Content Domination"])
async def api_emotional_caption(data: EmotionCaptionData):
    """Feature #147: Caption Emotion Engine."""
    result = await generate_emotional_captions(data.topic, data.niche, data.platform, data.emotion, data.count, data.language)
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# P7 — BRAND AUTHORITY ENDPOINTS (#148–#152)
# ═══════════════════════════════════════════════════════════════════════════════

class BrandScorecardData(BaseModel):
    platform: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    bio: str = ""
    posting_freq: str = "3x/week"
    engagement_rate: float = Field(2.5, ge=0.0)
    follower_count: int = Field(1000, ge=0)
    has_website: bool = False
    has_email_list: bool = False
    language: str = "English"

class ContentAuditData(BaseModel):
    posts_summary: str = Field(..., min_length=1)
    platform: str = "Instagram"
    niche: str = "General"
    language: str = "English"

class ContentGapData(BaseModel):
    your_niche: str = Field(..., min_length=1)
    competitor_info: str = ""
    platform: str = "Instagram"
    language: str = "English"

class PersonaData(BaseModel):
    niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    product_or_service: str = "Coaching Program"
    language: str = "English"

class AlgorithmData(BaseModel):
    platform: str = Field(..., min_length=1)
    content_type: str = "Short Video"
    niche: str = "General"
    language: str = "English"

@app.post("/api/v1/brand/scorecard", tags=["Brand Authority"])
async def api_brand_scorecard(data: BrandScorecardData):
    """Feature #148: Personal Brand Scorecard."""
    result = await audit_personal_brand(data.platform, data.niche, data.bio, data.posting_freq,
                                        data.engagement_rate, data.follower_count,
                                        data.has_website, data.has_email_list, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/brand/content-audit", tags=["Brand Authority"])
async def api_content_audit(data: ContentAuditData):
    """Feature #149: Content Performance Audit."""
    result = await audit_content_performance(data.posts_summary, data.platform, data.niche, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/brand/content-gap", tags=["Brand Authority"])
async def api_content_gap(data: ContentGapData):
    """Feature #150: Competitor Content Gap Finder."""
    result = await find_competitor_content_gap(data.your_niche, data.competitor_info, data.platform, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/brand/persona", tags=["Brand Authority"])
async def api_persona(data: PersonaData):
    """Feature #151: Audience Persona Builder."""
    result = await build_audience_persona(data.niche, data.platform, data.product_or_service, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/brand/algorithm", tags=["Brand Authority"])
async def api_algorithm(data: AlgorithmData):
    """Feature #152: Algorithm Intelligence Tracker."""
    result = await get_algorithm_strategy(data.platform, data.content_type, data.niche, data.language)
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# P8 — COMMUNITY & COLLABORATION ENDPOINTS (#153–#157)
# ═══════════════════════════════════════════════════════════════════════════════

class InfluencerCollabData(BaseModel):
    brand: str = Field(..., min_length=1)
    influencer_niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    budget: str = "$500"
    goal: str = "Brand Awareness"
    language: str = "English"

class UGCData(BaseModel):
    brand: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    incentive: str = "Feature on our page"
    hashtag: str = ""
    language: str = "English"

class TestimonialData(BaseModel):
    testimonial: str = Field(..., min_length=5)
    platform: str = "Instagram"
    brand: str = "Brand"
    niche: str = "General"
    language: str = "English"

class CommunityPlaybookData(BaseModel):
    niche: str = Field(..., min_length=1)
    platform: str = "Instagram"
    current_followers: int = Field(1000, ge=0)
    goal_followers: int = Field(10000, ge=1)
    language: str = "English"

class LiveStreamData(BaseModel):
    topic: str = Field(..., min_length=1)
    platform: str = "Instagram Live"
    duration_minutes: int = Field(60, ge=15, le=180)
    niche: str = "General"
    language: str = "English"

@app.post("/api/v1/community/collab", tags=["Community Hub"])
async def api_influencer_collab(data: InfluencerCollabData):
    """Feature #153: Influencer Collaboration Hub."""
    result = await plan_influencer_collab(data.brand, data.influencer_niche, data.platform, data.budget, data.goal, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/community/ugc", tags=["Community Hub"])
async def api_ugc(data: UGCData):
    """Feature #154: UGC Campaign Planner."""
    result = await plan_ugc_campaign(data.brand, data.niche, data.platform, data.incentive, data.hashtag, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/community/testimonial", tags=["Community Hub"])
async def api_testimonial(data: TestimonialData):
    """Feature #155: Testimonial → Social Proof Post."""
    result = await transform_testimonial_to_post(data.testimonial, data.platform, data.brand, data.niche, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/community/playbook", tags=["Community Hub"])
async def api_community_playbook(data: CommunityPlaybookData):
    """Feature #156: Community Growth Playbook."""
    result = await generate_community_playbook(data.niche, data.platform, data.current_followers, data.goal_followers, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/community/livestream", tags=["Community Hub"])
async def api_livestream(data: LiveStreamData):
    """Feature #157: Live Stream Planner."""
    result = await plan_live_stream(data.topic, data.platform, data.duration_minutes, data.niche, data.language)
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# P9 — REAL-TIME INTELLIGENCE ENDPOINTS (#158–#161)
# ═══════════════════════════════════════════════════════════════════════════════

class TrendHijackData(BaseModel):
    trend_topic: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    platform: str = "TikTok"
    language: str = "English"

class ViralCloneData(BaseModel):
    viral_description: str = Field(..., min_length=5)
    your_niche: str = Field(..., min_length=1)
    platform: str = "TikTok"
    language: str = "English"

class PostingTimesData(BaseModel):
    platform: str = Field(..., min_length=1)
    niche: str = "General"
    audience_timezone: str = "EST (UTC-5)"
    language: str = "English"

class NicheScanData(BaseModel):
    broad_niche: str = Field(..., min_length=1)
    platform: str = "TikTok"
    language: str = "English"

@app.post("/api/v1/realtime/trend-hijack", tags=["Real-Time Intel"])
async def api_trend_hijack(data: TrendHijackData):
    """Feature #158: Trend Hijacker."""
    result = await hijack_trend(data.trend_topic, data.niche, data.platform, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/realtime/viral-clone", tags=["Real-Time Intel"])
async def api_viral_clone(data: ViralCloneData):
    """Feature #159: Viral Content Cloner."""
    result = await clone_viral_content(data.viral_description, data.your_niche, data.platform, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/realtime/posting-times", tags=["Real-Time Intel"])
async def api_posting_times(data: PostingTimesData):
    """Feature #160: Optimal Posting Times Intelligence."""
    result = await get_optimal_posting_times(data.platform, data.niche, data.audience_timezone, data.language)
    return {"status": "ok", "data": result}

@app.post("/api/v1/realtime/niche-scan", tags=["Real-Time Intel"])
async def api_niche_scan(data: NicheScanData):
    """Feature #161: Niche Opportunity Scanner."""
    result = await scan_niche_opportunity(data.broad_niche, data.platform, data.language)
    return {"status": "ok", "data": result}


# ═══════════════════════════════════════════════════════════════════════════════
# FACEBOOK PAGES MANAGER
# Real Graph API v21.0 endpoints — use stored Facebook account tokens
# ═══════════════════════════════════════════════════════════════════════════════

_FB_API = "https://graph.facebook.com/v21.0"
_FB_TIMEOUT = 20


def _get_fb_token(account_id: str = "") -> tuple:
    """
    Return (user_access_token, account_record) for the first connected Facebook
    account.  If ``account_id`` is provided, look that specific account up.
    Returns ("", None) when no token is found.
    """
    accounts = list_accounts("Facebook")
    if not accounts:
        return "", None
    if account_id:
        acc = next((a for a in accounts if a["id"] == account_id), None)
    else:
        # prefer a 'connected' account; fall back to first
        acc = next((a for a in accounts if a.get("status") == "connected"), accounts[0])
    if not acc:
        return "", None
    # We need the raw token — list_accounts masks it; use _load_accounts directly
    from ai_core.social_auth import _load_accounts as _raw_load
    raw_accounts = _raw_load()
    raw = next((r for r in raw_accounts if r["id"] == acc["id"]), None)
    token = raw.get("access_token", "") if raw else ""
    return token, acc


# ── Pydantic models ──────────────────────────────────────────────────────────

class FBAccountSelector(BaseModel):
    account_id: str = ""

class FBPublishPost(BaseModel):
    account_id: str = ""
    page_id: str
    message: str
    link: str = ""
    image_url: str = ""
    scheduled_time: str = ""      # ISO-8601 unix timestamp string (optional)

class FBCommentReply(BaseModel):
    account_id: str = ""
    comment_id: str
    message: str

class FBMessengerReply(BaseModel):
    account_id: str = ""
    page_id: str = ""          # Page ID — required for Messenger Send API
    recipient_id: str
    message: str

class FBAIGeneratePost(BaseModel):
    account_id: str = ""
    page_name: str = ""
    tone: str = "engaging"
    goal: str = "grow followers"
    audience: str = "general"
    topic: str = ""

class FBAISuggestReply(BaseModel):
    account_id: str = ""
    original_text: str
    context: str = ""
    tone: str = "friendly"

class FBAIAnalyzePost(BaseModel):
    account_id: str = ""
    post_id: str
    post_text: str = ""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: int = 0

class FBAIBulkSchedule(BaseModel):
    account_id: str = ""
    page_name: str = ""
    topic: str
    num_posts: int = 5
    tone: str = "engaging"
    goal: str = "grow followers"

class FBLikePost(BaseModel):
    account_id: str = ""
    post_id: str

class FBPageInsights(BaseModel):
    account_id: str = ""
    page_id: str
    since: str = ""   # YYYY-MM-DD
    until: str = ""


# ── GET /api/v1/facebook/accounts ─────────────────────────────────────────────

@app.get("/api/v1/facebook/accounts", tags=["Facebook Manager"])
async def fb_list_accounts():
    """List all stored Facebook accounts (tokens masked)."""
    accs = list_accounts("Facebook")
    if not accs:
        return {"status": "ok", "accounts": [], "message": "No Facebook accounts connected. Go to 🔐 Social Accounts to connect one."}
    return {"status": "ok", "accounts": accs}


# ── GET /api/v1/facebook/pages ────────────────────────────────────────────────

@app.get("/api/v1/facebook/pages", tags=["Facebook Manager"])
async def fb_list_pages(account_id: str = Query("")):
    """List all Facebook Pages the user manages."""
    token, acc = _get_fb_token(account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected. Go to 🔐 Social Accounts to connect one."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,name,category,fan_count,picture,access_token"},
            )
        data = r.json()
        if "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Facebook API error")}
        pages = data.get("data", [])
        return {"status": "ok", "pages": pages, "account": acc.get("display_name", "Facebook")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── GET /api/v1/facebook/pages/{page_id}/posts ────────────────────────────────

@app.get("/api/v1/facebook/pages/{page_id}/posts", tags=["Facebook Manager"])
async def fb_get_page_posts(page_id: str, account_id: str = Query(""), limit: int = Query(20)):
    """Get posts from a specific Facebook Page with engagement metrics."""
    token, _ = _get_fb_token(account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    # Get Page access token first
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token"},
            )
        pages_data = pages_r.json()
        page_token = next(
            (p["access_token"] for p in pages_data.get("data", []) if p["id"] == page_id),
            token,  # fallback to user token
        )
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.get(
                f"{_FB_API}/{page_id}/posts",
                params={
                    "access_token": page_token,
                    "fields": "id,message,story,created_time,likes.summary(true),comments.summary(true),shares,full_picture,permalink_url",
                    "limit": limit,
                },
            )
        data = r.json()
        if "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Facebook API error")}
        return {"status": "ok", "posts": data.get("data", []), "page_id": page_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── POST /api/v1/facebook/pages/{page_id}/publish ─────────────────────────────

@app.post("/api/v1/facebook/pages/{page_id}/publish", tags=["Facebook Manager"])
async def fb_publish_post(page_id: str, data: FBPublishPost):
    """Publish a new text/link/photo post to a Facebook Page."""
    token, _ = _get_fb_token(data.account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    if not data.message.strip():
        return {"status": "error", "message": "Post message cannot be empty."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token"},
            )
        pages_data = pages_r.json()
        page_token = next(
            (p["access_token"] for p in pages_data.get("data", []) if p["id"] == page_id),
            token,
        )
        payload: dict = {"message": data.message, "access_token": page_token}
        if data.link:
            payload["link"] = data.link
        endpoint = f"{_FB_API}/{page_id}/photos" if data.image_url else f"{_FB_API}/{page_id}/feed"
        if data.image_url:
            payload["url"] = data.image_url
        if data.scheduled_time:
            payload["scheduled_publish_time"] = data.scheduled_time
            payload["published"] = "false"
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.post(endpoint, data=payload)
        result = r.json()
        if "error" in result:
            return {"status": "error", "message": result["error"].get("message", "Publish failed")}
        return {"status": "ok", "post_id": result.get("id", ""), "message": "Post published successfully! ✅"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── GET /api/v1/facebook/posts/{post_id}/comments ─────────────────────────────

@app.get("/api/v1/facebook/posts/{post_id}/comments", tags=["Facebook Manager"])
async def fb_get_comments(post_id: str, account_id: str = Query(""), limit: int = Query(25)):
    """Get comments on a Facebook post using the Page Access Token."""
    token, _ = _get_fb_token(account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    try:
        # Page posts require a Page Access Token — extract page_id from composite post_id
        # Facebook post_id format: {page_id}_{post_id}
        page_id_from_post = post_id.split("_")[0] if "_" in post_id else ""
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token"},
            )
        pages_data = pages_r.json()
        page_token = token  # fallback to user token
        if page_id_from_post:
            page_token = next(
                (p["access_token"] for p in pages_data.get("data", []) if p["id"] == page_id_from_post),
                token,
            )
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.get(
                f"{_FB_API}/{post_id}/comments",
                params={
                    "access_token": page_token,
                    "fields": "id,message,from,created_time,like_count,can_reply_privately",
                    "limit": limit,
                    "summary": "true",
                },
            )
        data = r.json()
        if "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Facebook API error")}
        return {"status": "ok", "comments": data.get("data", []), "total": data.get("summary", {}).get("total_count", 0)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── POST /api/v1/facebook/comments/{comment_id}/reply ────────────────────────

@app.post("/api/v1/facebook/comments/{comment_id}/reply", tags=["Facebook Manager"])
async def fb_reply_comment(comment_id: str, data: FBCommentReply):
    """Reply to a comment on a Facebook post."""
    token, _ = _get_fb_token(data.account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    if not data.message.strip():
        return {"status": "error", "message": "Reply message cannot be empty."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.post(
                f"{_FB_API}/{comment_id}/comments",
                data={"message": data.message, "access_token": token},
            )
        result = r.json()
        if "error" in result:
            return {"status": "error", "message": result["error"].get("message", "Reply failed")}
        return {"status": "ok", "reply_id": result.get("id", ""), "message": "Reply sent! ✅"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── POST /api/v1/facebook/posts/{post_id}/like ───────────────────────────────

@app.post("/api/v1/facebook/posts/{post_id}/like", tags=["Facebook Manager"])
async def fb_like_post(post_id: str, data: FBLikePost):
    """Like a Facebook post on behalf of the connected account."""
    token, _ = _get_fb_token(data.account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.post(
                f"{_FB_API}/{post_id}/likes",
                data={"access_token": token},
            )
        result = r.json()
        if "error" in result:
            return {"status": "error", "message": result["error"].get("message", "Like failed")}
        return {"status": "ok", "message": "Post liked! 👍"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── GET /api/v1/facebook/pages/{page_id}/conversations ───────────────────────

@app.get("/api/v1/facebook/pages/{page_id}/conversations", tags=["Facebook Manager"])
async def fb_get_conversations(page_id: str, account_id: str = Query(""), limit: int = Query(20)):
    """Get Messenger conversations for a Facebook Page."""
    token, _ = _get_fb_token(account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token"},
            )
        pages_data = pages_r.json()
        page_token = next(
            (p["access_token"] for p in pages_data.get("data", []) if p["id"] == page_id),
            token,
        )
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.get(
                f"{_FB_API}/{page_id}/conversations",
                params={
                    "access_token": page_token,
                    "fields": "id,updated_time,participants,messages{message,from,created_time}",
                    "limit": limit,
                },
            )
        data = r.json()
        if "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Facebook API error")}
        return {"status": "ok", "conversations": data.get("data", [])}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── POST /api/v1/facebook/messenger/reply ────────────────────────────────────

@app.post("/api/v1/facebook/messenger/reply", tags=["Facebook Manager"])
async def fb_messenger_reply(data: FBMessengerReply):
    """Send a message reply via Messenger Send API using the Page Access Token."""
    token, _ = _get_fb_token(data.account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    if not data.message.strip():
        return {"status": "error", "message": "Message cannot be empty."}
    try:
        # Messenger Platform requires a Page Access Token at /{page_id}/messages
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token"},
            )
        pages_data = pages_r.json()
        page_token = token
        endpoint_page = data.page_id
        if data.page_id:
            pt = next((p["access_token"] for p in pages_data.get("data", []) if p["id"] == data.page_id), None)
            if pt:
                page_token = pt
        else:
            # Fall back to first available page token
            page_list = pages_data.get("data", [])
            if page_list:
                page_token = page_list[0].get("access_token", token)
                endpoint_page = page_list[0].get("id", "me")

        send_endpoint = f"{_FB_API}/{endpoint_page}/messages" if endpoint_page else f"{_FB_API}/me/messages"
        payload = {
            "recipient": {"id": data.recipient_id},
            "message": {"text": data.message},
        }
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.post(
                send_endpoint,
                params={"access_token": page_token},
                json=payload,
            )
        result = r.json()
        if "error" in result:
            return {"status": "error", "message": result["error"].get("message", "Messenger send failed")}
        return {"status": "ok", "message_id": result.get("message_id", ""), "message": "Message sent! ✅"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── GET /api/v1/facebook/pages/{page_id}/insights ────────────────────────────

@app.get("/api/v1/facebook/pages/{page_id}/insights", tags=["Facebook Manager"])
async def fb_page_insights(page_id: str, account_id: str = Query(""), since: str = Query(""), until: str = Query("")):
    """Get Page Insights metrics (reach, impressions, engagement, fans)."""
    token, _ = _get_fb_token(account_id)
    if not token:
        return {"status": "error", "message": "No Facebook account connected."}
    try:
        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            pages_r = await client.get(
                f"{_FB_API}/me/accounts",
                params={"access_token": token, "fields": "id,access_token,name,fan_count"},
            )
        pages_data = pages_r.json()
        page_info = next((p for p in pages_data.get("data", []) if p["id"] == page_id), {})
        page_token = page_info.get("access_token", token)

        metrics = "page_impressions,page_impressions_unique,page_engaged_users,page_fans,page_fan_adds"
        params: dict = {"access_token": page_token, "metric": metrics, "period": "day"}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
            r = await client.get(f"{_FB_API}/{page_id}/insights", params=params)
        data = r.json()
        # Fallback: if any metric is invalid, retry with a minimal safe set
        if "error" in data:
            err_code = data["error"].get("code", 0)
            err_msg  = data["error"].get("message", "")
            if err_code == 100 or "valid insights metric" in err_msg.lower():
                params["metric"] = "page_impressions,page_engaged_users,page_fans,page_fan_adds"
                async with httpx.AsyncClient(timeout=_FB_TIMEOUT) as client:
                    r = await client.get(f"{_FB_API}/{page_id}/insights", params=params)
                data = r.json()
        if "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Insights API error")}
        return {
            "status": "ok",
            "page_name": page_info.get("name", page_id),
            "fan_count": page_info.get("fan_count", 0),
            "insights": data.get("data", []),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── POST /api/v1/facebook/ai/generate-post ───────────────────────────────────

@app.post("/api/v1/facebook/ai/generate-post", tags=["Facebook Manager"])
async def fb_ai_generate_post(data: FBAIGeneratePost):
    """AI-generate an optimised Facebook post for a Page."""
    try:
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        if not USE_AI:
            raise ImportError("AI disabled")
        topic_hint = f"Topic: {data.topic}\n" if data.topic else ""
        prompt = (
            f"Write a highly engaging Facebook post for a Page called '{data.page_name or 'our brand'}'.\n"
            f"{topic_hint}"
            f"Tone: {data.tone}\n"
            f"Goal: {data.goal}\n"
            f"Target audience: {data.audience}\n\n"
            "Requirements:\n"
            "- Start with a strong hook (question or bold statement)\n"
            "- Add 2-3 short paragraphs of value\n"
            "- Include a clear call-to-action\n"
            "- Add 5 relevant hashtags at the end\n"
            "- Use emojis naturally\n"
            "Keep it under 300 words."
        )
        resp = await LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        post_text = resp.choices[0].message.content.strip()
    except Exception:
        topics = data.topic or "your brand"
        post_text = (
            f"🚀 Exciting news for {data.audience}!\n\n"
            f"We're sharing something special about {topics} today. "
            f"Our mission is to {data.goal} and we're just getting started. 💪\n\n"
            "What do you think? Drop your thoughts in the comments below! 👇\n\n"
            "#GrowthOS #SocialMedia #Marketing #DigitalMarketing #ContentCreator"
        )
    return {"status": "ok", "post": post_text, "word_count": len(post_text.split())}


# ── POST /api/v1/facebook/ai/suggest-reply ───────────────────────────────────

@app.post("/api/v1/facebook/ai/suggest-reply", tags=["Facebook Manager"])
async def fb_ai_suggest_reply(data: FBAISuggestReply):
    """AI-suggest the best reply to a comment or Messenger message."""
    try:
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        if not USE_AI:
            raise ImportError("AI disabled")
        context_hint = f"Context: {data.context}\n" if data.context else ""
        prompt = (
            f"A user wrote this on our Facebook page:\n\"{data.original_text}\"\n\n"
            f"{context_hint}"
            f"Write a {data.tone}, professional, and helpful reply as the Page manager.\n"
            "Requirements:\n"
            "- Keep it concise (1-3 sentences)\n"
            "- Be warm and human-sounding\n"
            "- Address their point directly\n"
            "- If it's a complaint, show empathy and offer to help\n"
            "- Do NOT use corporate jargon\n"
            "Reply only with the message text."
        )
        resp = await LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        reply = resp.choices[0].message.content.strip()
    except Exception:
        if any(w in data.original_text.lower() for w in ["bad", "terrible", "worst", "hate", "awful", "problem"]):
            reply = "Thank you for your feedback! We're sorry to hear about your experience. Please DM us so we can make this right for you. 🙏"
        elif "?" in data.original_text:
            reply = "Great question! We'd love to help. Please DM us or check our website for more details. 😊"
        else:
            reply = "Thank you so much for your comment! We really appreciate your support and engagement. ❤️"
    return {"status": "ok", "reply": reply}


# ── POST /api/v1/facebook/ai/analyze-post ────────────────────────────────────

@app.post("/api/v1/facebook/ai/analyze-post", tags=["Facebook Manager"])
async def fb_ai_analyze_post(data: FBAIAnalyzePost):
    """AI analysis of post performance + actionable improvement suggestions."""
    engagement_rate = 0.0
    if data.reach > 0:
        engagement_rate = round((data.likes + data.comments + data.shares) / data.reach * 100, 2)

    try:
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        if not USE_AI:
            raise ImportError("AI disabled")
        post_preview = data.post_text[:300] if data.post_text else "(no text)"
        prompt = (
            f"Analyze this Facebook post performance:\n\n"
            f"Post text: {post_preview}\n"
            f"Likes: {data.likes}  Comments: {data.comments}  Shares: {data.shares}  Reach: {data.reach}\n"
            f"Engagement rate: {engagement_rate}%\n\n"
            "Provide:\n"
            "1. Performance rating (Excellent/Good/Average/Poor)\n"
            "2. What worked well (2 points)\n"
            "3. What to improve (2 points)\n"
            "4. A specific rewrite suggestion for the opening line\n"
            "5. Best time to post next similar content\n"
            "Be concise and actionable."
        )
        resp = await LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        analysis = resp.choices[0].message.content.strip()
    except Exception:
        rating = "Excellent" if engagement_rate > 5 else ("Good" if engagement_rate > 2 else ("Average" if engagement_rate > 0.5 else "Poor"))
        analysis = (
            f"📊 Performance Rating: {rating} ({engagement_rate}% engagement rate)\n\n"
            f"✅ What worked:\n"
            f"• {data.likes} likes shows the content resonated emotionally\n"
            f"• {data.comments} comments indicate community interest\n\n"
            f"🔧 Improve:\n"
            f"• Add a stronger call-to-action to increase shares\n"
            f"• Post at peak hours (9-11AM or 7-9PM) for more reach\n\n"
            f"💡 Tip: Start your next post with a question to boost comments."
        )
    return {
        "status": "ok",
        "engagement_rate": engagement_rate,
        "analysis": analysis,
        "metrics": {"likes": data.likes, "comments": data.comments, "shares": data.shares, "reach": data.reach},
    }


# ── POST /api/v1/facebook/ai/bulk-schedule ───────────────────────────────────

@app.post("/api/v1/facebook/ai/bulk-schedule", tags=["Facebook Manager"])
async def fb_ai_bulk_schedule(data: FBAIBulkSchedule):
    """AI-generate a batch of Facebook posts ready for scheduling."""
    num = max(1, min(data.num_posts, 10))
    try:
        from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, USE_AI
        if not USE_AI:
            raise ImportError("AI disabled")
        prompt = (
            f"Generate {num} different Facebook post ideas for a Page about '{data.topic}'.\n"
            f"Tone: {data.tone} | Goal: {data.goal} | Page: {data.page_name or 'our brand'}\n\n"
            f"For each post provide:\n"
            f"POST [number]:\n"
            f"[Full post text with hashtags and emojis]\n"
            f"Best day: [day of week]\n"
            f"Best time: [time]\n\n"
            f"Make each post unique in style and angle."
        )
        resp = await LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        raw = resp.choices[0].message.content.strip()
        # Split into individual posts
        import re
        parts = re.split(r"POST\s*\[\d+\]:", raw, flags=re.IGNORECASE)
        posts = [p.strip() for p in parts if p.strip()]
    except Exception:
        posts = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        times = ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM", "8:00 PM"]
        for i in range(num):
            posts.append(
                f"🌟 Tip #{i+1} for {data.topic}!\n\n"
                f"Every expert was once a beginner. Here's what you need to know to {data.goal}. 💡\n\n"
                f"Save this post for later! 🔖\n\n"
                f"#Tips #{data.topic.replace(' ', '')} #Growth #SocialMedia\n\n"
                f"Best day: {days[i % len(days)]} | Best time: {times[i % len(times)]}"
            )
    return {"status": "ok", "posts": posts[:num], "count": min(len(posts), num)}


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("backend_api:app", host="0.0.0.0", port=8000, reload=False)
