"""Agent schemas — maps to frontend AgentDef / AgentOutput interfaces."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.models.test_cases import TestCase


class AgentDefinition(BaseModel):
    id: str
    name: str
    role: str
    color: str
    icon: str
    model: str
    description: str
    provider: str | None = None  # resolved at runtime


class ExecutionResult(BaseModel):
    id: str
    status: Literal["pass", "fail"]
    duration: str
    error: str | None = None


class AgentOutput(BaseModel):
    agent_id: str
    content: str
    test_cases: list[TestCase] | None = None
    automation_code: str | None = None
    execution_results: list[ExecutionResult] | None = None


class AgentHealth(BaseModel):
    agent_id: str
    provider: str
    model: str
    status: Literal["healthy", "degraded", "unavailable"]
    latency_ms: float | None = None
