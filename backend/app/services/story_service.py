"""Story service — manages Jira stories (in-memory for demo, pluggable to real Jira)."""

from __future__ import annotations

from app.core import StoryNotFoundError
from app.models.stories import JiraStory

# ── In-memory story store (seed data matches frontend mock.ts) ──
_stories: dict[str, JiraStory] = {}


def _seed_stories() -> None:
    """Seed demo stories matching the frontend mock data."""
    seeds = [
        JiraStory(
            id="PROJ-1042",
            title="User Authentication with OAuth2",
            description=(
                "As a user, I want to log in using my Google or GitHub account so that "
                "I don't need to remember separate credentials. The system should redirect "
                "to the OAuth provider, receive the callback token, validate the JWT, "
                "create or update the user profile, and establish a secure session with "
                "httpOnly cookies."
            ),
            priority="High",
            labels=["auth", "security", "oauth"],
            story_points=8,
            sprint="Sprint 23",
            acceptance=[
                "Given valid OAuth credentials, user is redirected to dashboard within 2 seconds",
                "Given invalid or expired token, user sees clear error and retry option",
                "Given new user, profile is auto-created from OAuth provider data",
                "Session expires after 24 hours of inactivity",
                "Concurrent sessions from different devices are supported",
            ],
        ),
        JiraStory(
            id="PROJ-1043",
            title="Shopping Cart Checkout Flow",
            description=(
                "As a shopper, I want to complete purchase of items in my cart, including "
                "applying discount codes, selecting shipping method, entering payment via "
                "Stripe, and receiving order confirmation email with tracking link."
            ),
            priority="Critical",
            labels=["payments", "cart", "stripe"],
            story_points=13,
            sprint="Sprint 23",
            acceptance=[
                "Valid discount codes reduce total price correctly",
                "Invalid discount codes show clear error without clearing cart",
                "Stripe payment succeeds and order record is created",
                "Failed payment shows retry option and preserves cart state",
                "Order confirmation email with tracking sent within 60 seconds",
            ],
        ),
        JiraStory(
            id="PROJ-1044",
            title="Real-time Notifications System",
            description=(
                "As a user, I want to receive instant notifications for mentions, task "
                "assignments, and system alerts via WebSocket connection, with the ability "
                "to mark as read, filter by type, and configure notification preferences "
                "per category."
            ),
            priority="Medium",
            labels=["websocket", "notifications", "realtime"],
            story_points=5,
            sprint="Sprint 24",
            acceptance=[
                "Notifications appear within 500ms of triggering event",
                "Badge count updates in real-time across all open tabs",
                "Mark all as read clears badge count instantly",
                "Notification filter preferences persist across sessions",
            ],
        ),
    ]
    for story in seeds:
        _stories[story.id] = story


# Initialize on import
_seed_stories()


def list_stories() -> list[JiraStory]:
    return list(_stories.values())


def get_story(story_id: str) -> JiraStory:
    if story_id not in _stories:
        raise StoryNotFoundError(story_id)
    return _stories[story_id]


def create_story(story: JiraStory) -> JiraStory:
    _stories[story.id] = story
    return story
