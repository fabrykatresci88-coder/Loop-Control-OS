from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class BackendAgent(BaseAgent):
    """Agent responsible for backend architecture and API design."""

    def __init__(self) -> None:
        super().__init__(
            name="backend",
            description="Designs backend platform, API contracts, and authentication patterns.",
            priority=30,
            capabilities={Capability.BACKEND_GENERATION, Capability.API_DESIGN, Capability.AUTHENTICATION},
        )
        self.backend_design = ""
        self.authentication_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        if state.backend and state.backend != "None":
            self.backend_design = f"Use {state.backend} with RESTful API endpoints and optional JWT authentication."
            self.authentication_strategy = "JWT authentication with role-based access control"
        else:
            self.backend_design = "No backend required for this project type."
            self.authentication_strategy = "None"
        state.backend = state.backend or "FastAPI"
        state.authentication = self.authentication_strategy

    def validate(self, state: ProjectState) -> bool:
        return self.backend_design != ""

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "BACKEND REPORT",
            "",
            f"Backend Design: {self.backend_design}",
            "",
            f"Authentication Strategy: {self.authentication_strategy}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
