"""
GrowthOS AI — Sales & Revenue Engine
======================================
P5: Sales Funnel Mapper, Lead Magnet Builder, Social Commerce,
    Email Sequence Generator, Offer & CTA Generator
"""
import json, re, asyncio
from ai_core.llm_client import LLM_CLIENT, LLM_MODEL, LLM_FAST_MODEL, USE_AI


def _parse_json(raw: str):
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


async def map_sales_funnel(
    niche: str, product: str, platform: str = "Instagram",
    audience: str = "General", language: str = "English"
) -> dict:
    """Map content to TOFU/MOFU/BOFU sales funnel stages."""
    if not USE_AI or not LLM_CLIENT:
        return {
            "funnel_overview": f"3-stage funnel for {product} in {niche}",
            "tofu": {
                "goal": "Awareness — attract cold strangers",
                "content_types": ["Educational Reels", "Trending Duets", "Viral Quote Cards", "How-To Carousels"],
                "cta": "Follow for more tips / Save this post",
                "post_ratio": "60% of all posts",
                "examples": [
                    f"'5 {niche} mistakes you're making right now'",
                    f"'Why most people fail at {niche} — and how to fix it'",
                    f"Trending sound + {niche} tip overlay",
                ],
            },
            "mofu": {
                "goal": "Consideration — warm up warm audience",
                "content_types": ["Behind-the-Scenes", "Case Studies", "Testimonials", "Live Q&A", "Comparison Posts"],
                "cta": "DM me 'INFO' / Click link in bio",
                "post_ratio": "30% of all posts",
                "examples": [
                    f"'How I helped [client] achieve X with {product}'",
                    f"'Here's what's inside {product} — honest walkthrough'",
                    "Customer success story (before/after)",
                ],
            },
            "bofu": {
                "goal": "Decision — convert warm leads to buyers",
                "content_types": ["Limited Offers", "FAQ Posts", "Urgency Stories", "Direct Sales Posts"],
                "cta": f"Buy now / Link in bio / DM '{product.upper()[:6]}'",
                "post_ratio": "10% of all posts",
                "examples": [
                    f"'Last 24h — {product} at launch price'",
                    "'I'm only taking 10 clients this month'",
                    "'Answering your top 5 questions about [product]'",
                ],
            },
            "weekly_plan": "Mon: TOFU → Tue: TOFU → Wed: MOFU → Thu: TOFU → Fri: MOFU → Sat: BOFU → Sun: Rest/Engagement",
            "funnel_tips": [
                "Never jump straight to BOFU — warm up first with 3–5 TOFU posts",
                "MOFU content should show PROOF (results, testimonials, demos)",
                "BOFU should have urgency + specificity (price, deadline, slots)",
                "Retarget story viewers for MOFU/BOFU — they're warm already",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social media sales funnel strategist. Language: {language}."},
            {"role": "user", "content": (
                f"Create a TOFU/MOFU/BOFU social media content funnel.\n"
                f"Niche: {niche}, Product/Service: {product}, Platform: {platform}, Audience: {audience}\n\n"
                f"Return JSON only: {{\"funnel_overview\",\"tofu\":{{\"goal\",\"content_types\":[],\"cta\","
                f"\"post_ratio\",\"examples\":[]}},\"mofu\":{{...}},\"bofu\":{{...}},"
                f"\"weekly_plan\",\"funnel_tips\":[]}}"
            )},
        ],
        temperature=0.5, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"funnel_overview": resp.choices[0].message.content[:500]}


