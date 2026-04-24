"""
GrowthOS AI — Content Domination Engine
==========================================
P6: Viral Hook Library, Reels/Short Script Engine, Content Series Planner,
    Thumbnail Concept Generator, Caption Emotion Engine
"""
import json, re
from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str):
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def generate_viral_hooks(
    niche: str, platform: str = "TikTok",
    content_type: str = "Video", count: int = 20,
    language: str = "English"
) -> dict:
    """Generate proven viral hook formulas for the first 3 seconds."""
    if not USE_AI or not LLM_CLIENT:
        hook_formulas = [
            ("Shock/Controversy",   f"Nobody talks about this {niche} secret — but it changes EVERYTHING 👀"),
            ("Number Hook",         f"5 {niche} mistakes that are silently killing your growth (and how to fix them)"),
            ("POV Hook",            f"POV: You just discovered the {niche} strategy that got me [result] in 30 days"),
            ("Question Hook",       f"Did you know most {niche} creators are doing THIS completely wrong?"),
            ("Warning Hook",        f"STOP using this {niche} strategy — it's actually hurting your account"),
            ("Story Hook",          f"6 months ago I had 0 {niche} knowledge. Here's what changed everything →"),
            ("Result Hook",         f"I gained [X] followers in 7 days using this {niche} trick. Here's exactly how:"),
            ("Curiosity Hook",      f"The {niche} algorithm hack nobody is sharing… until now"),
            ("Pain Point Hook",     f"Struggling with {niche}? This one change made all the difference for me"),
            ("Comparison Hook",     f"This is what [top creator] does in {niche} that you're NOT doing"),
            ("Secret Hook",         f"The {niche} strategy that got banned from being taught publicly (not illegal, just powerful)"),
            ("Time-Based Hook",     f"In 60 seconds, I'll show you the fastest {niche} growth method that actually works"),
            ("Mistake Hook",        f"I wasted 2 years doing {niche} wrong. Here's the lesson that changed everything:"),
            ("Free Value Hook",     f"Saving this will make you better at {niche} instantly — you're welcome 🎁"),
            ("Challenge Hook",      f"I challenge you to try this {niche} strategy for 7 days — post your results"),
            ("Trend Hijack",        f"Using this viral trend to share the most important {niche} tip I know"),
            ("Expert Reveal",       f"After [X] years in {niche}, here's the #1 thing I wish someone told me"),
            ("Objection Hook",      f"You think {niche} is too hard? Watch this and thank me later"),
            ("FOMO Hook",           f"Everyone in {niche} is already doing this — are you?"),
            ("Pattern Interrupt",   f"*Pause* — if you're serious about {niche}, you NEED to hear this"),
        ]
        hooks = [
            {"hook_type": h[0], "hook_text": h[1],
             "predicted_ctr": f"{72 - i * 2}%", "best_for": platform,
             "tip": "Deliver the payoff within 3 seconds of the hook or viewers drop off"}
            for i, h in enumerate(hook_formulas[:count])
        ]
        return {
            "hooks": hooks,
            "top_3": hooks[:3],
            "hook_principles": [
                "First 1–3 words are the most critical — front-load the value/shock",
                "Use 'you' — make it personal and directly relevant",
                "Create an open loop — tease the answer without giving it away",
                "Numbers perform 40% better than generic statements",
                "Negative hooks ('stop doing X') outperform positive by 2x",
            ],
            "platform_tips": {
                "TikTok": "Hook text overlay appears in first frame — use bold contrast colors",
                "Instagram Reels": "First frame thumbnail is key — face + expression + text",
                "YouTube Shorts": "Hook must work WITHOUT sound — 60% watch muted",
            }.get(platform, "Hook must work without sound — add text overlay"),
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a viral content strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Generate {count} viral hooks for: Niche={niche}, Platform={platform}, Type={content_type}\n\n"
                f"Return JSON: {{\"hooks\":[{{\"hook_type\",\"hook_text\",\"predicted_ctr\","
                f"\"best_for\",\"tip\"}}],\"top_3\":[],\"hook_principles\":[],\"platform_tips\":\"str\"}}"
            )},
        ],
        temperature=0.8, max_tokens=1200,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"hooks": [], "top_3": [], "hook_principles": []}


