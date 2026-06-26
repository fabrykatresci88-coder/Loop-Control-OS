from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProjectState:
    """Represents the complete state of a project within Loop-Control OS."""

    idea: str
    customer: Optional[str] = None
    industry: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    frontend: Optional[str] = None
    backend: Optional[str] = None
    database: Optional[str] = None
    deployment: Optional[str] = None
    authentication: Optional[str] = None
    architecture: Optional[str] = None
    business: Optional[str] = None
    marketing: Optional[str] = None
    sales: Optional[str] = None
    qa: Optional[str] = None
    devops: Optional[str] = None
    status: str = "initialized"
    reports: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)

    def add_report(self, agent_name: str, report: str) -> None:
        """Add or update a report produced by an agent."""
        self.reports[agent_name] = report

    def add_log(self, message: str) -> None:
        """Append a log message to the project log."""
        self.logs.append(message)

    def add_error(self, message: str) -> None:
        """Append an error message to the project errors list."""
        self.errors.append(message)

    def mark_step_completed(self, step_name: str) -> None:
        """Record a completed pipeline step."""
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
