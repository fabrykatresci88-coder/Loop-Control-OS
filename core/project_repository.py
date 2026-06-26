from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.project_state import ProjectState


class ProjectRepository(ABC):
    """Abstract persistence interface for project artifacts."""

    @abstractmethod
    def save_idea(self, idea: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_report(self, name: str, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_idea(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def load_report(self, name: str) -> str:
        raise NotImplementedError


class FileProjectRepository(ProjectRepository):
    """File-backed implementation for project persistence."""

    def __init__(self, project_root: Path | None = None) -> None:
        root = (project_root or Path.cwd()).resolve()
        self.project_dir = root / "projects"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.idea_file = self.project_dir / "IDEA.md"
        self.cto_report_file = self.project_dir / "CTO_REPORT.md"
        self.business_report_file = self.project_dir / "BUSINESS_REPORT.md"

    def save_idea(self, idea: str) -> None:
        self.idea_file.write_text(idea, encoding="utf-8")

    def save_report(self, name: str, content: str) -> None:
        report_path = self.project_dir / f"{name.upper()}_REPORT.md"
        report_path.write_text(content, encoding="utf-8")

    def load_idea(self) -> str:
        if not self.idea_file.exists():
            raise FileNotFoundError("IDEA.md not found")
        return self.idea_file.read_text(encoding="utf-8")

    def load_report(self, name: str) -> str:
        report_path = self.project_dir / f"{name.upper()}_REPORT.md"
        if not report_path.exists():
            raise FileNotFoundError(f"{report_path} not found")
        return report_path.read_text(encoding="utf-8")
