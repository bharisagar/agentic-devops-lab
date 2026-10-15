"""LangGraph orchestration for the fixture-only Day 4 investigation."""

from __future__ import annotations

import json
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from .cli import render_markdown
from .investigation import build_report
from .loop import EvidenceBasedSelector, MAX_INVESTIGATION_STEPS, ToolSelector, ToolRequest
from .models import DiagnosticEvidence, Incident, InvestigationReport
from .registry import build_default_registry

MAX_GRAPH_SUPERSTEPS = 16


class InvestigationState(TypedDict, total=False):
    """JSON-friendly state passed between the graph's named nodes."""

    incident_data: dict[str, Any]
    triage: dict[str, Any]
    evidence: list[dict[str, Any]]
    steps: list[dict[str, Any]]
    stop_reason: str | None
    diagnosis: dict[str, Any]
    verification: dict[str, Any]
    report_markdown: str


def _incident_from_state(state: InvestigationState) -> Incident:
    return Incident.from_dict(state["incident_data"])


def _evidence_from_state(state: InvestigationState) -> tuple[DiagnosticEvidence, ...]:
    return tuple(
        DiagnosticEvidence(
            tool_name=item["tool_name"],
            summary=item["summary"],
            details=tuple(item["details"]),
            source=item["source"],
        )
        for item in state.get("evidence", [])
    )


def _report_from_dict(value: dict[str, Any]) -> InvestigationReport:
    evidence = tuple(
        DiagnosticEvidence(
            tool_name=item["tool_name"],
            summary=item["summary"],
            details=tuple(item["details"]),
            source=item["source"],
        )
        for item in value["evidence"]
    )
    return InvestigationReport(
        incident_id=value["incident_id"],
        title=value["title"],
        status=value["status"],
        root_cause=value["root_cause"],
        evidence=evidence,
        recommended_fix=value["recommended_fix"],
        prevention=tuple(value["prevention"]),
        uncertainty=value["uncertainty"],
    )


def _json_ready(value: Any) -> Any:
    """Normalize tuples and nested dataclasses to plain JSON values."""
    return json.loads(json.dumps(value, ensure_ascii=False))


def _verify_report(report: InvestigationReport) -> dict[str, Any]:
    """Check a diagnosed root cause against independent evidence requirements."""
    by_tool = {item.tool_name: item for item in report.evidence}
    status_text = " ".join(
        [by_tool["inspect_container_status"].summary, *by_tool["inspect_container_status"].details]
    ).lower() if "inspect_container_status" in by_tool else ""
    log_text = " ".join(
        [by_tool["read_container_logs"].summary, *by_tool["read_container_logs"].details]
    ).lower() if "read_container_logs" in by_tool else ""
    config_text = " ".join(
        [
            by_tool["inspect_environment_configuration"].summary,
            *by_tool["inspect_environment_configuration"].details,
        ]
    ).lower() if "inspect_environment_configuration" in by_tool else ""
    checks = {
        "status_confirms_a_container_failure": (
            ("state is restarting" in status_text and "restart count is 0" not in status_text)
            or ("state is exited" in status_text and "last exit code is 0" not in status_text)
        ),
        "logs_identify_missing_database_url": (
            "database_url" in log_text
            and any(marker in log_text for marker in ("missing", "not set", "not configured"))
        ),
        "configuration_confirms_required_name_is_missing": (
            "database_url" in config_text
            and "required" in config_text
            and "not configured" in config_text
        ),
    }
    verified = all(checks.values())
    return {
        "passed": report.root_cause is None or verified,
        "root_cause_verified": report.root_cause is not None and verified,
        "checks": checks,
    }


