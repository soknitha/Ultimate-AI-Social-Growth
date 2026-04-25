"""
GrowthOS AI — Social Commerce Engine
=======================================
Feature #110 : Shoppable Content Generator
Feature #111 : Product Showcase Caption AI
Feature #112 : DM Sales Funnel Builder
Feature #113 : Social Proof Collector
Feature #114 : Conversion Rate Optimizer
"""
import json
import random
import re
import sys
import os

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
                {"role": "system", "content": system or "You are an elite social commerce and conversion rate optimization specialist."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.82,
            max_tokens=2200,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ─── Feature #110: Shoppable Content Generator ───────────────────────────────
async def generate_shoppable_content(
    product_name: str,
    price: str,
    platform: str = "Instagram",
    target_audience: str = "General",
    language: str = "English",
) -> dict:
    """Generate shoppable post content optimized for social commerce conversion."""
    if USE_AI and _client:
        prompt = (
            f"Create a complete shoppable {platform} post for:\n"
            f"Product: {product_name}\nPrice: {price}\n"
            f"Target Audience: {target_audience}\nLanguage: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"hook":"scroll-stopping first line",'
            f'"product_description":"benefit-driven 2-sentence description",'
            f'"pain_point":"problem this product solves",'
            f'"social_proof":"fictional but realistic proof statement",'
            f'"price_anchor":"psychological pricing statement",'
            f'"cta":"strong action CTA",'
            f'"caption":"full ready-to-post caption",'
            f'"story_frames":["5 Instagram Story slide descriptions"],'
            f'"product_tags":["5 relevant product hashtags"],'
            f'"conversion_tips":["3 tips to increase purchase rate"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "hook": f"✨ This {product_name} is SELLING OUT — and now I understand why...",
        "product_description": f"The {product_name} delivers professional-grade results in minutes. Designed for {target_audience}, it's the last tool you'll ever need.",
        "pain_point": f"Tired of wasting money on solutions that don't work? {product_name} is different.",
        "social_proof": "⭐⭐⭐⭐⭐ 2,847 happy customers | '10/10 — completely changed my routine' - @verified_user",
        "price_anchor": f"💰 Most alternatives cost 3x more. Get yours for only {price} — limited stock!",
        "cta": f"👆 Tap the link in bio or DM us '{product_name.split()[0].upper()}' for instant access!",
        "caption": (
            f"✨ This {product_name} is SELLING OUT — and now I understand why...\n\n"
            f"Tired of spending money on things that don't deliver? This is different.\n\n"
            f"⭐⭐⭐⭐⭐ 2,847 happy customers say it changed everything.\n\n"
            f"💰 Only {price} — but stock is running low!\n\n"
            f"👆 Tap the link in bio or DM '{product_name.split()[0].upper()}' to grab yours now!\n\n"
            f"#shop #shopnow #{product_name.replace(' ', '').lower()} #sale #trending"
        ),
        "story_frames": [
            "Frame 1: Bold text — 'Wait, have you seen this yet?' on dark background",
            f"Frame 2: Product close-up with '{product_name}' text and arrow pointing to it",
            "Frame 3: Before/After or problem vs. solution graphic",
            f"Frame 4: Price reveal — '{price} only!' with countdown sticker",
            "Frame 5: Swipe-up/Link sticker CTA — 'Grab yours NOW →'",
        ],
        "product_tags": [
            f"#{product_name.replace(' ', '').lower()}",
            "#shopnow", "#musthave", "#newdrop", f"#{platform.lower()}shop",
        ],
        "conversion_tips": [
            "Add a countdown timer in Stories to create urgency (increases purchase rate by 32%)",
            "Pin the product post to your profile grid for maximum visibility",
            "Reply to every comment with a personalized product benefit to build trust",
        ],
    }


# ─── Feature #111: Product Showcase Caption AI ───────────────────────────────
async def generate_product_showcase(
    product: str,
    features: str,
    benefit: str,
    platform: str = "Instagram",
    language: str = "English",
) -> dict:
    """Generate multiple product showcase captions with different angles."""
    if USE_AI and _client:
        prompt = (
            f"Write 4 different {platform} product showcase captions for:\n"
            f"Product: {product}\nFeatures: {features}\nKey Benefit: {benefit}\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"angles":[{{"approach":"Lifestyle","caption":"...","emoji_score":"X/10"}},'
            f'{{"approach":"Problem-Solution","caption":"...","emoji_score":"X/10"}},'
            f'{{"approach":"Educational","caption":"...","emoji_score":"X/10"}},'
            f'{{"approach":"Community/UGC","caption":"...","emoji_score":"X/10"}}],'
            f'"best_angle":"...","carousel_slide_texts":["5 carousel slide headlines"]}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "angles": [
            {
                "approach": "Lifestyle",
                "caption": f"✨ Imagine your life with {product}...\n\nThis isn't just a product — it's a lifestyle upgrade. {benefit}.\n\nShop via link in bio! 🛍️",
                "emoji_score": "8/10",
            },
            {
                "approach": "Problem-Solution",
                "caption": f"❌ Struggling without {product}?\n\n✅ Here's the solution: {benefit}\n\nTap the link to get yours → #solution #productreview",
                "emoji_score": "9/10",
            },
            {
                "approach": "Educational",
                "caption": f"📚 Did you know {product} can {benefit}?\n\nHere's how it works:\n\n{features}\n\nQuestions? Drop them below! 👇",
                "emoji_score": "7/10",
            },
            {
                "approach": "Community/UGC",
                "caption": f"🙌 Our community LOVES {product}!\n\n\"{benefit}\" — real customer review\n\nShare your experience below ↓ We feature the best! 💫",
                "emoji_score": "8/10",
            },
        ],
        "best_angle": "Problem-Solution",
        "carousel_slide_texts": [
            f"The Problem With {product} Alternatives 😤",
            f"Introducing: {product} 🚀",
            f"Feature Breakdown: {features[:50]}...",
            f"Real Results: {benefit}",
            "Get Yours → Link in Bio! 🛍️",
        ],
    }


