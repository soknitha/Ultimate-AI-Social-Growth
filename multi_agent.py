"""
GrowthOS AI — Multi-Agent Orchestration System
================================================
Advanced Feature #1 : Autonomous Multi-Agent System
Feature #99          : AI Decision Engine (Central Brain)
Feature #12          : AI Debate Mode (Strategy Validation)
Feature #8           : Memory-based Personalization AI
Feature #18          : Human-AI Collaboration Score
Feature #16          : Smart Collaboration AI
"""
import json
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.llm_client import LLM_CLIENT as _client, LLM_MODEL as OPENAI_MODEL, LLM_FAST_MODEL as OPENAI_FAST_MODEL, USE_AI as USE_REAL_AI


class BaseAgent:
    """Base class for all GrowthOS AI agents."""

    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    async def think(self, task: str, context: dict = None) -> str:
        """Agent processes a task and returns its recommendation."""
        if not _client:
            return self._mock_response(task)
        ctx = json.dumps(context or {}, indent=2)
        try:
            resp = await _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user",   "content": f"Task: {task}\n\nContext:\n{ctx}"},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return self._mock_response(task)

    def _mock_response(self, task: str) -> str:
        return f"[{self.name}] Analysis complete for: {task[:80]}. Recommendation ready."


class StrategyAgent(BaseAgent):
    """Plans long-term growth strategy and goals."""

    def __init__(self):
        super().__init__(
            name="Strategy Agent",
            role="Growth Strategist",
            system_prompt=(
                "You are an elite social media growth strategist. "
                "You analyze accounts, set goals, and create detailed growth plans. "
                "You prioritize sustainable, organic growth and ROI. "
                "Always consider platform policies and audience psychology."
            ),
        )

    async def plan(self, account_data: dict) -> dict:
        result = await self.think(
            f"Create a comprehensive growth strategy for this account",
            account_data,
        )
        return {
            "agent": self.name,
            "type": "Strategy Plan",
            "recommendation": result,
            "confidence": "85%",
            "generated_at": datetime.now().isoformat(),
        }


class CreatorAgent(BaseAgent):
    """Generates content ideas and creative assets."""

    def __init__(self):
        super().__init__(
            name="Creator Agent",
            role="Content Creator & Copywriter",
            system_prompt=(
                "You are a viral content creation expert. "
                "You specialize in hooks, captions, video scripts, and creative concepts "
                "that stop the scroll and drive massive engagement. "
                "You understand platform-specific formats deeply."
            ),
        )

    async def create(self, brief: dict) -> dict:
        result = await self.think("Generate creative content for this brief", brief)
        return {
            "agent": self.name,
            "type": "Creative Content",
            "output": result,
            "formats_covered": ["Hook", "Caption", "Script", "Hashtags"],
            "generated_at": datetime.now().isoformat(),
        }


class AnalystAgent(BaseAgent):
    """Analyzes performance data and provides insights."""

    def __init__(self):
        super().__init__(
            name="Analyst Agent",
            role="Performance Analyst & Data Scientist",
            system_prompt=(
                "You are a social media analytics expert. "
                "You interpret performance data, identify patterns, explain why content succeeds or fails, "
                "and provide clear, actionable insights. "
                "You speak in plain language, not jargon."
            ),
        )

    async def analyze(self, metrics: dict) -> dict:
        result = await self.think("Analyze these performance metrics and explain what they mean", metrics)
        return {
            "agent": self.name,
            "type": "Performance Analysis",
            "insights": result,
            "data_quality": "Good" if len(metrics) > 3 else "Limited",
            "generated_at": datetime.now().isoformat(),
        }


class ComplianceAgent(BaseAgent):
    """Monitors policy compliance and account safety."""

    def __init__(self):
        super().__init__(
            name="Compliance Agent",
            role="Platform Policy & Safety Officer",
            system_prompt=(
                "You are a social media platform policy expert. "
                "You ensure all actions comply with platform guidelines (Meta, TikTok, YouTube, Telegram). "
                "You proactively identify risks, prevent bans, and protect account health. "
                "You always err on the side of caution."
            ),
        )

    async def audit(self, action_plan: dict) -> dict:
        result = await self.think(
            "Review this action plan for policy compliance and safety risks",
            action_plan,
        )
        return {
            "agent": self.name,
            "type": "Compliance Audit",
            "verdict": result,
            "approved": "risk" not in result.lower() and "violation" not in result.lower(),
            "generated_at": datetime.now().isoformat(),
        }


