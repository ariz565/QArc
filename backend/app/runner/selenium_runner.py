"""Pytest/Selenium test runner — runs generated Python Selenium tests."""

from __future__ import annotations

from pathlib import Path

import structlog

from app.runner.base import BaseRunner, RunResult
from app.runner.process_manager import ProcessManager

logger = structlog.get_logger()

CONFTEST = '''
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def browser(request):
    """Create browser instance."""
    options = Options()
    if request.config.getoption("--headless", default=True):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
'''

REQUIREMENTS = """
pytest>=8.0
pytest-html
selenium>=4.20
webdriver-manager
"""


class SeleniumRunner(BaseRunner):
    framework_id = "selenium"
    framework_name = "Selenium WebDriver"

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url

    async def setup(self, workspace: Path) -> None:
        """Install Python test dependencies."""
        req_file = workspace / "requirements.txt"
        req_file.write_text(REQUIREMENTS.strip(), encoding="utf-8")

        # Write conftest.py
        (workspace / "tests" / "conftest.py").write_text(CONFTEST.strip(), encoding="utf-8")

        result = await ProcessManager.run(
            ["pip", "install", "-r", "requirements.txt", "-q"],
            cwd=str(workspace),
            timeout_seconds=120,
        )
        if result.exit_code != 0:
            logger.warning("pip_install_failed", stderr=result.stderr[:500])

    async def run(
        self,
        workspace: Path,
        test_file: str,
        *,
        headless: bool = True,
        timeout_ms: int = 30000,
        retries: int = 0,
    ) -> RunResult:
        """Execute pytest with JUnit XML output."""
        cmd = [
            "python", "-m", "pytest",
            f"tests/{test_file}",
            f"--junitxml=results/junit.xml",
            f"--timeout={timeout_ms // 1000}",
            "-v",
        ]
        if headless:
            cmd.append("--headless")

        result = await ProcessManager.run(
            cmd,
            cwd=str(workspace),
            timeout_seconds=timeout_ms // 1000 + 30,
        )

        # Parse JUnit XML
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
            from app.parsers.console_parser import parse_pytest_output

            parsed = parse_pytest_output(result.stdout)
            passed = parsed.get("passed", 0)
            failed = parsed.get("failed", 0)
            skipped = parsed.get("skipped", 0)

        return RunResult(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            report_path=report_path,
            passed=passed,
            failed=failed,
            skipped=skipped,
        )

    async def cleanup(self, workspace: Path) -> None:
        import shutil

        for d in ["__pycache__", ".pytest_cache"]:
            p = workspace / d
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
