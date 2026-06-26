from __future__ import annotations

from core.base_agent import BaseAgent
from core.capabilities import Capability
from core.project_state import ProjectState


class QAAgent(BaseAgent):
    """Agent responsible for quality assurance and testing strategy."""

    def __init__(self) -> None:
        super().__init__(
            name="qa",
            description="Defines testing strategy, quality checks, and validation workflows.",
            priority=80,
            capabilities={Capability.TESTING, Capability.AUTOMATION},
        )
        self.qa_strategy = ""

    def analyze(self, state: ProjectState) -> None:
        if state.backend != "None":
            self.qa_strategy = "Include unit tests, integration tests, and end-to-end regression coverage."
        else:
            self.qa_strategy = "Include UI/UX validation and smoke testing for static flows."
        state.qa = self.qa_strategy

    def validate(self, state: ProjectState) -> bool:
        return bool(self.qa_strategy)

    def build_report(self, state: ProjectState) -> str:
        report_lines = [
            "================================",
            "",
            "QA REPORT",
            "",
            f"QA Strategy: {self.qa_strategy}",
            "",
            "================================",
        ]
        return "\n".join(report_lines)
