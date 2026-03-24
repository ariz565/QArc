"""Framework adapter registry — mirrors frontend adapters.ts exactly.

Each framework defines its capabilities, browser support, and status.
The Automation Engineer agent uses this to generate framework-specific code.
"""

from __future__ import annotations

from app.models.settings import EnvironmentPreset, FrameworkConfig, Viewport

# ── Framework Registry (matches frontend FRAMEWORKS array) ──

FRAMEWORKS: list[FrameworkConfig] = [
    FrameworkConfig(
        id="playwright",
        name="Playwright",
        short_name="PW",
        color="#2EAD33",
        language="TypeScript",
        description="Modern end-to-end testing with auto-wait, multi-browser support, and native mobile emulation.",
        capabilities=["e2e", "component", "api", "visual", "mobile", "cross-browser", "parallel", "headless"],
        browser_support=["chromium", "firefox", "webkit"],
        status="active",
        docs="https://playwright.dev",
    ),
    FrameworkConfig(
        id="selenium",
        name="Selenium WebDriver",
        short_name="Se",
        color="#43B02A",
        language="Python",
        description="Industry-standard browser automation with the largest ecosystem and enterprise support.",
        capabilities=["e2e", "cross-browser", "parallel", "headless"],
        browser_support=["chromium", "firefox", "webkit", "edge"],
        status="active",
        docs="https://selenium.dev",
    ),
    FrameworkConfig(
        id="cypress",
        name="Cypress",
        short_name="Cy",
        color="#69D3A7",
        language="TypeScript",
        description="Developer-friendly testing with real-time reloads, time-travel debugging, and automatic waiting.",
        capabilities=["e2e", "component", "api", "visual", "headless"],
        browser_support=["chromium", "firefox", "edge"],
        status="active",
        docs="https://cypress.io",
    ),
    FrameworkConfig(
        id="appium",
        name="Appium",
        short_name="Ap",
        color="#662D91",
        language="Python",
        description="Cross-platform mobile testing for native, hybrid, and mobile web apps on iOS and Android.",
        capabilities=["e2e", "mobile", "cross-browser", "parallel"],
        browser_support=["chromium", "webkit"],
        status="available",
        docs="https://appium.io",
    ),
    FrameworkConfig(
        id="k6",
        name="k6 (Grafana)",
        short_name="k6",
        color="#7D64FF",
        language="JavaScript",
        description="Modern load testing with scripted scenarios, thresholds, and Grafana integration.",
        capabilities=["performance", "api"],
        browser_support=[],
        status="available",
        docs="https://k6.io",
    ),
    FrameworkConfig(
        id="axe-core",
        name="axe-core",
        short_name="axe",
        color="#4B83F0",
        language="TypeScript",
        description="Automated accessibility testing engine with WCAG 2.1 compliance checking.",
        capabilities=["accessibility", "e2e"],
        browser_support=["chromium", "firefox", "webkit"],
        status="available",
        docs="https://www.deque.com/axe/",
    ),
]

# ── Environment Presets (matches frontend ENVIRONMENTS array) ──

ENVIRONMENTS: list[EnvironmentPreset] = [
    EnvironmentPreset(id="desktop-chrome", label="Desktop Chrome", browser="chromium", viewport=Viewport(width=1920, height=1080), platform="Windows 11", enabled=True),
    EnvironmentPreset(id="desktop-firefox", label="Desktop Firefox", browser="firefox", viewport=Viewport(width=1920, height=1080), platform="Windows 11", enabled=True),
    EnvironmentPreset(id="desktop-safari", label="Desktop Safari", browser="webkit", viewport=Viewport(width=1920, height=1080), platform="macOS Sonoma", enabled=False),
    EnvironmentPreset(id="desktop-edge", label="Desktop Edge", browser="edge", viewport=Viewport(width=1920, height=1080), platform="Windows 11", enabled=False),
    EnvironmentPreset(id="tablet-ipad", label="iPad Pro", browser="webkit", viewport=Viewport(width=1024, height=1366), platform="iPadOS 17", enabled=True),
    EnvironmentPreset(id="mobile-iphone", label="iPhone 15 Pro", browser="webkit", viewport=Viewport(width=393, height=852), platform="iOS 17", enabled=False),
    EnvironmentPreset(id="mobile-pixel", label="Pixel 8", browser="chromium", viewport=Viewport(width=412, height=915), platform="Android 14", enabled=False),
]


def get_framework(framework_id: str) -> FrameworkConfig | None:
    return next((f for f in FRAMEWORKS if f.id == framework_id), None)


def get_active_frameworks() -> list[FrameworkConfig]:
    return [f for f in FRAMEWORKS if f.status == "active"]
