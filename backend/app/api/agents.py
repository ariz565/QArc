"""Agent routes — definitions, health checks, provider info."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.models.agents import AgentDefinition, AgentHealth
from app.providers import registry

router = APIRouter(prefix="/agents", tags=["agents"])

# Agent definitions matching frontend AGENTS array
_AGENT_DEFS = [
    AgentDefinition(
        id="story", name="Story Analyzer", role="Requirement Intelligence",
        color="#22d3ee", icon="story", model="", description="Reads Jira stories and extracts requirements, edge cases, risks, and testable acceptance criteria",
    ),
    AgentDefinition(
        id="strategy", name="Test Strategist", role="Strategy & Planning",
        color="#fb923c", icon="strategy", model="", description="Determines optimal test types, priority matrix, and risk-based test allocation",
    ),
    AgentDefinition(
        id="writer", name="Test Case Writer", role="BDD Test Generation",
        color="#a78bfa", icon="writer", model="", description="Generates comprehensive BDD test cases with Given/When/Then scenarios",
    ),
    AgentDefinition(
        id="automation", name="Automation Engineer", role="Code Generation",
        color="#34d399", icon="automation", model="", description="Converts test cases into executable Playwright/Cypress automation code",
    ),
    AgentDefinition(
        id="executor", name="Test Executor", role="Execution Engine",
        color="#60a5fa", icon="executor", model="", description="Executes automated tests with parallel browser contexts and collects results",
    ),
    AgentDefinition(
        id="bug", name="Bug Detective", role="Failure Analysis",
        color="#fb7185", icon="bug", model="", description="Analyzes test failures, identifies root causes, and generates detailed bug reports",
    ),
    AgentDefinition(
        id="coverage", name="Coverage Analyst", role="Quality Insights",
        color="#fbbf24", icon="coverage", model="", description="Evaluates test coverage, identifies gaps, and provides go/no-go recommendations",
    ),
]


def _resolve_agent_model(agent_id: str) -> str:
    """Resolve the model name for display based on provider config."""
    provider_name = settings.provider_for_agent(agent_id)
    model_map = {
        "ollama": settings.ollama_model,
        "openai": settings.openai_model,
        "anthropic": settings.anthropic_model,
        "groq": settings.groq_model,
        "mock": "Mock (Demo)",
    }
    return model_map.get(provider_name, provider_name)


@router.get("", response_model=list[AgentDefinition])
async def list_agents() -> list[AgentDefinition]:
    """Get all agent definitions with resolved provider/model info."""
    result = []
    for agent in _AGENT_DEFS:
        provider_name = settings.provider_for_agent(agent.id)
        resolved = agent.model_copy(update={
            "model": _resolve_agent_model(agent.id),
            "provider": provider_name,
        })
        result.append(resolved)
    return result


@router.get("/health", response_model=list[AgentHealth])
async def check_agents_health() -> list[AgentHealth]:
    """Health check all agents' LLM providers."""
    results = []
    for agent in _AGENT_DEFS:
        provider_name = settings.provider_for_agent(agent.id)
        try:
            provider = registry.get(provider_name)
            is_healthy, latency = await provider.health_check()
            results.append(AgentHealth(
                agent_id=agent.id,
                provider=provider_name,
                model=_resolve_agent_model(agent.id),
                status="healthy" if is_healthy else "degraded",
                latency_ms=round(latency, 1),
            ))
        except Exception:
            results.append(AgentHealth(
                agent_id=agent.id,
                provider=provider_name,
                model=_resolve_agent_model(agent.id),
                status="unavailable",
            ))
    return results
