from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Set

from core.capabilities import Capability
from core.project_state import ProjectState


@dataclass
class BaseAgent(ABC):
    """Abstract base class for all agents in Loop-Control OS."""

    name: str
    description: str
    priority: int
    capabilities: Set[Capability] = field(default_factory=set)

    @abstractmethod
    def analyze(self, state: ProjectState) -> None:
        """Analyze the project description and prepare state values."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, state: ProjectState) -> bool:
        """Validate the agent's internal state before generating a report."""
        raise NotImplementedError

    @abstractmethod
    def build_report(self, state: ProjectState) -> str:
        """Build a report summarizing analysis results."""
        raise NotImplementedError

    def run(self, state: ProjectState) -> str:
        """Execute the agent workflow using shared project state."""
        self.analyze(state)
        if not self.validate(state):
            raise RuntimeError(f"Agent '{self.name}' failed validation.")
        return self.build_report(state)
