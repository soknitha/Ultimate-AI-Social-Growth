"""
GrowthOS AI — Audio & Voice Content Engine
============================================
Feature #115 : Trending Audio Finder & Analyzer
Feature #116 : Podcast Episode Script Generator
Feature #117 : Voice Note / Audio DM Script
Feature #118 : Audio Branding Identifier
Feature #119 : Transcription-to-Caption Optimizer
"""
import json
import random
import re
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _clean(raw: str) -> str:
    return re.sub(r"```json|```", "", raw).strip()


async def _gpt(prompt: str, system: str = "", fast: bool = False) -> str:
    if not _client:
        return ""
    try:
        model = LLM_FAST_MODEL if fast else LLM_MODEL
        resp = await _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or "You are a leading audio content strategist and podcast production expert."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.85,
            max_tokens=2200,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #115: Trending Audio Analyzer ───────────────────────────────────
async def analyze_trending_audio(
    niche: str = "General",
    platform: str = "TikTok",
    content_type: str = "Educational",
    language: str = "English",
) -> dict:
    """Find and analyze trending audio/sounds for content creation."""
    if USE_AI and _client:
        prompt = (
            f"Identify trending audio/music strategies for {platform} {content_type} content in the {niche} niche.\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"trending_audio_types":['
            f'{{"type":"audio type name","mood":"...","best_content_for":"...","viral_potential":"High/Medium/Low","how_to_use":"..."}}],'
            f'"audio_strategy":"overall audio content strategy",'
            f'"sound_categories":["5 sound/music categories trending right now"],'
            f'"audio_tips":["5 pro tips for using audio to boost reach"],'
            f'"platform_audio_hacks":["3 platform-specific audio algorithm hacks"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    audio_types_map = {
        "TikTok": [
            {"type": "Phonk/Dark Electronic", "mood": "Intense, mysterious", "best_content_for": "Transformation videos, before/after", "viral_potential": "High", "how_to_use": "Use for montage-style content, sync cuts to bass drops"},
            {"type": "Lo-fi Chill Beats", "mood": "Relaxed, focused", "best_content_for": "Educational, study, productivity content", "viral_potential": "High", "how_to_use": "Background for talking-head educational videos"},
            {"type": "Trending Pop Remix", "mood": "Upbeat, energetic", "best_content_for": "Comedy, lifestyle, day-in-my-life", "viral_potential": "Very High", "how_to_use": "Lip-sync, trending dance, or ironically use for unexpected niche"},
            {"type": "Emotional Cinematic", "mood": "Nostalgic, heartfelt", "best_content_for": "Storytelling, personal journeys, testimonials", "viral_potential": "High", "how_to_use": "Use for emotional narrative videos with text overlays"},
            {"type": "Voiceover + Beat", "mood": "Professional, authoritative", "best_content_for": "Business tips, tutorials, facts", "viral_potential": "Medium-High", "how_to_use": "Record clear voiceover, add subtle beat underneath"},
        ],
        "Instagram": [
            {"type": "Ambient Electronic", "mood": "Modern, aesthetic", "best_content_for": "Product showcases, aesthetics, brand content", "viral_potential": "High", "how_to_use": "Use as soft background for slow Reels"},
            {"type": "Upbeat Pop", "mood": "Happy, energetic", "best_content_for": "Lifestyle, fashion, fitness content", "viral_potential": "Very High", "how_to_use": "Match transitions to beat drops for satisfying effect"},
            {"type": "Acoustic/Indie", "mood": "Authentic, personal", "best_content_for": "Behind-the-scenes, personal brand, stories", "viral_potential": "Medium", "how_to_use": "Perfect for authentic 'real talk' or coffee shop aesthetic"},
        ],
    }
    audio_types = audio_types_map.get(platform, audio_types_map["TikTok"])
    return {
        "trending_audio_types": audio_types,
        "audio_strategy": f"For {niche} content on {platform}: Use trending sounds in the first 24 hours of their peak to catch the algorithm wave. Mix 70% trending sounds with 30% original audio to build unique brand recognition.",
        "sound_categories": [
            "Viral trend sounds (catch within 48 hours of trending)",
            "Niche-specific background music",
            "Original voice + background beat",
            "Viral speech/quote clips",
            "ASMR / ambient sounds (high engagement in specific niches)",
        ],
        "audio_tips": [
            f"Use trending sounds within 24-48 hours of them going viral on {platform} — this is when the algorithm pushes them hardest",
            "Save trending audio to a playlist and check it weekly for what's gaining momentum",
            "Original audio that trends can establish you as a trendsetter, not a follower",
            "Match your visual cuts EXACTLY to the beat — editing to music increases watch time by 40%",
            f"For {platform}, sounds with 10K-500K uses are in the 'sweet spot' — not too saturated, still trending",
        ],
        "platform_audio_hacks": [
            f"{platform}'s algorithm actively boosts content using trending sounds — check the 'trending' audio tab daily",
            "Duet/Stitch viral audios to hijack their existing traffic and redirect to your content",
            "Upload original audio with a keyword-rich name to appear in sound searches",
        ],
    }


