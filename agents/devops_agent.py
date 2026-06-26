from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class DevOpsAgent(BaseAgent):
    """Agent responsible for deployment and CI/CD recommendations."""

    def __init__(self) -> None:
        super().__init__(
            name="devops",
            description="Recommends deployment patterns, infrastructure, and automation.",
            priority=50,
            capabilities={Capability.DEPLOYMENT, Capability.CI_CD, Capability.AUTOMATION},
        )
        self.deployment_plan = ""

    def analyze(self, state: ProjectState) -> None:
        if state.deployment:
            self.deployment_plan = f"Deploy to {state.deployment} with CI/CD pipelines." \
                f" Use automated tests and infrastructure as code."
        else:
            self.deployment_plan = "Deploy to Railway with automated build and release pipelines."
        state.deployment = state.deployment or "Railway"

    def validate(self, state: ProjectState) -> bool:
        return bool(self.deployment_plan)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "DEVOPS REPORT",
            "",
            f"Deployment Plan: {self.deployment_plan}",
            "",
            f"Deployment Target: {state.deployment}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
