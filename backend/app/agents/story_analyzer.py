"""Agent 1: Story Analyzer — Requirements extraction."""

from app.agents.base import BaseAgent


class StoryAnalyzerAgent(BaseAgent):
    agent_id = "story"
    agent_name = "Story Analyzer"
    role = "Requirement Intelligence"
