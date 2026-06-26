from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set


class Capability(Enum):
    BUSINESS_ANALYSIS = "business_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    STACK_SELECTION = "stack_selection"
    BACKEND_GENERATION = "backend_generation"
    FRONTEND_GENERATION = "frontend_generation"
    DATABASE_DESIGN = "database_design"
    API_DESIGN = "api_design"
    AUTHENTICATION = "authentication"
    LANDING_PAGE = "landing_page"
    DEPLOYMENT = "deployment"
    CI_CD = "ci_cd"
    TESTING = "testing"
    MARKETING = "marketing"
    SEO = "seo"
    SALES = "sales"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    WEB = "web"
    AI_AGENT = "ai_agent"
    AUTOMATION = "automation"


@dataclass(frozen=True)
class AgentCapability:
    """Represents the capabilities owned by a single agent."""

    agent_name: str
    capabilities: Set[Capability] = field(default_factory=set)

    def supports(self, capability: Capability) -> bool:
        """Return whether the agent supports the provided capability."""
        return capability in self.capabilities


class CapabilityRegistry:
    """Registry for storing and querying agent capabilities."""

    def __init__(self) -> None:
        self._registry: Dict[str, AgentCapability] = {}
        self._capability_index: Dict[Capability, Set[str]] = {}

    def register_agent(self, agent_capability: AgentCapability) -> None:
        """Register or update the capabilities for a given agent."""
        self._registry[agent_capability.agent_name] = agent_capability
        for capability in agent_capability.capabilities:
            self._capability_index.setdefault(capability, set()).add(agent_capability.agent_name)

    def get_agent_capabilities(self, agent_name: str) -> Set[Capability]:
        """Return the capabilities registered for the specified agent."""
        return set(self._registry.get(agent_name, AgentCapability(agent_name)).capabilities)

    def get_agents_with_capability(self, capability: Capability) -> List[str]:
        """Return agent names that support a given capability."""
        return sorted(self._capability_index.get(capability, set()))

    def supports(self, agent_name: str, capability: Capability) -> bool:
        """Return whether a given agent supports a specific capability."""
        agent_capability = self._registry.get(agent_name)
        return bool(agent_capability and agent_capability.supports(capability))

    def all_agents(self) -> List[str]:
        """Return all registered agent names."""
        return sorted(self._registry.keys())

    def all_capabilities(self) -> Set[Capability]:
        """Return all capabilities currently present in the registry."""
        return set(self._capability_index.keys())

    def register_agent_capabilities(self, agent_name: str, capabilities: Iterable[Capability]) -> None:
        """Register or extend capabilities for a given agent name."""
        existing = self._registry.get(agent_name)
        if existing is not None:
            merged_capabilities = set(existing.capabilities) | set(capabilities)
        else:
            merged_capabilities = set(capabilities)
        self.register_agent(AgentCapability(agent_name=agent_name, capabilities=merged_capabilities))
