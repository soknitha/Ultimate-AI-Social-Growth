"""
GrowthOS AI — Video Studio Engine
====================================
Feature #100 : AI Short-Form Video Script Generator (TikTok / Reels / Shorts)
Feature #101 : Scene-by-Scene Storyboard Builder
Feature #102 : Video Hook Optimizer
Feature #103 : Caption & Subtitle Script AI
Feature #104 : Video SEO Title Generator
"""
import json
import random
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _clean_json(raw: str) -> str:
    return re.sub(r"```json|```", "", raw).strip()


async def _gpt(prompt: str, system: str = "", fast: bool = False) -> str:
    if not _client:
        return ""
    try:
        model = LLM_FAST_MODEL if fast else LLM_MODEL
        resp = await _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or "You are a world-class short-form video content strategist."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.88,
            max_tokens=2500,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #100: AI Short-Form Video Script Generator ──────────────────────
async def generate_video_script(
    topic: str,
    platform: str = "TikTok",
    duration: int = 60,
    style: str = "Educational",
    niche: str = "General",
    language: str = "English",
) -> dict:
    """Generate a full short-form video script with hook, body, and CTA."""
    if USE_AI and _client:
        prompt = (
            f"Create a complete {duration}-second {style} {platform} video script.\n"
            f"Topic: {topic}\nNiche: {niche}\nLanguage: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"title":"catchy video title","hook":"first 3-second spoken hook","script_sections":['
            f'{{"section":"Hook","duration_sec":3,"on_screen_text":"...","voiceover":"...","action":"..."}},'
            f'{{"section":"Problem","duration_sec":8,"on_screen_text":"...","voiceover":"...","action":"..."}},'
            f'{{"section":"Solution","duration_sec":20,"on_screen_text":"...","voiceover":"...","action":"..."}},'
            f'{{"section":"Proof","duration_sec":15,"on_screen_text":"...","voiceover":"...","action":"..."}},'
            f'{{"section":"CTA","duration_sec":5,"on_screen_text":"...","voiceover":"...","action":"..."}}],'
            f'"hashtags":["5 relevant hashtags"],'
            f'"viral_tip":"one key tip to boost virality",'
            f'"caption":"engaging post caption with emojis"}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean_json(raw))
            except Exception:
                pass

    # Fallback mock
    sections = [
        {"section": "Hook",     "duration_sec": 3,  "on_screen_text": f"🔥 {topic} changed everything...", "voiceover": f"Nobody talks about this {topic} secret...", "action": "Jump cut + text overlay"},
        {"section": "Problem",  "duration_sec": 8,  "on_screen_text": f"❌ Most people do {topic} wrong", "voiceover": f"Here's what 99% of people get wrong about {topic}...", "action": "Screen recording or B-roll"},
        {"section": "Solution", "duration_sec": 20, "on_screen_text": f"✅ The {topic} framework", "voiceover": f"I discovered this {topic} system that changed everything...", "action": "Step-by-step list animation"},
        {"section": "Proof",    "duration_sec": 15, "on_screen_text": "📈 Results: +10K in 30 days", "voiceover": "After using this method, here's what happened...", "action": "Show stats screenshot"},
        {"section": "CTA",      "duration_sec": 5,  "on_screen_text": "💾 Save this for later!", "voiceover": "Save this video so you never forget it!", "action": "Point at camera + smile"},
    ]
    return {
        "title": f"The {topic} Secret Nobody Tells You 🤫",
        "hook": f"Stop what you're doing — this {topic} trick changes everything...",
        "script_sections": sections,
        "hashtags": [f"#{topic.replace(' ', '')}", f"#{platform.lower()}tips", "#growthhack", "#viral2025", "#fyp"],
        "viral_tip": "Film the hook 5 different ways and use the one with the most energy.",
        "caption": f"🚨 The {topic} trick that got me 10K followers in 30 days 👇\n\nSave this before it disappears! #fyp #{platform.lower()}",
    }


# ─── Feature #101: Scene-by-Scene Storyboard Builder ─────────────────────────
async def build_storyboard(topic: str, platform: str = "TikTok", num_scenes: int = 6, language: str = "English") -> dict:
    """Build a detailed visual storyboard for short-form video."""
    if USE_AI and _client:
        prompt = (
            f"Create a {num_scenes}-scene visual storyboard for a viral {platform} video about: {topic}.\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"concept":"overall video concept","scenes":['
            f'{{"scene":1,"timestamp":"0:00-0:03","visual":"describe exact shot","text_overlay":"...","audio_cue":"...","emotion":"...","camera":"..."}}],'
            f'"b_roll_suggestions":["3 B-roll ideas"],'
            f'"music_vibe":"describe the music mood",'
            f'"editing_style":"describe the edit pace and style"}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean_json(raw))
            except Exception:
                pass

    moods = ["curiosity", "excitement", "inspiration", "humor", "surprise"]
    cameras = ["Close-up", "Wide shot", "Over-shoulder", "POV", "Talking head", "Screen record"]
    scenes = []
    ts_start = 0
    for i in range(1, num_scenes + 1):
        dur = [3, 8, 12, 10, 8, 5][i - 1] if i <= 6 else 8
        ts_end = ts_start + dur
        scenes.append({
            "scene": i,
            "timestamp": f"0:{ts_start:02d}-0:{ts_end:02d}",
            "visual": f"Scene {i}: Dynamic visual showing key point about {topic}",
            "text_overlay": f"KEY POINT {i}: Bold text animation",
            "audio_cue": "Beat drop / transition sound",
            "emotion": random.choice(moods),
            "camera": random.choice(cameras),
        })
        ts_start = ts_end

    return {
        "concept": f"Fast-paced educational breakdown of {topic} with cinematic transitions",
        "scenes": scenes,
        "b_roll_suggestions": [
            f"Close-up of hands demonstrating {topic}",
            "Reaction face showing surprise/excitement",
            f"Screen recording of {topic} results/data",
        ],
        "music_vibe": "High-energy trap / upbeat phonk with clear beat drops",
        "editing_style": "Fast jump cuts every 2-3 seconds, text animations, zoom-in transitions",
    }


# ─── Feature #102: Video Hook Optimizer ──────────────────────────────────────
async def optimize_video_hook(existing_hook: str, platform: str = "TikTok", language: str = "English") -> dict:
    """Rewrite and optimize an existing hook for maximum retention."""
    if USE_AI and _client:
        prompt = (
            f"Optimize this video hook for {platform}:\n\"{existing_hook}\"\n\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"original_score":int,"optimized_hooks":['
            f'{{"hook":"...","score":int,"technique":"hook technique name","why":"explanation"}},'
            f'{{"hook":"...","score":int,"technique":"...","why":"..."}},{{"hook":"...","score":int,"technique":"...","why":"..."}}],'
            f'"best_hook":"the single best hook",'
            f'"retention_prediction":"X% of viewers will watch past 3 seconds",'
            f'"key_change":"main improvement made"}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean_json(raw))
            except Exception:
                pass

    techniques = ["Pattern Interrupt", "Curiosity Gap", "Bold Claim", "Relatable Problem", "Shocking Statistic"]
    hooks = [
        {"hook": f"Wait — you've been doing {existing_hook[:20]}... completely wrong 😱", "score": 92, "technique": "Pattern Interrupt", "why": "Triggers cognitive dissonance and fear of missing out"},
        {"hook": f"The {existing_hook[:20]} method that got me banned (but worked) 🔥", "score": 88, "technique": "Curiosity Gap", "why": "Creates irresistible need to know what happened"},
        {"hook": f"I tested 100 ways to {existing_hook[:20]} — here's what actually works:", "score": 85, "technique": "Bold Claim + Data", "why": "Establishes authority and promises specific value"},
    ]
    return {
        "original_score": 42,
        "optimized_hooks": hooks,
        "best_hook": hooks[0]["hook"],
        "retention_prediction": "78% of viewers will watch past 3 seconds",
        "key_change": "Added emotional trigger + pattern interrupt to stop the scroll",
    }


# ─── Feature #103: Caption & Subtitle Script ────────────────────────────────
async def generate_captions(topic: str, platform: str = "TikTok", style: str = "Energetic", language: str = "English") -> dict:
    """Generate optimized captions and subtitles for video content."""
    if USE_AI and _client:
        prompt = (
            f"Create optimized {style} captions/subtitles for a {platform} video about: {topic}\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"main_caption":"full post caption with line breaks and emojis",'
            f'"subtitle_lines":["5 short subtitle lines for on-screen text"],'
            f'"cta_variations":["3 different CTA options"],'
            f'"hashtag_sets":{{"primary":"5 broad hashtags","niche":"5 niche hashtags","trending":"5 trending hashtags"}},'
            f'"alt_text":"accessible alt text for the video"}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean_json(raw))
            except Exception:
                pass

    return {
        "main_caption": f"🚨 {topic} is changing the game in 2025\n\nHere's everything you need to know 👇\n\n✅ Point 1\n✅ Point 2\n✅ Point 3\n\nSave this for later! Drop a 🔥 if this helped!\n\n#fyp #viral #growthhack",
        "subtitle_lines": [
            f"🔥 {topic} Changed Everything...",
            "Here's What Nobody Tells You",
            "Step 1: Stop doing THIS",
            "Step 2: Do THIS instead",
            "Save this before it's gone! 💾",
        ],
        "cta_variations": [
            "💾 Save this and share with someone who NEEDS this!",
            "🔔 Follow for more daily growth tips!",
            "💬 Comment 'YES' if this helped you!",
        ],
        "hashtag_sets": {
            "primary": "#fyp #viral #trending #foryou #explore",
            "niche": f"#{topic.replace(' ', '')} #growthhack #socialmediatips #contentcreator #2025",
            "trending": "#tiktokmademebuyit #dayinmylife #learnontiktok #greenscreen #pov",
        },
        "alt_text": f"Educational video about {topic} with step-by-step instructions and text overlays",
    }


# ─── Feature #104: Video SEO Title Generator ─────────────────────────────────
async def generate_video_seo(topic: str, platform: str = "YouTube", language: str = "English") -> dict:
    """Generate SEO-optimized titles, descriptions and tags for video platforms."""
    if USE_AI and _client:
        prompt = (
            f"Generate SEO-optimized metadata for a {platform} video about: {topic}\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"titles":["5 SEO-optimized title options, ranked by CTR potential"],'
            f'"description":"full {platform} description with keywords, timestamps, and links placeholder",'
            f'"tags":["20 relevant search tags"],'
            f'"thumbnail_text":"3-5 word bold thumbnail text",'
            f'"chapters":["5 chapter markers with timestamps"],'
            f'"search_keywords":["top 5 keywords this video targets"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean_json(raw))
            except Exception:
                pass

    return {
        "titles": [
            f"{topic} Tutorial 2025 (Complete Guide)",
            f"How to Master {topic} in 10 Minutes | Step-by-Step",
            f"{topic} EXPOSED: What Nobody Tells You",
            f"I Tried {topic} for 30 Days — Here Are the Results",
            f"The ONLY {topic} Guide You'll Ever Need",
        ],
        "description": f"In this video, I break down everything about {topic}...\n\n📌 Chapters:\n0:00 - Introduction\n1:30 - The Problem\n4:00 - The Solution\n8:00 - Results\n9:30 - Conclusion\n\n🔗 Links:\n→ Tool: [link]\n→ Free Guide: [link]\n\n##{topic.replace(' ', '')} #{platform.lower()} #tutorial",
        "tags": [topic, f"{topic} tutorial", f"how to {topic}", f"{topic} 2025", f"learn {topic}", "social media", "growth hack", "viral", "tips", "strategy", "beginner guide", "advanced", "results", "case study", "step by step", "complete guide", "best way", "fastest method", "proven", "secret"],
        "thumbnail_text": f"{topic.upper()} SECRETS",
        "chapters": [
            "0:00 - Why This Matters",
            "1:00 - The Biggest Mistake",
            "3:00 - The Framework",
            "6:00 - Live Example",
            "9:00 - Results & Next Steps",
        ],
        "search_keywords": [topic, f"how to {topic}", f"{topic} tips", f"best {topic} strategy", f"{topic} 2025"],
    }
