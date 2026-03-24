"""Agent 3b: Test Critic — adversarial debate partner for Test Case Writer."""

from app.agents.base import BaseAgent


class TestCriticAgent(BaseAgent):
    agent_id = "critic"
    agent_name = "Test Critic"
    role = "Adversarial Test Review"
