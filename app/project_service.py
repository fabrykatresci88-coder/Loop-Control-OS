from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import traceback
from typing import List

from agents.business_agent import BusinessAgent
from agents.cto_agent import CTOAgent
from core.ai_provider import AIProvider
from core.pipeline import PipelineEngine
from core.project_repository import ProjectRepository
from core.prompt_generator import PromptGenerator
from core.project_state import ProjectState


@dataclass(frozen=True)
class ProjectResult:
    idea: str
    business_report: str
    cto_report: str
    final_prompt: str
    final_prompt_path: Path
    business_report_path: Path
    cto_report_path: Path
    success: bool
    errors: List[str] = field(default_factory=list)


class ProjectService:
    """Application service coordinating project generation and AI execution."""

    def __init__(
        self,
        repository: ProjectRepository,
        prompt_generator: PromptGenerator,
        ai_provider: AIProvider,
    ) -> None:
        self.repository = repository
        self.prompt_generator = prompt_generator
        self.ai_provider = ai_provider

    def create_project(self, idea: str) -> ProjectState:
        self.repository.save_idea(idea)
        prompt = self.prompt_generator.generate(idea)
        self.repository.save_report("final_prompt", prompt)
        state = ProjectState(idea=idea)
        return state

    def analyze(self, state: ProjectState, selected_modules: list[str] | None = None) -> str:
        print("[DEBUG] ProjectService.analyze: start")
        try:
            print("[DEBUG] ProjectService.analyze: before prompt_generator.generate()")
            prompt = self.prompt_generator.generate(state.idea)
            print("[DEBUG] ProjectService.analyze: after prompt_generator.generate()")

            if selected_modules:
                print("[DEBUG] ProjectService.analyze: before selected_modules formatting")
                module_list = "\n".join(f"- {module}" for module in selected_modules)
                prompt += f"\n\nSelected pipeline modules:\n{module_list}\n"
                print("[DEBUG] ProjectService.analyze: after selected_modules formatting")

            print("[DEBUG] ProjectService.analyze: before ai_provider.generate_text()")
            result = self.ai_provider.generate_text(prompt)
            print("[DEBUG] ProjectService.analyze: after ai_provider.generate_text()")
            print("[DEBUG] ProjectService.analyze: end")
            return result
        except Exception:
            print("[DEBUG] ProjectService.analyze: exception caught, full traceback below")
            traceback.print_exc()
            raise

    def generate_architecture_report(self, state: ProjectState, selected_modules: list[str] | None = None) -> str:
        return self.analyze(state, selected_modules=selected_modules)

    def run_project(self, idea: str) -> ProjectResult:
        """Run the Executor MVP project flow from idea to saved outputs."""
        cleaned_idea = idea.strip()
        if not cleaned_idea:
            raise ValueError("Project idea must not be empty.")

        state = ProjectState(idea=cleaned_idea)
        errors: List[str] = []

        # Persist the project idea.
        self.repository.save_idea(cleaned_idea)

        # Business agent analysis.
        business_agent = BusinessAgent()
        business_report = business_agent.run(state)
        state.add_report("business", business_report)
        self.repository.save_report("business", business_report)

        # CTO agent analysis.
        cto_agent = CTOAgent()
        cto_report = cto_agent.run(state)
        state.add_report("cto", cto_report)
        self.repository.save_report("cto", cto_report)

        # Execute the available pipeline flow.
        pipeline_engine = PipelineEngine()
        try:
            pipeline_engine.run_cto(cleaned_idea)
        except Exception as error:  # Keep pipeline failures visible without crashing the service.
            errors.append(str(error))

        # Generate and persist the final prompt.
        final_prompt = self.prompt_generator.generate(cleaned_idea)
        final_prompt_path = self._save_final_prompt(final_prompt)

        return ProjectResult(
            idea=cleaned_idea,
            business_report=business_report,
            cto_report=cto_report,
            final_prompt=final_prompt,
            final_prompt_path=final_prompt_path,
            business_report_path=self._project_dir() / "BUSINESS_REPORT.md",
            cto_report_path=self._project_dir() / "CTO_REPORT.md",
            success=len(errors) == 0,
            errors=errors,
        )

    def _project_dir(self) -> Path:
        root = Path(__file__).resolve().parents[1]
        project_dir = root / "projects"
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def _save_final_prompt(self, prompt: str) -> Path:
        final_prompt_path = self._project_dir() / "FINAL_PROMPT.md"
        final_prompt_path.write_text(prompt, encoding="utf-8")
        return final_prompt_path
