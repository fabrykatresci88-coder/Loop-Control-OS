from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class MarketingAgent(BaseAgent):
    """Agent responsible for marketing and go-to-market strategy."""

    def __init__(self) -> None:
        super().__init__(
            name="marketing",
            description="Generates marketing positioning, growth, and SEO guidance.",
            priority=60,
            capabilities={Capability.MARKETING, Capability.SEO},
        )
        self.marketing_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        idea = state.idea.lower()
        if "crm" in idea:
            self.marketing_strategy = "Focus on SMB channels, partnerships, and product-led growth."
        elif "ai" in idea or "machine learning" in idea:
            self.marketing_strategy = "Use case studies, developer outreach, and enterprise pilot programs."
        else:
            self.marketing_strategy = "Combine content marketing, SEO, and referral incentives."
        state.marketing = self.marketing_strategy

    def validate(self, state: ProjectState) -> bool:
        return bool(self.marketing_strategy)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "MARKETING REPORT",
            "",
            f"Marketing Strategy: {self.marketing_strategy}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
