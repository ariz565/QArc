"""WebSocket routes — real-time pipeline streaming.

Two WebSocket endpoints:
  /ws/pipeline/{execution_id} — agent outputs (streaming tokens)
  /ws/logs/{execution_id}     — structured log entries

Both subscribe to the event bus and forward events to connected clients.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import Event, EventType, event_bus

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/pipeline/{execution_id}")
async def ws_pipeline(websocket: WebSocket, execution_id: str) -> None:
    """Stream pipeline events (agent starts, tokens, completions) to the frontend."""
    await websocket.accept()
    queue = event_bus.subscribe(execution_id)

    try:
        while True:
            event: Event = await asyncio.wait_for(queue.get(), timeout=300.0)

            # Forward relevant events as JSON
            if event.type in {
                EventType.PIPELINE_STARTED,
                EventType.AGENT_STARTED,
                EventType.AGENT_CHUNK,
                EventType.AGENT_COMPLETED,
                EventType.PIPELINE_COMPLETED,
                EventType.PIPELINE_FAILED,
            }:
                await websocket.send_text(json.dumps({
                    "type": event.type.value,
                    "data": event.data,
                }))

            # Close on terminal events
            if event.type in {EventType.PIPELINE_COMPLETED, EventType.PIPELINE_FAILED}:
                break

    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        event_bus.unsubscribe(execution_id, queue)


@router.websocket("/ws/logs/{execution_id}")
async def ws_logs(websocket: WebSocket, execution_id: str) -> None:
    """Stream structured log entries during pipeline execution."""
    await websocket.accept()
    queue = event_bus.subscribe(execution_id)

    try:
        while True:
            event: Event = await asyncio.wait_for(queue.get(), timeout=300.0)

            if event.type == EventType.LOG:
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "data": event.data,
                }))

            # Also forward agent lifecycle events as logs
            if event.type == EventType.AGENT_STARTED:
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "data": {
                        "agentId": event.data.get("agentId", ""),
                        "message": f"▶ {event.data.get('agentName', 'Agent')} started",
                        "level": "info",
                    },
                }))

            if event.type == EventType.AGENT_COMPLETED:
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "data": {
                        "agentId": event.data.get("agentId", ""),
                        "message": f"✓ {event.data.get('agentId', 'Agent')} completed",
                        "level": "success",
                    },
                }))

            if event.type in {EventType.PIPELINE_COMPLETED, EventType.PIPELINE_FAILED}:
                level = "success" if event.type == EventType.PIPELINE_COMPLETED else "error"
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "data": {
                        "agentId": "pipeline",
                        "message": f"Pipeline {event.type.value}",
                        "level": level,
                    },
                }))
                break

    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        event_bus.unsubscribe(execution_id, queue)
