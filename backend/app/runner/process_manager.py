"""Subprocess manager — async process execution with timeout and streaming."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()


@dataclass
class ProcessOutput:
    """Output from a completed subprocess."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False


class ProcessManager:
    """Run subprocesses with timeout, output capture, and streaming callbacks."""

    @staticmethod
    async def run(
        cmd: list[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout_seconds: int = 120,
        on_stdout: asyncio.coroutines | None = None,
        on_stderr: asyncio.coroutines | None = None,
    ) -> ProcessOutput:
        """
        Execute a command asynchronously.

        Args:
            cmd: Command and arguments.
            cwd: Working directory.
            env: Environment variables (merged with system env).
            timeout_seconds: Max execution time.
            on_stdout: Async callback for each stdout line.
            on_stderr: Async callback for each stderr line.
        """
        import os

        merged_env = {**os.environ}
        if env:
            merged_env.update(env)

        logger.info("process_start", cmd=" ".join(cmd), cwd=cwd)
        start = time.perf_counter()

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=merged_env,
        )

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        async def _read_stream(stream, lines_buf, callback):
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").rstrip("\n")
                lines_buf.append(text)
                if callback:
                    await callback(text)

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    _read_stream(proc.stdout, stdout_lines, on_stdout),
                    _read_stream(proc.stderr, stderr_lines, on_stderr),
                    proc.wait(),
                ),
                timeout=timeout_seconds,
            )
            timed_out = False
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            timed_out = True
            logger.warning("process_timeout", cmd=" ".join(cmd), timeout=timeout_seconds)

        elapsed = int((time.perf_counter() - start) * 1000)

        output = ProcessOutput(
            exit_code=proc.returncode or -1,
            stdout="\n".join(stdout_lines),
            stderr="\n".join(stderr_lines),
            duration_ms=elapsed,
            timed_out=timed_out,
        )

        logger.info(
            "process_done",
            cmd=" ".join(cmd),
            exit_code=output.exit_code,
            duration_ms=elapsed,
            timed_out=timed_out,
        )
        return output
