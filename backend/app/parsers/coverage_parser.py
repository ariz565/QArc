"""Coverage report parser — extract coverage percentages from various formats."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger()


@dataclass
class CoverageData:
    """Parsed coverage metrics."""

    lines: float = 0.0
    branches: float = 0.0
    functions: float = 0.0
    statements: float = 0.0
    overall: float = 0.0


def parse_istanbul_json(path: Path) -> CoverageData:
    """
    Parse Istanbul/NYC JSON coverage summary.

    Expects format:
    {
      "total": {
        "lines": { "pct": 85.5 },
        "branches": { "pct": 72.0 },
        "functions": { "pct": 90.0 },
        "statements": { "pct": 85.0 }
      }
    }
    """
    if not path.exists():
        return CoverageData()

    data = json.loads(path.read_text(encoding="utf-8"))
    total = data.get("total", {})

    lines = total.get("lines", {}).get("pct", 0)
    branches = total.get("branches", {}).get("pct", 0)
    functions = total.get("functions", {}).get("pct", 0)
    statements = total.get("statements", {}).get("pct", 0)
    overall = (lines + branches + functions + statements) / 4

    result = CoverageData(
        lines=lines,
        branches=branches,
        functions=functions,
        statements=statements,
        overall=round(overall, 1),
    )
    logger.info("istanbul_coverage_parsed", overall=result.overall)
    return result


def parse_coverage_text(stdout: str) -> CoverageData:
    """
    Parse text-based coverage output from various tools.

    Matches patterns like:
      "Statements   : 85.5%"
      "Branches     : 72.0%"
      "Lines        : 85.0%"
      "All files    |   85.5 |   72.0 |   90.0 |   85.0 |"
    """
    data = CoverageData()

    # Istanbul text table format
    stmts = re.search(r"Stmts\s*\|\s*([\d.]+)", stdout)
    branch = re.search(r"Branch\s*\|\s*([\d.]+)", stdout)
    funcs = re.search(r"Funcs\s*\|\s*([\d.]+)", stdout)
    lines = re.search(r"Lines\s*\|\s*([\d.]+)", stdout)

    if stmts:
        data.statements = float(stmts.group(1))
    if branch:
        data.branches = float(branch.group(1))
    if funcs:
        data.functions = float(funcs.group(1))
    if lines:
        data.lines = float(lines.group(1))

    # Fallback: "Coverage: 85.5%"
    if not any([stmts, branch, funcs, lines]):
        overall = re.search(r"[Cc]overage[:\s]+([\d.]+)%", stdout)
        if overall:
            data.overall = float(overall.group(1))
            data.lines = data.overall
            data.statements = data.overall

    if data.overall == 0 and data.lines > 0:
        data.overall = round(
            (data.lines + data.branches + data.functions + data.statements) / 4,
            1,
        )

    return data


def parse_pytest_coverage(stdout: str) -> CoverageData:
    """
    Parse pytest-cov output.

    Matches:
      "TOTAL    1234   123    90%"
    """
    data = CoverageData()

    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
    if match:
        data.overall = float(match.group(1))
        data.lines = data.overall
        data.statements = data.overall

    return data
