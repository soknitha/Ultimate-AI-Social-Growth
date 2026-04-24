"""
GrowthOS AI — Automation Engine
=================================
Features: Comment Manager, Content Repurposing, DM Campaign Templates, Video Storyboard
"""
import asyncio
import random
import json
import re

from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str) -> dict | list:
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def bulk_reply_comments(
    comments: list, tone: str = "Friendly & Warm",
    brand_name: str = "", platform: str = "Instagram",
    language: str = "English"
) -> list:
    """Generate smart replies for multiple comments with sentiment + action flags."""
    if not USE_AI or not LLM_CLIENT:
        demo_replies = [
            "Thank you so much! 😊❤️ We really appreciate your support!",
            "We're so happy to hear that! 🙏 Feel free to DM us anytime!",
            "Great question! Check the link in our bio for full details! 👇",
            "Thank you for your feedback! We're always improving! 💪",
            "Amazing! Keep it up! ✨ Follow for more tips like this!",
        ]
        spam_keywords = ["follow me", "f4f", "check my page", "buy followers", "dm me fast"]
        result = []
        for i, comment in enumerate(comments[:20]):
            text_lower = str(comment).lower()
            is_spam = any(kw in text_lower for kw in spam_keywords)
            is_negative = any(w in text_lower for w in ["hate", "terrible", "scam", "bad", "worst", "refund"])
            result.append({
                "original": comment,
                "reply": "" if is_spam else (
                    f"We're sorry to hear that! 😔 Please DM us so we can resolve this immediately."
                    if is_negative else demo_replies[i % len(demo_replies)]
                ),
                "sentiment": "spam" if is_spam else ("negative" if is_negative else "positive"),
                "priority": "urgent" if is_negative else ("low" if is_spam else "normal"),
                "action": "report" if is_spam else "reply",
            })
        return result

    comments_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(comments[:15])])
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a {tone} social media manager for {brand_name or 'a brand'} on {platform}. "
                f"Language: {language}. Detect spam, flag urgent negatives, craft genuine replies."
            )},
            {"role": "user", "content": (
                f"Generate replies for these {platform} comments:\n{comments_text}\n\n"
                f"Return JSON array only: [{{\"original\",\"reply\",\"sentiment\":"
                f"\"positive|negative|neutral|spam\","
                f"\"priority\":\"urgent|normal|low\",\"action\":\"reply|hide|report|ignore\"}}]"
            )},
        ],
        temperature=0.7, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return [{"original": c, "reply": "Thank you! 😊",
                 "sentiment": "positive", "priority": "normal", "action": "reply"}
                for c in comments[:15]]


