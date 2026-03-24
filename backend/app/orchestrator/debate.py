"""Debate engine — adversarial N-round debate between two agents.

Inspired by TradingAgents' Bull-vs-Bear and Risk debate patterns.
Two agents argue back and forth for N rounds, then a judge renders a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from app.agents.base import BaseAgent
from app.config import settings
from app.core.events import Event, EventType, event_bus

logger = structlog.get_logger()


@dataclass
class DebateTurn:
    """One turn in a debate."""

    round: int
    agent_id: str
    agent_name: str
    content: str


@dataclass
class DebateResult:
    """Full debate transcript + judge verdict."""

    turns: list[DebateTurn] = field(default_factory=list)
    judge_verdict: str = ""
    total_rounds: int = 0

    @property
    def transcript(self) -> str:
        """Format the full debate as a readable transcript."""
        lines = []
        for turn in self.turns:
            lines.append(f"── Round {turn.round} | {turn.agent_name} ──")
            lines.append(turn.content)
            lines.append("")
        return "\n".join(lines)


class DebateEngine:
    """Run N-round adversarial debates between two agents.

    Usage:
        engine = DebateEngine(
            agent_a=test_case_writer,   # produces initial content
            agent_b=test_critic,        # challenges it
            judge=coverage_judge,       # renders verdict
            max_rounds=3,
        )
        result = await engine.run(topic, context, execution_id)
    """

    def __init__(
        self,
        agent_a: BaseAgent,
        agent_b: BaseAgent,
        judge: BaseAgent | None = None,
        max_rounds: int = 3,
    ) -> None:
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.judge = judge
        self.max_rounds = max_rounds

    async def run(
        self,
        topic: str,
        context: str = "",
        execution_id: str = "",
    ) -> DebateResult:
        """Execute the full debate: N rounds of A↔B, then judge verdict.

        Flow:
          Round 1: agent_a produces → agent_b critiques
          Round 2: agent_a defends → agent_b re-critiques
          ...
          Judge: synthesizes debate transcript → verdict
        """
        result = DebateResult(total_rounds=self.max_rounds)
        debate_context = context

        for round_num in range(1, self.max_rounds + 1):
            logger.info(
                "debate_round_start",
                round=round_num,
                max_rounds=self.max_rounds,
                agent_a=self.agent_a.agent_id,
                agent_b=self.agent_b.agent_id,
            )

            if execution_id:
                await event_bus.publish(Event(
                    type=EventType.LOG,
                    execution_id=execution_id,
                    data={
                        "agentId": "debate",
                        "message": f"⚔ Debate Round {round_num}/{self.max_rounds}: "
                                   f"{self.agent_a.agent_name} vs {self.agent_b.agent_name}",
                        "level": "info",
                    },
                ))

            # ── Agent A's turn ──
            a_prompt = self._build_prompt(
                round_num=round_num,
                role="proposer",
                topic=topic,
                debate_history=result.transcript,
            )
            a_output = await self._run_agent(
                self.agent_a, a_prompt, debate_context, execution_id,
            )
            result.turns.append(DebateTurn(
                round=round_num,
                agent_id=self.agent_a.agent_id,
                agent_name=self.agent_a.agent_name,
                content=a_output,
            ))

            # ── Agent B's turn ──
            b_prompt = self._build_prompt(
                round_num=round_num,
                role="challenger",
                topic=topic,
                debate_history=result.transcript,
            )
            b_output = await self._run_agent(
                self.agent_b, b_prompt, debate_context, execution_id,
            )
            result.turns.append(DebateTurn(
                round=round_num,
                agent_id=self.agent_b.agent_id,
                agent_name=self.agent_b.agent_name,
                content=b_output,
            ))

            # Update context with debate progress
            debate_context = f"{context}\n\n{result.transcript}"

        # ── Judge verdict (optional) ──
        if self.judge:
            logger.info("debate_judge_start", judge=self.judge.agent_id)
            if execution_id:
                await event_bus.publish(Event(
                    type=EventType.LOG,
                    execution_id=execution_id,
                    data={
                        "agentId": "debate",
                        "message": f"⚖ Judge {self.judge.agent_name} reviewing debate...",
                        "level": "info",
                    },
                ))

            judge_prompt = (
                f"You are the judge. Review this debate and render your verdict.\n\n"
                f"TOPIC: {topic}\n\n"
                f"DEBATE TRANSCRIPT:\n{result.transcript}"
            )
            result.judge_verdict = await self._run_agent(
                self.judge, judge_prompt, context, execution_id,
            )

        logger.info(
            "debate_completed",
            rounds=self.max_rounds,
            turns=len(result.turns),
            has_verdict=bool(result.judge_verdict),
        )
        return result

    async def _run_agent(
        self,
        agent: BaseAgent,
        prompt: str,
        context: str,
        execution_id: str,
    ) -> str:
        """Run an agent, collecting streamed output into a single string."""
        full_output = ""
        async for token in agent.stream(prompt, context, execution_id):
            full_output += token
        return full_output

    @staticmethod
    def _build_prompt(
        round_num: int,
        role: str,
        topic: str,
        debate_history: str,
    ) -> str:
        """Build the prompt for a debate participant."""
        if round_num == 1 and role == "proposer":
            return topic

        role_label = "proposer" if role == "proposer" else "challenger"
        return (
            f"This is debate round {round_num}. You are the {role_label}.\n\n"
            f"ORIGINAL TOPIC:\n{topic}\n\n"
            f"DEBATE SO FAR:\n{debate_history}\n\n"
            f"Respond to the latest arguments. "
            f"{'Defend and improve your position.' if role == 'proposer' else 'Challenge weaknesses and push for improvement.'}"
        )
