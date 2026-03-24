"""Console output parser — extract test results from CLI stdout."""

from __future__ import annotations

import re

import structlog

logger = structlog.get_logger()


def parse_playwright_output(stdout: str) -> dict[str, int]:
    """
    Parse Playwright test runner stdout for pass/fail/skip counts.

    Matches patterns like:
      "5 passed"
      "2 failed"
      "1 skipped"
    """
    counts = {"passed": 0, "failed": 0, "skipped": 0}

    # Playwright summary line: "  5 passed (3.2s)"
    for key in counts:
        match = re.search(rf"(\d+)\s+{key}", stdout)
        if match:
            counts[key] = int(match.group(1))

    logger.debug("playwright_parsed", **counts)
    return counts


def parse_pytest_output(stdout: str) -> dict[str, int]:
    """
    Parse pytest stdout for pass/fail/skip counts.

    Matches patterns like:
      "====== 5 passed, 2 failed, 1 skipped in 3.45s ======"
      "PASSED" / "FAILED" / "SKIPPED" per test
    """
    counts = {"passed": 0, "failed": 0, "skipped": 0}

    # Summary line
    summary = re.search(
        r"=+\s*(.*?)\s*in\s+[\d.]+s\s*=+",
        stdout,
    )
    if summary:
        text = summary.group(1)
        for key in counts:
            match = re.search(rf"(\d+)\s+{key}", text)
            if match:
                counts[key] = int(match.group(1))
    else:
        # Fallback: count individual PASSED/FAILED/SKIPPED
        counts["passed"] = stdout.count(" PASSED")
        counts["failed"] = stdout.count(" FAILED")
        counts["skipped"] = stdout.count(" SKIPPED")

    logger.debug("pytest_parsed", **counts)
    return counts


def parse_cypress_output(stdout: str) -> dict[str, int]:
    """
    Parse Cypress test runner stdout for pass/fail/skip counts.

    Matches:
      "Tests:  4"
      "Passing:  3"
      "Failing:  1"
      "Pending:  0"
    """
    counts = {"passed": 0, "failed": 0, "skipped": 0}

    passing = re.search(r"Passing:\s*(\d+)", stdout)
    failing = re.search(r"Failing:\s*(\d+)", stdout)
    pending = re.search(r"Pending:\s*(\d+)", stdout)

    if passing:
        counts["passed"] = int(passing.group(1))
    if failing:
        counts["failed"] = int(failing.group(1))
    if pending:
        counts["skipped"] = int(pending.group(1))

    logger.debug("cypress_parsed", **counts)
    return counts
