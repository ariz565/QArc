"""Agent 6b: Quality Advocate — optimistic debate partner for Bug Detective."""

from app.agents.base import BaseAgent


class QualityAdvocateAgent(BaseAgent):
    agent_id = "advocate"
    agent_name = "Quality Advocate"
    role = "Optimistic Quality Defense"
