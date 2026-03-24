"""Event bus — async pub/sub for real-time pipeline events.

Agents publish events → WebSocket handlers consume them.
Inspired by DeerFlow's SSE event-streaming architecture.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    AGENT_STARTED = "agent_started"
    AGENT_CHUNK = "agent_chunk"       # streaming token
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    LOG = "log"


@dataclass
class Event:
    type: EventType
    execution_id: str
    data: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """In-process async event bus.

    Each execution_id gets its own set of subscriber queues.
    WebSocket handlers subscribe; agents publish.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Event]]] = defaultdict(list)

    def subscribe(self, execution_id: str) -> asyncio.Queue[Event]:
        """Create a new subscriber queue for an execution."""
        queue: asyncio.Queue[Event] = asyncio.Queue()
        self._subscribers[execution_id].append(queue)
        return queue

    def unsubscribe(self, execution_id: str, queue: asyncio.Queue[Event]) -> None:
        """Remove a subscriber queue."""
        subs = self._subscribers.get(execution_id, [])
        if queue in subs:
            subs.remove(queue)
        if not subs:
            self._subscribers.pop(execution_id, None)

    async def publish(self, event: Event) -> None:
        """Broadcast an event to all subscribers of that execution."""
        for queue in self._subscribers.get(event.execution_id, []):
            await queue.put(event)

    async def publish_log(
        self,
        execution_id: str,
        agent_id: str,
        message: str,
        level: str = "info",
    ) -> None:
        """Convenience: publish a log event."""
        await self.publish(
            Event(
                type=EventType.LOG,
                execution_id=execution_id,
                data={"agentId": agent_id, "message": message, "level": level},
            )
        )

    def cleanup(self, execution_id: str) -> None:
        """Remove all subscribers for a finished execution."""
        self._subscribers.pop(execution_id, None)


# Singleton — imported by agents, orchestrator, and WS handlers
event_bus = EventBus()