async def repurpose_content(
    original: str, source_format: str = "Blog Post",
    target_formats: list = None, brand_name: str = "",
    niche: str = "General", language: str = "English"
) -> dict:
    """Repurpose one piece of content into multiple platform formats automatically."""
    if target_formats is None:
        target_formats = ["Instagram Caption", "TikTok Script",
                          "Twitter/X Thread", "LinkedIn Post", "YouTube Description"]

    if not USE_AI or not LLM_CLIENT:
        snippet = original[:180].strip()
        result = {}
        for fmt in target_formats:
            if "instagram" in fmt.lower():
                result[fmt] = (
                    f"✨ Key insight:\n\n{snippet}…\n\n"
                    f"Save this for later! 🔖\n\n"
                    f"#{niche.lower().replace(' ', '')} #growthtips #contentcreator"
                )
            elif "tiktok" in fmt.lower():
                result[fmt] = (
                    f"Hook (0–3s): 'Wait… this {niche} secret changes everything!'\n\n"
                    f"Content: {snippet}…\n\n"
                    f"CTA: 'Follow for Part 2 👇 | Save so you don't lose this'"
                )
            elif "twitter" in fmt.lower() or "x thread" in fmt.lower():
                result[fmt] = (
                    f"🧵 Thread:\n\n1/ {snippet}…\n\n"
                    f"2/ Here's what this means for your {niche} strategy…\n\n"
                    f"3/ The #1 takeaway most people miss…\n\n"
                    f"4/ Action step you can do TODAY:\n\nRT if this helped! 🔁"
                )
            elif "linkedin" in fmt.lower():
                result[fmt] = (
                    f"📌 {niche} Insight:\n\n{snippet}…\n\n"
                    f"3 key lessons:\n1. Focus on what drives results\n"
                    f"2. Consistency beats perfection\n3. Data guides decisions\n\n"
                    f"What's your experience with this? Comment below 👇"
                )
            elif "youtube" in fmt.lower():
                result[fmt] = (
                    f"{snippet}…\n\n"
                    f"🔔 SUBSCRIBE for weekly {niche} insights!\n\n"
                    f"📌 CHAPTERS:\n0:00 Introduction\n1:00 Main content\n5:00 Key tips\n8:00 Summary\n\n"
                    f"🏷 Tags: {niche}, tutorial, guide, tips, {niche} for beginners"
                )
            else:
                result[fmt] = f"[{fmt}]: {snippet}…"
        return {
            "repurposed": result,
            "original_format": source_format,
            "tip": "Post each format 24–48h apart across platforms for maximum total reach.",
            "schedule_suggestion": "Day 1: Instagram → Day 2: TikTok → Day 3: LinkedIn → Day 4: Twitter Thread",
        }

    formats_str = ", ".join(target_formats)
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are an expert content repurposing strategist. "
                f"Brand: {brand_name or 'N/A'}. Language: {language}."
            )},
            {"role": "user", "content": (
                f"Repurpose this {source_format} content for: {formats_str}.\n"
                f"Niche: {niche}\n\nOriginal:\n{original[:800]}\n\n"
                f"Return JSON only: {{\"repurposed\":{{\"format_name\":\"content_str\",...}},"
                f"\"original_format\":\"str\","
                f"\"tip\":\"str\",\"schedule_suggestion\":\"str\"}}"
            )},
        ],
        temperature=0.75, max_tokens=1400,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"repurposed": {f: original[:200] for f in target_formats},
                "original_format": source_format, "tip": ""}


async def generate_video_storyboard(
    topic: str, platform: str = "TikTok", duration_seconds: int = 60,
    style: str = "Educational", niche: str = "General",
    language: str = "English"
) -> dict:
    """Generate detailed shot-by-shot video storyboard."""
    if not USE_AI or not LLM_CLIENT:
        shots = [
            {"shot": 1, "time": "0–3s", "type": "Hook",
             "visual": "Close-up face, excited expression OR bold text reveal",
             "audio": "Trending hook sound / Voiceover: 'You need to hear this…'",
             "text_overlay": "Wait... THIS changed everything 🔥", "purpose": "Grab attention instantly"},
            {"shot": 2, "time": "3–12s", "type": "Problem Setup",
             "visual": "Show relatable struggle or common mistake",
             "audio": f"Voiceover: 'Most {niche} creators struggle with…'",
             "text_overlay": "The mistake 90% make", "purpose": "Build relatability"},
            {"shot": 3, "time": "12–30s", "type": "Value Content",
             "visual": "Screen recording / talking head / step-by-step demo",
             "audio": "Clear voiceover with upbeat background music",
             "text_overlay": "Step 1: … | Step 2: … | Step 3: …", "purpose": "Deliver the core value"},
            {"shot": 4, "time": "30–50s", "type": "Proof / Result",
             "visual": "Show transformation, screenshot, or before/after",
             "audio": "Continue clear voiceover",
             "text_overlay": "Here's the result after 7 days →", "purpose": "Build trust & credibility"},
            {"shot": 5, "time": f"50–{min(duration_seconds-2, 56)}s", "type": "CTA",
             "visual": "Face to camera, enthusiastic direct address",
             "audio": "Upbeat tone, direct address",
             "text_overlay": "Follow for Part 2 👇 | Save so you don't lose this",
             "purpose": "Drive follow/save/share"},
            {"shot": 6, "time": f"{min(duration_seconds-2, 56)}–{duration_seconds}s", "type": "Outro",
             "visual": "Brand handle / logo overlay",
             "audio": "Fade out music",
             "text_overlay": f"@your{niche.lower().replace(' ', '')}handle", "purpose": "Brand recall"},
        ]
        return {
            "title": f"[{style}] {topic}",
            "platform": platform, "duration": f"{duration_seconds}s",
            "shots": shots,
            "equipment": ["Smartphone on tripod (vertical 9:16)", "Ring light", "Lavalier mic"],
            "editing_tips": [
                "Cut on beat with the music",
                "Add captions — 80% watch without sound",
                "Use zoom cuts for energy between shots",
                "Color grade for consistency across all videos",
            ],
            "hook_ideas": [
                f"'Did you know THIS about {topic}?'",
                f"'Stop doing THIS if you're into {niche}'",
                f"'The {niche} secret nobody tells you about {topic}'",
                f"'I gained X followers doing THIS with {topic}'",
            ],
            "trending_sounds": f"Search '{niche} motivation' or 'trending {platform} sounds 2026'",
            "thumbnail_tip": "Bright background + readable text (max 5 words) + human face with expression",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a professional {platform} video director and content strategist. Language: {language}."
            )},
            {"role": "user", "content": (
                f"Create a detailed storyboard for a {duration_seconds}s {style} {platform} video.\n"
                f"Topic: {topic}. Niche: {niche}.\n\n"
                f"Return JSON only: {{\"title\",\"platform\",\"duration\","
                f"\"shots\":[{{\"shot\":int,\"time\",\"type\",\"visual\",\"audio\","
                f"\"text_overlay\",\"purpose\"}}],"
                f"\"equipment\":[],\"editing_tips\":[],\"hook_ideas\":[],"
                f"\"trending_sounds\":\"str\",\"thumbnail_tip\":\"str\"}}"
            )},
        ],
        temperature=0.7, max_tokens=1200,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"title": topic, "shots": [], "hook_ideas": [], "editing_tips": []}


