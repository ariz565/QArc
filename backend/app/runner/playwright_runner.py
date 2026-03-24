"""Playwright test runner — runs generated Playwright TypeScript tests."""

from __future__ import annotations

from pathlib import Path

import structlog

from app.runner.base import BaseRunner, RunResult
from app.runner.process_manager import ProcessManager

logger = structlog.get_logger()

# Minimal playwright.config.ts for sandboxed execution
PLAYWRIGHT_CONFIG = """
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: %(timeout_ms)d,
  retries: %(retries)d,
  reporter: [['junit', { outputFile: 'results/junit.xml' }], ['html', { open: 'never' }]],
  use: {
    headless: %(headless)s,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    baseURL: '%(base_url)s',
  },
  outputDir: './artifacts',
});
"""

PACKAGE_JSON = """{
  "name": "qa-nexus-test-run",
  "private": true,
  "devDependencies": {
    "@playwright/test": "^1.50.0"
  }
}
"""


class PlaywrightRunner(BaseRunner):
    framework_id = "playwright"
    framework_name = "Playwright"

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url

    async def setup(self, workspace: Path) -> None:
        """Install Playwright and browsers in the sandbox."""
        # Write package.json
        (workspace / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")

        # npm install
        result = await ProcessManager.run(
            ["npm", "install", "--no-audit", "--no-fund"],
            cwd=str(workspace),
            timeout_seconds=120,
        )
        if result.exit_code != 0:
            logger.warning("npm_install_failed", stderr=result.stderr[:500])

        # Install browsers
        result = await ProcessManager.run(
            ["npx", "playwright", "install", "chromium"],
            cwd=str(workspace),
            timeout_seconds=180,
        )
        if result.exit_code != 0:
            logger.warning("browser_install_failed", stderr=result.stderr[:500])

    async def run(
        self,
        workspace: Path,
        test_file: str,
        *,
        headless: bool = True,
        timeout_ms: int = 30000,
        retries: int = 0,
    ) -> RunResult:
        """Execute Playwright tests and return parsed results."""

        # Write config
        config_content = PLAYWRIGHT_CONFIG % {
            "timeout_ms": timeout_ms,
            "retries": retries,
            "headless": "true" if headless else "false",
            "base_url": self.base_url,
        }
        (workspace / "playwright.config.ts").write_text(config_content, encoding="utf-8")

        # Run tests
        result = await ProcessManager.run(
            ["npx", "playwright", "test", f"tests/{test_file}", "--config=playwright.config.ts"],
            cwd=str(workspace),
            timeout_seconds=timeout_ms // 1000 + 30,
        )

        # Parse JUnit XML if generated
        junit_path = workspace / "results" / "junit.xml"
        report_path = junit_path if junit_path.exists() else None

        passed = failed = skipped = 0
        if report_path:
            from app.parsers.junit_parser import parse_junit_xml

            parsed = parse_junit_xml(report_path)
            passed = parsed.passed
            failed = parsed.failed
            skipped = parsed.skipped
        else:
            # Fallback: parse stdout
            from app.parsers.console_parser import parse_playwright_output

            parsed = parse_playwright_output(result.stdout)
            passed = parsed.get("passed", 0)
            failed = parsed.get("failed", 0)
            skipped = parsed.get("skipped", 0)

        # Collect artifacts
        artifacts_dir = workspace / "artifacts"
        artifacts = list(artifacts_dir.rglob("*")) if artifacts_dir.exists() else []
        artifact_files = [f for f in artifacts if f.is_file()]

        return RunResult(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            report_path=report_path,
            passed=passed,
            failed=failed,
            skipped=skipped,
            artifacts=artifact_files,
        )

    async def cleanup(self, workspace: Path) -> None:
        """Clean up node_modules and build artifacts."""
        import shutil

        for d in ["node_modules", ".cache"]:
            p = workspace / d
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
