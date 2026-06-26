from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class CTOAgent(BaseAgent):
    """Agent responsible for choosing the technical architecture."""

    def __init__(self) -> None:
        super().__init__(
            name="cto",
            description="Recommends the technical stack, database, frontend, and deployment.",
            priority=10,
            capabilities={
                Capability.STACK_SELECTION,
                Capability.BACKEND_GENERATION,
                Capability.FRONTEND_GENERATION,
                Capability.DATABASE_DESIGN,
                Capability.DEPLOYMENT,
            },
        )
        self.project_type = ""
        self.estimated_cost = ""
        self.reasoning = ""

    def analyze(self, state: ProjectState) -> None:
        idea = state.idea.lower()
        if "crm" in idea:
            self.project_type = "CRM"
            state.backend = "FastAPI"
            state.frontend = "React"
            state.database = "PostgreSQL"
            state.deployment = "Railway"
        elif "ai" in idea or "machine learning" in idea:
            self.project_type = "AI SaaS"
            state.backend = "FastAPI"
            state.frontend = "React"
            state.database = "PostgreSQL"
            state.deployment = "Railway"
        elif "mobile" in idea or "flutter" in idea:
            self.project_type = "Mobile"
            state.backend = "None"
            state.frontend = "Flutter"
            state.database = "Firebase"
            state.deployment = "Firebase"
        elif "landing page" in idea or "website" in idea:
            self.project_type = "Landing Page"
            state.backend = "None"
            state.frontend = "HTML/CSS/JS"
            state.database = "None"
            state.deployment = "GitHub Pages"
        else:
            self.project_type = "General Web App"
            state.backend = "FastAPI"
            state.frontend = "React"
            state.database = "PostgreSQL"
            state.deployment = "Railway"

        state.architecture = f"{state.frontend} frontend, {state.backend} backend, {state.database} database"
        self.estimated_cost = self._estimate_cost()
        self.reasoning = self._build_reasoning(state)

    def validate(self, state: ProjectState) -> bool:
        return bool(state.frontend and state.deployment and state.architecture)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "AI CTO REPORT",
            "",
            f"Project Type: {self.project_type}",
            "",
            f"Recommended Stack: Frontend={state.frontend}, Backend={state.backend}, Database={state.database}, Deployment={state.deployment}",
            "",
            f"Backend: {state.backend}",
            "",
            f"Frontend: {state.frontend}",
            "",
            f"Database: {state.database}",
            "",
            f"Deployment: {state.deployment}",
            "",
            f"Estimated Monthly Cost: {self.estimated_cost}",
            "",
            "Reasoning:",
            self.reasoning,
            "",
            "================================",
        ]
        return "\n".join(report_lines)

    def _estimate_cost(self) -> str:
        if self.project_type == "Landing Page":
            return "0 PLN"
        if self.project_type == "CRM":
            return "20 PLN"
        if self.project_type == "AI SaaS":
            return "50 PLN"
        return "15 PLN"

    def _build_reasoning(self, state: ProjectState) -> str:
        reasoning_parts = [
            f"Detected project type from idea: '{state.idea}'.",
            f"Recommended backend is {state.backend}.",
            f"Recommended frontend is {state.frontend}.",
            f"Recommended database is {state.database}.",
            f"Recommended deployment is {state.deployment}.",
            f"Estimated monthly cost is {self.estimated_cost}.",
        ]

        if self.project_type == "Landing Page":
            reasoning_parts.append("A landing page does not require a backend or database, so a static deployment is ideal.")
        if self.project_type == "CRM":
            reasoning_parts.append("A CRM requires a reliable backend, structured database, and a rich frontend.")
        if self.project_type == "AI SaaS":
            reasoning_parts.append("AI SaaS benefits from a backend API, relational storage, and integration with OpenAI API.")
        if self.project_type == "Mobile":
            reasoning_parts.append("Mobile experience is best served with a cross-platform framework and mobile-friendly cloud services.")
        return " ".join(reasoning_parts)