# ─── Feature #112: DM Sales Funnel Builder ───────────────────────────────────
async def build_dm_funnel(
    product: str,
    trigger_keyword: str,
    audience: str = "General",
    language: str = "English",
) -> dict:
    """Build a complete automated DM sales funnel sequence."""
    if USE_AI and _client:
        prompt = (
            f"Build a complete 5-step DM sales funnel for {product}.\n"
            f"Trigger keyword: '{trigger_keyword}' | Target audience: {audience}\n"
            f"Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"trigger_setup":"how to set up the keyword trigger",'
            f'"funnel_steps":[{{"step":1,"trigger":"initial keyword received",'
            f'"message":"...","wait_time":"immediately","goal":"..."}}],'
            f'"objection_handlers":[{{"objection":"price too high","response":"..."}},'
            f'{{"objection":"need to think about it","response":"..."}},'
            f'{{"objection":"already have something similar","response":"..."}}],'
            f'"conversion_rate_estimate":"X-Y%",'
            f'"best_trigger_keywords":["5 high-converting keyword options"]}}'
        )
        raw = await _gpt(prompt)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "trigger_setup": f"Set up keyword '{trigger_keyword}' as an auto-DM trigger in your social inbox. When anyone DMs or comments with this word, the funnel activates automatically.",
        "funnel_steps": [
            {
                "step": 1,
                "trigger": f"User sends '{trigger_keyword}'",
                "message": f"Hey! 👋 Thanks for your interest in {product}! I'm so excited to share this with you.\n\nCan I ask — what's your biggest challenge right now that {product} might help with?",
                "wait_time": "Immediately",
                "goal": "Qualify the lead and open conversation",
            },
            {
                "step": 2,
                "trigger": "User replies with their challenge",
                "message": f"Wow, that's EXACTLY what {product} was designed for! 🎯\n\nHere's what makes it different: [KEY BENEFIT]\n\nWould it help if I sent you our quick 2-minute overview?",
                "wait_time": "After user replies",
                "goal": "Build interest and establish relevance",
            },
            {
                "step": 3,
                "trigger": "User says yes / shows interest",
                "message": f"Perfect! Here's the quick breakdown of {product}:\n\n✅ [Feature 1] — [Benefit]\n✅ [Feature 2] — [Benefit]\n✅ [Feature 3] — [Benefit]\n\nHundreds of people are already getting results. Want to see the pricing? 💰",
                "wait_time": "Immediately after previous",
                "goal": "Present core value proposition",
            },
            {
                "step": 4,
                "trigger": "User asks about price / clicks link",
                "message": f"Great news — we have a special offer running right now! 🎉\n\n🔥 {product}: [PRICE] (normally [HIGHER PRICE])\n\nThis deal expires [DATE/TONIGHT]. Here's your direct link: [LINK]\n\nAny questions before you grab it?",
                "wait_time": "Immediately",
                "goal": "Close the sale with urgency",
            },
            {
                "step": 5,
                "trigger": "After purchase OR no response for 24h",
                "message": f"Hey! Just checking in 😊 Did you get a chance to look at {product}?\n\nI don't want you to miss out — we only have limited spots/units left!\n\nReply 'HELP' if you have any questions. I'm here for you! 🙏",
                "wait_time": "24 hours after step 4",
                "goal": "Follow-up and handle objections",
            },
        ],
        "objection_handlers": [
            {
                "objection": "Price too high",
                "response": f"I totally get that! 💯 Think of it this way — most people spend 3x more on alternatives that don't work. {product} is the last investment you'll need to make. Plus, we have a [X]-day money-back guarantee — zero risk! 🛡️",
            },
            {
                "objection": "Need to think about it",
                "response": f"Absolutely, take your time! 😊 Just a heads up — this pricing is only available until [DATE]. After that, it goes back to full price. I'd hate for you to miss out. What specific questions can I answer to help you decide? 🤔",
            },
            {
                "objection": "Already have something similar",
                "response": f"That's actually great to hear! 🙌 Most of our best customers came from exactly that situation. Here's what makes {product} different: [UNIQUE DIFFERENTIATOR]. Would you like to do a quick comparison? I think you'll be surprised! 🔥",
            },
        ],
        "conversion_rate_estimate": "12-28%",
        "best_trigger_keywords": [
            trigger_keyword,
            "INFO",
            "DETAILS",
            "HOW",
            "PRICE",
        ],
    }


