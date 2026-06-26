from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass(frozen=True)
class AIProviderConfig:
    name: str
    endpoint: str
    api_key: Optional[str] = None
    region: Optional[str] = None


@dataclass(frozen=True)
class DeploymentSettings:
    provider: str
    region: str
    container_registry: Optional[str] = None
    resource_group: Optional[str] = None


@dataclass(frozen=True)
class PathsConfig:
    project_root: Path
    idea_file: Path
    final_prompt_file: Path
    cto_report_file: Path
    business_report_file: Path
    logs_dir: Path


@dataclass(frozen=True)
class FeatureFlags:
    enable_cto: bool = True
    enable_business: bool = True
    enable_backend: bool = False
    enable_frontend: bool = False
    enable_devops: bool = False
    enable_marketing: bool = False
    enable_sales: bool = False
    enable_qa: bool = False


@dataclass(frozen=True)
class DefaultStackConfig:
    frontend: str = "React"
    backend: str = "FastAPI"
    database: str = "PostgreSQL"
    deployment: str = "Railway"


@dataclass(frozen=True)
class DefaultModelConfig:
    language_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3"
    code_model: str = "gpt-4-code"


@dataclass(frozen=True)
class AppConfig:
    environment: Environment
    ai_providers: List[AIProviderConfig]
    deployment_settings: DeploymentSettings
    paths: PathsConfig
    feature_flags: FeatureFlags
    logging_level: str
    default_stack: DefaultStackConfig
    default_models: DefaultModelConfig


class ConfigurationManager:
    """Load and manage application configuration profiles."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.profiles: Dict[Environment, AppConfig] = self._load_profiles()
        self.active_profile: AppConfig = self.profiles[Environment.DEVELOPMENT]

    def _load_profiles(self) -> Dict[Environment, AppConfig]:
        root = self.project_root
        default_paths = PathsConfig(
            project_root=root,
            idea_file=root / "projects" / "IDEA.md",
            final_prompt_file=root / "projects" / "FINAL_PROMPT.md",
            cto_report_file=root / "projects" / "CTO_REPORT.md",
            business_report_file=root / "projects" / "BUSINESS_REPORT.md",
            logs_dir=root / "logs",
        )

        return {
            Environment.DEVELOPMENT: AppConfig(
                environment=Environment.DEVELOPMENT,
                ai_providers=[
                    AIProviderConfig(name="openai", endpoint="https://api.openai.com", api_key=None)
                ],
                deployment_settings=DeploymentSettings(
                    provider="railway",
                    region="us-east-1",
                    container_registry="",
                    resource_group="",
                ),
                paths=default_paths,
                feature_flags=FeatureFlags(),
                logging_level="DEBUG",
                default_stack=DefaultStackConfig(),
                default_models=DefaultModelConfig(),
            ),
            Environment.PRODUCTION: AppConfig(
                environment=Environment.PRODUCTION,
                ai_providers=[
                    AIProviderConfig(name="openai", endpoint="https://api.openai.com", api_key=None)
                ],
                deployment_settings=DeploymentSettings(
                    provider="railway",
                    region="us-east-1",
                    container_registry="",
                    resource_group="",
                ),
                paths=default_paths,
                feature_flags=FeatureFlags(
                    enable_backend=True,
                    enable_frontend=True,
                    enable_devops=True,
                    enable_marketing=True,
                    enable_sales=True,
                    enable_qa=True,
                ),
                logging_level="INFO",
                default_stack=DefaultStackConfig(),
                default_models=DefaultModelConfig(),
            ),
            Environment.TESTING: AppConfig(
                environment=Environment.TESTING,
                ai_providers=[
                    AIProviderConfig(name="mock", endpoint="https://mock.api", api_key="test")
                ],
                deployment_settings=DeploymentSettings(
                    provider="local",
                    region="local",
                    container_registry=None,
                    resource_group=None,
                ),
                paths=default_paths,
                feature_flags=FeatureFlags(
                    enable_backend=True,
                    enable_frontend=True,
                    enable_devops=True,
                    enable_marketing=True,
                    enable_sales=True,
                    enable_qa=True,
                ),
                logging_level="DEBUG",
                default_stack=DefaultStackConfig(),
                default_models=DefaultModelConfig(
                    language_model="gpt-4-test",
                    embedding_model="text-embedding-3-test",
                    code_model="gpt-4-code-test",
                ),
            ),
        }

    def select_profile(self, environment: Environment) -> None:
        """Select the active configuration profile."""
        if environment not in self.profiles:
            raise ValueError(f"Unknown environment profile: {environment}")
        self.active_profile = self.profiles[environment]

    def get_config(self) -> AppConfig:
        """Return the currently selected active configuration."""
        return self.active_profile

    def get_path(self, name: str) -> Path:
        """Return a configured Path by key name."""
        if not hasattr(self.active_profile.paths, name):
            raise AttributeError(f"Path '{name}' is not defined in configuration.")
        return getattr(self.active_profile.paths, name)
