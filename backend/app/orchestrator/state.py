"""Pipeline state — tracks execution progress across 7 agents.

Inspired by DeerFlow's ThreadState: append-only messages, immutable config.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PipelinePhase(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineState:
    """Mutable state that flows through the 7-agent pipeline."""

    execution_id: str
    story_id: str
    framework: str

    # Lifecycle
    phase: PipelinePhase = PipelinePhase.QUEUED
    current_agent: str | None = None
    agents_completed: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

    # Agent outputs (append-only — each agent adds its output)
    outputs: dict[str, str] = field(default_factory=dict)

    # Parsed results (populated by executor + coverage agents)
    test_cases_generated: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    coverage_percent: float = 0.0
    verdict: str | None = None

    def start(self) -> None:
        self.phase = PipelinePhase.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        self.phase = PipelinePhase.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        self.phase = PipelinePhase.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def agent_started(self, agent_id: str) -> None:
        self.current_agent = agent_id

    def agent_completed(self, agent_id: str, output: str) -> None:
        self.outputs[agent_id] = output
        self.agents_completed.append(agent_id)
        self.current_agent = None

    @property
    def duration_ms(self) -> int:
        if not self.started_at:
            return 0
        end = self.completed_at or datetime.now(timezone.utc)
        return int((end - self.started_at).total_seconds() * 1000)

    @property
    def accumulated_context(self) -> str:
        """Build context string from all completed agent outputs."""
        parts = []
        for agent_id, output in self.outputs.items():
            parts.append(f"=== {agent_id.upper()} OUTPUT ===\n{output}")
        return "\n\n".join(parts)
