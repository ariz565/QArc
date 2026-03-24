"""Base agent — all 7 QA agents inherit from this.

Each agent:
  1. Loads its system prompt from prompts/ directory
  2. Resolves its LLM provider from the registry
  3. Exposes run() for full response and stream() for real-time output
  4. Publishes events to the event bus during execution
"""

from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

from app.core.events import Event, EventType, event_bus
from app.providers.base import LLMMessage
from app.providers.registry import build_resilient, get_for_agent

PROMPTS_DIR = Path(__file__).parent / "prompts"


class BaseAgent:
    agent_id: str = ""
    agent_name: str = ""
    role: str = ""

    def __init__(self) -> None:
        self._system_prompt: str | None = None

    @property
    def system_prompt(self) -> str:
        """Lazy-load the system prompt from the markdown file."""
        if self._system_prompt is None:
            prompt_file = PROMPTS_DIR / f"{self.agent_id}.md"
            if prompt_file.exists():
                self._system_prompt = prompt_file.read_text(encoding="utf-8")
            else:
                self._system_prompt = f"You are the {self.agent_name}. {self.role}."
        return self._system_prompt

    def build_messages(self, user_input: str, context: str = "") -> list[LLMMessage]:
        """Build the message list for the LLM call."""
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if context:
            messages.append(LLMMessage(role="user", content=f"Context from previous agents:\n{context}"))
        messages.append(LLMMessage(role="user", content=user_input))
        return messages

    async def run(self, user_input: str, context: str = "") -> str:
        """Execute the agent and return the full response (with retry/fallback)."""
        resilient = build_resilient(self.agent_id)
        messages = self.build_messages(user_input, context)
        response = await resilient.generate(messages, agent_id=self.agent_id)
        return response.content

    async def stream(
        self,
        user_input: str,
        context: str = "",
        execution_id: str = "",
    ) -> AsyncIterator[str]:
        """Stream the agent's response token-by-token, publishing events."""
        resilient = build_resilient(self.agent_id)
        messages = self.build_messages(user_input, context)

        # Notify: agent started
        if execution_id:
            await event_bus.publish(Event(
                type=EventType.AGENT_STARTED,
                execution_id=execution_id,
                data={"agentId": self.agent_id, "agentName": self.agent_name},
            ))
            await event_bus.publish_log(
                execution_id, self.agent_id,
                f"▶ {self.agent_name} started",
                "info",
            )

        full_content = ""
        async for token in resilient.stream(messages, agent_id=self.agent_id):
            full_content += token
            if execution_id:
                await event_bus.publish(Event(
                    type=EventType.AGENT_CHUNK,
                    execution_id=execution_id,
                    data={"agentId": self.agent_id, "token": token},
                ))
            yield token

        # Notify: agent completed
        if execution_id:
            await event_bus.publish(Event(
                type=EventType.AGENT_COMPLETED,
                execution_id=execution_id,
                data={"agentId": self.agent_id, "content": full_content},
            ))
            await event_bus.publish_log(
                execution_id, self.agent_id,
                f"✓ {self.agent_name} completed",
                "success",
            )