async def build_lead_magnet(
    niche: str, topic: str, format_type: str = "Checklist",
    audience: str = "Beginners", language: str = "English"
) -> dict:
    """Generate a complete lead magnet (ebook, checklist, template, mini-course)."""
    if not USE_AI or not LLM_CLIENT:
        templates = {
            "Checklist": {
                "title": f"The Ultimate {topic} Checklist for {audience}",
                "hook": f"Download this FREE checklist and never miss a step when doing {topic}!",
                "content_sections": [
                    f"✅ Step 1: Prepare your {niche} foundation",
                    f"✅ Step 2: Set clear goals for {topic}",
                    f"✅ Step 3: Choose the right tools and platforms",
                    f"✅ Step 4: Create your content/product roadmap",
                    f"✅ Step 5: Launch and promote effectively",
                    f"✅ Step 6: Analyze results and optimize",
                    f"✅ Step 7: Scale what works, cut what doesn't",
                ],
                "cta": "Ready for the next level? DM me 'READY' and let's talk!",
            },
            "Ebook": {
                "title": f"The Complete Guide to {topic} — For {audience}",
                "hook": f"Get this FREE ebook and master {topic} in 7 days!",
                "content_sections": [
                    f"Chapter 1: Why {topic} is the game-changer for {niche}",
                    f"Chapter 2: The common mistakes {audience} make (and how to avoid them)",
                    f"Chapter 3: The proven step-by-step {topic} system",
                    f"Chapter 4: Advanced techniques for faster results",
                    f"Chapter 5: Real case studies and success stories",
                    f"Chapter 6: Your 30-day action plan",
                ],
                "cta": "Want 1:1 help implementing this? Book a free call below!",
            },
        }
        t = templates.get(format_type, templates["Checklist"])
        return {
            "lead_magnet_title": t["title"],
            "format": format_type,
            "hook_line": t["hook"],
            "content_sections": t["content_sections"],
            "landing_page_headline": f"FREE {format_type}: {t['title']}",
            "landing_page_bullets": [
                f"✅ Discover the fastest way to succeed at {topic}",
                f"✅ Avoid the 3 biggest {niche} mistakes",
                f"✅ Get a step-by-step action plan you can start today",
            ],
            "opt_in_cta": f"Yes! Send Me the FREE {format_type}!",
            "thank_you_message": f"Your free {format_type} is on its way! Check your inbox in 5 minutes.",
            "follow_up_email_subject": f"Here's your FREE {format_type} about {topic}!",
            "closing_cta": t["cta"],
            "promotion_captions": [
                f"🎁 FREE {format_type} Alert!\n\nI just created the ultimate {format_type.lower()} for {audience} who want to master {topic}.\n\nComment '{topic.upper()[:5]}' below and I'll DM it to you! 👇",
                f"Stop guessing. Start winning.\n\nI put everything I know about {topic} into one FREE {format_type.lower()}.\n\nLink in bio → grab it before it's gone! 🔗",
            ],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are an expert digital marketer and content creator. Language: {language}."},
            {"role": "user", "content": (
                f"Build a complete lead magnet.\nNiche: {niche}, Topic: {topic}, "
                f"Format: {format_type}, Audience: {audience}\n\n"
                f"Return JSON only: {{\"lead_magnet_title\",\"format\",\"hook_line\","
                f"\"content_sections\":[],\"landing_page_headline\",\"landing_page_bullets\":[],"
                f"\"opt_in_cta\",\"thank_you_message\",\"follow_up_email_subject\","
                f"\"closing_cta\",\"promotion_captions\":[]}}"
            )},
        ],
        temperature=0.65, max_tokens=1100,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"lead_magnet_title": topic, "content_sections": []}


