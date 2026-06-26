from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional

from app.project_service import ProjectResult, ProjectService


class ExecutorController:
    """Coordinates Executor project execution and reports status updates."""

    def __init__(
        self,
        service: ProjectService,
        progress_callback: Optional[Callable[[str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.service = service
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.error_callback = error_callback

    def _report_progress(self, message: str) -> None:
        if self.progress_callback is not None:
            self.progress_callback(message)

    def _report_log(self, message: str) -> None:
        if self.log_callback is not None:
            self.log_callback(message)

    def _report_error(self, message: str) -> None:
        if self.error_callback is not None:
            self.error_callback(message)

    def run_project(self, idea: str) -> ProjectResult:
        """Run a project from idea through service execution and report outcomes."""
        idea_text = idea.strip()
        if not idea_text:
            raise ValueError("Project idea must not be empty.")

        self._report_progress("Validating input")
        self._report_log("Received project idea.")

        try:
            self._report_progress("Executing project flow")
            result = self.service.run_project(idea_text)

            self._report_log(f"Business report saved to {result.business_report_path}")
            self._report_log(f"CTO report saved to {result.cto_report_path}")
            self._report_log(f"Final prompt saved to {result.final_prompt_path}")

            if result.errors:
                for error in result.errors:
                    self._report_error(error)

            self._report_progress(
                "Project execution completed successfully"
                if result.success
                else "Project execution completed with errors"
            )
            return result

        except Exception as error:
            message = str(error)
            self._report_error(message)
            return ProjectResult(
                idea=idea_text,
                business_report="",
                cto_report="",
                final_prompt="",
                final_prompt_path=Path(),
                business_report_path=Path(),
                cto_report_path=Path(),
                success=False,
                errors=[message],
            )
