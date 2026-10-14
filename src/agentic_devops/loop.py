"""A bounded, evidence-driven investigation loop for Day 3."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from .investigation import build_report
from .models import DiagnosticEvidence, Incident, InvestigationReport
from .registry import build_default_registry

MAX_INVESTIGATION_STEPS = 3


@dataclass(frozen=True)
class ToolRequest:
    """A proposed call to one tool, including why it is needed."""

    name: str
    arguments: dict[str, object]
    rationale: str


@dataclass(frozen=True)
class InvestigationStep:
    """An executed tool call and the evidence it returned."""

    number: int
    tool_name: str
    rationale: str
    evidence_summary: str


@dataclass(frozen=True)
class InvestigationResult:
    report: InvestigationReport
    steps: tuple[InvestigationStep, ...]
    stop_reason: str

    def trace_dict(self) -> dict[str, object]:
        """Return a JSON-ready trace separate from the diagnosis report."""
        return {
            "steps": [asdict(step) for step in self.steps],
            "stop_reason": self.stop_reason,
            "max_steps": MAX_INVESTIGATION_STEPS,
        }


class ToolSelector(Protocol):
    """Choose an approved next diagnostic request from collected evidence."""

    def select_next(
        self,
        incident: Incident,
        evidence: tuple[DiagnosticEvidence, ...],
    ) -> ToolRequest | None: ...


class EvidenceBasedSelector:
    """A transparent local policy; later lessons can replace this selector."""

    def select_next(
        self,
        incident: Incident,
        evidence: tuple[DiagnosticEvidence, ...],
    ) -> ToolRequest | None:
        completed = {item.tool_name for item in evidence}

        if "inspect_container_status" not in completed:
            return ToolRequest(
                "inspect_container_status",
                {},
                "Start with the container state and restart count to confirm the reported symptom.",
            )

        status = next(item for item in evidence if item.tool_name == "inspect_container_status")
        status_text = " ".join(status.details).lower()
        has_failure_signal = (
            "state is restarting" in status_text
            or "state is exited" in status_text
            or any(
                detail.startswith("restart count is ") and detail != "restart count is 0"
                for detail in status.details
            )
        )
        if has_failure_signal and "read_container_logs" not in completed:
            state_detail = next(
                (detail for detail in status.details if detail.startswith("container state is ")),
                "container state needs investigation",
            )
            restart_detail = next(
                (detail for detail in status.details if detail.startswith("restart count is ")),
                "restart count is unavailable",
            )
            return ToolRequest(
                "read_container_logs",
                {"limit": 20},
                f"Status evidence says {state_detail} and {restart_detail}; inspect bounded startup logs for the immediate error.",
            )

        logs = next((item for item in evidence if item.tool_name == "read_container_logs"), None)
        log_text = " ".join(logs.details).lower() if logs else ""
        mentions_configuration = any(
            marker in log_text for marker in ("environment variable", "configuration", "database_url")
        )
        if mentions_configuration and "inspect_environment_configuration" not in completed:
            return ToolRequest(
                "inspect_environment_configuration",
                {},
                "The log points to configuration; compare required and configured names without reading values.",
            )

        return None


def investigate_with_loop(
    incident: Incident,
    *,
    selector: ToolSelector | None = None,
    max_steps: int = MAX_INVESTIGATION_STEPS,
) -> InvestigationResult:
    """Collect evidence through validated tools, stopping within a hard bound."""
    if not isinstance(incident, Incident):
        raise TypeError("investigate_with_loop() requires a validated Incident object")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= MAX_INVESTIGATION_STEPS:
        raise ValueError(f"max_steps must be an integer between 1 and {MAX_INVESTIGATION_STEPS}")

    choose = selector or EvidenceBasedSelector()
    registry = build_default_registry(incident)
    evidence: list[DiagnosticEvidence] = []
    steps: list[InvestigationStep] = []
    stop_reason = "selector_finished"

    while len(steps) < max_steps:
        request = choose.select_next(incident, tuple(evidence))
        if request is None:
            break
        if not isinstance(request, ToolRequest):
            raise TypeError("selector must return a ToolRequest or None")
        if request.name in {item.tool_name for item in evidence}:
            stop_reason = "repeated_tool_request"
            break

        # The registry remains the execution boundary for every selector,
        # including a future model-backed selector.
        result = registry.execute(request.name, request.arguments)
        evidence.append(result)
        steps.append(
            InvestigationStep(
                number=len(steps) + 1,
                tool_name=result.tool_name,
                rationale=request.rationale,
                evidence_summary=result.summary,
            )
        )
    else:
        stop_reason = "max_steps_reached"

    return InvestigationResult(
        report=build_report(incident, tuple(evidence)),
        steps=tuple(steps),
        stop_reason=stop_reason,
    )
