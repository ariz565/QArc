"""Provider Registry — plug-and-play LLM provider management.

Adapter pattern inspired by DeerFlow's model factory:
  1. Providers self-register by name
  2. Agents request a provider by flag → registry resolves
  3. Health checks run at startup + on-demand
"""

from __future__ import annotations

import structlog

from app.config import settings
from app.core import ProviderNotFoundError
from app.providers.base import LLMProvider
from app.providers.resilience import ResilientLLM

logger = structlog.get_logger()

# ── Registry ──
_providers: dict[str, LLMProvider] = {}


def register(name: str, provider: LLMProvider) -> None:
    """Register an LLM provider by name."""
    _providers[name] = provider
    logger.info("provider_registered", name=name)


def get(name: str) -> LLMProvider:
    """Get a registered provider by name. Raises if not found."""
    if name not in _providers:
        raise ProviderNotFoundError(name)
    return _providers[name]


def get_for_agent(agent_id: str) -> LLMProvider:
    """Resolve which provider an agent should use (per-agent override or default)."""
    provider_name = settings.provider_for_agent(agent_id)
    return get(provider_name)


def build_resilient(agent_id: str) -> ResilientLLM:
    """Build a ResilientLLM for an agent — primary + fallback chain + retry config."""
    primary = get_for_agent(agent_id)
    fallbacks = []
    for name in settings.llm_fallback_providers:
        if name in _providers and _providers[name] is not primary:
            fallbacks.append(_providers[name])
    return ResilientLLM(
        primary=primary,
        fallbacks=fallbacks,
        max_retries=settings.llm_max_retries,
        base_delay=settings.llm_retry_base_delay,
    )


def all_providers() -> dict[str, LLMProvider]:
    """Return all registered providers."""
    return dict(_providers)


def available_names() -> list[str]:
    """Return names of all registered providers."""
    return list(_providers.keys())


def initialize_providers() -> None:
    """Initialize and register all configured providers.

    Called once at app startup (lifespan).
    Only registers providers that have valid configuration.
    """
    from app.providers.mock import MockProvider

    # Mock is always available
    register("mock", MockProvider())

    # Ollama — local; register if URL is configured
    if settings.ollama_base_url:
        from app.providers.ollama import OllamaProvider

        register("ollama", OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        ))

    # OpenAI — register if API key is set
    if settings.openai_api_key:
        from app.providers.openai_provider import OpenAIProvider

        register("openai", OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url if settings.openai_base_url != "https://api.openai.com/v1" else None,
        ))

    # Anthropic — register if API key is set
    if settings.anthropic_api_key:
        from app.providers.anthropic_provider import AnthropicProvider

        register("anthropic", AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        ))

    # Groq — register if API key is set
    if settings.groq_api_key:
        from app.providers.groq_provider import GroqProvider

        register("groq", GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        ))

    # Google AI Studio (Gemini) — register if API key is set
    if settings.google_api_key:
        from app.providers.google_provider import GoogleAIProvider

        register("google", GoogleAIProvider(
            api_key=settings.google_api_key,
            model=settings.google_model,
        ))

    # Azure OpenAI — register if endpoint + key are set
    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        from app.providers.azure_openai_provider import AzureOpenAIProvider

        register("azure_openai", AzureOpenAIProvider(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
        ))

    # AWS Bedrock — register if credentials or profile are set
    if settings.bedrock_access_key or settings.bedrock_profile:
        from app.providers.bedrock_provider import BedrockProvider

        register("bedrock", BedrockProvider(
            model_id=settings.bedrock_model_id,
            region=settings.bedrock_region,
            access_key=settings.bedrock_access_key or None,
            secret_key=settings.bedrock_secret_key or None,
            profile=settings.bedrock_profile or None,
        ))

    logger.info("providers_initialized", count=len(_providers), names=available_names())