async def generate_dm_templates(
    purpose: str = "Influencer Outreach", platform: str = "Instagram",
    brand_name: str = "", niche: str = "General",
    tone: str = "Professional", count: int = 5,
    language: str = "English"
) -> list:
    """Generate personalized DM campaign templates with personalization variables."""
    if not USE_AI or not LLM_CLIENT:
        intros = [
            "Hey {{name}} 👋", "Hi {{name}}! Hope you're having an amazing day!",
            "Hey {{name}}, love your content! 🙌", "Hi {{name}}, quick question for you!",
            "Hey {{name}}, noticed your latest post about {{latest_post}} — amazing! 🔥",
        ]
        bodies = {
            "Influencer Outreach": f"We're {brand_name or 'a brand'} in the {niche} space looking for authentic creators like you.",
            "Lead Generation": f"We help {niche} professionals achieve better results faster.",
            "Partnership": f"We're building a {niche} community and your content aligns perfectly.",
            "Sales": f"We have a solution that helps {niche} businesses like yours grow.",
            "Networking": f"Your work in {niche} is inspiring — would love to connect!",
        }
        body = bodies.get(purpose, f"We're reaching out about an exciting {purpose.lower()} opportunity.")
        return [
            {
                "template_name": f"Template {i+1}: {purpose} (Variation {i+1})",
                "message": (
                    f"{intros[i % len(intros)]}\n\n{body}\n\n"
                    f"This is specifically because of {{{{latest_post}}}} — it really resonated with us!\n\n"
                    f"Would you be open to a quick chat? Reply YES and I'll send the details! 🚀\n\n"
                    f"— {brand_name or 'The Team'}"
                ),
                "best_for": f"Cold {purpose.lower()} outreach",
                "estimated_open_rate": f"{35 + i * 4}%",
                "estimated_reply_rate": f"{8 + i * 2}%",
                "personalization_vars": ["{{name}}", "{{latest_post}}", "{{follower_count}}"],
                "follow_up_timing": f"{2 + i} days if no reply",
            }
            for i in range(count)
        ]
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                f"You are a DM outreach marketing expert for {platform}. Language: {language}."
            )},
            {"role": "user", "content": (
                f"Create {count} {tone} DM templates for: {purpose}\n"
                f"Platform: {platform}, Brand: {brand_name or 'N/A'}, Niche: {niche}\n"
                f"Use personalization vars: {{{{name}}}}, {{{{latest_post}}}}, {{{{follower_count}}}}\n\n"
                f"Return JSON array only: [{{\"template_name\",\"message\",\"best_for\","
                f"\"estimated_open_rate\",\"estimated_reply_rate\","
                f"\"personalization_vars\":[],\"follow_up_timing\"}}]"
            )},
        ],
        temperature=0.8, max_tokens=1000,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return [{"template_name": "Template 1", "message": "AI unavailable",
                 "best_for": purpose, "estimated_open_rate": "35%",
                 "estimated_reply_rate": "8%", "personalization_vars": []}]
