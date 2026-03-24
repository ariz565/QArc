"""Settings schemas — frameworks, environments, connections."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


FrameworkCapability = Literal[
    "e2e", "component", "api", "visual", "accessibility",
    "performance", "mobile", "cross-browser", "parallel", "headless",
]
BrowserType = Literal["chromium", "firefox", "webkit", "edge"]


class FrameworkConfig(BaseModel):
    id: str
    name: str
    short_name: str
    color: str
    language: str
    description: str
    capabilities: list[FrameworkCapability]
    browser_support: list[BrowserType]
    status: Literal["active", "available", "coming-soon"]
    docs: str


class Viewport(BaseModel):
    width: int
    height: int


class EnvironmentPreset(BaseModel):
    id: str
    label: str
    browser: BrowserType
    viewport: Viewport
    platform: str
    enabled: bool = True


class ExecutionConfig(BaseModel):
    parallel_workers: int = 4
    timeout_ms: int = 30000
    retries: int = 2
    headless: bool = True
    screenshots_on_failure: bool = True
    video_on_failure: bool = False
    base_url: str = "http://localhost:3000"


class LLMProviderInfo(BaseModel):
    id: str
    name: str
    status: Literal["connected", "disconnected", "not-configured"]
    model: str
    base_url: str | None = None
