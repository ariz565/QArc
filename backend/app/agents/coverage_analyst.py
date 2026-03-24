"""Agent 7: Coverage Judge — independent judge using deep_think tier."""

from app.agents.base import BaseAgent


class CoverageAnalystAgent(BaseAgent):
    agent_id = "coverage"
    agent_name = "Coverage Judge"
    role = "Independent Verdict"