async def generate_product_descriptions(
    product_name: str, product_type: str, niche: str,
    price: str = "", platform: str = "Instagram Shopping",
    language: str = "English"
) -> dict:
    """Generate AI social commerce product descriptions for Instagram/TikTok Shop."""
    if not USE_AI or not LLM_CLIENT:
        p = product_name
        return {
            "short_description": f"✨ {p} — the {niche} essential you didn't know you needed. {f'Only {price}!' if price else ''} 🔥",
            "long_description": (
                f"Introducing {p} — your ultimate {niche} companion.\n\n"
                f"🎯 Perfect for: Anyone serious about {niche}\n"
                f"💎 What you get: Premium quality, proven results\n"
                f"⚡ Why it works: Designed specifically for {niche} enthusiasts\n\n"
                f"{'💰 Price: ' + price if price else ''}\n\n"
                f"🛒 Tap the link to grab yours before it sells out!"
            ),
            "instagram_caption": (
                f"This {p} is EVERYTHING for {niche} lovers 🙌\n\n"
                f"✅ Feature 1: Premium quality\n"
                f"✅ Feature 2: Easy to use\n"
                f"✅ Feature 3: Proven results\n\n"
                f"{'Price: ' + price + ' 💸' if price else ''}\n\n"
                f"👉 Tap the link in bio to shop now!\n\n"
                f"#{niche.lower().replace(' ','')} #shop #newproduct"
            ),
            "tiktok_caption": (
                f"POV: You finally found the {p} you've been looking for 😍 "
                f"#{niche.lower().replace(' ','')} #tiktokmademebuyit #musthave"
            ),
            "story_swipe_up_text": f"Shop {p} — {price or 'Limited Stock!'} 👆 Swipe Up!",
            "urgency_lines": [
                f"⏰ Only {{}}/units left — grab yours now!",
                f"🔥 {p} is selling fast — don't miss out!",
                "🚀 New drop — first 50 orders get a bonus!",
            ],
            "seo_tags": [p.lower(), niche.lower(), "shop", "buy", product_type.lower(), "new", "trending"],
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a social commerce copywriter. Language: {language}."},
            {"role": "user", "content": (
                f"Write social commerce copy for: {product_name}\n"
                f"Type: {product_type}, Niche: {niche}, Price: {price or 'N/A'}, Platform: {platform}\n\n"
                f"Return JSON: {{\"short_description\",\"long_description\",\"instagram_caption\","
                f"\"tiktok_caption\",\"story_swipe_up_text\",\"urgency_lines\":[],\"seo_tags\":[]}}"
            )},
        ],
        temperature=0.7, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"short_description": product_name, "instagram_caption": ""}


async def generate_email_sequence(
    topic: str, niche: str, product: str = "",
    num_emails: int = 5, tone: str = "Conversational",
    language: str = "English"
) -> list:
    """Convert social content into email autoresponder sequences."""
    if not USE_AI or not LLM_CLIENT:
        subjects = [
            f"Welcome! Here's what's coming 🎉",
            f"The #1 {niche} mistake (are you making it?)",
            f"How [Name] went from zero to results with {topic}",
            f"My proven {topic} system — revealed",
            f"Last email: are you ready to transform your {niche}?",
            f"BONUS: I'm giving this away for free",
            f"Final reminder + a special gift for you",
        ]
        bodies = [
            f"Hey {{{{first_name}}}},\n\nWelcome to the {niche} community! I'm so glad you're here.\n\nOver the next few days, I'm going to share my best {topic} strategies with you — the same ones I use to [result].\n\nStay tuned — tomorrow I'll reveal the #1 mistake most {niche} beginners make.\n\n— [Your Name]",
            f"Hey {{{{first_name}}}},\n\nMost people who struggle with {topic} make the same critical mistake...\n\nThey [common mistake]. And it costs them [negative outcome].\n\nThe fix? [Brief solution teaser]\n\nI'll explain exactly how to fix this tomorrow.\n\n— [Your Name]",
            f"Hey {{{{first_name}}}},\n\nLet me tell you about [Client Name]...\n\nWhen they came to me, they were struggling with {topic}. After just 30 days of applying my {niche} system, they achieved [specific result].\n\nHere's exactly what we did: [3-step summary]\n\n— [Your Name]",
            f"Hey {{{{first_name}}}},\n\nToday I'm pulling back the curtain on my complete {topic} system.\n\nStep 1: [Action]\nStep 2: [Action]\nStep 3: [Action]\n\n{'Want me to walk you through it live? Reply YES and I will.' if not product else f'Ready to go deeper? {product} covers all of this and more → [Link]'}\n\n— [Your Name]",
            f"Hey {{{{first_name}}}},\n\nThis is my last email in this series — but it might be the most important one.\n\nYou now have everything you need to transform your {niche} results. The question is: will you take action?\n\n{'If you want my 1:1 help, reply to this email.' if not product else f'{product} is your shortcut → [Link]'}\n\nI believe in you.\n\n— [Your Name]",
        ]
        return [
            {
                "email_number": i + 1,
                "subject": subjects[i],
                "preview_text": subjects[i][:60],
                "body": bodies[min(i, len(bodies) - 1)],
                "send_day": f"Day {[0, 1, 3, 5, 7, 9, 11][i]}",
                "primary_cta": "Reply to this email" if i < num_emails - 1 else (f"Get {product}" if product else "Book a free call"),
                "goal": ["Welcome & set expectations", "Identify problem", "Build trust with proof",
                          "Reveal system/value", "Close/convert", "Bonus offer", "Final urgency"][i],
            }
            for i in range(min(num_emails, 7))
        ]
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": f"You are an email marketing specialist. Tone: {tone}. Language: {language}."},
            {"role": "user", "content": (
                f"Create a {num_emails}-email autoresponder sequence.\n"
                f"Topic: {topic}, Niche: {niche}, Product: {product or 'N/A'}\n\n"
                f"Return JSON array: [{{\"email_number\":int,\"subject\",\"preview_text\","
                f"\"body\",\"send_day\",\"primary_cta\",\"goal\"}}]"
            )},
        ],
        temperature=0.6, max_tokens=1400,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return [{"email_number": 1, "subject": topic, "body": "", "send_day": "Day 0"}]