class OrchestratorAgent:
    """
    Feature #99: Central AI Decision Engine.
    Coordinates all agents, synthesizes their outputs, and makes final decisions.
    """

    def __init__(self):
        self.strategy_agent   = StrategyAgent()
        self.creator_agent    = CreatorAgent()
        self.analyst_agent    = AnalystAgent()
        self.compliance_agent = ComplianceAgent()

    async def run_full_analysis(self, account_data: dict, metrics: dict) -> dict:
        """
        Run all agents in parallel and synthesize a unified recommendation.
        This is the 'autonomous multi-agent AI team' working together.
        """
        # Run strategy and analyst in parallel (independent)
        strategy_task   = self.strategy_agent.plan(account_data)
        analytics_task  = self.analyst_agent.analyze(metrics)

        strategy_result, analytics_result = await asyncio.gather(strategy_task, analytics_task)

        # Creator gets context from strategy
        content_brief = {
            "platform": account_data.get("platform"),
            "niche":    account_data.get("niche"),
            "strategy": strategy_result.get("recommendation", ""),
        }
        creator_result = await self.creator_agent.create(content_brief)

        # Compliance reviews the final plan
        action_plan = {
            "strategy":  strategy_result,
            "analytics": analytics_result,
            "content":   creator_result,
        }
        compliance_result = await self.compliance_agent.audit(action_plan)

        # Synthesize final decision
        final_decision = self._synthesize(
            account_data, strategy_result, analytics_result,
            creator_result, compliance_result,
        )

        return {
            "orchestrator": "GrowthOS AI Central Brain",
            "account": account_data.get("username", "N/A"),
            "platform": account_data.get("platform", "N/A"),
            "agent_reports": {
                "strategy":   strategy_result,
                "analytics":  analytics_result,
                "content":    creator_result,
                "compliance": compliance_result,
            },
            "final_decision": final_decision,
            "system_confidence": "88%",
            "generated_at": datetime.now().isoformat(),
        }

    def _synthesize(
        self, account: dict,
        strategy: dict, analytics: dict,
        content: dict, compliance: dict,
    ) -> dict:
        """Combine all agent outputs into one actionable decision."""
        approved = compliance.get("approved", True)
        platform = account.get("platform", "")
        niche    = account.get("niche", "")

        priority_actions = [
            f"✅ [Strategy] {strategy.get('recommendation', '')[:120]}",
            f"📊 [Analytics] {analytics.get('insights', '')[:120]}",
            f"✍️ [Content] Focus on {platform}-native formats for {niche} audience",
            f"🛡️ [Compliance] {'All clear — proceed' if approved else 'Review compliance notes before launching'}",
        ]

        return {
            "overall_status": "Green — Launch Ready" if approved else "Yellow — Review Required",
            "priority_actions": priority_actions,
            "estimated_30day_growth": f"+{account.get('current_followers', 5000) // 5:,} followers",
            "key_risk": "Low" if approved else "Medium — address compliance flags",
            "next_step": "Execute Week 1 of the strategy plan immediately",
            "human_approval_needed": not approved,
        }

    async def ai_debate(self, question: str, strategy_a: str, strategy_b: str) -> dict:
        """
        Feature #12: AI Debate Mode — Strategy Validation.
        AI argues both sides then picks the winner.
        """
        if _client:
            try:
                prompt = (
                    f"Debate these two strategies for: '{question}'\n\n"
                    f"Strategy A: {strategy_a}\n"
                    f"Strategy B: {strategy_b}\n\n"
                    "Argue pros and cons of each. Then choose the winner with reasoning. "
                    "Return JSON: pros_a(list), cons_a(list), pros_b(list), cons_b(list), "
                    "winner(A or B), winner_reasoning(str), hybrid_option(str)"
                )
                resp = await _client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert debate judge for marketing strategy."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.6,
                    max_tokens=1000,
                )
                raw = resp.choices[0].message.content.strip()
                try:
                    return json.loads(raw)
                except Exception:
                    return {"debate_result": raw, "winner": "Inconclusive", "generated_at": datetime.now().isoformat()}
            except Exception:
                pass

        return {
            "question": question,
            "strategy_a": strategy_a,
            "strategy_b": strategy_b,
            "pros_a": ["Proven track record", "Lower risk", "Easier to execute"],
            "cons_a": ["Slower results", "Higher initial cost", "Requires more resources"],
            "pros_b": ["Faster results", "Lower cost", "More innovative"],
            "cons_b": ["Higher risk", "Less tested", "May not scale"],
            "winner": "A",
            "winner_reasoning": f"Strategy A is more sustainable for long-term growth in {question[:50]}",
            "hybrid_option": "Start with Strategy B's speed, then transition to Strategy A's sustainability model",
            "debated_at": datetime.now().isoformat(),
        }
