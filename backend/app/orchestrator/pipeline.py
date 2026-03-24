"""Pipeline runner — 3-phase orchestration with adversarial debates.

Architecture (inspired by TradingAgents' multi-phase debate pattern):

  PHASE 1 — ANALYSIS (quick_think)
    ① Story Analyzer → ② Test Strategist
    → summarize context

  PHASE 2 — GENERATION + REVIEW DEBATE
    ③ Test Case Writer ↔ ③b Test Critic (N rounds)
    → ④ Automation Engineer → ⑤ Test Executor
    → summarize context

  PHASE 3 — VERDICT DEBATE
    ⑥ Bug Detective ↔ ⑥b Quality Advocate (N rounds)
    → ⑦ Coverage Judge (deep_think) — independent GO/NO-GO

Each phase compresses context via the summarizer to prevent
context-window overflow (instead of TradingAgents' message clearing).
Reflection memory injects relevant past experiences per agent.
"""

from __future__ import annotations

import re

import structlog

from app.agents.automation_engineer import AutomationEngineerAgent
from app.agents.bug_detective import BugDetectiveAgent
from app.agents.coverage_analyst import CoverageAnalystAgent
from app.agents.quality_advocate import QualityAdvocateAgent
from app.agents.story_analyzer import StoryAnalyzerAgent
from app.agents.test_case_writer import TestCaseWriterAgent
from app.agents.test_critic import TestCriticAgent
from app.agents.test_executor import TestExecutorAgent
from app.agents.test_strategist import TestStrategistAgent
from app.config import settings
from app.core.events import Event, EventType, event_bus
from app.memory import memory
from app.models.stories import JiraStory
from app.orchestrator.debate import DebateEngine
from app.orchestrator.state import PipelineState
from app.orchestrator.summarizer import summarize_phase

logger = structlog.get_logger()

# ── Agent instances ──
_story_analyzer = StoryAnalyzerAgent()
_test_strategist = TestStrategistAgent()
_test_case_writer = TestCaseWriterAgent()
_test_critic = TestCriticAgent()
_automation_engineer = AutomationEngineerAgent()
_test_executor = TestExecutorAgent()
_bug_detective = BugDetectiveAgent()
_quality_advocate = QualityAdvocateAgent()
_coverage_judge = CoverageAnalystAgent()


def _build_user_input(story: JiraStory, framework: str) -> str:
    """Build the initial user input from the Jira story."""
    acceptance = "\n".join(f"  - {a}" for a in story.acceptance)
    return f"""Story: {story.id} — {story.title}
Priority: {story.priority}
Labels: {", ".join(story.labels)}
Story Points: {story.story_points}
Sprint: {story.sprint}

Description:
{story.description}

Acceptance Criteria:
{acceptance}

Target Framework: {framework}"""


async def run_pipeline(state: PipelineState, story: JiraStory) -> PipelineState:
    """Execute the 3-phase pipeline with debates and context summarization.

    Signature unchanged for backward compatibility with API routes.
    """
    state.start()
    user_input = _build_user_input(story, state.framework)

    await event_bus.publish(Event(
        type=EventType.PIPELINE_STARTED,
        execution_id=state.execution_id,
        data={"storyId": story.id, "framework": state.framework},
    ))

    try:
        # ════════════════════════════════════════
        # PHASE 1: ANALYSIS (quick_think tier)
        # ════════════════════════════════════════
        await _publish_phase_log(state.execution_id, "Phase 1: Analysis")

        await _run_agent(
            _story_analyzer, user_input, state,
        )
        await _run_agent(
            _test_strategist, user_input, state,
        )

        # Compress Phase 1 context before Phase 2
        phase1_summary = await summarize_phase(
            "Phase 1 (Analysis)",
            state.accumulated_context,
            state.execution_id,
        )

        # ════════════════════════════════════════
        # PHASE 2: GENERATION + REVIEW DEBATE
        # ════════════════════════════════════════
        await _publish_phase_log(state.execution_id, "Phase 2: Generation + Review Debate")

        # Writer ↔ Critic debate
        debate_engine = DebateEngine(
            agent_a=_test_case_writer,
            agent_b=_test_critic,
            max_rounds=settings.debate_max_rounds,
        )

        # Inject memory context for the writer
        writer_memory = memory.retrieve_formatted("writer", user_input)
        debate_context = phase1_summary
        if writer_memory:
            debate_context = f"{writer_memory}\n\n{phase1_summary}"

        debate_result = await debate_engine.run(
            topic=user_input,
            context=debate_context,
            execution_id=state.execution_id,
        )

        # Store the writer's final output (last proposer turn) and critic's output
        writer_output = ""
        critic_output = ""
        for turn in debate_result.turns:
            if turn.agent_id == "writer":
                writer_output = turn.content
            elif turn.agent_id == "critic":
                critic_output = turn.content
        state.agent_completed("writer", writer_output)
        state.agent_completed("critic", critic_output)

        # Store debate transcript as context for downstream agents
        state.outputs["debate_review"] = debate_result.transcript

        # Automation + Execution (sequential, using debate-refined tests)
        await _run_agent(
            _automation_engineer, user_input, state,
        )
        await _run_agent(
            _test_executor, user_input, state,
        )

        # Compress Phase 2 context before Phase 3
        phase2_summary = await summarize_phase(
            "Phase 2 (Generation + Execution)",
            state.accumulated_context,
            state.execution_id,
        )

        # ════════════════════════════════════════
        # PHASE 3: VERDICT DEBATE
        # ════════════════════════════════════════
        await _publish_phase_log(state.execution_id, "Phase 3: Verdict Debate")

        # Bug Detective ↔ Quality Advocate debate → Coverage Judge verdict
        verdict_engine = DebateEngine(
            agent_a=_bug_detective,
            agent_b=_quality_advocate,
            judge=_coverage_judge,
            max_rounds=settings.risk_debate_max_rounds,
        )

        bug_memory = memory.retrieve_formatted("bug", user_input)
        verdict_context = phase2_summary
        if bug_memory:
            verdict_context = f"{bug_memory}\n\n{phase2_summary}"

        verdict_result = await verdict_engine.run(
            topic=user_input,
            context=verdict_context,
            execution_id=state.execution_id,
        )

        # Store outputs
        bug_output = ""
        advocate_output = ""
        for turn in verdict_result.turns:
            if turn.agent_id == "bug":
                bug_output = turn.content
            elif turn.agent_id == "advocate":
                advocate_output = turn.content
        state.agent_completed("bug", bug_output)
        state.agent_completed("advocate", advocate_output)
        state.agent_completed("coverage", verdict_result.judge_verdict)
        state.outputs["debate_verdict"] = verdict_result.transcript

        # ════════════════════════════════════════
        # FINALIZE
        # ════════════════════════════════════════
        _extract_metrics(state)
        state.complete()

        # Store reflections for future runs
        _store_reflections(state)

        await event_bus.publish(Event(
            type=EventType.PIPELINE_COMPLETED,
            execution_id=state.execution_id,
            data={
                "storyId": story.id,
                "testsGenerated": state.test_cases_generated,
                "passed": state.tests_passed,
                "failed": state.tests_failed,
                "coverage": state.coverage_percent,
                "verdict": state.verdict,
                "durationMs": state.duration_ms,
            },
        ))

    except Exception as exc:
        state.fail(str(exc))
        logger.error(
            "pipeline_failed",
            execution_id=state.execution_id,
            error=str(exc),
        )
        await event_bus.publish(Event(
            type=EventType.PIPELINE_FAILED,
            execution_id=state.execution_id,
            data={"error": str(exc)},
        ))

    return state