async def generate_ctas(
    niche: str, product: str = "", platform: str = "Instagram",
    goal: str = "Drive Sales", count: int = 20, language: str = "English"
) -> dict:
    """Generate high-converting CTAs, offers, and promo copy."""
    if not USE_AI or not LLM_CLIENT:
        cta_templates = {
            "Drive Sales": [
                f"👉 Tap link in bio to get {product or 'it'} now",
                f"💳 Grab your {product or niche + ' solution'} before price goes up",
                f"🔥 DM me '{(product or niche)[:8].upper()}' for instant access",
                f"🛒 Shop now → link in bio (limited stock!)",
                f"⚡ Only 48 hours left at this price — act fast!",
            ],
            "Grow Followers": [
                "👆 Follow for daily {niche} tips you won't find anywhere else",
                "🔔 Hit that follow so you never miss a post!",
                "Tag someone who needs to see this 👇",
                "Follow + comment your biggest {niche} challenge below!",
                "Turn on notifications — I post something valuable every day 💡",
            ],
            "Get Leads": [
                f"💌 DM me 'FREE' and I'll send you [lead magnet] right now",
                f"📧 Drop your email in my bio → get the free {niche} guide",
                f"Comment 'YES' below if you want the free checklist!",
                f"Link in bio → grab your free {niche} resource today",
                f"Reply to this story 👆 and I'll send you the bonus",
            ],
        }
        base = cta_templates.get(goal, cta_templates["Drive Sales"])
        all_ctas = base * ((count // len(base)) + 1)
        return {
            "ctas": all_ctas[:count],
            "urgency_lines": [
                "⏰ Offer ends in 24 hours!", "🔥 Only 5 spots left!",
                "⚡ Price going up midnight tonight!", "🚨 Last chance — closing enrollment!",
                "💥 This deal disappears at [time]!",
            ],
            "discount_offers": [
                f"Save 20% with code {niche[:4].upper()}20",
                "First 10 customers get a FREE bonus worth $[X]",
                "Bundle deal: Buy 2, get 1 FREE",
                "Early bird special — 30% off for next 48h only",
            ],
            "story_poll_ctas": [
                "Are you ready to [desired outcome]? YES 🔥 / Not yet 🤔",
                "Which do you struggle with more? [Option A] / [Option B]",
                f"Want the FREE {niche} guide? TAP YES 👇",
            ],
            "bio_cta": f"👇 Grab the free {niche} guide",
        }
    resp = await LLM_CLIENT.chat.completions.create(
        model=LLM_FAST_MODEL,
        messages=[
            {"role": "system", "content": f"You are a conversion copywriter. Language: {language}."},
            {"role": "user", "content": (
                f"Generate {count} high-converting CTAs for: Niche={niche}, "
                f"Product={product or 'N/A'}, Platform={platform}, Goal={goal}\n\n"
                f"Return JSON: {{\"ctas\":[],\"urgency_lines\":[],\"discount_offers\":[],"
                f"\"story_poll_ctas\":[],\"bio_cta\"}}"
            )},
        ],
        temperature=0.75, max_tokens=900,
    )
    try:
        return _parse_json(resp.choices[0].message.content)
    except Exception:
        return {"ctas": [], "urgency_lines": [], "discount_offers": []}
