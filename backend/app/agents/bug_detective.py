"""Agent 6: Bug Detective — Failure root-cause analysis."""

from app.agents.base import BaseAgent


class BugDetectiveAgent(BaseAgent):
    agent_id = "bug"
    agent_name = "Bug Detective"
    role = "Failure Analysis"
