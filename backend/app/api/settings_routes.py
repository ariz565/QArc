"""Settings routes — frameworks, environments, providers, execution config."""

from __future__ import annotations

from fastapi import APIRouter

from app.adapters.frameworks import ENVIRONMENTS, FRAMEWORKS
from app.config import settings
from app.models.settings import (
    EnvironmentPreset,
    ExecutionConfig,
    FrameworkConfig,
    LLMProviderInfo,
)
from app.providers import registry

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/frameworks", response_model=list[FrameworkConfig])
async def list_frameworks() -> list[FrameworkConfig]:
    """Get all supported test frameworks."""
    return FRAMEWORKS


@router.get("/environments", response_model=list[EnvironmentPreset])
async def list_environments() -> list[EnvironmentPreset]:
    """Get all environment presets."""
    return ENVIRONMENTS


@router.get("/execution", response_model=ExecutionConfig)
async def get_execution_config() -> ExecutionConfig:
    """Get current execution configuration."""
    return ExecutionConfig(
        parallel_workers=settings.execution_parallel_workers,
        timeout_ms=settings.execution_timeout_ms,
        retries=settings.execution_retries,
        headless=settings.execution_headless,
    )


@router.get("/providers", response_model=list[LLMProviderInfo])
async def list_providers() -> list[LLMProviderInfo]:
    """Get all configured LLM providers and their status."""
    providers_info = []
    all_cfg = [
        ("ollama", "Ollama (Local)", settings.ollama_model, settings.ollama_base_url),
        ("openai", "OpenAI", settings.openai_model, settings.openai_base_url),
        ("anthropic", "Anthropic", settings.anthropic_model, None),
        ("groq", "Groq", settings.groq_model, None),
        ("mock", "Mock (Demo)", "mock-model", None),
    ]
    registered = registry.available_names()
    for pid, name, model, base_url in all_cfg:
        if pid in registered:
            status = "connected"
        elif pid == "mock":
            status = "connected"
        else:
            status = "not-configured"
        providers_info.append(LLMProviderInfo(
            id=pid,
            name=name,
            status=status,
            model=model,
            base_url=base_url,
        ))
    return providers_info


@router.get("/providers/active")
async def get_active_provider() -> dict:
    """Get the currently active default LLM provider."""
    return {
        "default": settings.llm_default_provider,
        "registered": registry.available_names(),
    }
