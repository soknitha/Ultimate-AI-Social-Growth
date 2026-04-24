"""
GrowthOS AI — Community & Real-Time Intelligence Engine
=========================================================
P8: Influencer Collab Hub, UGC Campaign, Social Proof Creator,
    Community Playbook, Live Stream Planner
P9: Trend Hijacker, Viral Content Cloner, Posting Time Intelligence,
    Niche Opportunity Scanner
"""
import json, re
from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str):
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


# ─── P8: Community & Collaboration ─────────────────────────────────────────

async def plan_influencer_collab(
    brand: str, influencer_niche: str, platform: str = "Instagram",
    budget: str = "$500", goal: str = "Brand Awareness",
    language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        return {
            "brand": brand,
            "collaboration_type": "Sponsored Post + Story Takeover",
            "outreach_message": (
                f"Hey [Influencer Name]! 👋\n\n"
                f"I've been following your {influencer_niche} content on {platform} — "
                f"your [specific post/style] really resonated with me.\n\n"
                f"I'm [Your Name] from {brand}. We [what you do] and our audience is very "
                f"similar to yours — [why they're aligned].\n\n"
                f"I'd love to explore a collaboration that would genuinely add value for your "
                f"audience. Here's what I had in mind: [brief idea].\n\n"
                f"Would you be open to a quick 15-min chat or I can send over a full brief?\n\n"
                f"No pressure at all — excited to see what you create either way! 🙏\n"
                f"— [Your Name]"
            ),
            "collaboration_brief": (
                f"## {brand} x [Influencer] Collaboration Brief\n\n"
                f"**Goal:** {goal}\n"
                f"**Platform:** {platform}\n"
                f"**Budget:** {budget}\n"
                f"**Deliverables:** 1x Feed Post + 3x Stories + 1x Story Link (if eligible)\n"
                f"**Timeline:** Content to go live within 2 weeks of agreement\n"
                f"**Messaging:** [Key message — what we want audience to know/feel]\n"
                f"**Hashtags:** #Ad #Sponsored #{brand.replace(' ','')}Collab\n"
                f"**Approval:** Content to be shared with us 48h before posting for review"
            ),
            "contract_key_points": [
                "Usage rights: Brand can repurpose content for 6 months on owned channels",
                "Exclusivity: Influencer agrees not to post competitor content 2 weeks before/after",
                "Disclosure: Must include #Ad or #Sponsored (FTC compliant)",
                "Payment terms: 50% upfront, 50% within 7 days of post going live",
                "Performance clause: Reshoot if content violates brand guidelines",
            ],
            "deliverables": [
                f"1x {platform} feed post (photo or Reel)",
                "3x Stories with swipe-up / link sticker",
                "Content usage rights for brand's social + ads",
            ],
            "kpis": [
                "Reach & impressions",
                "Story link clicks (conversion metric)",
                "New followers gained during collaboration window",
                "Promo code redemptions",
            ],
            "outreach_tips": [
                "Contact mid-week (Tue–Thu) for higher response rates",
                "Personalize the first line with a genuine compliment on specific content",
                "Keep initial message under 200 words",
                "Follow up once after 5 days if no response",
                "Micro-influencers (10k–50k) deliver 60% higher engagement than mega",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are an influencer marketing strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Plan a full influencer collaboration.\n"
                f"Brand: {brand}, Influencer Niche: {influencer_niche}, Platform: {platform}, "
                f"Budget: {budget}, Goal: {goal}\n\n"
                f"Return JSON: {{\"brand\",\"collaboration_type\",\"outreach_message\","
                f"\"collaboration_brief\",\"contract_key_points\":[],\"deliverables\":[],"
                f"\"kpis\":[],\"outreach_tips\":[]}}"
            )},
        ],
        temperature=0.6, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"brand": brand, "outreach_message": "", "contract_key_points": []}