async def generate_short_script(
    topic: str, platform: str = "TikTok",
    duration: str = "60s", style: str = "Educational",
    niche: str = "General", language: str = "English"
) -> dict:
    """Generate full Hook→Problem→Value→Proof→CTA optimized video script."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "title": f"[{style}] {topic}",
            "platform": platform, "duration": duration,
            "script": {
                "hook": {
                    "time": "0–3s",
                    "spoken": f"Wait — if you care about {topic}, you NEED to see this.",
                    "visual": "Extreme close-up / bold text reveal on screen",
                    "on_screen_text": f"The {topic} secret nobody talks about 🔥",
                },
                "problem": {
                    "time": "3–12s",
                    "spoken": f"Most people struggle with {topic} because they're doing ONE thing wrong.",
                    "visual": "Talking head OR relatable struggle B-roll",
                    "on_screen_text": "The mistake 90% make →",
                },
                "value": {
                    "time": "12–40s",
                    "spoken": f"Here's what actually works: [Tip 1], [Tip 2], [Tip 3].",
                    "visual": "Screen recording / step demo / talking head with text bullets",
                    "on_screen_text": "Step 1 → Step 2 → Step 3",
                },
                "proof": {
                    "time": "40–52s",
                    "spoken": "I used this exact approach and got [specific result] in [timeframe].",
                    "visual": "Screenshot / graph / before-after",
                    "on_screen_text": "Proof: [Result] in [Time]",
                },
                "cta": {
                    "time": "52–60s",
                    "spoken": "Follow me for Part 2 — I'm sharing the advanced version next week.",
                    "visual": "Face to camera, pointing down",
                    "on_screen_text": "Follow + Save so you don't lose this 👇",
                },
            },
            "total_words": 95,
            "caption": (
                f"The truth about {topic} 👀\n\nSave this before it disappears!\n\n"
                f"#{niche.lower().replace(' ','')} #growthtips #{platform.lower().replace('/','')} #viral"
            ),
            "hashtags": [f"#{niche.lower()}", f"#{topic.lower().replace(' ','')}", "#growthhacks", "#viral", f"#{platform.lower()}"],
            "thumbnail_concept": f"Close-up face with shocked expression + bold text '{topic.upper()[:20]}' + bright background",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a viral {platform} script writer. Language: {language}."},
            {"role": "user", "content": (
                f"Write a complete {duration} {style} script for {platform}.\n"
                f"Topic: {topic}, Niche: {niche}\n"
                f"Structure: Hook(0-3s) → Problem(3-12s) → Value(12-40s) → Proof(40-52s) → CTA(52-end)\n\n"
                f"Return JSON: {{\"title\",\"platform\",\"duration\","
                f"\"script\":{{\"hook\":{{\"time\",\"spoken\",\"visual\",\"on_screen_text\"}},"
                f"\"problem\":{{...}},\"value\":{{...}},\"proof\":{{...}},\"cta\":{{...}}}},"
                f"\"total_words\":int,\"caption\",\"hashtags\":[],\"thumbnail_concept\"}}"
            )},
        ],
        temperature=0.7, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"title": topic, "script": {}, "caption": ""}


async def plan_content_series(
    theme: str, niche: str, platform: str = "Instagram",
    series_type: str = "7-Day Challenge", language: str = "English"
) -> dict:
    """Plan episodic content series for maximum retention and follower growth."""
    if not USE_AI or not LLM_CLIENT:
        lengths = {"7-Day Challenge": 7, "5-Part Series": 5, "30-Day Program": 30,
                   "4-Week Course": 28, "10-Day Boot Camp": 10}
        n = lengths.get(series_type, 7)
        episodes = [
            {
                "episode": i + 1,
                "title": f"Day {i+1}: {'Introduction & Why' if i==0 else ('Foundations' if i==1 else ('Advanced Tips' if i==n-2 else ('Graduation + Results' if i==n-1 else f'Key Strategy {i}')))}",
                "topic": f"{theme} — Part {i+1} of {n}",
                "hook": ("Day {} of the {}: You won't believe what comes next...".format(i+1, series_type) if i < n-1 else "Day {} of the {}: Final reveal - the results are in!".format(i+1, series_type)),
                "cta": "Follow to catch Day {} tomorrow!" .format(i+2) if i < n-1 else "Share your results with #{}Challenge!".format(theme.replace(" ", "")[:10]),
                "engagement_trigger": ["Poll", "Q&A box", "Comment challenge", "DM prompt", "Share challenge"][i % 5],
            }
            for i in range(min(n, 30))
        ]
        return {
            "series_title": f"The {series_type}: {theme}",
            "series_type": series_type,
            "platform": platform,
            "total_episodes": len(episodes),
            "episodes": episodes,
            "hashtag_strategy": f"#{theme.replace(' ','')[:12]}Challenge | #{niche.lower()}tips | Series hashtag consistent across all posts",
            "launch_strategy": [
                "Announce 3 days before with a teaser post",
                "Post at same time each day for routine formation",
                "Add 'Day X/Y' to every title for completion tracking",
                "Create a highlight reel to save the whole series",
                "End each episode with a preview of the next",
            ],
            "retention_tricks": [
                "End every post with an open loop ('Tomorrow I reveal…')",
                "Create a private group/DM list for series followers",
                "Give a completion bonus at the end (freebie, discount)",
                "Do a Q&A mid-series to re-engage dropoffs",
            ],
            "monetization": f"At end of series → pitch {niche} product/service to highly engaged audience",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a content series strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Plan a complete {series_type} content series.\n"
                f"Theme: {theme}, Niche: {niche}, Platform: {platform}\n\n"
                f"Return JSON: {{\"series_title\",\"series_type\",\"platform\",\"total_episodes\":int,"
                f"\"episodes\":[{{\"episode\":int,\"title\",\"topic\",\"hook\",\"cta\",\"engagement_trigger\"}}],"
                f"\"hashtag_strategy\",\"launch_strategy\":[],\"retention_tricks\":[],\"monetization\"}}"
            )},
        ],
        temperature=0.65, max_tokens=1300,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"series_title": theme, "episodes": [], "launch_strategy": []}


async def generate_thumbnail_concepts(
    title: str, niche: str, platform: str = "YouTube",
    style: str = "Bold & Dramatic", count: int = 5,
    language: str = "English"
) -> dict:
    """Generate viral thumbnail concepts with Midjourney/DALL-E prompts."""
    if not USE_AI or not LLM_CLIENT:
        concepts = [
            {
                "concept_number": i + 1,
                "name": ["Shock Face", "Before/After Split", "Bold Text Dominant", "Color Contrast Pop", "Minimalist Clean"][i],
                "layout": ["Left: shocked face, Right: big bold text", "Split screen before/after", "Text fills 70%, small image corner", "Neon colors on dark background", "Single subject, white space, tiny text"][i],
                "text_overlay": title[:25] + ("…" if len(title) > 25 else ""),
                "color_scheme": ["Red + Yellow (high urgency)", "Blue + White (trust)", "Orange + Black (energy)", "Purple + Gold (premium)", "Green + White (growth)"][i],
                "face_expression": ["Shocked/disbelief", "Before=sad, After=happy", "Confident pointing", "Excited open mouth", "Calm authoritative"][i],
                "midjourney_prompt": f"YouTube thumbnail, {['shocked face close-up', 'split before after', 'bold text graphic', 'neon color background', 'clean minimal'][i]}, {title[:30]}, {niche} channel, professional, high contrast, --ar 16:9 --v 6",
                "dalle_prompt": f"YouTube thumbnail design for '{title[:30]}', {niche} niche, {style} style, {['red and yellow', 'blue and white', 'orange and black', 'purple and gold', 'green and white'][i]} color scheme",
                "predicted_ctr": f"{12 - i}%",
            }
            for i in range(min(count, 5))
        ]
        return {
            "concepts": concepts,
            "best_concept": concepts[0],
            "thumbnail_rules": [
                "Must be readable at 120px wide (mobile size)",
                "Max 5 words of text — less is more",
                "High contrast between text and background",
                "Human face with strong emotion = +38% CTR",
                "Avoid cluttered layouts — 1 focal point only",
                "Use brand colors consistently for recognition",
            ],
            "a_b_test_tip": "Test 2 thumbnails — swap after 48h and keep the higher CTR one",
            "size_specs": "1280x720px minimum | 2560x1440px ideal | Under 2MB | JPG/PNG",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a thumbnail design strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Generate {count} viral thumbnail concepts.\n"
                f"Title: {title}, Niche: {niche}, Platform: {platform}, Style: {style}\n\n"
                f"Return JSON: {{\"concepts\":[{{\"concept_number\":int,\"name\",\"layout\","
                f"\"text_overlay\",\"color_scheme\",\"face_expression\","
                f"\"midjourney_prompt\",\"dalle_prompt\",\"predicted_ctr\"}}],"
                f"\"best_concept\":{{}},\"thumbnail_rules\":[],\"a_b_test_tip\",\"size_specs\"}}"
            )},
        ],
        temperature=0.7, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"concepts": [], "thumbnail_rules": []}


async def generate_emotional_captions(
    topic: str, niche: str, platform: str = "Instagram",
    emotion: str = "Curiosity", count: int = 5, language: str = "English"
) -> dict:
    """Generate captions by emotional trigger for maximum engagement."""
    if not USE_AI or not LLM_CLIENT:
        emotion_templates = {
            "Curiosity": [
                f"I wasn't supposed to share this… but here we are 👀\n\n[Hook about {topic}]\n\nSave this before it disappears.\n\n#{niche.lower()}",
                f"The {topic} secret they don't want you to know 🤫\n\n[Reveal the insight]\n\nDrop a 🔥 if this helped!\n\n#{niche.lower()}",
            ],
            "FOMO": [
                f"Everyone in {niche} is already doing this — are you?\n\n[Explain {topic}]\n\nDon't get left behind. Save this now 📌\n\n#{niche.lower()}",
                f"While you're reading this, your competitors are already using {topic}.\n\n[Value]\n\nAre you in or out? Comment below 👇\n\n#{niche.lower()}",
            ],
            "Inspiration": [
                f"This time last year, I knew NOTHING about {topic}.\n\nToday? [Transformation result].\n\nIf I can do it, so can you. Here's exactly what changed:\n\n[Steps]\n\nSave this for when you need motivation 💪\n\n#{niche.lower()}",
            ],
            "Humor": [
                f"Me before learning {topic}: 😵\nMe after learning {topic}: 😎\n\n[Funny/relatable content about {topic}]\n\nTag someone who needs this energy ☕\n\n#{niche.lower()}",
            ],
            "Authority": [
                f"After [X] years in {niche}, here's what I know about {topic} that nobody teaches:\n\n1. [Insight]\n2. [Insight]\n3. [Insight]\n\nSave this. It took me years to learn. 📌\n\n#{niche.lower()}",
            ],
        }
        captions = emotion_templates.get(emotion, emotion_templates["Curiosity"])
        # Pad to count
        while len(captions) < count:
            captions.append(captions[len(captions) % len(captions)])
        return {
            "emotion": emotion,
            "captions": captions[:count],
            "emotion_triggers": {
                "Curiosity": ["Incomplete information", "Open loops", "Secrets/reveals"],
                "FOMO": ["Social proof", "Urgency", "Comparison"],
                "Inspiration": ["Transformation story", "Underdog journey", "Proof of possibility"],
                "Humor": ["Relatable pain", "Exaggeration", "Unexpected twist"],
                "Authority": ["Years of experience", "Specific data", "Contrarian insight"],
            }.get(emotion, []),
            "best_platform_for_emotion": {
                "Curiosity": "TikTok, Twitter/X",
                "FOMO": "Instagram Stories, LinkedIn",
                "Inspiration": "Instagram, LinkedIn",
                "Humor": "TikTok, Twitter/X, Instagram Reels",
                "Authority": "LinkedIn, Twitter/X",
            }.get(emotion, platform),
            "engagement_prediction": f"{emotion} posts get on average 35–55% more comments than neutral posts",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are an emotional copywriter for {platform}. Language: {language}."},
            {"role": "user", "content": (
                f"Write {count} {emotion}-trigger captions.\n"
                f"Topic: {topic}, Niche: {niche}, Platform: {platform}\n\n"
                f"Return JSON: {{\"emotion\",\"captions\":[],\"emotion_triggers\":[],"
                f"\"best_platform_for_emotion\",\"engagement_prediction\"}}"
            )},
        ],
        temperature=0.85, max_tokens=1000,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"emotion": emotion, "captions": [], "emotion_triggers": []}
