from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class BusinessAgent(BaseAgent):
    """Agent responsible for evaluating the business value of a startup idea."""

    def __init__(self) -> None:
        super().__init__(
            name="business",
            description="Analyzes market opportunity, competition, target customer, and pricing.",
            priority=20,
            capabilities={Capability.BUSINESS_ANALYSIS, Capability.COMPETITOR_ANALYSIS, Capability.MARKETING},
        )
        self.market_size = ""
        self.competition = ""
        self.target_customer = ""
        self.business_potential = ""
        self.pricing_strategy = ""
        self.recommended_mvp = ""
        self.growth_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        idea = state.idea.lower()
        if "crm" in idea:
            self.market_size = "Large"
            self.competition = "Medium"
            self.business_potential = "High"
            self.pricing_strategy = "SaaS Subscription"
            self.target_customer = "SMBs that need customer relationship management."
        elif "ai" in idea or "machine learning" in idea:
            self.market_size = "Very Large"
            self.competition = "High"
            self.business_potential = "Very High"
            self.pricing_strategy = "Usage-based SaaS with tiered API pricing"
            self.target_customer = "Enterprises and product teams seeking AI-enhanced automation."
        elif "landing page" in idea or "website" in idea:
            self.market_size = "Small"
            self.competition = "Low"
            self.business_potential = "Medium"
            self.pricing_strategy = "One-time setup fee with optional maintenance plans"
            self.target_customer = "Small business owners, freelancers, and startups needing a web presence."
        else:
            self.market_size = "Medium"
            self.competition = "Medium"
            self.business_potential = "High"
            self.pricing_strategy = "Subscription-based pricing with freemium entry tier"
            self.target_customer = "Early adopters valuing fast, polished digital experiences."

        self.recommended_mvp = self._recommend_mvp(idea)
        self.growth_strategy = self._recommend_growth_strategy(idea)
        state.business = self.build_report(state)
        state.customer = self.target_customer

    def validate(self, state: ProjectState) -> bool:
        return bool(self.market_size and self.competition and self.business_potential)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "BUSINESS REPORT",
            "",
            f"Target Customer: {self.target_customer}",
            "",
            f"Market Size: {self.market_size}",
            "",
            f"Competition: {self.competition}",
            "",
            f"Business Potential: {self.business_potential}",
            "",
            f"Pricing Strategy: {self.pricing_strategy}",
            "",
            f"Recommended MVP: {self.recommended_mvp}",
            "",
            f"Growth Strategy: {self.growth_strategy}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)

    def _recommend_mvp(self, idea: str) -> str:
        if "crm" in idea:
            return "A lightweight CRM with contact management, task tracking, and sales pipeline views."
        if "ai" in idea or "machine learning" in idea:
            return "A focused AI feature that solves a core automation or insight problem."
        if "landing page" in idea or "website" in idea:
            return "A polished landing page with clear value proposition and a lead capture form."
        return "A minimum viable product that delivers the main value proposition quickly."

    def _recommend_growth_strategy(self, idea: str) -> str:
        if "crm" in idea:
            return "Target SMBs through partnerships, inbound marketing, and product-led trials."
        if "ai" in idea or "machine learning" in idea:
            return "Focus on case studies, developer adoption, and enterprise pilot programs."
        if "landing page" in idea or "website" in idea:
            return "Promote with digital marketing, portfolio showcases, and referral incentives."
        return "Use customer feedback to iterate quickly and expand into adjacent segments."
