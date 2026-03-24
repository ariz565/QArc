"""Context summarizer — compress phase outputs to prevent context window overflow.

Between pipeline phases we LLM-summarize the accumulated context, keeping it
under control for downstream agents (like TradingAgents clearing messages
between phases to avoid "growing prompt" problem).
"""

from __future__ import annotations

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class ContextSummarizerAgent(BaseAgent):
    """Special agent that compresses accumulated context between phases.

    Uses the deep_think tier for high-quality summarization.
    """

    agent_id = "summarizer"
    agent_name = "Context Summarizer"
    role = "Phase context compression"


SUMMARIZER = ContextSummarizerAgent()

# Token approximation: ~4 chars per token
_CHARS_PER_TOKEN = 4
_MAX_CONTEXT_CHARS = 12_000  # ~3K tokens — summarize if longer


async def summarize_phase(
    phase_name: str,
    accumulated_context: str,
    execution_id: str = "",
) -> str:
    """Summarize accumulated context if it exceeds the threshold.

    Returns the original context if it's short enough, or a compressed
    summary if it's too long.
    """
    if len(accumulated_context) <= _MAX_CONTEXT_CHARS:
        logger.debug(
            "context_within_limit",
            phase=phase_name,
            chars=len(accumulated_context),
        )
        return accumulated_context

    logger.info(
        "context_summarizing",
        phase=phase_name,
        original_chars=len(accumulated_context),
        threshold=_MAX_CONTEXT_CHARS,
    )

    prompt = (
        f"Summarize the following QA pipeline output from {phase_name}. "
        f"Preserve ALL: test case IDs, bug IDs, pass/fail counts, coverage percentages, "
        f"severity ratings, and key findings. Remove repetition and verbose formatting.\n\n"
        f"{accumulated_context}"
    )

    summary = await SUMMARIZER.run(prompt)

    logger.info(
        "context_summarized",
        phase=phase_name,
        original_chars=len(accumulated_context),
        summary_chars=len(summary),
        compression_ratio=round(len(summary) / len(accumulated_context), 2),
    )

    return f"[Summarized from {phase_name}]\n{summary}"
