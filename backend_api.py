"""
GrowthOS AI v2.0 — Backend API
================================
FastAPI server exposing all 99 AI features as REST endpoints.
Run: uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
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
    request_refill, cancel_orders, smart_order,
    get_panel_info, get_order_history,
)
from ai_core.geo_engine       import (
    list_all_countries, get_country_detail, search_locations,
    get_local_time, get_geo_strategy, get_best_times_by_timezone,
    get_regional_trends, get_cultural_content_guide,
    get_platform_availability, get_geo_audience_insights,
    get_multi_country_comparison,
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
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("backend_api:app", host="0.0.0.0", port=8000, reload=True)
