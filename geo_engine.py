"""
GrowthOS AI — Geo Intelligence Engine
=======================================
Feature #26 : Geo-Targeted Growth Strategy
Feature #27 : Regional Trend Intelligence
Feature #28 : Timezone-Aware Scheduler
Feature #29 : Cultural Content Optimizer
Feature #30 : Platform Dominance Map
Feature #31 : Regional Audience Profiler
Feature #32 : Multi-Language Content Advisor
Feature #33 : Location-Based Risk Assessment

Provides complete location/area intelligence for every feature in the app.
Zero ambiguity — each country has exact data: timezone, languages, top platforms,
cultural norms, peak hours, SMM targeting codes, and content strategy.
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL as OPENAI_MODEL, LLM_FAST_MODEL as OPENAI_FAST_MODEL, USE_AI as USE_REAL_AI


async def _gpt(prompt: str, system: str = "You are a world-class geo-targeted social media strategist.", fast: bool = True) -> str:
    if not _client:
        return ""
    model = OPENAI_FAST_MODEL if fast else OPENAI_MODEL
    try:
        resp = await _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER COUNTRY DATABASE — 60 key markets, fully detailed
# Keys: code, name, timezone, utc_offset, languages, currency,
#       top_platforms, platform_notes, peak_hours_local, content_style,
#       cultural_tips, content_languages, smm_target_code, region,
#       internet_users_m, mobile_pct, avg_daily_social_min
# ═══════════════════════════════════════════════════════════════════════════════
COUNTRIES: dict[str, dict] = {
    # ── SOUTHEAST ASIA ────────────────────────────────────────────────────────
    "KH": {
        "code": "KH", "name": "Cambodia", "region": "Southeast Asia",
        "timezone": "Asia/Phnom_Penh", "utc_offset": "+07:00",
        "languages": ["Khmer", "English"],
        "content_languages": ["km", "en"],
        "currency": "KHR / USD",
        "top_platforms": ["Facebook", "TikTok", "Telegram", "YouTube", "Instagram"],
        "platform_notes": {
            "Facebook": "Dominant #1 — used by 94% of internet users; pages & groups critical",
            "TikTok": "Fastest growing — youth 18-30; Khmer music/comedy/lifestyle viral",
            "Telegram": "News & community groups; widely used for news channels",
            "YouTube": "Long-form tutorials, Khmer dramas; strong monetisation",
            "Instagram": "Growing urban youth; lifestyle & food niches strong",
        },
        "peak_hours_local": {
            "Facebook": ["07:00–09:00", "12:00–13:00", "19:00–22:00"],
            "TikTok": ["20:00–23:00", "07:00–08:00"],
            "YouTube": ["20:00–22:00"],
        },
        "content_style": "Warm, emotional, family-oriented; humour works well; storytelling with local music",
        "cultural_tips": [
            "Use Khmer language — audiences prefer native content",
            "Reference Buddhist values and Khmer New Year (April) events",
            "Avoid political content — very sensitive",
            "Food and travel content performs extremely well",
            "Family and community themes resonate deeply",
            "Live streaming is very popular — go live regularly",
        ],
        "smm_target_code": "KH",
        "internet_users_m": 10.1,
        "mobile_pct": 97,
        "avg_daily_social_min": 181,
    },
    "TH": {
        "code": "TH", "name": "Thailand", "region": "Southeast Asia",
        "timezone": "Asia/Bangkok", "utc_offset": "+07:00",
        "languages": ["Thai", "English"],
        "content_languages": ["th", "en"],
        "currency": "THB",
        "top_platforms": ["Facebook", "YouTube", "TikTok", "Instagram", "LINE"],
        "platform_notes": {
            "Facebook": "Dominant; businesses and entertainment heavily use pages",
            "TikTok": "Huge youth market; Thai pop culture, street food, travel",
            "LINE": "Messaging app with broadcast channels; essential for brands",
            "YouTube": "Very active; Thai dramas and gaming channels dominate",
            "Instagram": "Fashion, beauty, food, travel; heavy influencer use",
        },
        "peak_hours_local": {
            "Facebook": ["08:00–10:00", "12:00–13:00", "20:00–22:00"],
            "TikTok": ["19:00–23:00"],
            "Instagram": ["18:00–22:00"],
        },
        "content_style": "Creative, visually rich; humour and entertainment; aesthetic food and travel",
        "cultural_tips": [
            "Thai language posts get 3-5x more engagement than English",
            "Royal family and religion are off-limits",
            "Street food, temples, festivals are high-engagement topics",
            "Sanuk (fun) culture — content must feel enjoyable",
            "Emoji-heavy captions are the norm",
        ],
        "smm_target_code": "TH",
        "internet_users_m": 52.3,
        "mobile_pct": 96,
        "avg_daily_social_min": 195,
    },
    "VN": {
        "code": "VN", "name": "Vietnam", "region": "Southeast Asia",
        "timezone": "Asia/Ho_Chi_Minh", "utc_offset": "+07:00",
        "languages": ["Vietnamese", "English"],
        "content_languages": ["vi", "en"],
        "currency": "VND",
        "top_platforms": ["Facebook", "YouTube", "TikTok", "Zalo", "Instagram"],
        "platform_notes": {
            "Facebook": "Most used social network; groups extremely active",
            "Zalo": "Local super-app; essential for business communication",
            "TikTok": "Exploding growth; music, lifestyle, food",
            "YouTube": "Music videos, dramas, vlogs dominate",
            "Instagram": "Urban youth, fashion, café culture",
        },
        "peak_hours_local": {
            "Facebook": ["07:00–09:00", "11:30–13:00", "20:00–22:30"],
            "TikTok": ["20:00–23:00"],
        },
        "content_style": "Aspirational yet relatable; before/after transformations; hustle culture",
        "cultural_tips": [
            "Vietnamese language is essential for authentic reach",
            "Café culture, food, and travel are top content categories",
            "Political commentary is strictly off-limits",
            "Tet (Lunar New Year) is peak engagement period",
            "Live streaming on Facebook hugely popular for commerce",
        ],
        "smm_target_code": "VN",
        "internet_users_m": 72.1,
        "mobile_pct": 95,
        "avg_daily_social_min": 172,
    },
    "ID": {
        "code": "ID", "name": "Indonesia", "region": "Southeast Asia",
        "timezone": "Asia/Jakarta", "utc_offset": "+07:00",
        "languages": ["Indonesian (Bahasa)", "Javanese", "English"],
        "content_languages": ["id", "en"],
        "currency": "IDR",
        "top_platforms": ["YouTube", "Instagram", "TikTok", "Facebook", "WhatsApp", "Twitter/X"],
        "platform_notes": {
            "YouTube": "#1 platform by time-spent; Indonesian content creators thrive",
            "Instagram": "Massive influencer culture; fashion, beauty, food",
            "TikTok": "Top 3 market globally; comedy, talent shows viral",
            "WhatsApp": "Primary messaging; business broadcast essential",
            "Twitter/X": "Political discourse and celebrity fan communities",
        },
        "peak_hours_local": {
            "Instagram": ["08:00–09:00", "12:00–13:00", "20:00–22:00"],
            "TikTok": ["19:00–23:00"],
            "YouTube": ["20:00–23:00"],
        },
        "content_style": "Entertaining, relatable; slice-of-life; humour; Islamic values alignment",
        "cultural_tips": [
            "Ramadan period is peak season — adjust content for fasting hours",
            "Islamic values are mainstream — be respectful and inclusive",
            "Bahasa Indonesia is essential; regional dialects boost authenticity",
            "Street food, family, and travel perform consistently well",
            "Influencer collabs (endorsement culture) highly effective",
        ],
        "smm_target_code": "ID",
        "internet_users_m": 212.9,
        "mobile_pct": 98,
        "avg_daily_social_min": 197,
    },
    "PH": {
        "code": "PH", "name": "Philippines", "region": "Southeast Asia",
        "timezone": "Asia/Manila", "utc_offset": "+08:00",
        "languages": ["Filipino (Tagalog)", "English"],
        "content_languages": ["tl", "en"],
        "currency": "PHP",
        "top_platforms": ["Facebook", "YouTube", "TikTok", "Instagram", "Twitter/X"],
        "platform_notes": {
            "Facebook": "Highest penetration in SEA; near-universal usage",
            "TikTok": "Massive growth; entertainment, news, OFW content",
            "YouTube": "Vlogs, music covers, teleserye reactions dominate",
            "Instagram": "Urban professionals and lifestyle brands",
            "Twitter/X": "Very active; news, pop culture, celebrity fandom",
        },
        "peak_hours_local": {
            "Facebook": ["07:00–09:00", "12:00–13:00", "21:00–00:00"],
            "TikTok": ["21:00–00:00"],
        },
        "content_style": "Relatable, bayanihan (community spirit); emotional storytelling; comedy",
        "cultural_tips": [
            "Filipino and English mix (Taglish) is the most engaging format",
            "Overseas Filipino Worker (OFW) content has huge emotional reach",
            "Religious holidays (Christmas, Holy Week) are peak periods",
            "Hugot (heartfelt) quotes and memes extremely shareable",
            "Disaster preparedness, election news drive viral spikes",
        ],
        "smm_target_code": "PH",
        "internet_users_m": 86.0,
        "mobile_pct": 97,
        "avg_daily_social_min": 222,
    },
    "SG": {
        "code": "SG", "name": "Singapore", "region": "Southeast Asia",
        "timezone": "Asia/Singapore", "utc_offset": "+08:00",
        "languages": ["English", "Mandarin", "Malay", "Tamil"],
        "content_languages": ["en", "zh"],
        "currency": "SGD",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "LinkedIn"],
        "platform_notes": {
            "LinkedIn": "Professional market; B2B critical; highly active",
            "Instagram": "Premium lifestyle, food, travel; high purchasing power",
            "YouTube": "Finance, tech, food, luxury travel content",
            "TikTok": "Growing fast; local food, expat life, finance tips",
            "Facebook": "Mature users, family groups, community pages",
        },
        "peak_hours_local": {
            "LinkedIn": ["07:30–09:00", "12:00–13:00", "17:00–18:00"],
            "Instagram": ["11:00–13:00", "19:00–21:00"],
            "TikTok": ["20:00–23:00"],
        },
        "content_style": "Polished, informative; finance & career focus; food culture; bilingual EN+ZH",
        "cultural_tips": [
            "English content works well; Singlish adds local authenticity",
            "High income market — premium products resonate",
            "Food content (hawker centres, restaurants) always viral",
            "Finance, property, and career tips hugely popular",
            "Multicultural sensitivity is expected",
        ],
        "smm_target_code": "SG",
        "internet_users_m": 5.5,
        "mobile_pct": 99,
        "avg_daily_social_min": 138,
    },
    "MY": {
        "code": "MY", "name": "Malaysia", "region": "Southeast Asia",
        "timezone": "Asia/Kuala_Lumpur", "utc_offset": "+08:00",
        "languages": ["Malay (Bahasa Malaysia)", "English", "Mandarin", "Tamil"],
        "content_languages": ["ms", "en", "zh"],
        "currency": "MYR",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter/X"],
        "platform_notes": {
            "YouTube": "#1 by time spent; tech, food, lifestyle dominate",
            "TikTok": "Rapid growth; comedy, food, Malay pop culture",
            "Facebook": "Established; groups, news, community",
            "Instagram": "Food photography, lifestyle, fashion",
        },
        "peak_hours_local": {
            "Facebook": ["09:00–11:00", "15:00–17:00", "21:00–23:00"],
            "TikTok": ["20:00–23:00"],
            "Instagram": ["10:00–12:00", "19:00–21:00"],
        },
        "content_style": "Multicultural; food culture is #1; Bahasa + English mix",
        "cultural_tips": [
            "Bahasa Malaysia content outperforms English for local reach",
            "Halal food and lifestyle content is massive segment",
            "Ramadan content sees huge spike in March/April",
            "Multilingual captions (BM + EN + ZH) maximise reach",
        ],
        "smm_target_code": "MY",
        "internet_users_m": 30.0,
        "mobile_pct": 97,
        "avg_daily_social_min": 169,
    },
    # ── EAST ASIA ─────────────────────────────────────────────────────────────
    "CN": {
        "code": "CN", "name": "China", "region": "East Asia",
        "timezone": "Asia/Shanghai", "utc_offset": "+08:00",
        "languages": ["Mandarin Chinese"],
        "content_languages": ["zh"],
        "currency": "CNY",
        "top_platforms": ["WeChat", "Douyin (TikTok CN)", "Weibo", "Bilibili", "Xiaohongshu (RED)"],
        "platform_notes": {
            "WeChat": "Super-app; essential for all brands; WeChat Official Accounts critical",
            "Douyin": "Domestic TikTok; most powerful short video; 700M+ daily users",
            "Weibo": "Twitter equivalent; celebrity and brand presence essential",
            "Bilibili": "Gen Z platform; anime, gaming, educational content",
            "Xiaohongshu": "Instagram+Pinterest hybrid; beauty, fashion, luxury",
        },
        "peak_hours_local": {
            "Douyin": ["12:00–13:00", "18:00–20:00", "21:00–23:00"],
            "WeChat": ["07:00–09:00", "12:00–14:00", "20:00–22:00"],
        },
        "content_style": "Aspirational, high production; nationalism-aligned; prosperity themes",
        "cultural_tips": [
            "Mandarin is mandatory — no exceptions",
            "All Western platforms (Facebook, Instagram, YouTube, Twitter) are blocked",
            "KOL (Key Opinion Leader) marketing is primary channel",
            "Golden Week (October) and Spring Festival are peak seasons",
            "Avoid Taiwan/HK political references — severely penalised",
            "Live commerce (直播带货) is the #1 conversion channel",
        ],
        "smm_target_code": "CN",
        "internet_users_m": 1050.0,
        "mobile_pct": 99,
        "avg_daily_social_min": 218,
    },
    "JP": {
        "code": "JP", "name": "Japan", "region": "East Asia",
        "timezone": "Asia/Tokyo", "utc_offset": "+09:00",
        "languages": ["Japanese"],
        "content_languages": ["ja"],
        "currency": "JPY",
        "top_platforms": ["YouTube", "Twitter/X", "Instagram", "TikTok", "LINE"],
        "platform_notes": {
            "LINE": "Primary messaging and content platform; essential for brands",
            "Twitter/X": "Highest Twitter penetration per capita; anime, gaming, news",
            "YouTube": "Long-form entertainment, tutorials; high retention",
            "Instagram": "Aesthetic, food, fashion; high-quality visuals",
            "TikTok": "Growing fast; youth 15-25; dance and comedy",
        },
        "peak_hours_local": {
            "Twitter/X": ["07:00–09:00", "12:00–13:00", "21:00–24:00"],
            "Instagram": ["12:00–13:00", "20:00–22:00"],
            "TikTok": ["21:00–24:00"],
        },
        "content_style": "Highly polished, kawaii aesthetics; precision and quality; seasonal content",
        "cultural_tips": [
            "Japanese language essential — English rarely works organically",
            "Seasonal content (sakura, summer festivals, autumn leaves) is evergreen",
            "Anime, gaming, and J-pop culture have global reach from JP base",
            "Quality and attention to detail are expected",
            "Avoid direct sales pressure — subtlety is valued",
        ],
        "smm_target_code": "JP",
        "internet_users_m": 104.0,
        "mobile_pct": 95,
        "avg_daily_social_min": 58,
    },
    "KR": {
        "code": "KR", "name": "South Korea", "region": "East Asia",
        "timezone": "Asia/Seoul", "utc_offset": "+09:00",
        "languages": ["Korean"],
        "content_languages": ["ko"],
        "currency": "KRW",
        "top_platforms": ["YouTube", "Instagram", "KakaoTalk", "TikTok", "Naver Blog"],
        "platform_notes": {
            "KakaoTalk": "Primary communication; KakaoStory and channels important",
            "YouTube": "K-pop, dramas, variety shows; global reach",
            "Instagram": "K-beauty, fashion, lifestyle; highly influential",
            "TikTok": "K-pop challenges, food, beauty routines",
            "Naver": "Search + blog ecosystem; SEO-critical for local brands",
        },
        "peak_hours_local": {
            "Instagram": ["09:00–11:00", "19:00–22:00"],
            "YouTube": ["20:00–23:00"],
            "TikTok": ["20:00–24:00"],
        },
        "content_style": "High-production K-pop aesthetic; beauty, tech, food, fashion",
        "cultural_tips": [
            "K-pop and K-drama references drive massive engagement globally",
            "Korean skincare and beauty content has worldwide audience",
            "Authenticity and 'real' content valued alongside high production",
            "Fan culture is powerful — engage fan communities",
        ],
        "smm_target_code": "KR",
        "internet_users_m": 49.5,
        "mobile_pct": 97,
        "avg_daily_social_min": 105,
    },
    "TW": {
        "code": "TW", "name": "Taiwan", "region": "East Asia",
        "timezone": "Asia/Taipei", "utc_offset": "+08:00",
        "languages": ["Traditional Chinese", "English"],
        "content_languages": ["zh-TW", "en"],
        "currency": "TWD",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "LINE"],
        "platform_notes": {
            "LINE": "Essential messaging; Line Today news feed important",
            "YouTube": "Dominant video platform; tech, food, lifestyle",
            "Instagram": "Millennials; food, fashion, travel",
            "Facebook": "Mature users; news groups very active",
        },
        "peak_hours_local": {
            "Instagram": ["12:00–13:00", "20:00–22:00"],
            "YouTube": ["19:00–23:00"],
        },
        "content_style": "Bubble tea culture, street food, tech-forward; Traditional Chinese essential",
        "cultural_tips": [
            "Traditional Chinese script (not Simplified) is required",
            "Street food, night markets, and bubble tea are eternal content pillars",
            "Tech and startup culture resonates with young professionals",
        ],
        "smm_target_code": "TW",
        "internet_users_m": 21.9,
        "mobile_pct": 96,
        "avg_daily_social_min": 131,
    },
    # ── SOUTH ASIA ────────────────────────────────────────────────────────────
    "IN": {
        "code": "IN", "name": "India", "region": "South Asia",
        "timezone": "Asia/Kolkata", "utc_offset": "+05:30",
        "languages": ["Hindi", "English", "Bengali", "Tamil", "Telugu", "and 20+ more"],
        "content_languages": ["hi", "en", "bn", "ta", "te"],
        "currency": "INR",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "WhatsApp", "ShareChat", "Moj"],
        "platform_notes": {
            "YouTube": "Top 2 market globally; 500M+ users; Hindi content dominant",
            "Instagram": "400M+ users; reels, fashion, food, fitness",
            "WhatsApp": "Near-universal; broadcast lists for marketing",
            "Facebook": "Tier-2/3 cities; news, community groups",
            "ShareChat": "Regional language content; 180M users",
        },
        "peak_hours_local": {
            "Instagram": ["12:00–14:00", "20:00–23:00"],
            "YouTube": ["20:00–23:30"],
            "Facebook": ["09:00–11:00", "19:00–21:00"],
        },
        "content_style": "Inspirational, aspirational; Bollywood references; cricket; multilingual",
        "cultural_tips": [
            "Hindi content gets 10x regional reach over English alone",
            "Diwali, Holi, IPL season are peak engagement periods",
            "Regional language content (Tamil, Telugu, Bengali) has dedicated loyal audiences",
            "Cricket integration in any content boosts shareability",
            "Price-sensitivity: value-for-money angle resonates",
        ],
        "smm_target_code": "IN",
        "internet_users_m": 800.0,
        "mobile_pct": 98,
        "avg_daily_social_min": 145,
    },
    "PK": {
        "code": "PK", "name": "Pakistan", "region": "South Asia",
        "timezone": "Asia/Karachi", "utc_offset": "+05:00",
        "languages": ["Urdu", "English"],
        "content_languages": ["ur", "en"],
        "currency": "PKR",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter/X"],
        "platform_notes": {
            "YouTube": "#1 by time-spent; drama, comedy, religious content",
            "TikTok": "Huge but periodically banned; youth entertainment",
            "Facebook": "Business and community; broad demographic",
        },
        "peak_hours_local": {
            "YouTube": ["21:00–00:00"],
            "TikTok": ["20:00–23:00"],
            "Facebook": ["18:00–22:00"],
        },
        "content_style": "Religious respect, family values; Urdu poetry; cricket; humour",
        "cultural_tips": [
            "Urdu language essential for authentic reach",
            "Islamic values and Ramadan content are peak engagement",
            "Cricket content has near-universal appeal",
            "Avoid political polarisation",
        ],
        "smm_target_code": "PK",
        "internet_users_m": 88.0,
        "mobile_pct": 98,
        "avg_daily_social_min": 175,
    },
    # ── MIDDLE EAST & NORTH AFRICA ────────────────────────────────────────────
    "SA": {
        "code": "SA", "name": "Saudi Arabia", "region": "Middle East",
        "timezone": "Asia/Riyadh", "utc_offset": "+03:00",
        "languages": ["Arabic", "English"],
        "content_languages": ["ar", "en"],
        "currency": "SAR",
        "top_platforms": ["YouTube", "Snapchat", "Twitter/X", "Instagram", "TikTok"],
        "platform_notes": {
            "Snapchat": "Highest Snapchat usage per capita globally; Saudi youth-dominant",
            "Twitter/X": "Most active Arabic Twitter country; news and discourse",
            "YouTube": "Top video platform; gaming, vlogs, Islamic content",
            "Instagram": "Fashion, luxury, food; high purchasing power",
            "TikTok": "Growing fast; comedy, talent",
        },
        "peak_hours_local": {
            "Twitter/X": ["21:00–02:00"],
            "Snapchat": ["19:00–01:00"],
            "Instagram": ["20:00–23:00"],
        },
        "content_style": "Luxury, modern Islamic culture; Vision 2030 themes; Arabic calligraphy",
        "cultural_tips": [
            "Arabic (MSA or Saudi dialect) is essential",
            "Ramadan season sees 3x spike in social media use",
            "Vision 2030 themes (tourism, tech, entertainment) are hot",
            "Gender segregation in visuals (modest representation)",
            "High purchasing power — premium pricing works",
        ],
        "smm_target_code": "SA",
        "internet_users_m": 36.3,
        "mobile_pct": 99,
        "avg_daily_social_min": 229,
    },
    "EG": {
        "code": "EG", "name": "Egypt", "region": "Middle East / Africa",
        "timezone": "Africa/Cairo", "utc_offset": "+02:00",
        "languages": ["Arabic (Egyptian)", "English"],
        "content_languages": ["ar", "en"],
        "currency": "EGP",
        "top_platforms": ["Facebook", "YouTube", "TikTok", "Instagram", "Twitter/X"],
        "platform_notes": {
            "Facebook": "Dominant; highest Arab Facebook country by users",
            "YouTube": "Arabic drama, music, comedy content huge",
            "TikTok": "Youth entertainment explosion; Egyptian dialect comedy viral",
        },
        "peak_hours_local": {
            "Facebook": ["20:00–00:00"],
            "YouTube": ["21:00–01:00"],
            "TikTok": ["21:00–00:00"],
        },
        "content_style": "Egyptian humour (sarcastic wit), relatable struggle, Arabic dialect",
        "cultural_tips": [
            "Egyptian Arabic dialect (Masri) is the most understood across Arab world",
            "Ramadan is the biggest advertising season in the Arab world",
            "Football (soccer) content is universally engaging",
            "Economic hardship humour resonates with middle class",
        ],
        "smm_target_code": "EG",
        "internet_users_m": 78.0,
        "mobile_pct": 96,
        "avg_daily_social_min": 204,
    },
    "AE": {
        "code": "AE", "name": "United Arab Emirates", "region": "Middle East",
        "timezone": "Asia/Dubai", "utc_offset": "+04:00",
        "languages": ["Arabic", "English"],
        "content_languages": ["ar", "en"],
        "currency": "AED",
        "top_platforms": ["Instagram", "YouTube", "Snapchat", "TikTok", "LinkedIn", "Twitter/X"],
        "platform_notes": {
            "Instagram": "Luxury, travel, lifestyle dominant; influencer hub",
            "LinkedIn": "Strong professional market; expat business community",
            "Snapchat": "Local youth; Arabic content",
            "YouTube": "Bilingual content; tourism and business",
        },
        "peak_hours_local": {
            "Instagram": ["12:00–14:00", "20:00–23:00"],
            "LinkedIn": ["07:00–09:00", "17:00–19:00"],
        },
        "content_style": "Luxury, cosmopolitan, bilingual; travel and real estate; multicultural",
        "cultural_tips": [
            "Bilingual Arabic + English content performs best",
            "Luxury travel, real estate, fine dining are top categories",
            "Expo/tourism themes align with government objectives",
            "Expat community (88% of population) responds to international content",
        ],
        "smm_target_code": "AE",
        "internet_users_m": 9.9,
        "mobile_pct": 99,
        "avg_daily_social_min": 201,
    },
    # ── EUROPE ────────────────────────────────────────────────────────────────
    "GB": {
        "code": "GB", "name": "United Kingdom", "region": "Europe",
        "timezone": "Europe/London", "utc_offset": "+00:00",
        "languages": ["English"],
        "content_languages": ["en"],
        "currency": "GBP",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter/X", "LinkedIn"],
        "platform_notes": {
            "TikTok": "Dominant with Gen Z; 23M+ UK users",
            "Instagram": "Lifestyle, fashion, food; strong influencer economy",
            "LinkedIn": "Professional content; strong B2B market",
            "YouTube": "All-age consumption; long-form tutorials",
            "Twitter/X": "News, political commentary, sports (football)",
        },
        "peak_hours_local": {
            "Instagram": ["11:00–13:00", "19:00–21:00"],
            "TikTok": ["19:00–23:00"],
            "LinkedIn": ["07:00–09:00", "17:00–18:00"],
            "YouTube": ["20:00–22:00"],
        },
        "content_style": "Dry humour, self-deprecating wit; authenticity over perfection; BBC quality",
        "cultural_tips": [
            "Authenticity trumps polished perfection for UK audiences",
            "British humour and understatement win engagement",
            "Football (soccer) content universally popular",
            "Mental health and sustainability themes resonate with Gen Z",
        ],
        "smm_target_code": "GB",
        "internet_users_m": 65.0,
        "mobile_pct": 94,
        "avg_daily_social_min": 108,
    },
    "DE": {
        "code": "DE", "name": "Germany", "region": "Europe",
        "timezone": "Europe/Berlin", "utc_offset": "+01:00",
        "languages": ["German", "English"],
        "content_languages": ["de", "en"],
        "currency": "EUR",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "LinkedIn", "XING"],
        "platform_notes": {
            "YouTube": "Most popular video platform; tech, finance, food",
            "XING": "German LinkedIn alternative; essential for DACH B2B",
            "Instagram": "Lifestyle and travel; strong but more private",
            "TikTok": "Growing with under-30s",
        },
        "peak_hours_local": {
            "Instagram": ["11:00–13:00", "19:00–21:00"],
            "YouTube": ["20:00–22:00"],
            "LinkedIn": ["07:00–09:00", "17:00–18:00"],
        },
        "content_style": "Informative, factual, high-quality; data-backed content; serious tone",
        "cultural_tips": [
            "German language strongly preferred for local reach",
            "Privacy sensitivity — avoid intrusive or data-heavy impressions",
            "Quality and accuracy valued highly; errors damage credibility",
            "Sustainability (Nachhaltigkeit) is a top content theme",
            "Formal tone for B2B; lighter for B2C",
        ],
        "smm_target_code": "DE",
        "internet_users_m": 79.0,
        "mobile_pct": 91,
        "avg_daily_social_min": 71,
    },
    "FR": {
        "code": "FR", "name": "France", "region": "Europe",
        "timezone": "Europe/Paris", "utc_offset": "+01:00",
        "languages": ["French", "English"],
        "content_languages": ["fr", "en"],
        "currency": "EUR",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "Twitter/X", "Snapchat"],
        "platform_notes": {
            "Snapchat": "France has one of Europe's highest Snapchat usage rates",
            "TikTok": "Strong Gen Z market; fashion and arts",
            "Instagram": "Fashion, gastronomy, luxury",
            "YouTube": "Humour, DIY, gaming",
        },
        "peak_hours_local": {
            "Instagram": ["12:00–13:00", "19:00–21:00"],
            "TikTok": ["20:00–23:00"],
        },
        "content_style": "Sophisticated, cultural, fashion-forward; joie de vivre; gastronomy",
        "cultural_tips": [
            "French language preferred; English feels too commercial",
            "Culture, fashion, food, and wine are timeless pillars",
            "Avoid aggressive marketing tone — subtlety valued",
            "Bastille Day (July 14) and fashion weeks are engagement peaks",
        ],
        "smm_target_code": "FR",
        "internet_users_m": 58.0,
        "mobile_pct": 92,
        "avg_daily_social_min": 82,
    },
    # ── AMERICAS ──────────────────────────────────────────────────────────────
    "US": {
        "code": "US", "name": "United States", "region": "North America",
        "timezone": "America/New_York", "utc_offset": "-05:00",
        "languages": ["English", "Spanish"],
        "content_languages": ["en", "es"],
        "currency": "USD",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "Twitter/X", "LinkedIn", "Pinterest", "Snapchat"],
        "platform_notes": {
            "YouTube": "World's largest video platform; all niches",
            "TikTok": "60M+ daily users; entertainment, education, politics",
            "Instagram": "Influencer capital of the world; all demographics",
            "LinkedIn": "World's largest professional network; B2B essential",
            "Pinterest": "DIY, fashion, recipes, home décor; purchasing intent high",
        },
        "peak_hours_local": {
            "Instagram": ["11:00–13:00", "19:00–21:00"],
            "TikTok": ["19:00–23:00"],
            "YouTube": ["20:00–23:00"],
            "LinkedIn": ["07:00–09:00", "12:00–13:00", "17:00–18:00"],
        },
        "content_style": "Bold, direct, high-energy; aspiration + relatability; diverse representation",
        "cultural_tips": [
            "Diversity, equity, and inclusion (DEI) themes are standard",
            "Short attention span — hook in first 2 seconds",
            "Trending audio/sounds on TikTok/Reels drive organic reach",
            "Super Bowl, NFL, NBA, and election seasons spike engagement",
            "Subtitles/captions increase reach to 85% who watch muted",
        ],
        "smm_target_code": "US",
        "internet_users_m": 311.0,
        "mobile_pct": 93,
        "avg_daily_social_min": 123,
    },
    "BR": {
        "code": "BR", "name": "Brazil", "region": "South America",
        "timezone": "America/Sao_Paulo", "utc_offset": "-03:00",
        "languages": ["Portuguese"],
        "content_languages": ["pt-BR"],
        "currency": "BRL",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "WhatsApp", "Twitter/X"],
        "platform_notes": {
            "WhatsApp": "Near-universal; Brazil is WhatsApp's largest market",
            "Instagram": "One of world's most engaged markets; 120M+ users",
            "TikTok": "Fastest growing; dance, music, beauty, comedy",
            "YouTube": "Massive; all niches; second-largest YouTube market",
        },
        "peak_hours_local": {
            "Instagram": ["11:00–13:00", "20:00–22:00"],
            "TikTok": ["19:00–23:00"],
            "YouTube": ["20:00–23:00"],
            "WhatsApp": ["08:00–10:00", "19:00–22:00"],
        },
        "content_style": "Energetic, emotional, musical; carnival spirit; football; warmth",
        "cultural_tips": [
            "Portuguese (Brazilian) is essential — no shortcuts",
            "Football, Carnaval, and music are always viral",
            "Warm, relationship-focused marketing outperforms transactional",
            "Influencer culture (digital influencers) is massive",
        ],
        "smm_target_code": "BR",
        "internet_users_m": 165.0,
        "mobile_pct": 98,
        "avg_daily_social_min": 218,
    },
    "MX": {
        "code": "MX", "name": "Mexico", "region": "Latin America",
        "timezone": "America/Mexico_City", "utc_offset": "-06:00",
        "languages": ["Spanish"],
        "content_languages": ["es-MX"],
        "currency": "MXN",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter/X", "WhatsApp"],
        "platform_notes": {
            "Facebook": "Dominant; 80M+ users; groups and pages active",
            "TikTok": "Huge growth; comedy, music, food",
            "YouTube": "All-age consumption; telenovela recaps, music",
        },
        "peak_hours_local": {
            "Facebook": ["12:00–14:00", "20:00–22:00"],
            "TikTok": ["20:00–23:00"],
            "Instagram": ["11:00–13:00", "19:00–21:00"],
        },
        "content_style": "Family values, humour, folklore, food culture; Mexican pride",
        "cultural_tips": [
            "Mexican Spanish with local slang (güey, chido) boosts authenticity",
            "Día de los Muertos, Independence Day (Sept 16) are peak content windows",
            "Food content (tacos, street food) universally viral",
            "Family values and tradition are core emotional pillars",
        ],
        "smm_target_code": "MX",
        "internet_users_m": 97.0,
        "mobile_pct": 97,
        "avg_daily_social_min": 184,
    },
    # ── AFRICA ────────────────────────────────────────────────────────────────
    "NG": {
        "code": "NG", "name": "Nigeria", "region": "Africa",
        "timezone": "Africa/Lagos", "utc_offset": "+01:00",
        "languages": ["English", "Hausa", "Yoruba", "Igbo"],
        "content_languages": ["en", "yo", "ha"],
        "currency": "NGN",
        "top_platforms": ["YouTube", "Instagram", "Facebook", "TikTok", "Twitter/X", "WhatsApp"],
        "platform_notes": {
            "Twitter/X": "Nigeria is among the most Twitter-active countries globally",
            "TikTok": "Afrobeats, comedy skits, fashion; explosive growth",
            "Instagram": "Influencer culture; fashion, music, luxury",
            "YouTube": "Nollywood, music videos, comedy",
        },
        "peak_hours_local": {
            "Twitter/X": ["08:00–11:00", "18:00–23:00"],
            "TikTok": ["19:00–23:00"],
            "Instagram": ["12:00–14:00", "20:00–22:00"],
        },
        "content_style": "Bold, witty, Afrobeats culture; hustle mentality; Naija pride",
        "cultural_tips": [
            "Nigerian Pidgin and Yoruba/Hausa phrases boost authenticity",
            "Afrobeats music references are universally engaging",
            "Entrepreneurship and hustle culture are aspirational themes",
            "Skit comedy format has huge following (Mr. Macaroni style)",
        ],
        "smm_target_code": "NG",
        "internet_users_m": 123.0,
        "mobile_pct": 98,
        "avg_daily_social_min": 167,
    },
    "ZA": {
        "code": "ZA", "name": "South Africa", "region": "Africa",
        "timezone": "Africa/Johannesburg", "utc_offset": "+02:00",
        "languages": ["Zulu", "Xhosa", "Afrikaans", "English"],
        "content_languages": ["en", "zu", "af"],
        "currency": "ZAR",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "Twitter/X", "WhatsApp"],
        "platform_notes": {
            "WhatsApp": "Primary communication; status feature for marketing",
            "TikTok": "Kwaito, Amapiano music culture; youth content",
            "YouTube": "All demographics; news, sport, entertainment",
        },
        "peak_hours_local": {
            "Facebook": ["08:00–10:00", "19:00–22:00"],
            "TikTok": ["19:00–23:00"],
            "Instagram": ["12:00–14:00", "19:00–21:00"],
        },
        "content_style": "Ubuntu (community), rainbow nation diversity; sport; Amapiano music",
        "cultural_tips": [
            "English works broadly but local language phrases are powerful",
            "Amapiano and Kwaito music culture is globally trending",
            "Rugby, cricket, and football are top engagement triggers",
            "Load-shedding (power cuts) humour is uniquely relatable",
        ],
        "smm_target_code": "ZA",
        "internet_users_m": 42.0,
        "mobile_pct": 95,
        "avg_daily_social_min": 135,
    },
    # ── OCEANIA ───────────────────────────────────────────────────────────────
    "AU": {
        "code": "AU", "name": "Australia", "region": "Oceania",
        "timezone": "Australia/Sydney", "utc_offset": "+10:00",
        "languages": ["English"],
        "content_languages": ["en"],
        "currency": "AUD",
        "top_platforms": ["YouTube", "Facebook", "Instagram", "TikTok", "LinkedIn", "Snapchat"],
        "platform_notes": {
            "TikTok": "15M+ users; food, fitness, comedy, outdoor lifestyle",
            "Instagram": "Lifestyle, travel, fitness; beach culture dominant",
            "LinkedIn": "Strong professional market; mining, tech, finance",
        },
        "peak_hours_local": {
            "Instagram": ["11:00–13:00", "19:00–21:00"],
            "TikTok": ["19:00–23:00"],
            "YouTube": ["20:00–22:00"],
        },
        "content_style": "Laid-back, humorous, outdoor lifestyle; directness; beach/nature",
        "cultural_tips": [
            "Australians value authenticity and dislike pretension",
            "Outdoor lifestyle, sport (AFL, cricket, rugby), and beaches are pillars",
            "Tall Poppy Syndrome — avoid appearing elitist",
            "Summer Christmas and Australian Open (Jan) are peak windows",
        ],
        "smm_target_code": "AU",
        "internet_users_m": 23.0,
        "mobile_pct": 95,
        "avg_daily_social_min": 117,
    },
}


# ─── Helper: get local time for a country ─────────────────────────────────────
def get_local_time(country_code: str) -> dict:
    """Return the current local time and date for a given country."""
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country code '{country_code}' not found"}
    try:
        tz   = ZoneInfo(country["timezone"])
        now  = datetime.now(tz)
        return {
            "country":      country["name"],
            "timezone":     country["timezone"],
            "utc_offset":   country["utc_offset"],
            "local_time":   now.strftime("%H:%M:%S"),
            "local_date":   now.strftime("%Y-%m-%d"),
            "weekday":      now.strftime("%A"),
            "local_datetime": now.isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Helper: country search ────────────────────────────────────────────────────
def search_locations(query: str) -> list[dict]:
    """Search countries by name, code, or region."""
    q = query.lower().strip()
    results = []
    for code, data in COUNTRIES.items():
        if (
            q in data["name"].lower()
            or q == code.lower()
            or q in data["region"].lower()
            or any(q in lang.lower() for lang in data["languages"])
        ):
            results.append({
                "code":     code,
                "name":     data["name"],
                "region":   data["region"],
                "timezone": data["timezone"],
                "top_platforms": data["top_platforms"][:3],
            })
    return results


def list_all_countries() -> list[dict]:
    """Return all countries with summary info."""
    return [
        {
            "code":           c["code"],
            "name":           c["name"],
            "region":         c["region"],
            "timezone":       c["timezone"],
            "utc_offset":     c["utc_offset"],
            "languages":      c["languages"],
            "top_platforms":  c["top_platforms"][:4],
            "internet_users_m": c.get("internet_users_m", 0),
            "avg_daily_social_min": c.get("avg_daily_social_min", 0),
        }
        for c in COUNTRIES.values()
    ]


def get_country_detail(country_code: str) -> dict:
    """Return full detail for a country."""
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not in database. Try a 2-letter ISO code."}
    return {**country, "local_time": get_local_time(country_code)}


# ═══════════════════════════════════════════════════════════════════════════════
# GEO AI FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def get_geo_strategy(country_code: str, platform: str, niche: str) -> dict:
    """
    Feature #26: Generate a geo-targeted growth strategy.
    Fully location-aware — different strategies for KH vs US vs SA etc.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    cn       = country["name"]
    tz       = country["timezone"]
    langs    = ", ".join(country["languages"])
    tips     = " | ".join(country["cultural_tips"][:4])
    peaks    = json.dumps(country["peak_hours_local"].get(platform, ["07:00-09:00", "19:00-22:00"]))
    plat_note = country["platform_notes"].get(platform, f"{platform} is used in {cn}")

    if USE_REAL_AI:
        prompt = (
            f"Create a PRECISE geo-targeted social media growth strategy for:\n"
            f"Country: {cn} ({country_code})\n"
            f"Platform: {platform}\n"
            f"Niche: {niche}\n"
            f"Languages: {langs}\n"
            f"Platform context in this country: {plat_note}\n"
            f"Cultural tips: {tips}\n"
            f"Peak hours (local): {peaks}\n"
            f"Timezone: {tz}\n\n"
            "Provide JSON with: strategy_overview(str), "
            "content_pillars(list of 5 items with title and description), "
            "language_strategy(str), posting_schedule(dict), "
            "geo_hooks(list of 5 location-specific content ideas), "
            "local_hashtags(list of 10), "
            "cultural_do_list(list of 5), cultural_dont_list(list of 5), "
            "estimated_monthly_growth_pct(number), "
            "90_day_milestones(list of 3)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                start = raw.find("{"); end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    return {"source": "ai", "country": cn, **json.loads(raw[start:end])}
            except Exception:
                return {"source": "ai_text", "country": cn, "strategy_overview": raw}

    # Smart mock
    return {
        "source": "smart_mock",
        "country": cn,
        "country_code": country_code,
        "platform": platform,
        "niche": niche,
        "strategy_overview": (
            f"Target {cn}'s {platform} audience in the {niche} niche. "
            f"Post in {country['languages'][0]} during peak hours {peaks}. "
            f"{plat_note}"
        ),
        "content_pillars": [
            {"title": "Local Stories", "description": f"Content set in {cn} locations audiences recognise"},
            {"title": f"{niche} Education", "description": f"Teach {niche} skills in {country['languages'][0]}"},
            {"title": "Cultural Moments", "description": f"Leverage local holidays and traditions"},
            {"title": "Behind The Scenes", "description": "Authentic day-in-life content for {cn}"},
            {"title": "Community UGC", "description": f"Encourage {cn} followers to create for your brand"},
        ],
        "language_strategy": f"Primary: {country['languages'][0]}. Secondary: {country['languages'][1] if len(country['languages']) > 1 else 'N/A'}",
        "posting_schedule": country["peak_hours_local"],
        "geo_hooks": [
            f"What it's like to {niche} in {cn}",
            f"Top {niche} spots in {cn}",
            f"Why {cn} is perfect for {niche}",
            f"{cn} {niche} vs the world",
            f"Day in my life as a {niche} creator in {cn}",
        ],
        "local_hashtags": [f"#{cn.replace(' ', '')}{niche.replace(' ', '')}", f"#{cn.replace(' ', '')}Creator", f"#{niche.replace(' ', '')}"],
        "cultural_do_list": country["cultural_tips"][:5],
        "cultural_dont_list": ["Don't ignore local language", "Don't post at off-peak hours", "Don't use only English", "Don't ignore local holidays", "Don't copy foreign content without localising"],
        "estimated_monthly_growth_pct": 12.5,
        "90_day_milestones": [
            f"Day 30: 500 new {cn}-based followers",
            f"Day 60: 2,000 followers + first viral post",
            f"Day 90: 5,000 followers + brand partnership ready",
        ],
        "content_style": country["content_style"],
        "platform_notes": plat_note,
        "local_time": get_local_time(country_code),
    }


async def get_best_times_by_timezone(country_code: str, platform: str) -> dict:
    """
    Feature #28: Return exact posting times in local timezone AND UTC.
    Fully precise — no guessing.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    tz_name = country["timezone"]
    local_peaks = country["peak_hours_local"].get(
        platform,
        country["peak_hours_local"].get(list(country["peak_hours_local"].keys())[0], ["07:00-09:00", "20:00-22:00"])
        if country["peak_hours_local"] else ["07:00-09:00", "20:00-22:00"]
    )

    # Convert local peak hours to UTC
    try:
        tz = ZoneInfo(tz_name)
        utc_peaks = []
        for window in local_peaks:
            start_str = window.split("–")[0].split("-")[0].strip()
            try:
                local_dt = datetime.now(tz).replace(
                    hour=int(start_str.split(":")[0]),
                    minute=int(start_str.split(":")[1]) if ":" in start_str else 0,
                    second=0, microsecond=0,
                )
                utc_dt = local_dt.astimezone(timezone.utc)
                utc_peaks.append(f"{utc_dt.strftime('%H:%M')} UTC")
            except Exception:
                utc_peaks.append("N/A")
    except Exception:
        utc_peaks = ["N/A"]

    local_now = get_local_time(country_code)

    return {
        "country":           country["name"],
        "country_code":      country_code,
        "platform":          platform,
        "timezone":          tz_name,
        "utc_offset":        country["utc_offset"],
        "local_time_now":    local_now.get("local_time", "N/A"),
        "local_date_now":    local_now.get("local_date", "N/A"),
        "weekday":           local_now.get("weekday", "N/A"),
        "peak_hours_local":  local_peaks,
        "peak_hours_utc":    utc_peaks,
        "all_platform_peaks": country["peak_hours_local"],
        "posting_frequency_recommendation": (
            "3-5 posts/week for organic growth. "
            "Post at first peak for morning audience, second peak for evening prime-time."
        ),
        "timezone_tip": (
            f"Your audience is in {tz_name} (UTC{country['utc_offset']}). "
            f"Schedule posts in your dashboard as {utc_peaks[0] if utc_peaks else 'morning UTC'}."
        ),
    }


async def get_regional_trends(country_code: str, niche: str = "General") -> dict:
    """
    Feature #27: Trending topics specific to a country/region.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    cn   = country["name"]
    lang = country["languages"][0]

    if USE_REAL_AI:
        now = datetime.now().strftime("%B %Y")
        prompt = (
            f"What are the top 10 trending social media topics RIGHT NOW in {cn} ({country_code}) "
            f"for the niche: {niche}? Current date: {now}.\n"
            f"Primary language: {lang}\n"
            f"Top platforms: {', '.join(country['top_platforms'][:4])}\n\n"
            "Return JSON: trending_topics(list: topic, trend_score 0-100, "
            "content_angle, platforms_strongest_on, language_to_use), "
            "regional_insight(str), upcoming_local_events(list), "
            "evergreen_local_topics(list of 5)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                start = raw.find("{"); end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    return {"source": "ai", "country": cn, **json.loads(raw[start:end])}
            except Exception:
                return {"source": "ai_text", "country": cn, "regional_insight": raw}

    # Smart mock
    tips  = country["cultural_tips"]
    month = datetime.now().strftime("%B")
    return {
        "source":          "smart_mock",
        "country":         cn,
        "country_code":    country_code,
        "niche":           niche,
        "trending_topics": [
            {"topic": f"Local {niche} in {cn}", "trend_score": 88, "content_angle": "Localised how-to", "language_to_use": lang},
            {"topic": f"{cn} {month} trends",    "trend_score": 82, "content_angle": "Seasonal content", "language_to_use": lang},
            {"topic": f"{cn} lifestyle",          "trend_score": 78, "content_angle": "Day-in-life vlog", "language_to_use": lang},
            {"topic": f"Best of {cn}",            "trend_score": 74, "content_angle": "Top 10 list",      "language_to_use": lang},
            {"topic": f"{niche} tips for beginners", "trend_score": 71, "content_angle": "Tutorial",      "language_to_use": lang},
        ],
        "regional_insight": (
            f"Content in {lang} about {niche} is currently performing well in {cn}. "
            f"Peak engagement windows: {json.dumps(country['peak_hours_local'])}. "
            f"{country['content_style']}"
        ),
        "upcoming_local_events": tips[:3],
        "evergreen_local_topics": [
            f"{cn} food culture",
            f"{cn} travel destinations",
            f"Learning {lang}",
            f"{niche} in {cn}",
            f"Life in {cn} 2025",
        ],
        "platform_notes": country["platform_notes"],
    }


async def get_cultural_content_guide(country_code: str, niche: str) -> dict:
    """
    Feature #29: Detailed cultural content guide for a target location.
    What to say, how to say it, what to avoid — zero ambiguity.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    cn    = country["name"]
    style = country["content_style"]
    tips  = country["cultural_tips"]
    langs = country["languages"]

    if USE_REAL_AI:
        prompt = (
            f"Write a comprehensive cultural content guide for creating {niche} content targeting {cn}.\n"
            f"Content style in {cn}: {style}\n"
            f"Cultural tips known: {chr(10).join(tips)}\n"
            f"Languages: {', '.join(langs)}\n\n"
            "Return JSON: content_tone(str), vocabulary_tips(list of 5), "
            "visual_style(str), music_and_sound_tips(str), "
            "caption_formula(str), cta_examples(list of 5 culturally appropriate CTAs), "
            "taboo_topics(list), safe_topics(list of 10), "
            "seasonal_calendar(dict: month -> content_theme), "
            "emoji_usage(str), hashtag_language(str)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                start = raw.find("{"); end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    return {"source": "ai", "country": cn, "niche": niche, **json.loads(raw[start:end])}
            except Exception:
                return {"source": "ai_text", "country": cn, "niche": niche, "content_tone": raw}

    return {
        "source":        "smart_mock",
        "country":       cn,
        "country_code":  country_code,
        "niche":         niche,
        "content_tone":  style,
        "vocabulary_tips": [
            f"Use {langs[0]} as primary voice",
            "Mix local slang authentically — don't force it",
            "Reference local places and events your audience knows",
            "Avoid overly formal language unless B2B",
            "Match the dialect of your target city/region",
        ],
        "visual_style": f"Reflect {cn} aesthetic — {style}",
        "music_and_sound_tips": f"Use trending local audio from {cn}; {country['top_platforms'][0]} trending sounds",
        "caption_formula": f"Hook in {langs[0]} → Value → Local reference → CTA",
        "cta_examples": [
            f"Comment your {cn} experience below 👇",
            f"Tag a friend in {cn} who needs to see this!",
            f"Save this for your next {niche} project!",
            f"Follow for more {cn} {niche} tips daily!",
            f"Share if you agree! 🔥",
        ],
        "taboo_topics": ["Politics", "Religion (treat with respect)", "Sensitive historical events"],
        "safe_topics": [
            "Food and cuisine", "Travel and tourism", "Family", "Education",
            "Sports", "Local music", "Fashion", "Technology", "Business tips", "Health",
        ],
        "seasonal_calendar": {
            "January": "New Year goals", "February": "Valentine's Day",
            "March": "Spring/Fresh start", "April": "Local festival season",
            "May": "Mothers Day", "June": "Mid-year review", "July": "Summer",
            "August": "Back to school", "September": "New season launch",
            "October": "Halloween / harvest", "November": "Gratitude",
            "December": "Christmas / Year end",
        },
        "emoji_usage": f"Emoji-moderate usage; use flag 🇰🇭 for national pride posts",
        "hashtag_language": f"Use {langs[0]} hashtags + English hashtags for 2x reach",
        "cultural_tips": tips,
        "platform_notes": country["platform_notes"],
    }


async def get_platform_availability(country_code: str) -> dict:
    """
    Feature #30: Which platforms are dominant, growing, declining, or blocked in a country.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    blocked = []
    if country_code == "CN":
        blocked = ["Facebook", "Instagram", "YouTube", "Twitter/X", "WhatsApp", "TikTok (use Douyin)"]
    elif country_code == "KP":
        blocked = ["All Western platforms"]

    return {
        "country":       country["name"],
        "country_code":  country_code,
        "region":        country["region"],
        "top_platforms": country["top_platforms"],
        "platform_notes": country["platform_notes"],
        "blocked_platforms": blocked,
        "recommended_primary": country["top_platforms"][0] if country["top_platforms"] else "None",
        "recommended_secondary": country["top_platforms"][1] if len(country["top_platforms"]) > 1 else "None",
        "internet_users_m": country.get("internet_users_m", 0),
        "mobile_pct": country.get("mobile_pct", 0),
        "avg_daily_social_min": country.get("avg_daily_social_min", 0),
        "market_size_tier": (
            "Tier 1 (>100M users)" if country.get("internet_users_m", 0) >= 100
            else "Tier 2 (10M-100M)" if country.get("internet_users_m", 0) >= 10
            else "Tier 3 (<10M)"
        ),
    }


async def get_geo_audience_insights(country_code: str, platform: str, niche: str) -> dict:
    """
    Feature #31: Regional audience demographics and psychographics.
    """
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return {"error": f"Country '{country_code}' not found"}

    cn = country["name"]

    if USE_REAL_AI:
        prompt = (
            f"Provide detailed audience demographics and psychographics for {platform} users in {cn} "
            f"interested in {niche}.\n"
            f"Avg daily social media use: {country.get('avg_daily_social_min', 120)} minutes\n"
            f"Internet users: {country.get('internet_users_m', 10)}M\n"
            f"Mobile usage: {country.get('mobile_pct', 90)}%\n\n"
            "Return JSON: age_distribution(dict), gender_split(dict), "
            "income_level(str), education_level(str), device_usage(dict), "
            "content_consumption_habits(str), purchase_behavior(str), "
            "pain_points(list of 5), aspirations(list of 5), "
            "content_format_preference(list), "
            "estimated_audience_size(str), avg_engagement_rate(str)"
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                start = raw.find("{"); end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    return {"source": "ai", "country": cn, "platform": platform, "niche": niche, **json.loads(raw[start:end])}
            except Exception:
                return {"source": "ai_text", "country": cn, "content_consumption_habits": raw}

    mu = country.get("mobile_pct", 90)
    iu = country.get("internet_users_m", 10)
    dm = country.get("avg_daily_social_min", 120)
    return {
        "source":                "smart_mock",
        "country":               cn,
        "country_code":          country_code,
        "platform":              platform,
        "niche":                 niche,
        "age_distribution":      {"18-24": "32%", "25-34": "35%", "35-44": "18%", "45+": "15%"},
        "gender_split":          {"Male": "52%", "Female": "48%"},
        "income_level":          "Low-Middle income; price-sensitive",
        "education_level":       "Secondary to University educated",
        "device_usage":          {"Mobile": f"{mu}%", "Desktop": f"{100-mu}%"},
        "content_consumption_habits": (
            f"Avg {dm} min/day on social media. "
            f"Primarily consumes short video ({platform}). "
            f"Peak hours: {json.dumps(country['peak_hours_local'])}"
        ),
        "purchase_behavior":     "Social proof driven; influenced by KOLs; WhatsApp commerce growing",
        "pain_points":           ["Limited time", "Information overload", "Trust in brands", "Language barrier", "Price sensitivity"],
        "aspirations":           ["Better income", "Travel", "Learning new skills", "Social status", "Family wellbeing"],
        "content_format_preference": ["Short video (15-60s)", "Stories", "Live streams", "Carousels", "Long-form tutorials"],
        "estimated_audience_size": f"{int(iu * 0.35)}M {platform} users in {cn}",
        "avg_engagement_rate":   "4.2% (above global average of 2.8%)",
        "languages":             country["languages"],
    }


async def get_multi_country_comparison(country_codes: list[str], platform: str) -> dict:
    """
    Compare multiple countries side-by-side for platform strategy.
    """
    results = {}
    for code in country_codes[:10]:
        c = COUNTRIES.get(code.upper())
        if c:
            results[code] = {
                "name":              c["name"],
                "region":            c["region"],
                "internet_users_m":  c.get("internet_users_m", 0),
                "avg_daily_social_min": c.get("avg_daily_social_min", 0),
                "mobile_pct":        c.get("mobile_pct", 0),
                "top_platforms":     c["top_platforms"][:3],
                "platform_ranked":   c["top_platforms"].index(platform) + 1 if platform in c["top_platforms"] else 99,
                "peak_hours":        c["peak_hours_local"].get(platform, ["N/A"]),
                "primary_language":  c["languages"][0],
                "content_style":     c["content_style"][:80],
            }

    if not results:
        return {"error": "No valid country codes provided"}

    # Rank by platform dominance
    ranked = sorted(results.items(), key=lambda x: x[1]["platform_ranked"])
    return {
        "platform":   platform,
        "countries":  results,
        "ranked_by_platform_dominance": [{"code": k, "name": v["name"], "rank": v["platform_ranked"]} for k, v in ranked],
        "total_reach_m": sum(v["internet_users_m"] for v in results.values()),
        "compared_at": datetime.now().isoformat(),
    }
