"""GitHub webhook API — receive push/PR events and trigger pipelines."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Header, Request
import structlog

from app.integrations.github.webhook import (
    parse_pull_request_event,
    parse_push_event,
    should_trigger_pipeline,
    verify_signature,
)
from app.models.webhooks import WebhookTriggerResponse
from app.orchestrator.pipeline import run_pipeline
from app.orchestrator.state import PipelineState
from app.services import story_service, execution_service

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/github", response_model=WebhookTriggerResponse)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=""),
) -> WebhookTriggerResponse:
    """
    Receive GitHub webhook events.
    Triggers QA pipeline on push to main/develop or PR opened/updated.
    """
    body = await request.body()

    # Verify signature
    if x_hub_signature_256 and not verify_signature(body, x_hub_signature_256):
        return WebhookTriggerResponse(triggered=False, reason="Invalid signature")

    payload = await request.json()

    # Parse event
    if x_github_event == "push":
        event = parse_push_event(payload)
    elif x_github_event == "pull_request":
        event = parse_pull_request_event(payload)
    else:
        return WebhookTriggerResponse(
            triggered=False,
            reason=f"Unsupported event type: {x_github_event}",
        )

    logger.info(
        "webhook_received",
        event=event.event_type,
        action=event.action,
        repo=event.repo_name,
        branch=event.branch,
    )

    if not should_trigger_pipeline(event):
        return WebhookTriggerResponse(
            triggered=False,
            reason=f"Event {event.event_type}/{event.action} on {event.branch} does not trigger pipeline",
        )

    # Find a story to test (use the first available)
    stories = story_service.list_stories()
    if not stories:
        return WebhookTriggerResponse(triggered=False, reason="No stories available")

    story = stories[0]
    execution_id = f"ci-{uuid4().hex[:8]}"

    state = PipelineState(
        execution_id=execution_id,
        story_id=story.id,
        framework="playwright",
    )
    execution_service.store_state(state)

    async def _run():
        result_state = await run_pipeline(state, story)
        execution_service.save_execution(result_state, story.title)

        # Post results to PR if applicable
        if event.pr_number:
            from app.integrations.github.pr_commenter import GitHubCommenter

            commenter = GitHubCommenter()
            if commenter.is_configured:
                await commenter.post_results_comment(
                    repo=event.repo_name,
                    pr_number=event.pr_number,
                    execution_id=execution_id,
                    passed=result_state.tests_passed,
                    failed=result_state.tests_failed,
                    skipped=result_state.tests_skipped,
                    coverage=result_state.coverage_percent,
                    verdict=result_state.verdict,
                )

    background_tasks.add_task(_run)

    return WebhookTriggerResponse(
        triggered=True,
        execution_id=execution_id,
        reason=f"Pipeline triggered by {event.event_type} on {event.branch}",
    )
