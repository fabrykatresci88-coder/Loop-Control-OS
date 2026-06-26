from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    project_dir: Path
    metadata_file: Path


class ProjectStorage:
    """Stores reports in isolated project folders."""

    def __init__(self, root: Path | None = None) -> None:
        base = root or Path(__file__).resolve().parents[1]
        self.projects_root = base / "projects"
        self.projects_root.mkdir(parents=True, exist_ok=True)

    def project_paths(self, idea: str) -> ProjectPaths:
        slug = self._slugify(idea)
        project_dir = self.projects_root / slug
        project_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = project_dir / "metadata.json"
        if not metadata_file.exists():
            metadata_file.write_text(json.dumps({"idea": idea.strip()}, ensure_ascii=False, indent=2), encoding="utf-8")
        return ProjectPaths(project_dir=project_dir, metadata_file=metadata_file)

    def save_report(self, project_dir: Path, module: str, content: str) -> Path:
        report_file = project_dir / f"{self._module_file_name(module)}.md"
        report_file.write_text(content, encoding="utf-8")
        return report_file

    def load_report(self, project_dir: Path, module: str) -> str | None:
        report_file = project_dir / f"{self._module_file_name(module)}.md"
        if report_file.exists():
            return report_file.read_text(encoding="utf-8")
        return None

    @staticmethod
    def _module_file_name(module: str) -> str:
        normalized = module.strip().lower().replace(" ", "_")
        return normalized or "report"

    @staticmethod
    def _slugify(text: str) -> str:
        cleaned = re.sub(r"[^\w\s-]", "", text.strip().lower(), flags=re.UNICODE)
        cleaned = re.sub(r"[-\s]+", "_", cleaned, flags=re.UNICODE).strip("_")
        return cleaned or "project"
