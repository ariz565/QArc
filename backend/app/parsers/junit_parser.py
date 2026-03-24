"""JUnit XML parser — extract test results from standard JUnit XML reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

import structlog

logger = structlog.get_logger()


@dataclass
class JUnitTestCase:
    name: str
    classname: str
    time_seconds: float
    status: str  # "pass" | "fail" | "error" | "skip"
    message: str = ""
    stack_trace: str = ""


@dataclass
class JUnitReport:
    name: str
    tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    time_seconds: float
    test_cases: list[JUnitTestCase] = field(default_factory=list)


def parse_junit_xml(path: Path) -> JUnitReport:
    """
    Parse a JUnit XML file into a structured report.

    Handles both single <testsuite> and <testsuites> root elements.
    """
    if not path.exists():
        logger.warning("junit_file_not_found", path=str(path))
        return JUnitReport(name="", tests=0, passed=0, failed=0, errors=0, skipped=0, time_seconds=0)

    tree = ElementTree.parse(path)  # noqa: S314
    root = tree.getroot()

    # Handle <testsuites> wrapper
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    elif root.tag == "testsuite":
        suites = [root]
    else:
        logger.warning("unexpected_junit_root", tag=root.tag)
        return JUnitReport(name="", tests=0, passed=0, failed=0, errors=0, skipped=0, time_seconds=0)

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    all_cases: list[JUnitTestCase] = []

    for suite in suites:
        total_tests += int(suite.get("tests", "0"))
        total_failures += int(suite.get("failures", "0"))
        total_errors += int(suite.get("errors", "0"))
        total_skipped += int(suite.get("skipped", "0"))
        total_time += float(suite.get("time", "0"))

        for tc in suite.findall("testcase"):
            name = tc.get("name", "unknown")
            classname = tc.get("classname", "")
            time_s = float(tc.get("time", "0"))

            failure = tc.find("failure")
            error = tc.find("error")
            skip = tc.find("skipped")

            if failure is not None:
                status = "fail"
                message = failure.get("message", "")
                stack_trace = failure.text or ""
            elif error is not None:
                status = "error"
                message = error.get("message", "")
                stack_trace = error.text or ""
            elif skip is not None:
                status = "skip"
                message = skip.get("message", "")
                stack_trace = ""
            else:
                status = "pass"
                message = ""
                stack_trace = ""

            all_cases.append(JUnitTestCase(
                name=name,
                classname=classname,
                time_seconds=time_s,
                status=status,
                message=message,
                stack_trace=stack_trace,
            ))

    passed = total_tests - total_failures - total_errors - total_skipped

    report = JUnitReport(
        name=suites[0].get("name", "Test Suite") if suites else "Test Suite",
        tests=total_tests,
        passed=max(passed, 0),
        failed=total_failures,
        errors=total_errors,
        skipped=total_skipped,
        time_seconds=total_time,
        test_cases=all_cases,
    )

    logger.info(
        "junit_parsed",
        tests=report.tests,
        passed=report.passed,
        failed=report.failed,
        skipped=report.skipped,
    )
    return report