# ─── Feature #116: Podcast Episode Script Generator ─────────────────────────
async def generate_podcast_script(
    topic: str,
    episode_length: int = 20,
    show_name: str = "My Podcast",
    host_name: str = "Host",
    style: str = "Educational",
    language: str = "English",
) -> dict:
    """Generate a complete podcast episode script with intro, segments, and outro."""
    if USE_AI and _client:
        prompt = (
            f"Write a complete {episode_length}-minute {style} podcast episode script.\n"
            f"Show: {show_name} | Host: {host_name} | Topic: {topic}\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"episode_title":"catchy episode title",'
            f'"show_notes_summary":"2-3 sentence episode summary",'
            f'"intro_script":"30-second intro script (read verbatim)",'
            f'"segments":['
            f'{{"segment":"Segment 1: Hook & Context","duration_min":3,"script":"full script for this segment"}},'
            f'{{"segment":"Segment 2: Main Content","duration_min":12,"script":"..."}},'
            f'{{"segment":"Segment 3: Key Takeaways","duration_min":3,"script":"..."}},'
            f'{{"segment":"Segment 4: Outro & CTA","duration_min":2,"script":"..."}}],'
            f'"interview_questions":["5 potential follow-up questions if interviewing a guest"],'
            f'"social_clips":["3 viral quote clips from the episode"],'
            f'"seo_keywords":["5 SEO keywords for this episode"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "episode_title": f"The Truth About {topic}: Everything You Need to Know in {episode_length} Minutes",
        "show_notes_summary": f"In this episode, {host_name} breaks down everything you need to know about {topic}. From the biggest mistakes to the proven strategies, this is the only {topic} guide you'll ever need.",
        "intro_script": f"Welcome back to {show_name}! I'm your host, {host_name}. Today we're diving deep into {topic} — and I promise, by the end of this episode, you'll have everything you need to take action immediately. Let's get into it!",
        "segments": [
            {
                "segment": "Segment 1: Hook & Context",
                "duration_min": 3,
                "script": f"So let me ask you something — when's the last time you really thought about {topic}? [PAUSE] Most people haven't. And that's exactly why they're stuck. Here's what I mean: [CONTEXT/STORY about {topic}]. This matters because [RELEVANCE]. Over the next {episode_length} minutes, here's exactly what we're covering: [PREVIEW KEY POINTS].",
            },
            {
                "segment": "Segment 2: Main Content",
                "duration_min": max(10, episode_length - 8),
                "script": f"Alright, let's get into the meat of this. Point number one: [KEY INSIGHT 1 about {topic}]. Now here's why this is critical... [EXPLAIN]. Point number two: [KEY INSIGHT 2]. The data on this is fascinating — [SUPPORT]. And point number three, which most people completely miss: [KEY INSIGHT 3]. Let me give you a real example of this in action: [EXAMPLE/STORY].",
            },
            {
                "segment": "Segment 3: Key Takeaways",
                "duration_min": 3,
                "script": f"Okay, so let's bring this all together. The three things I want you to walk away with today: ONE — [TAKEAWAY 1 from {topic}]. TWO — [TAKEAWAY 2]. And THREE — [TAKEAWAY 3]. If you do nothing else this week, do these three things and you WILL see a difference. I guarantee it.",
            },
            {
                "segment": "Segment 4: Outro & CTA",
                "duration_min": 2,
                "script": f"That's a wrap on today's episode of {show_name}! If this was helpful, do me a favor — hit subscribe, leave a review, and share this with one person who needs to hear it. I'll see you in the next episode. Until then — keep growing! 🎙️",
            },
        ],
        "interview_questions": [
            f"What's the single biggest misconception people have about {topic}?",
            f"Walk me through the moment you realized {topic} was going to change everything.",
            f"If someone has zero experience with {topic}, where do they start?",
            f"What's one thing you wish someone had told you about {topic} when you were starting out?",
            f"What does the future of {topic} look like in the next 2-3 years?",
        ],
        "social_clips": [
            f"\"The truth about {topic} that nobody in the industry wants you to know...\" — {host_name}, {show_name}",
            f"\"I've seen people fail at {topic} for ONE reason — and it has nothing to do with skill.\" — {host_name}",
            f"\"If I had to start {topic} from scratch tomorrow, here's the ONLY three things I'd focus on first...\" — {host_name}",
        ],
        "seo_keywords": [topic, f"{topic} tips", f"how to {topic}", f"{topic} podcast", f"learn {topic}"],
    }