# ─── Feature #113: Social Proof Generator ────────────────────────────────────
async def generate_social_proof(
    product: str,
    result: str,
    platform: str = "Instagram",
    language: str = "English",
) -> dict:
    """Generate social proof content templates for product marketing."""
    if USE_AI and _client:
        prompt = (
            f"Generate social proof content templates for {product} that achieved: {result}\n"
            f"Platform: {platform} | Language: {language}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"testimonial_templates":["3 customer testimonial templates"],'
            f'"ugc_request_message":"DM to request user-generated content",'
            f'"screenshot_caption":"caption for sharing customer results screenshot",'
            f'"review_compilation_script":"script for a review compilation reel",'
            f'"trust_badges":["5 trust/credibility statements"],'
            f'"milestone_posts":["3 milestone announcement post templates"]}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "testimonial_templates": [
            f"⭐⭐⭐⭐⭐ 'I was skeptical at first, but {product} actually delivered — {result}! Highly recommend!' — @customer_name",
            f"🙌 '{product} is the real deal. I've tried everything and nothing worked until this. {result} speaks for itself!' — @verified_buyer",
            f"💯 'Don't waste time on anything else. {product} gave me {result} in just [timeframe]. Game changer!' — @happy_user",
        ],
        "ugc_request_message": f"Hey @[username]! We noticed you've been using {product} 🙌 We'd LOVE to feature your story! Would you be open to sharing your experience? We'll tag you and share with our {random.randint(10, 100)}K community! 💫",
        "screenshot_caption": f"💥 Real results from a real customer!\n\nThis is what {product} can do for you → {result}\n\nDM us 'RESULTS' to learn how!\n\n#realresults #proof #customerreview",
        "review_compilation_script": f"[INTRO] 'Don't just take our word for it...' → [CLIP 1: customer saying result] → [CLIP 2: before/after] → [CLIP 3: another testimonial] → [OUTRO] 'Join [X] happy customers — link in bio!'",
        "trust_badges": [
            f"✅ {random.randint(2000, 50000):,}+ happy customers",
            f"🛡️ {random.randint(30, 90)}-day money-back guarantee",
            f"⭐ {random.uniform(4.7, 4.9):.1f}/5 average rating",
            f"🚚 Fast delivery — ships within 24 hours",
            f"🔒 Secure checkout — 256-bit SSL encryption",
        ],
        "milestone_posts": [
            f"🎉 WE HIT {random.randint(1000, 10000):,} CUSTOMERS! Thank you for trusting {product}. To celebrate, we're offering [DISCOUNT] for the next 24 hours! 🎊",
            f"📈 {result} — this is what {product} users are achieving every single day. Are you next? Link in bio!",
            f"💫 One year ago, we launched {product} with a dream. Today, {random.randint(500, 5000):,} people have transformed their [niche] because of it. Thank YOU 🙏",
        ],
    }