def build_investigation_graph(
    *,
    selector: ToolSelector | None = None,
    max_tool_steps: int = MAX_INVESTIGATION_STEPS,
):
    """Build and compile the bounded LangGraph workflow.

    The graph uses an in-memory checkpointer for this local learning example.
    Production systems need an appropriately secured persistent checkpointer.
    """
    if (
        isinstance(max_tool_steps, bool)
        or not isinstance(max_tool_steps, int)
        or not 1 <= max_tool_steps <= MAX_INVESTIGATION_STEPS
    ):
        raise ValueError(
            f"max_tool_steps must be an integer between 1 and {MAX_INVESTIGATION_STEPS}"
        )

    choose = selector or EvidenceBasedSelector()
    builder = StateGraph(InvestigationState)

    def triage(state: InvestigationState) -> dict[str, Any]:
        incident = _incident_from_state(state)
        return {
            "triage": {
                "incident_id": incident.incident_id,
                "service": incident.service,
                "environment": incident.environment,
                "reported_state": incident.container_status.state,
                "reported_restart_count": incident.container_status.restart_count,
                "simulated": incident.simulated,
            },
            "evidence": [],
            "steps": [],
            "stop_reason": None,
        }

    def collect_evidence(state: InvestigationState) -> dict[str, Any]:
        incident = _incident_from_state(state)
        evidence = _evidence_from_state(state)
        request = choose.select_next(incident, evidence)
        steps = list(state.get("steps", []))
        evidence_data = list(state.get("evidence", []))

        if request is None:
            return {"stop_reason": "selector_finished"}
        if not isinstance(request, ToolRequest):
            raise TypeError("selector must return a ToolRequest or None")
        if request.name in {item.tool_name for item in evidence}:
            return {"stop_reason": "repeated_tool_request"}

        # The allowlist validates every requested name and argument before a
        # fixture-backed diagnostic function can run.
        result = build_default_registry(incident).execute(request.name, request.arguments)
        evidence_data.append(_json_ready({
            "tool_name": result.tool_name,
            "summary": result.summary,
            "details": result.details,
            "source": result.source,
        }))
        steps.append({
            "number": len(steps) + 1,
            "tool_name": result.tool_name,
            "rationale": request.rationale,
            "evidence_summary": result.summary,
        })
        stop_reason = "max_steps_reached" if len(steps) >= max_tool_steps else None
        return {"evidence": evidence_data, "steps": steps, "stop_reason": stop_reason}

    def route_after_evidence(state: InvestigationState) -> str:
        if state.get("stop_reason") is not None:
            return "diagnosis"
        return "collect_evidence"

    def diagnosis(state: InvestigationState) -> dict[str, Any]:
        report = build_report(_incident_from_state(state), _evidence_from_state(state))
        return {"diagnosis": _json_ready(report.to_dict())}

    def verification(state: InvestigationState) -> dict[str, Any]:
        report = _report_from_dict(state["diagnosis"])
        result = _verify_report(report)
        if report.root_cause is not None and not result["root_cause_verified"]:
            report = InvestigationReport(
                incident_id=report.incident_id,
                title=report.title,
                status="insufficient_evidence",
                root_cause=None,
                evidence=report.evidence,
                recommended_fix=(
                    "Collect the missing status, log, or configuration evidence before identifying a root cause. "
                    "Do not print or copy secret values into the report."
                ),
                prevention=(),
                uncertainty="The verification node could not confirm every required evidence check.",
            )
        return {
            "verification": result,
            "diagnosis": _json_ready(report.to_dict()),
        }

    def report(state: InvestigationState) -> dict[str, Any]:
        return {"report_markdown": render_markdown(_report_from_dict(state["diagnosis"]))}

    builder.add_node("triage", triage)
    builder.add_node(
        "collect_evidence",
        collect_evidence,
        retry_policy=RetryPolicy(
            max_attempts=2,
            retry_on=ConnectionError,
            initial_interval=0.0,
            max_interval=0.0,
        ),
    )
    builder.add_node("diagnosis", diagnosis)
    builder.add_node("verification", verification)
    builder.add_node("report", report)

    builder.add_edge(START, "triage")
    builder.add_edge("triage", "collect_evidence")
    builder.add_conditional_edges(
        "collect_evidence",
        route_after_evidence,
        {"collect_evidence": "collect_evidence", "diagnosis": "diagnosis"},
    )
    builder.add_edge("diagnosis", "verification")
    builder.add_edge("verification", "report")
    builder.add_edge("report", END)

    return builder.compile(checkpointer=InMemorySaver())
