from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import traceback
from typing import List

from core.ai_provider import AIProvider
from core.cache_manager import CacheManager
from core.project_storage import ProjectStorage
from core.project_repository import ProjectRepository
from core.prompt_builder import PromptBuilder
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

    ANALYZE_MAX_OUTPUT_TOKENS = 1200
    ANALYZE_TEMPERATURE = 0.2

    def __init__(
        self,
        repository: ProjectRepository,
        prompt_generator: PromptGenerator,
        ai_provider: AIProvider,
    ) -> None:
        self.repository = repository
        self.prompt_generator = prompt_generator
        self.ai_provider = ai_provider
        self.cache_enabled = True
        self.cache_manager = CacheManager()
        self.storage = ProjectStorage()
        self.debug_enabled = os.getenv("DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}

    def create_project(self, idea: str) -> ProjectState:
        self.repository.save_idea(idea)
        prompt = self.prompt_generator.generate(idea)
        self.repository.save_report("final_prompt", prompt)
        paths = self.storage.project_paths(idea)
        self.storage.save_report(paths.project_dir, "idea", idea.strip())
        state = ProjectState(idea=idea)
        return state

    def analyze(self, state: ProjectState, selected_modules: list[str] | None = None) -> str:
        self._debug("ProjectService.analyze: start")
        try:
            modules = selected_modules or ["Brain"]
            paths = self.storage.project_paths(state.idea)
            module_reports: list[str] = []

            for module in modules:
                report = self._get_or_generate_module_report(
                    idea=state.idea,
                    module=module,
                    project_dir=paths.project_dir,
                )
                module_reports.append(f"## {module}\n{report.strip()}")

            result = "\n\n".join(module_reports).strip()
            self._debug("ProjectService.analyze: end")
            return result
        except Exception:
            self._debug("ProjectService.analyze: exception caught, full traceback below")
            traceback.print_exc()
            raise

    def set_cache_enabled(self, enabled: bool) -> None:
        self.cache_enabled = enabled

    def clear_cache(self) -> int:
        return self.cache_manager.clear()

    def generate_architecture_report(self, state: ProjectState, selected_modules: list[str] | None = None) -> str:
        return self.analyze(state, selected_modules=selected_modules)

    def run_project(self, idea: str) -> ProjectResult:
        """Run MVP flow with report reuse and low-cost merge."""
        cleaned_idea = idea.strip()
        if not cleaned_idea:
            raise ValueError("Project idea must not be empty.")

        project_paths = self.storage.project_paths(cleaned_idea)
        errors: List[str] = []
        self.repository.save_idea(cleaned_idea)

        try:
            brain_report = self._get_or_generate_module_report(cleaned_idea, "Brain", project_paths.project_dir)
            business_report = self._get_or_generate_module_report(cleaned_idea, "Business", project_paths.project_dir)
            cto_report = self._get_or_generate_module_report(cleaned_idea, "CTO", project_paths.project_dir)

            reports_for_mvp = {
                "Brain": brain_report,
                "Business": business_report,
                "CTO": cto_report,
            }
            final_prompt = self._build_or_reuse_mvp(cleaned_idea, reports_for_mvp, project_paths.project_dir)
            final_prompt_path = self.storage.save_report(project_paths.project_dir, "mvp", final_prompt)

            self.repository.save_report("business", business_report)
            self.repository.save_report("cto", cto_report)
            self.repository.save_report("final_prompt", final_prompt)
        except Exception as error:
            errors.append(str(error))
            business_report = self.storage.load_report(project_paths.project_dir, "business") or ""
            cto_report = self.storage.load_report(project_paths.project_dir, "cto") or ""
            final_prompt = self.storage.load_report(project_paths.project_dir, "mvp") or ""
            final_prompt_path = project_paths.project_dir / "mvp.md"

        business_report_path = project_paths.project_dir / "business.md"
        cto_report_path = project_paths.project_dir / "cto.md"

        return ProjectResult(
            idea=cleaned_idea,
            business_report=business_report,
            cto_report=cto_report,
            final_prompt=final_prompt,
            final_prompt_path=final_prompt_path,
            business_report_path=business_report_path,
            cto_report_path=cto_report_path,
            success=len(errors) == 0,
            errors=errors,
        )

    def _get_or_generate_module_report(self, idea: str, module: str, project_dir: Path) -> str:
        prompt = PromptBuilder.build_module_prompt(module, idea)
        self._debug(f"Prompt chars: {len(prompt)}")
        self._debug(f"Selected model: {getattr(self.ai_provider, 'model', 'unknown')}")

        if self.cache_enabled:
            cached = self.cache_manager.get_cached(module, prompt)
            if cached is not None:
                self._debug(f"OpenAI request skipped for {module}: cache hit")
                self.storage.save_report(project_dir, module, cached)
                self._debug("Tokens: unavailable")
                return cached

        existing = self.storage.load_report(project_dir, module)
        if existing and existing.strip():
            self._debug(f"OpenAI request skipped for {module}: existing project report")
            self._debug("Tokens: unavailable")
            if self.cache_enabled:
                self.cache_manager.set_cached(module, prompt, existing)
            return existing

        self._debug(f"OpenAI request executed for {module}")
        import time
        start = time.perf_counter()
        report = self.ai_provider.generate_text(
            prompt,
            max_output_tokens=self.ANALYZE_MAX_OUTPUT_TOKENS,
            temperature=self.ANALYZE_TEMPERATURE,
        )
        elapsed = time.perf_counter() - start
        self._debug(f"Execution time: {elapsed:.2f}s")
        self._debug("Tokens: unavailable")

        self.storage.save_report(project_dir, module, report)
        if self.cache_enabled:
            self.cache_manager.set_cached(module, prompt, report)
        return report

    def _build_or_reuse_mvp(self, idea: str, reports: dict[str, str], project_dir: Path) -> str:
        existing_mvp = self.storage.load_report(project_dir, "mvp")
        if existing_mvp and existing_mvp.strip():
            self._debug("OpenAI request skipped for mvp: existing project report")
            return existing_mvp

        prompt = PromptBuilder.build_mvp_merge_prompt(idea, reports)
        self._debug(f"Prompt chars: {len(prompt)}")
        self._debug(f"Selected model: {getattr(self.ai_provider, 'model', 'unknown')}")

        if self.cache_enabled:
            cached = self.cache_manager.get_cached("mvp", prompt)
            if cached is not None:
                self._debug("OpenAI request skipped for mvp: cache hit")
                return cached

        self._debug("OpenAI request executed for mvp")
        import time
        start = time.perf_counter()
        merged = self.ai_provider.generate_text(
            prompt,
            max_output_tokens=self.ANALYZE_MAX_OUTPUT_TOKENS,
            temperature=self.ANALYZE_TEMPERATURE,
        )
        elapsed = time.perf_counter() - start
        self._debug(f"Execution time: {elapsed:.2f}s")
        self._debug("Tokens: unavailable")

        if self.cache_enabled:
            self.cache_manager.set_cached("mvp", prompt, merged)
        return merged

    def _debug(self, message: str) -> None:
        if self.debug_enabled:
            print(f"[DEBUG] {message}")
