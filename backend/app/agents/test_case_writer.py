"""Agent 3: Test Case Writer — BDD scenario generation."""

from app.agents.base import BaseAgent


class TestCaseWriterAgent(BaseAgent):
    agent_id = "writer"
    agent_name = "Test Case Writer"
    role = "BDD Test Generation"