# ── Helpers ──


async def _run_agent(
    agent,
    user_input: str,
    state: PipelineState,
) -> str:
    """Run a single agent with memory injection and streaming."""
    state.agent_started(agent.agent_id)
    logger.info("agent_started", execution_id=state.execution_id, agent=agent.agent_id)

    # Inject reflection memory
    past_experience = memory.retrieve_formatted(agent.agent_id, user_input)
    context = state.accumulated_context
    if past_experience:
        context = f"{past_experience}\n\n{context}"

    full_output = ""
    async for token in agent.stream(
        user_input=user_input,
        context=context,
        execution_id=state.execution_id,
    ):
        full_output += token

    state.agent_completed(agent.agent_id, full_output)
    logger.info(
        "agent_completed",
        execution_id=state.execution_id,
        agent=agent.agent_id,
        output_len=len(full_output),
    )
    return full_output


async def _publish_phase_log(execution_id: str, phase_name: str) -> None:
    """Publish a phase-transition log event."""
    await event_bus.publish(Event(
        type=EventType.LOG,
        execution_id=execution_id,
        data={
            "agentId": "pipeline",
            "message": f"═══ {phase_name} ═══",
            "level": "info",
        },
    ))


def _store_reflections(state: PipelineState) -> None:
    """Store agent outputs as reflections for future BM25 retrieval."""
    for agent_id in ("writer", "bug", "coverage"):
        output = state.outputs.get(agent_id, "")
        if output:
            memory.store(agent_id, state.execution_id, output)


def _extract_metrics(state: PipelineState) -> None:
    """Parse agent outputs to extract summary metrics.

    This is a best-effort extraction from the text outputs.
    A production system would use structured JSON from agents.
    """
    executor_output = state.outputs.get("executor", "")
    coverage_output = state.outputs.get("coverage", "")

    # Count test cases from writer output
    writer_output = state.outputs.get("writer", "")
    state.test_cases_generated = writer_output.count("TC-")

    # Parse passed/failed from executor output
    passed_match = re.search(r"Passed:\s*(\d+)", executor_output)
    failed_match = re.search(r"Failed:\s*(\d+)", executor_output)
    skipped_match = re.search(r"Skipped:\s*(\d+)", executor_output)

    state.tests_passed = int(passed_match.group(1)) if passed_match else 0
    state.tests_failed = int(failed_match.group(1)) if failed_match else 0
    state.tests_skipped = int(skipped_match.group(1)) if skipped_match else 0

    # Parse coverage from coverage output
    coverage_match = re.search(r"Overall Coverage:\s*(\d+(?:\.\d+)?)%", coverage_output)
    state.coverage_percent = float(coverage_match.group(1)) if coverage_match else 0.0

    # Parse verdict
    verdict_match = re.search(r"Verdict:\s*(GO|CONDITIONAL GO|NO-GO)", coverage_output)
    state.verdict = verdict_match.group(1) if verdict_match else None