# ─── Feature #114: Conversion Rate Optimizer ─────────────────────────────────
async def optimize_conversion_rate(
    current_bio: str,
    product: str,
    traffic_source: str = "Instagram",
    language: str = "English",
) -> dict:
    """Optimize profile bio and content for maximum conversion to sales."""
    if USE_AI and _client:
        prompt = (
            f"Optimize this {traffic_source} bio for maximum conversion to {product} sales.\n"
            f"Language: {language}\n\nCurrent bio:\n{current_bio}\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"bio_score":int,"optimized_bio":"improved bio",'
            f'"bio_changes":["3 specific changes made and why"],'
            f'"link_in_bio_strategy":"how to optimize the bio link",'
            f'"profile_optimization_tips":["5 profile tips for conversion"],'
            f'"cta_hierarchy":"what CTAs to use and in what order",'
            f'"estimated_conversion_lift":"X% improvement expected"}}'
        )
        raw = await _gpt(prompt, fast=True)
        if raw:
            try:
                return json.loads(_clean(raw))
            except Exception:
                pass

    return {
        "bio_score": 52,
        "optimized_bio": f"🚀 Helping [target audience] achieve [result] with {product}\n💡 [Unique value proposition]\n✅ [Social proof: X+ customers]\n👇 Get [lead magnet] FREE:",
        "bio_changes": [
            "Added specific target audience so visitors instantly qualify themselves",
            "Moved CTA to final line with arrow emoji directing to link",
            "Added social proof number to build instant credibility",
        ],
        "link_in_bio_strategy": "Use a link-in-bio tool (Linktree/Beacons) with: 1) Main product/offer, 2) Free lead magnet, 3) Latest content, 4) Contact/DM CTA",
        "profile_optimization_tips": [
            "Use your target keyword in your name field (it's searchable!)",
            "Profile photo should be bright, high-contrast, and recognizable at tiny size",
            "Pin your 3 best-performing/converting posts to the top of your grid",
            "Add a Highlight titled '✅ Results' with customer testimonials",
            "Turn on 'Creator/Business' mode to unlock shopping and analytics features",
        ],
        "cta_hierarchy": "1st: 'Get Free [Lead Magnet]' → 2nd: 'DM for [product]' → 3rd: 'Shop Now' — layer these across your bio, posts, and stories",
        "estimated_conversion_lift": "35-60% improvement expected",
    }
