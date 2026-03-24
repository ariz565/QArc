"""Agent 5: Test Executor — Parallel test execution engine."""

from app.agents.base import BaseAgent


class TestExecutorAgent(BaseAgent):
    agent_id = "executor"
    agent_name = "Test Executor"
    role = "Execution Engine"
