"""
GrowthOS AI — Unified LLM Client
==================================
Priority order:
  1. Groq  (fastest, free tier — llama3 / mixtral models)
  2. OpenAI (GPT-4o / GPT-4o-mini)
  3. None  → all ai_core functions return mock data

Groq uses the openai Python package with a custom base_url.
No extra dependency needed.

Usage in any ai_core module:
    from ai_core.llm_client import (
        LLM_CLIENT as _client,
        LLM_MODEL  as OPENAI_MODEL,
        LLM_FAST_MODEL as OPENAI_FAST_MODEL,
        USE_AI     as USE_REAL_AI,
    )
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GROQ_API_KEY,   GROQ_MODEL,   GROQ_FAST_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_FAST_MODEL,
)

# ─── Build client ─────────────────────────────────────────────────────────────
LLM_CLIENT    = None
LLM_MODEL     = ""
LLM_FAST_MODEL = ""
LLM_PROVIDER  = "none"

try:
    from openai import AsyncOpenAI

    if GROQ_API_KEY:
        LLM_CLIENT     = AsyncOpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        LLM_MODEL      = GROQ_MODEL
        LLM_FAST_MODEL = GROQ_FAST_MODEL
        LLM_PROVIDER   = "groq"

    elif OPENAI_API_KEY:
        LLM_CLIENT     = AsyncOpenAI(api_key=OPENAI_API_KEY)
        LLM_MODEL      = OPENAI_MODEL
        LLM_FAST_MODEL = OPENAI_FAST_MODEL
        LLM_PROVIDER   = "openai"

except ImportError:
    pass

USE_AI = LLM_CLIENT is not None
