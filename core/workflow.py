from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set

from core.events import EventBus


WorkflowAction = Callable[[Dict[str, Any]], Any]
WorkflowRollback = Callable[[Dict[str, Any]], Any]


class WorkflowError(Exception):
    """Base workflow execution error."""


@dataclass(frozen=True)
class WorkflowStep:
    """Represents a single workflow step with optional rollback."""

    name: str
    action: WorkflowAction
    rollback_action: Optional[WorkflowRollback] = None
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)

    def rollback(self, context: Dict[str, Any]) -> Any:
        if self.rollback_action is None:
            raise WorkflowError(f"No rollback action configured for step '{self.name}'.")
        return self.rollback_action(context)


@dataclass
class WorkflowResult:
    success: bool = False
    executed_steps: List[str] = field(default_factory=list)
    rolled_back_steps: List[str] = field(default_factory=list)
    failed_step: Optional[str] = None
    error: Optional[Exception] = None
    progress: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Workflow engine responsible for step registration, execution, and rollback."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._steps: Dict[str, WorkflowStep] = {}
        self._registration_order: List[str] = []

    def register_step(self, step: WorkflowStep) -> None:
        """Register a workflow step for later execution."""
        if step.name in self._steps:
            raise WorkflowError(f"Step '{step.name}' is already registered.")
        if step.name in step.dependencies:
            raise WorkflowError(f"Step '{step.name}' cannot depend on itself.")
        self._steps[step.name] = step
        self._registration_order.append(step.name)
        self._publish("workflow.step.registered", {"step": step.name})

    def register_steps(self, steps: Iterable[WorkflowStep]) -> None:
        """Register multiple workflow steps at once."""
        for step in steps:
            self.register_step(step)

    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Execute registered workflow steps sequentially, honoring dependencies."""
        context = dict(initial_context or {})
        result = WorkflowResult(context=context)

        try:
            execution_order = self._resolve_execution_order()
            total = len(execution_order)
            self._publish("workflow.started", {"total_steps": total})
            result.progress.append(f"Workflow started with {total} step(s).")

            for index, step_name in enumerate(execution_order, start=1):
                step = self._steps[step_name]
                self._publish(
                    "workflow.step.started",
                    {"step": step.name, "index": index, "total": total, "metadata": step.metadata},
                )
                result.progress.append(f"Starting step {index}/{total}: {step.name}.")

                try:
                    step.execute(context)
                except Exception as exc:
                    result.failed_step = step.name
                    result.error = exc
                    self._publish(
                        "workflow.step.failed",
                        {"step": step.name, "error": exc, "index": index, "total": total},
                    )
                    result.progress.append(f"Step failed: {step.name}.")
                    self._rollback(result, context)
                    result.success = False
                    self._publish("workflow.failed", {"failed_step": step.name, "error": exc})
                    return result

                result.executed_steps.append(step.name)
                result.progress.append(f"Completed step {index}/{total}: {step.name}.")
                self._publish(
                    "workflow.step.completed",
                    {"step": step.name, "index": index, "total": total},
                )

            result.success = True
            result.progress.append("Workflow completed successfully.")
            self._publish("workflow.completed", {"executed_steps": result.executed_steps})
            return result

        except Exception as exc:
            if result.failed_step is None:
                result.error = exc
                result.progress.append("Workflow aborted before execution.")
                self._publish("workflow.error", {"error": exc})
            return result

    def _rollback(self, result: WorkflowResult, context: Dict[str, Any]) -> None:
        if not result.executed_steps:
            return

        self._publish("workflow.rollback.started", {"executed_steps": result.executed_steps})
        for step_name in reversed(result.executed_steps):
            step = self._steps[step_name]
            if step.rollback_action is None:
                result.progress.append(f"No rollback configured for step: {step.name}.")
                self._publish("workflow.rollback.skipped", {"step": step.name})
                continue

            self._publish("workflow.step.rollback.started", {"step": step.name})
            result.progress.append(f"Rolling back step: {step.name}.")
            try:
                step.rollback(context)
                result.rolled_back_steps.append(step.name)
                result.progress.append(f"Rollback completed: {step.name}.")
                self._publish("workflow.step.rollback.completed", {"step": step.name})
            except Exception as exc:
                result.progress.append(f"Rollback failed for step: {step.name}.")
                self._publish(
                    "workflow.step.rollback.failed",
                    {"step": step.name, "error": exc},
                )

        self._publish("workflow.rollback.completed", {"rolled_back_steps": result.rolled_back_steps})

    def _resolve_execution_order(self) -> List[str]:
        if not self._steps:
            return []

        graph: Dict[str, Set[str]] = {name: set() for name in self._steps}
        indegree: Dict[str, int] = {name: 0 for name in self._steps}

        for step in self._steps.values():
            for dependency in step.dependencies:
                if dependency not in self._steps:
                    raise WorkflowError(
                        f"Step '{step.name}' depends on unknown step '{dependency}'."
                    )
                graph[dependency].add(step.name)
                indegree[step.name] += 1

        ready = deque([name for name in self._registration_order if indegree[name] == 0])
        order: List[str] = []

        while ready:
            current = ready.popleft()
            order.append(current)
            for dependent in sorted(graph[current], key=self._registration_order.index):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)

        if len(order) != len(self._steps):
            raise WorkflowError("Circular dependency detected in workflow steps.")

        return order

    def clear(self) -> None:
        """Remove all registered workflow steps."""
        self._steps.clear()
        self._registration_order.clear()
        self._publish("workflow.cleared", {})

    def _publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        self._event_bus.publish(event_name, payload)
