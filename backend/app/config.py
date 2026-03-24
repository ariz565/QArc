"""Environment-driven configuration using Pydantic Settings v2."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Server ──
    app_env: str = "development"
    app_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5190"]

    # ── LLM Provider Flags ──
    llm_default_provider: str = "mock"

    # Two-tier LLM strategy (like TradingAgents deep_think / quick_think)
    llm_deep_provider: str | None = None    # judges, critical decisions (falls back to default)
    llm_quick_provider: str | None = None   # workers, analysts (falls back to default)

    # Per-agent provider overrides (fall back to tier → default)
    agent_story_provider: str | None = None
    agent_strategy_provider: str | None = None
    agent_writer_provider: str | None = None
    agent_automation_provider: str | None = None
    agent_executor_provider: str | None = None
    agent_bug_provider: str | None = None
    agent_coverage_provider: str | None = None
    agent_critic_provider: str | None = None
    agent_advocate_provider: str | None = None
    agent_summarizer_provider: str | None = None

    # ── Debate Configuration ──
    debate_max_rounds: int = 3              # rounds per debate (Test Critic ↔ Writer)
    risk_debate_max_rounds: int = 2         # rounds for Bug Detective ↔ Quality Advocate
    debate_temperature: float = 0.8         # slightly creative for diverse arguments

    # ── LLM Retry / Fallback ──
    llm_max_retries: int = 3               # retry attempts per LLM call
    llm_retry_base_delay: float = 1.0      # base delay (seconds) for exponential backoff
    llm_fallback_providers: list[str] = []  # ordered fallback chain: ["anthropic", "openai", "ollama"]

    # ── Ollama ──
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # ── OpenAI ──
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"

    # ── Anthropic ──
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # ── Groq ──
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Google AI Studio (Gemini) ──
    google_api_key: str = ""
    google_model: str = "gemini-2.5-flash"

    # ── Azure OpenAI ──
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""       # https://<resource>.openai.azure.com
    azure_openai_deployment: str = ""      # deployment name
    azure_openai_api_version: str = "2024-12-01-preview"

    # ── AWS Bedrock ──
    bedrock_model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    bedrock_region: str = "us-east-1"
    bedrock_access_key: str = ""
    bedrock_secret_key: str = ""
    bedrock_profile: str = ""              # AWS CLI profile (alternative to keys)

    # ── Execution ──
    execution_parallel_workers: int = 4
    execution_timeout_ms: int = 30000
    execution_retries: int = 2
    execution_headless: bool = True

    # ── Database ──
    db_url: str = "sqlite+aiosqlite:///data/qa_nexus.db"

    # ── Workspace (generated files) ──
    workspace_dir: str = "./workspace"

    # ── Jira ──
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = ""

    # ── GitHub ──
    github_token: str = ""
    github_webhook_secret: str = ""

    # ── Slack ──
    slack_webhook_url: str = ""

    # ── Email / SMTP ──
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: list[str] = []

    # Agents that use deep_think tier (judges, critical decisions)
    DEEP_THINK_AGENTS: set[str] = {"coverage", "summarizer"}

    def provider_for_agent(self, agent_id: str) -> str:
        """Resolve which LLM provider an agent should use.

        Resolution order:
          1. Per-agent override (AGENT_{ID}_PROVIDER)
          2. Tier-based (deep_think for judges, quick_think for workers)
          3. Global default (LLM_DEFAULT_PROVIDER)
        """
        # 1. Explicit per-agent override
        override = getattr(self, f"agent_{agent_id}_provider", None)
        if override:
            return override

        # 2. Tier-based resolution
        if agent_id in self.DEEP_THINK_AGENTS:
            if self.llm_deep_provider:
                return self.llm_deep_provider
        else:
            if self.llm_quick_provider:
                return self.llm_quick_provider

        # 3. Global default
        return self.llm_default_provider


settings = Settings()