async def plan_ugc_campaign(
    brand: str, niche: str, platform: str = "Instagram",
    incentive: str = "Feature on our page", hashtag: str = "",
    language: str = "English"
) -> dict:
    campaign_hashtag = hashtag or f"#{brand.replace(' ','')[:12]}Community"
    if not USE_AI or not LLM_CLIENT:
        return {
            "campaign_name": f"The {brand} Creator Challenge",
            "hashtag": campaign_hashtag,
            "brief": (
                f"We want to see how YOU use {brand}! Share your best {niche}-related content, "
                f"tag us, and use {campaign_hashtag} for a chance to be featured."
            ),
            "submission_guidelines": [
                f"Post on {platform} (Photo, Reel, or Story)",
                f"Include {campaign_hashtag} in your caption",
                f"Tag @{brand.lower().replace(' ','')} in the post",
                "Content must be your original work",
                "Must follow our brand values (no offensive content)",
            ],
            "incentive_details": incentive,
            "promotional_captions": [
                f"🎉 CHALLENGE TIME! Show us your {niche} journey and get featured to our audience!\n\nUse {campaign_hashtag} + tag us 👇\n\nTop submissions get [incentive]. GO! 🔥",
                f"We love seeing how our community uses {brand} for {niche}! \n\nPost your best content with {campaign_hashtag} — we're featuring our favorites this week 🙌",
            ],
            "selection_criteria": [
                "Authenticity and genuine personal story",
                "Content quality (lighting, composition, sound)",
                "Engagement on the submitted post",
                "Brand alignment and positive messaging",
            ],
            "repurpose_strategy": [
                "Feature top UGC in weekly 'Community Spotlight' Stories",
                "Use best UGC in paid social ads (get explicit permission)",
                "Compile top 10 into a monthly roundup Reel",
                "Add to website testimonials section",
                "Quote card posts from best text submissions",
            ],
            "expected_results": "UGC campaigns generate 4x higher click-through rates than brand-created content",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a UGC campaign specialist. Language: {language}."},
            {"role": "user", "content": (
                f"Plan a full UGC campaign.\n"
                f"Brand: {brand}, Niche: {niche}, Platform: {platform}, "
                f"Incentive: {incentive}, Hashtag: {campaign_hashtag}\n\n"
                f"Return JSON: {{\"campaign_name\",\"hashtag\",\"brief\",\"submission_guidelines\":[],"
                f"\"incentive_details\",\"promotional_captions\":[],\"selection_criteria\":[],"
                f"\"repurpose_strategy\":[],\"expected_results\"}}"
            )},
        ],
        temperature=0.65, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"campaign_name": brand, "submission_guidelines": [], "repurpose_strategy": []}


async def transform_testimonial_to_post(
    testimonial: str, platform: str = "Instagram",
    brand: str = "Brand", niche: str = "General",
    language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        short_quote = testimonial[:120].rsplit(" ", 1)[0] + "…" if len(testimonial) > 120 else testimonial
        return {
            "original_testimonial": testimonial,
            "quote_card_text": f'"{short_quote}"\n— Happy Customer',
            "instagram_caption": (
                f"Real results from a real person 🙌\n\n"
                f'"{short_quote}"\n\n'
                f"This is exactly why we built {brand} — to help people in the {niche} space get results like this.\n\n"
                f"Want the same? Link in bio 👆\n\n"
                f"#{niche.lower().replace(' ','')} #testimonial #results #{brand.lower().replace(' ','')}"
            ),
            "story_text": f'New ⭐⭐⭐⭐⭐ review!\n\n"{short_quote}"\n\nTap to learn more 👆',
            "reel_hook": f"They tried {brand} for 30 days and this is what happened… 👀",
            "linkedin_post": (
                f"Client win 🏆\n\n{testimonial}\n\n"
                f"This is what {brand} exists for. If you're in {niche} and want similar results, "
                f"drop a comment or DM me. Happy to share more."
            ),
            "hashtags": [f"#{niche.lower()}", "#clientresults", "#testimonial", "#socialpoof", f"#{brand.lower().replace(' ','').replace('-','')}"],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social proof copywriter. Language: {language}."},
            {"role": "user", "content": (
                f"Transform this testimonial into social proof content.\n"
                f"Testimonial: {testimonial}\nPlatform: {platform}, Brand: {brand}, Niche: {niche}\n\n"
                f"Return JSON: {{\"original_testimonial\",\"quote_card_text\",\"instagram_caption\","
                f"\"story_text\",\"reel_hook\",\"linkedin_post\",\"hashtags\":[]}}"
            )},
        ],
        temperature=0.6, max_tokens=700,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"quote_card_text": testimonial[:100], "instagram_caption": "", "hashtags": []}