# ─── Feature #117: Voice Note / Audio DM Script ──────────────────────────────
async def generate_voice_note_script(
    purpose: str,
    recipient: str = "follower",
    tone: str = "Friendly",
    length: str = "30 seconds",
    language: str = "English",
) -> dict:
    """Generate natural-sounding voice note scripts for DMs and outreach."""
    if USE_AI and _client:
        prompt = (
            f"Write a {length} {tone} voice note script for: {purpose}\n"
            f"Recipient: {recipient} | Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"script":"full word-for-word voice note script (natural, conversational)",'
            f'"tone_notes":"how to deliver this for maximum impact",'
            f'"word_count":int,'
            f'"estimated_duration":"X seconds",'
            f'"alternative_opening":"different way to start",'
            f'"follow_up":"what to send if no reply after 48 hours"}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    script_map = {
        "30 seconds": f"Hey! [NAME], just wanted to send you a quick voice note rather than a text because I wanted you to actually feel the energy here! So, {purpose} — and I thought of YOU specifically because [REASON]. Anyway, I'd love to chat more about this. Just reply 'YES' or send me a voice note back and we'll figure it out together. Talk soon! 😊",
        "60 seconds": f"Hey [NAME], I'm sending this as a voice note because what I want to say deserves more than just a text. So, {purpose}. Here's the thing — I've been following your [work/content/journey] and I'm genuinely impressed. [SPECIFIC COMPLIMENT]. That's exactly why I wanted to reach out about this. I think this could be really valuable for you specifically because [PERSONALIZED REASON]. No pressure at all — I just think the timing is right and I'd love to explore this with you. Just reply whenever you get a chance! Looking forward to connecting. Take care! 👋",
    }
    script = script_map.get(length, script_map["30 seconds"])
    wc = len(script.split())
    return {
        "script": script,
        "tone_notes": f"Speak with energy and a smile — people can hear it in your voice. Keep it conversational, NOT salesy. Breathe naturally. If you mess up, laugh it off and keep going — it makes you sound more human and trustworthy.",
        "word_count": wc,
        "estimated_duration": length,
        "alternative_opening": f"Hi [NAME]! Okay so I almost sent you a DM but I felt like this deserved a voice note because I'm actually excited about this — {purpose}...",
        "follow_up": f"Hey [NAME]! Just circling back on my voice note from a couple days ago about {purpose}. I know life gets busy! When you get a moment, would love to hear your thoughts. No pressure, just wanted to make sure you didn't miss it 😊",
    }


