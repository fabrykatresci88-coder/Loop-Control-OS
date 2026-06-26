from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class PromptGenerator(ABC):
    """Abstract prompt generation interface."""

    @abstractmethod
    def generate(self, idea: str) -> str:
        """Generate the full prompt text for a project idea."""
        raise NotImplementedError


class TemplatePromptGenerator(PromptGenerator):
    """Prompt generator that uses a markdown template file."""

    def __init__(self, template_path: Path | None = None) -> None:
        self.template_path = template_path or self._discover_default_template()

    def generate(self, idea: str) -> str:
        template = self.template_path.read_text(encoding="utf-8")
        return (
            "==================== SYSTEM ====================\n\n"
            f"{template}\n\n"
            "==================== POMYSŁ ====================\n\n"
            f"{idea}\n"
        )

    def _discover_default_template(self) -> Path:
        repository_root = Path(__file__).resolve().parents[1]
        default_template = repository_root / "templates" / "PROMPT_TEMPLATE.md"
        if not default_template.exists():
            raise FileNotFoundError(
                f"Prompt template not found at {default_template}."
            )
        return default_template
