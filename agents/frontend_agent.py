from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class FrontendAgent(BaseAgent):
    """Agent responsible for frontend strategy and user experience."""

    def __init__(self) -> None:
        super().__init__(
            name="frontend",
            description="Defines frontend framework and user experience guidance.",
            priority=40,
            capabilities={Capability.FRONTEND_GENERATION, Capability.WEB, Capability.MOBILE, Capability.DESKTOP},
        )
        self.frontend_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        if state.frontend:
            self.frontend_strategy = f"Use {state.frontend} to deliver the user interface."
        else:
            self.frontend_strategy = "Use React for web and Flutter for mobile interfaces."
        state.frontend = state.frontend or "React"

    def validate(self, state: ProjectState) -> bool:
        return bool(self.frontend_strategy)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "FRONTEND REPORT",
            "",
            f"Frontend Strategy: {self.frontend_strategy}",
            "",
            f"Selected Frontend: {state.frontend}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
