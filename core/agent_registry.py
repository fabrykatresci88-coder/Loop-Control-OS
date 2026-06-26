from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set

from core.base_agent import BaseAgent
from core.capabilities import Capability


class AgentRegistry:
    """Registry for managing BaseAgent instances and capability lookup."""

    def __init__(self, agents: Optional[Iterable[BaseAgent]] = None) -> None:
        """Initialize the registry with optional pre-registered agents."""
        self._agents: Dict[str, BaseAgent] = {}
        self._capability_index: Dict[Capability, Set[str]] = {}
        if agents is not None:
            for agent in agents:
                self.register(agent)

    def register(self, agent: BaseAgent) -> None:
        """Register an agent for future lookup and execution."""
        if agent.name in self._agents:
            raise ValueError(f"Agent with name '{agent.name}' is already registered.")
        self._agents[agent.name] = agent
        for capability in self._extract_capabilities(agent):
            self._capability_index.setdefault(capability, set()).add(agent.name)

    def unregister(self, agent: BaseAgent) -> None:
        """Remove an agent from the registry."""
        if agent.name not in self._agents:
            raise KeyError(f"Agent '{agent.name}' is not registered.")
        self._agents.pop(agent.name)
        for capability, agent_names in list(self._capability_index.items()):
            agent_names.discard(agent.name)
            if not agent_names:
                self._capability_index.pop(capability)

    def find_by_name(self, name: str) -> Optional[BaseAgent]:
        """Return an agent by name, or None if not found."""
        return self._agents.get(name)

    def find_by_capability(self, capability: Capability) -> List[BaseAgent]:
        """Return all agents that declare support for the given capability."""
        agent_names = self._capability_index.get(capability, set())
        return [self._agents[name] for name in sorted(agent_names)]

    def find_all(self) -> List[BaseAgent]:
        """Return all registered agents in registration order."""
        return list(self._agents.values())

    def validate_registry(self) -> bool:
        """Validate the registry for duplicate names and capability consistency."""
        if len(self._agents) != len(set(self._agents.keys())):
            return False
        for agent in self._agents.values():
            if not agent.name or not agent.description:
                return False
            if not isinstance(agent.priority, int):
                return False
        return True

    def _extract_capabilities(self, agent: BaseAgent) -> Set[Capability]:
        """Extract declared capabilities from an agent, if available."""
        capabilities = getattr(agent, "capabilities", None)
        if capabilities is None:
            return set()
        if not isinstance(capabilities, set):
            raise TypeError("Agent capabilities must be a set of Capability values.")
        return {capability for capability in capabilities if isinstance(capability, Capability)}
