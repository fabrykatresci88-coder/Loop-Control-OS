from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class SalesAgent(BaseAgent):
    """Agent responsible for sales strategy and revenue model guidance."""

    def __init__(self) -> None:
        super().__init__(
            name="sales",
            description="Recommends sales channels and monetization strategy.",
            priority=70,
            capabilities={Capability.SALES},
        )
        self.sales_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        idea = state.idea.lower()
        if "crm" in idea:
            self.sales_strategy = "Sell to SMBs through direct sales and channel partners."
        elif "ai" in idea or "machine learning" in idea:
            self.sales_strategy = "Sell to enterprises through pilots, proof of concepts, and account-based marketing."
        else:
            self.sales_strategy = "Sell through online self-service and a freemium funnel."
        state.sales = self.sales_strategy

    def validate(self, state: ProjectState) -> bool:
        return bool(self.sales_strategy)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "SALES REPORT",
            "",
            f"Sales Strategy: {self.sales_strategy}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