async def generate_community_playbook(
    niche: str, platform: str = "Instagram",
    current_followers: int = 1000,
    goal_followers: int = 10000,
    language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        weeks_needed = max(4, min(24, int((goal_followers - current_followers) / 200) + 4))
        weeks = []
        phases = [
            (1, min(3, weeks_needed // 4), "Foundation Building", ["Define 3 core content pillars", "Optimize profile + bio keyword", "Post 5x to establish baseline", "Engage 20 accounts/day in niche"]),
            (min(3, weeks_needed // 4) + 1, weeks_needed // 2, "Consistency Sprint", ["Post 5x/week at optimal times", "Respond to every comment within 1h", "Start a content series (Day 1/7, etc.)", "Collaborate with 2 accounts"]),
            (weeks_needed // 2 + 1, weeks_needed * 3 // 4, "Amplification", ["Repurpose best posts to other formats", "Launch UGC campaign with hashtag", "Test Reels + video content", "Reach out to 5 micro-influencers"]),
            (weeks_needed * 3 // 4 + 1, weeks_needed, "Monetization Prep", ["Build email list from audience", "Introduce lead magnet", "Create highlight covers + story archive", "Soft pitch product/service to engaged followers"]),
        ]
        for phase_start, phase_end, focus, tasks in phases:
            for w in range(phase_start, phase_end + 1):
                weeks.append({
                    "week": w,
                    "phase": focus,
                    "focus": f"Week {w}: {focus}",
                    "daily_tasks": tasks,
                    "milestone": f"{current_followers + int((goal_followers - current_followers) * (w / weeks_needed)):,} followers",
                })
        return {
            "goal": f"{current_followers:,} → {goal_followers:,} followers on {platform}",
            "estimated_weeks": weeks_needed,
            "weekly_plan": weeks,
            "daily_non_negotiables": [
                "Post or engage with content (20–30 min)",
                "Reply to every comment on your posts",
                "Leave 10 genuine comments on other accounts",
                "Check analytics and note top-performing content",
            ],
            "community_engagement_tactics": [
                "Host weekly Q&A in Stories",
                "Create a poll or quiz 3x/week",
                "Share follower wins in 'Community Spotlight'",
                "DM new followers with a welcome message + value",
                "Celebrate follower milestones publicly",
            ],
            "retention_strategies": [
                "Create a signature content series followers expect weekly",
                "Reference past posts to build continuity (callback content)",
                "Make followers feel seen — mention their username in content",
                "Create exclusive content for email subscribers",
                "Run monthly challenge to keep audience active",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a community growth expert for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Create a community growth playbook for a {niche} creator on {platform}.\n"
                f"Current: {current_followers:,} followers → Goal: {goal_followers:,}\n\n"
                f"Return JSON: {{\"goal\",\"estimated_weeks\":int,\"weekly_plan\":[{{\"week\":int,"
                f"\"phase\",\"focus\",\"daily_tasks\":[],\"milestone\"}}],"
                f"\"daily_non_negotiables\":[],\"community_engagement_tactics\":[],"
                f"\"retention_strategies\":[]}}"
            )},
        ],
        temperature=0.55, max_tokens=1000,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"goal": f"→ {goal_followers:,}", "weekly_plan": [], "community_engagement_tactics": []}


async def plan_live_stream(
    topic: str, platform: str = "Instagram Live",
    duration_minutes: int = 60,
    niche: str = "General", language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        segments_per_min = duration_minutes // 10
        segments = [
            {"time_start": f"{i*10}:00", "time_end": f"{(i+1)*10}:00",
             "segment": ["Welcome + Set Expectations", "Deep Dive: Main Topic (Part 1)", "Q&A Round 1",
                         "Deep Dive: Main Topic (Part 2)", "Live Demo / Case Study",
                         "Q&A Round 2", "Action Steps + Recap"][i % 7],
             "interaction_prompt": ["Say 'HELLO' in the chat if you can hear me! 👋",
                                    "Drop a 🔥 if this is useful so far!",
                                    "Type your question in the chat — I'll answer in 2 min",
                                    "What's your biggest struggle with this? Comment below 👇",
                                    "Share this live with someone who needs this!",
                                    "Any final questions? I have 5 minutes left 🙏",
                                    "DM me 'LIVE' for the freebie I mentioned!"][i % 7]}
            for i in range(min(segments_per_min + 1, 7))
        ]
        return {
            "title": f"LIVE: {topic} — Everything You Need to Know",
            "platform": platform,
            "duration": f"{duration_minutes} minutes",
            "pre_live_checklist": [
                "Test audio: use wired headphones for clean sound",
                "Test lighting: face a window or use ring light",
                "Stable internet: minimum 10 Mbps upload",
                "Charge device or plug in",
                "Have notes/outline visible but not reading from script",
                "Announce live 24h + 1h before to build audience",
                "Prepare your freebie/CTA resource ready to share",
            ],
            "segments": segments,
            "promotion_captions": [
                f"🔴 GOING LIVE on {platform} — {topic}!\n\n📅 [Date] at [Time]\n\nI'm covering [key point 1], [key point 2], and taking live Q&A.\n\nSave this date 👆 and turn on notifications so you don't miss it!\n\n#{niche.lower()} #liveqa",
                f"24 HOURS until my LIVE on {topic}! 🕐\n\nWho's joining? Drop a 🙋 below if you'll be there → I'll answer YOUR question first!\n\nSet a reminder — {platform} at [Time] tomorrow!",
            ],
            "post_live_repurpose": [
                "Download replay → upload as YouTube video with SEO title",
                "Cut 3–5 key moments → TikTok / Reels clips",
                "Transcribe Q&A answers → Blog post or Threads/Twitter thread",
                "Best quote from live → Quote card for Instagram/LinkedIn",
                "Create 'Best moments' highlights Story for Instagram",
            ],
            "engagement_tactics": [
                "Pin a comment with the freebie link as soon as you go live",
                "Call viewers by name when answering their questions",
                "Do a poll or vote every 15 minutes",
                "Mention viewer screen names to encourage more participation",
                "End with a strong CTA + freebie/next step to capture leads",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a live streaming coach. Language: {language}."},
            {"role": "user", "content": (
                f"Plan a {duration_minutes}-minute live stream.\n"
                f"Topic: {topic}, Platform: {platform}, Niche: {niche}\n\n"
                f"Return JSON: {{\"title\",\"platform\",\"duration\",\"pre_live_checklist\":[],"
                f"\"segments\":[{{\"time_start\",\"time_end\",\"segment\",\"interaction_prompt\"}}],"
                f"\"promotion_captions\":[],\"post_live_repurpose\":[],\"engagement_tactics\":[]}}"
            )},
        ],
        temperature=0.6, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"title": topic, "segments": [], "pre_live_checklist": []}


# ─── P9: Real-Time Intelligence ─────────────────────────────────────────────

async def hijack_trend(
    trend_topic: str, niche: str,
    platform: str = "TikTok", language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        return {
            "trend": trend_topic,
            "trend_analysis": f"'{trend_topic}' is trending — high social conversation volume with broad audience awareness. This creates a hook that grabs attention from people already searching for it.",
            "content_ideas": [
                {
                    "idea": f"React/commentary on '{trend_topic}' from a {niche} perspective",
                    "hook": f"Wait — did you see what's happening with {trend_topic}? Here's what it means for {niche}…",
                    "angle": "Expert commentary / unique POV",
                    "urgency": "Post within 24–48 hours while trend is hot",
                    "format": "Talking head Reel/TikTok",
                },
                {
                    "idea": f"Use '{trend_topic}' audio/format + {niche} content",
                    "hook": f"Using this viral trend to share the most important {niche} tip I know",
                    "angle": "Trend format + niche value combo",
                    "urgency": "Post within 48 hours",
                    "format": f"Trending audio + {niche} educational content",
                },
                {
                    "idea": f"'{trend_topic}' vs {niche} — what you actually need to know",
                    "hook": f"Everyone's talking about {trend_topic}. Here's the {niche} truth nobody mentions…",
                    "angle": "Contrarian / demystification",
                    "urgency": "Post within 72 hours",
                    "format": "List-style breakdown",
                },
            ],
            "best_idea": f"React/commentary on '{trend_topic}' from a {niche} perspective — fastest to produce and positions you as the expert bridge between the trend and your audience.",
            "post_now_caption": (
                f"Okay we need to talk about {trend_topic} 👀\n\n"
                f"Here's what this actually means for {niche}:\n\n"
                f"[Your unique take]\n\n"
                f"Save this — this is important 📌\n\n"
                f"#{trend_topic.lower().replace(' ','')} #{niche.lower()} #trending"
            ),
            "hashtags": [
                f"#{trend_topic.lower().replace(' ','')}",
                f"#{niche.lower()}",
                "#trending",
                f"#{platform.lower()}viral",
                "#viral",
            ],
            "timing_warning": "Trend hijacking drops in effectiveness after 72 hours. Post NOW for maximum algorithmic boost.",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a trend marketing strategist for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Create a trend hijacking strategy.\n"
                f"Trend: {trend_topic}, Niche: {niche}, Platform: {platform}\n\n"
                f"Return JSON: {{\"trend\",\"trend_analysis\",\"content_ideas\":[{{\"idea\",\"hook\","
                f"\"angle\",\"urgency\",\"format\"}}],\"best_idea\",\"post_now_caption\","
                f"\"hashtags\":[],\"timing_warning\"}}"
            )},
        ],
        temperature=0.75, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"trend": trend_topic, "content_ideas": [], "post_now_caption": ""}


async def clone_viral_content(
    viral_description: str, your_niche: str,
    platform: str = "TikTok", language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        return {
            "original_viral_analysis": {
                "description": viral_description,
                "success_formula": "Strong hook (curiosity/shock) + relatable problem + fast value delivery + pattern interrupt + CTA",
                "emotional_triggers": ["Curiosity", "Surprise", "Relatability"],
                "format_elements": ["Text overlay", "Fast pacing", "Direct address to viewer"],
                "why_it_worked": "Created an open loop in the first 2 seconds, then delivered value that was share-worthy",
            },
            "your_version": {
                "hook": f"Wait — this {your_niche} truth will change how you think about [topic]…",
                "structure": "Hook (2s) → Relatable problem (5s) → Surprising fact (10s) → Actionable insight (20s) → CTA (5s)",
                "script_outline": [
                    f"Hook: Mirror the viral hook but adapt to {your_niche}",
                    "Problem: State the pain point your audience faces daily",
                    f"Insight: Share your unique {your_niche} perspective/data",
                    "Solution: One clear, memorable takeaway",
                    "CTA: 'Follow for part 2' or 'Save this for later'",
                ],
                "differentiation": f"Your version adds {your_niche}-specific expertise and authentic personal angle that the original lacked",
                "estimated_performance": "60–80% of original viral reach if executed well within 48h of original's peak",
            },
            "adaptations": [
                f"Replace any platform-specific references with {platform}-native context",
                f"Add your {your_niche} expert angle to elevate beyond mere copy",
                "Change the hook wording by at least 70% to avoid comparison",
                "Use your own b-roll and original audio — never copy audio directly",
                "Add your personal story or data point for authenticity",
            ],
            "ethical_note": "This framework is about using the STRUCTURE and FORMAT, not copying content. Always add original value.",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a viral content strategist for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Analyze this viral content and create a unique version for a different niche.\n"
                f"Viral content: {viral_description}\nYour niche: {your_niche}, Platform: {platform}\n\n"
                f"Return JSON: {{\"original_viral_analysis\":{{\"description\",\"success_formula\","
                f"\"emotional_triggers\":[],\"format_elements\":[],\"why_it_worked\"}},"
                f"\"your_version\":{{\"hook\",\"structure\",\"script_outline\":[],"
                f"\"differentiation\",\"estimated_performance\"}},"
                f"\"adaptations\":[],\"ethical_note\"}}"
            )},
        ],
        temperature=0.7, max_tokens=800,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"original_viral_analysis": {}, "your_version": {}, "adaptations": []}


async def get_optimal_posting_times(
    platform: str, niche: str = "General",
    audience_timezone: str = "EST (UTC-5)",
    language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        times_data = {
            "TikTok": {
                "best_times": {"Tuesday": ["7am", "9am", "2pm"], "Thursday": ["9am", "12pm", "7pm"], "Friday": ["5am", "1pm", "3pm"]},
                "peak_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
                "avoid": ["Late night 11pm–5am (unless 18–25 audience)", "Monday mornings"],
                "frequency": "1–3 posts per day for growth phase",
                "insight": "TikTok FYP transcends timezones — but posting at audience peak time gives the initial watch-rate signal boost needed to trigger broader distribution.",
            },
            "Instagram": {
                "best_times": {"Monday": ["8am", "12pm"], "Wednesday": ["9am", "6pm"], "Friday": ["8am", "2pm"], "Saturday": ["10am"]},
                "peak_days": ["Monday", "Wednesday", "Friday", "Saturday"],
                "avoid": ["Sunday nights", "Very early mornings before 6am"],
                "frequency": "Reels: 3–5/week | Posts: 3–4/week | Stories: daily",
                "insight": "Instagram rewards posting when your current followers are most active — check your Insights > Audience > Most Active Times for precise data.",
            },
            "LinkedIn": {
                "best_times": {"Tuesday": ["8am", "10am", "12pm"], "Wednesday": ["9am", "12pm"], "Thursday": ["9am", "2pm"]},
                "peak_days": ["Tuesday", "Wednesday", "Thursday"],
                "avoid": ["Weekends (30% lower reach)", "Very early (before 7am) or late (after 8pm)"],
                "frequency": "3–5 posts per week",
                "insight": "LinkedIn is a professional platform — post during work hours when people take content breaks (9am, 12pm, 5pm).",
            },
            "YouTube": {
                "best_times": {"Thursday": ["3pm", "5pm"], "Friday": ["2pm", "5pm"], "Saturday": ["9am", "11am", "3pm"], "Sunday": ["9am", "11am"]},
                "peak_days": ["Thursday", "Friday", "Saturday", "Sunday"],
                "avoid": ["Late night uploads (less likely to be surfaced)", "Major holidays"],
                "frequency": "1–3 videos per week for growth | 1–2 for maintenance",
                "insight": "YouTube Shorts follow TikTok patterns. Long-form does best Thursday–Sunday when people have leisure time.",
            },
        }
        data = times_data.get(platform, {
            "best_times": {"Wednesday": ["9am", "12pm", "6pm"], "Friday": ["8am", "2pm", "5pm"]},
            "peak_days": ["Wednesday", "Friday", "Saturday"],
            "avoid": ["Late night", "Very early morning"],
            "frequency": "3–5 posts per week",
            "insight": "Check your native analytics for audience-specific peak times.",
        })
        return {
            "platform": platform,
            "timezone": audience_timezone,
            "niche": niche,
            "best_posting_times": data.get("best_times", {}),
            "peak_days": data.get("peak_days", []),
            "avoid_times": data.get("avoid", []),
            "recommended_frequency": data.get("frequency", "3–5x/week"),
            "platform_insight": data.get("insight", ""),
            "pro_tip": "Use your native analytics to verify these benchmarks — YOUR audience may peak differently. Check after 30 days of consistent posting for personalized data.",
            "scheduling_tools": ["Buffer", "Later", "Hootsuite", "Meta Business Suite (free for FB/IG)", "TikTok Creator Tools (native, free)"],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social media timing expert. Language: {language}."},
            {"role": "user", "content": (
                f"Provide optimal posting times for {platform} in {niche} niche.\n"
                f"Audience timezone: {audience_timezone}\n\n"
                f"Return JSON: {{\"platform\",\"timezone\",\"niche\",\"best_posting_times\":{{}},"
                f"\"peak_days\":[],\"avoid_times\":[],\"recommended_frequency\","
                f"\"platform_insight\",\"pro_tip\",\"scheduling_tools\":[]}}"
            )},
        ],
        temperature=0.4, max_tokens=700,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"platform": platform, "best_posting_times": {}, "peak_days": [], "scheduling_tools": []}


async def scan_niche_opportunity(
    broad_niche: str, platform: str = "TikTok",
    language: str = "English"
) -> dict:
    if not USE_AI or not LLM_CLIENT:
        subs = [
            (f"{broad_niche} for beginners", 9, 6, "Evergreen demand with low competition in deep how-to format"),
            (f"Budget {broad_niche}", 8, 5, "Price-conscious audience underserved by premium-focused creators"),
            (f"{broad_niche} for [specific demographic]", 7, 4, "Niche within niche — hyper-targeted with passionate community"),
            (f"Advanced {broad_niche} strategies", 6, 3, "Experienced audience willing to pay premium for advanced content"),
            (f"{broad_niche} mistakes & corrections", 8, 5, "High watch-time format — 'what not to do' content performs strongly"),
        ]
        opportunities = [
            {
                "sub_niche": s[0],
                "demand_score": s[1],
                "competition_score": s[2],
                "opportunity_score": round((s[1] * 1.5 - s[2]) / 10 * 10, 1),
                "why_now": s[3],
                "content_angle": f"Own the '{s[0]}' topic before bigger creators notice the gap",
                "estimated_monthly_views": f"{(s[1] - s[2]) * 15_000:,}–{(s[1] - s[2]) * 50_000:,}",
                "entry_strategy": f"Create 10 pieces of deep content on '{s[0]}' in first 2 weeks to establish topic authority",
            }
            for s in subs
        ]
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return {
            "broad_niche": broad_niche,
            "platform": platform,
            "opportunities": opportunities,
            "best_opportunity": opportunities[0],
            "overall_entry_strategy": (
                f"Pick the #1 opportunity and create 20 pieces of content about it before moving to the next. "
                f"Topic authority = algorithm trust = faster growth. "
                f"Consistent niche content trains {platform}'s algorithm to classify and distribute your content to the right audience."
            ),
            "validation_method": [
                f"Search the sub-niche on {platform} — count views on top 10 posts",
                "Check if there are creators with 10k–100k followers (not too small, not too saturated)",
                "Google the keyword + check YouTube search volume as a proxy",
                "Post 5 test pieces and compare performance to your current average",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a niche market analyst for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Scan '{broad_niche}' for sub-niche opportunities on {platform}.\n\n"
                f"Return JSON: {{\"broad_niche\",\"platform\",\"opportunities\":[{{\"sub_niche\","
                f"\"demand_score\":int,\"competition_score\":int,\"opportunity_score\":float,"
                f"\"why_now\",\"content_angle\",\"estimated_monthly_views\",\"entry_strategy\"}}],"
                f"\"best_opportunity\":{{}},\"overall_entry_strategy\",\"validation_method\":[]}}"
            )},
        ],
        temperature=0.65, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"broad_niche": broad_niche, "opportunities": [], "best_opportunity": {}}
