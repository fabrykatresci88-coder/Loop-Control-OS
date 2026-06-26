from __future__ import annotations

from pathlib import Path

from agents.cto_agent import CTOAgent
from core.project_state import ProjectState


class PipelineEngine:
    """Central orchestration engine for Loop-Control OS.

    PipelineEngine is responsible for coordinating each agent workflow.
    Only the CTO flow is implemented for now; other agent flows are
    intentionally left unimplemented until their logic is added.
    """

    def run(self, idea: str) -> None:
        """Run the full pipeline for a project idea.

        Args:
            idea: The raw project idea description.
        """
        self.run_cto(idea)
        self.run_business(idea)
        self.run_backend(idea)
        self.run_frontend(idea)
        self.run_devops(idea)
        self.run_marketing(idea)
        self.run_sales(idea)
        self.run_qa(idea)

    def run_cto(self, idea: str) -> None:
        """Run the CTO agent workflow and persist the CTO report."""
        state = ProjectState(idea=idea)
        cto_agent = CTOAgent()
        report = cto_agent.run(state)

        report_path = Path("projects/CTO_REPORT.md")
        report_path.write_text(report, encoding="utf-8")

    def run_business(self, idea: str) -> None:
        """Run the business agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("Business workflow is not implemented yet.")

    def run_backend(self, idea: str) -> None:
        """Run the backend agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("Backend workflow is not implemented yet.")

    def run_frontend(self, idea: str) -> None:
        """Run the frontend agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("Frontend workflow is not implemented yet.")

    def run_devops(self, idea: str) -> None:
        """Run the DevOps agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("DevOps workflow is not implemented yet.")

    def run_marketing(self, idea: str) -> None:
        """Run the marketing agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("Marketing workflow is not implemented yet.")

    def run_sales(self, idea: str) -> None:
        """Run the sales agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("Sales workflow is not implemented yet.")

    def run_qa(self, idea: str) -> None:
        """Run the QA agent workflow.

        Args:
            idea: The raw project idea description.
        """
        raise NotImplementedError("QA workflow is not implemented yet.")
