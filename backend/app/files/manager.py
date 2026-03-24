"""File manager — save generated test suites, reports, and artifacts to disk."""

from __future__ import annotations

import re
from pathlib import Path

import structlog

from app.config import settings

logger = structlog.get_logger()


class FileManager:
    """
    Manages the output workspace where generated test files are persisted.

    Workspace layout:
        {workspace_root}/
        ├── {story_id}/
        │   ├── test-cases/
        │   │   └── test_cases.md
        │   ├── automation/
        │   │   ├── playwright/
        │   │   │   └── test_auth.spec.ts
        │   │   └── selenium/
        │   │       └── test_auth.py
        │   ├── reports/
        │   │   ├── junit.xml
        │   │   ├── coverage.json
        │   │   └── quality_report.md
        │   └── bugs/
        │       └── bug_report.md
    """

    def __init__(self, workspace_root: Path | None = None):
        self._root = workspace_root or Path(settings.workspace_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def story_dir(self, story_id: str) -> Path:
        """Get or create the directory for a story."""
        safe_id = self._sanitize(story_id)
        d = self._root / safe_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_test_cases(self, story_id: str, content: str) -> Path:
        """Save generated test case markdown."""
        d = self.story_dir(story_id) / "test-cases"
        d.mkdir(exist_ok=True)
        path = d / "test_cases.md"
        path.write_text(content, encoding="utf-8")
        logger.info("file_saved", type="test_cases", path=str(path))
        return path

    def save_automation_code(
        self, story_id: str, framework: str, filename: str, code: str
    ) -> Path:
        """Save generated automation test code."""
        d = self.story_dir(story_id) / "automation" / framework
        d.mkdir(parents=True, exist_ok=True)
        path = d / filename
        path.write_text(code, encoding="utf-8")
        logger.info("file_saved", type="automation", framework=framework, path=str(path))
        return path

    def save_report(self, story_id: str, filename: str, content: str | bytes) -> Path:
        """Save a report file (markdown, XML, JSON)."""
        d = self.story_dir(story_id) / "reports"
        d.mkdir(exist_ok=True)
        path = d / filename
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        logger.info("file_saved", type="report", path=str(path))
        return path

    def save_bug_report(self, story_id: str, content: str) -> Path:
        """Save bug detective output."""
        d = self.story_dir(story_id) / "bugs"
        d.mkdir(exist_ok=True)
        path = d / "bug_report.md"
        path.write_text(content, encoding="utf-8")
        logger.info("file_saved", type="bug_report", path=str(path))
        return path

    def save_analysis(self, story_id: str, agent_id: str, content: str) -> Path:
        """Save any agent's analysis output as markdown."""
        d = self.story_dir(story_id) / "analysis"
        d.mkdir(exist_ok=True)
        path = d / f"{agent_id}_output.md"
        path.write_text(content, encoding="utf-8")
        return path

    def save_artifact(self, story_id: str, execution_id: str, filename: str, data: bytes) -> Path:
        """Save a binary artifact (screenshot, video, trace)."""
        d = self.story_dir(story_id) / "artifacts" / execution_id
        d.mkdir(parents=True, exist_ok=True)
        path = d / filename
        path.write_bytes(data)
        logger.info("artifact_saved", path=str(path), size=len(data))
        return path

    def list_story_files(self, story_id: str) -> list[dict[str, str]]:
        """List all files for a story with relative paths."""
        d = self.story_dir(story_id)
        files = []
        for f in d.rglob("*"):
            if f.is_file():
                files.append({
                    "path": str(f.relative_to(self._root)),
                    "name": f.name,
                    "size": str(f.stat().st_size),
                    "type": self._classify_file(f),
                })
        return files

    def read_file(self, relative_path: str) -> str:
        """Read a file by its relative path within the workspace."""
        path = self._root / relative_path
        if not path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        # Ensure we don't escape the workspace (raises ValueError on traversal)
        try:
            path.resolve().relative_to(self._root.resolve())
        except ValueError:
            raise PermissionError(f"Access denied: path escapes workspace")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def extract_code_from_agent_output(output: str, framework: str) -> tuple[str, str]:
        """
        Extract code blocks from LLM agent output.

        Returns: (filename, code)
        """
        # Try to find fenced code blocks
        blocks = re.findall(r"```(?:\w+)?\n(.*?)```", output, re.DOTALL)
        if not blocks:
            return "", ""

        code = blocks[0].strip()

        # Determine filename based on framework
        ext_map = {
            "playwright": (".spec.ts", "test_generated.spec.ts"),
            "cypress": (".cy.ts", "test_generated.cy.ts"),
            "selenium": (".py", "test_generated.py"),
            "appium": (".py", "test_generated.py"),
        }
        _, default_name = ext_map.get(framework, (".txt", "test_generated.txt"))

        return default_name, code

    @staticmethod
    def _sanitize(name: str) -> str:
        """Sanitize a string for use as a directory name."""
        return re.sub(r"[^\w\-.]", "_", name)

    @staticmethod
    def _classify_file(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in (".ts", ".js", ".py"):
            return "code"
        if suffix in (".md", ".txt"):
            return "document"
        if suffix in (".xml", ".json", ".html"):
            return "report"
        if suffix in (".png", ".jpg", ".webp"):
            return "screenshot"
        if suffix in (".webm", ".mp4"):
            return "video"
        return "other"
