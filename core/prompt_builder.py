from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModulePromptConfig:
    role: str
    tasks: tuple[str, ...]


class PromptBuilder:
    """Builds compact prompts for each pipeline module."""

    _MODULE_CONFIGS: dict[str, ModulePromptConfig] = {
        "brain": ModulePromptConfig(
            role="Startup Architect",
            tasks=("problem framing", "solution scope", "core value"),
        ),
        "business": ModulePromptConfig(
            role="Business Analyst",
            tasks=("market", "competitors", "pricing", "MVP"),
        ),
        "cto": ModulePromptConfig(
            role="CTO",
            tasks=("architecture", "stack", "scalability", "risks"),
        ),
        "backend": ModulePromptConfig(
            role="Backend Engineer",
            tasks=("API design", "services", "security", "data flow"),
        ),
        "frontend": ModulePromptConfig(
            role="Frontend Engineer",
            tasks=("UI structure", "state flow", "accessibility", "UX"),
        ),
        "database": ModulePromptConfig(
            role="Database Architect",
            tasks=("schema", "indexes", "consistency", "backups"),
        ),
        "landing": ModulePromptConfig(
            role="Landing Page Strategist",
            tasks=("positioning", "sections", "copy", "CTA"),
        ),
        "roadmap": ModulePromptConfig(
            role="Product Planner",
            tasks=("milestones", "priorities", "dependencies", "timeline"),
        ),
        "qa": ModulePromptConfig(
            role="QA Engineer",
            tasks=("test strategy", "test pyramid", "quality gates", "risks"),
        ),
        "deploy": ModulePromptConfig(
            role="DevOps Engineer",
            tasks=("deployment", "observability", "rollback", "cost controls"),
        ),
    }

    @classmethod
    def build_module_prompt(cls, module: str, idea: str) -> str:
        normalized = module.strip().lower()
        config = cls._MODULE_CONFIGS.get(
            normalized,
            ModulePromptConfig(
                role=f"{module.strip() or 'General'} Specialist",
                tasks=("analysis",),
            ),
        )
        task_line = ", ".join(config.tasks)
        return (
            f"R:{config.role}\n"
            f"P:{idea.strip()}\n"
            f"T:{task_line}\n"
            "Markdown only."
        )

    @staticmethod
    def build_mvp_merge_prompt(idea: str, reports: dict[str, str]) -> str:
        sections = []
        for module, content in reports.items():
            if content.strip():
                sections.append(f"## {module}\n{content.strip()}")

        report_blob = "\n\n".join(sections) if sections else "No reports available."
        return (
            "Role: Product Strategist\n\n"
            f"Project:\n{idea.strip()}\n\n"
            "Existing reports:\n"
            f"{report_blob}\n\n"
            "Tasks:\n"
            "- consolidate\n"
            "- remove duplicates\n"
            "- produce MVP blueprint\n\n"
            "Return markdown only."
        )