# ─── Feature #118: Audio Brand Strategy ──────────────────────────────────────
async def build_audio_brand_strategy(
    brand_name: str,
    niche: str,
    target_emotion: str = "Trust & Excitement",
    language: str = "English",
) -> dict:
    """Build a complete audio branding strategy for social media presence."""
    if USE_AI and _client:
        prompt = (
            f"Create a complete audio branding strategy for {brand_name} in the {niche} niche.\n"
            f"Target emotion: {target_emotion} | Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"brand_sound_identity":"describe the sonic identity",'
            f'"music_palette":{{"primary_genre":"...","tempo":"...","instruments":["3-4 instruments"],"avoid":["2 sound types to avoid"]}},'
            f'"content_audio_map":[{{"content_type":"...","recommended_audio":"...","mood":"..."}}],'
            f'"original_audio_ideas":["3 original audio content ideas"],'
            f'"voice_guidelines":{"tone":"...","pacing":"...","characteristics":["3 voice characteristics"]},'
            f'"implementation_steps":["5 steps to build audio brand identity"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "brand_sound_identity": f"{brand_name} should sound: Modern, confident, and approachable. The audio identity should evoke {target_emotion} and make the audience feel both inspired and supported.",
        "music_palette": {
            "primary_genre": "Upbeat Electronic / Contemporary Pop",
            "tempo": "120-140 BPM for content, 80-100 BPM for calmer brand moments",
            "instruments": ["Clean electric piano", "Subtle synth pads", "Punchy drums", "Acoustic guitar (for authenticity moments)"],
            "avoid": ["Heavy metal / aggressive sounds", "Outdated jingles or overly corporate music"],
        },
        "content_audio_map": [
            {"content_type": "Product launches", "recommended_audio": "High-energy build-up with dramatic reveal drop", "mood": "Excitement, anticipation"},
            {"content_type": "Educational content", "recommended_audio": "Soft lo-fi beats, low-key background music", "mood": "Focus, learning"},
            {"content_type": "Testimonials/Social proof", "recommended_audio": "Warm acoustic or piano, emotional background", "mood": "Trust, authenticity"},
            {"content_type": "Behind the scenes", "recommended_audio": "Casual, upbeat, friendly vibe", "mood": "Relatability, human connection"},
            {"content_type": "Call-to-action / Promo", "recommended_audio": "Urgent, energetic, punchy rhythms", "mood": "Action, urgency"},
        ],
        "original_audio_ideas": [
            f"Create a signature {brand_name} intro jingle (3-5 seconds) — use it on every video for brand recall",
            f"Record a branded 'notification sound' that plays when sharing promotions",
            f"Develop a signature voiceover style with consistent tone, pacing, and energy across all content",
        ],
        "voice_guidelines": {
            "tone": f"Confident but warm — the {brand_name} voice should feel like a knowledgeable friend, not a corporate spokesperson",
            "pacing": "Medium pace — never rushed, but always energetic. Vary speed for emphasis",
            "characteristics": ["Clear enunciation", "Genuine enthusiasm (not fake)", "Conversational contractions (say 'you're' not 'you are')"],
        },
        "implementation_steps": [
            f"Step 1: Define {brand_name}'s 3 core audio emotions (e.g., motivated, trusted, excited)",
            "Step 2: Create a royalty-free music library with 10-15 tracks across your mood categories",
            "Step 3: Record a signature intro/outro to use consistently across all video content",
            "Step 4: Train yourself/your team on voice guidelines and practice consistently",
            "Step 5: Test audio A/B: same content with 2 different music tracks — see which performs better",
        ],
    }


# ─── Feature #119: Transcription-to-Caption Optimizer ────────────────────────
async def optimize_transcription_to_caption(
    raw_transcript: str,
    platform: str = "Instagram",
    max_length: int = 300,
    language: str = "English",
) -> dict:
    """Transform a raw audio/video transcript into an optimized social media caption."""
    if USE_AI and _client:
        prompt = (
            f"Transform this raw transcript into an optimized {platform} caption (max {max_length} chars).\n"
            f"Language: {language}\n\nRaw transcript:\n{raw_transcript[:2000]}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"optimized_caption":"ready-to-post caption",'
            f'"key_quotes":["3 standout quotes for Stories/Tweets"],'
            f'"thread_version":["5 tweet-sized chunks for a thread"],'
            f'"hook_sentence":"the single most compelling sentence from the transcript",'
            f'"suggested_hashtags":"10 relevant hashtags",'
            f'"repurpose_ideas":["3 ways to repurpose this content"]}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    # Smart extraction from transcript
    sentences = [s.strip() for s in raw_transcript.split(".") if len(s.strip()) > 20]
    hook = sentences[0] if sentences else raw_transcript[:100]
    quote_1 = sentences[1] if len(sentences) > 1 else "Key insight from the content"
    quote_2 = sentences[2] if len(sentences) > 2 else "Important takeaway"
    quote_3 = sentences[-1] if len(sentences) > 3 else "Final call to action"

    return {
        "optimized_caption": f"💡 {hook}\n\n{'. '.join(sentences[1:4]) if len(sentences) > 3 else raw_transcript[:200]}\n\nSave this for later! 💾 | What's your take? Drop it below 👇",
        "key_quotes": [
            f'"{quote_1}"',
            f'"{quote_2}"',
            f'"{quote_3}"',
        ],
        "thread_version": [
            f"🧵 THREAD: {hook}",
            f"1/ {sentences[1] if len(sentences) > 1 else 'First key point from the content'}",
            f"2/ {sentences[2] if len(sentences) > 2 else 'Second key point'}",
            f"3/ {sentences[3] if len(sentences) > 3 else 'Third key point'}",
            f"4/ 🔁 RT if this was helpful! Follow for more insights like this every day.",
        ],
        "hook_sentence": hook,
        "suggested_hashtags": "#content #knowledge #viral #tip #socialmedia #growth #learn #creator #trending #fyp",
        "repurpose_ideas": [
            "Turn key quotes into text-based Instagram carousel slides",
            "Use the transcript structure as a Twitter/X thread",
            "Extract the 3 main points for a 60-second Reels summary video",
        ],
    }
