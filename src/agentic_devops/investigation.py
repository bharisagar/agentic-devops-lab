"""Deterministic Day 1 incident analysis."""

from __future__ import annotations

from .models import DiagnosticEvidence, Incident, InvestigationReport
from .registry import build_default_registry

_ROOT_CAUSE = (
    "The application exits during startup because the required DATABASE_URL "
    "environment variable is not configured."
)
_REMEDIATION = (
    "Configure DATABASE_URL for the service through the deployment's approved secret-management "
    "mechanism, then restart the service and verify its health. Do not place the secret value in "
    "source control or incident reports."
)
_PREVENTION = (
    "Validate required configuration before the application starts.",
    "Document required variables with safe examples that contain no credentials.",
    "Add a startup or deployment check that reports missing variable names without printing values.",
)


def investigate(incident: Incident) -> InvestigationReport:
    """Inspect only fixture data and identify a narrowly defined startup failure."""
    if not isinstance(incident, Incident):
        raise TypeError("investigate() requires a validated Incident object")

    tools = build_default_registry(incident)
    evidence: tuple[DiagnosticEvidence, ...] = (
        tools.execute("inspect_container_status", {}),
        tools.execute("read_container_logs", {"limit": 20}),
        tools.execute("inspect_environment_configuration", {}),
    )
    return build_report(incident, evidence)


def build_report(
    incident: Incident,
    evidence: tuple[DiagnosticEvidence, ...],
) -> InvestigationReport:
    """Create a finding only from evidence actually collected by the caller."""
    log_evidence = next((item for item in evidence if item.tool_name == "read_container_logs"), None)
    config_evidence = next(
        (item for item in evidence if item.tool_name == "inspect_environment_configuration"),
        None,
    )
    status_evidence = next((item for item in evidence if item.tool_name == "inspect_container_status"), None)
    log_text = " ".join(log_evidence.details).lower() if log_evidence else ""
    configuration_text = " ".join(config_evidence.details).lower() if config_evidence else ""
    database_missing = (
        "database_url" in configuration_text
        and "required" in configuration_text
        and "not configured" in configuration_text
    )
    log_confirms_missing = "database_url" in log_text and any(
        marker in log_text for marker in ("missing", "not set", "not configured")
    )
    status_text = " ".join(status_evidence.details).lower() if status_evidence else ""
    restart_evidence = (
        any(state in status_text for state in ("state is restarting", "state is exited"))
        and "restart count is 0" not in status_text
    )

    if database_missing and log_confirms_missing and restart_evidence:
        status = "diagnosed"
        root_cause = _ROOT_CAUSE
        recommended_fix = _REMEDIATION
        uncertainty = "This conclusion applies only to the supplied simulated evidence; verify the same signals in a real environment."
    else:
        status = "insufficient_evidence"
        root_cause = None
        recommended_fix = (
            "Collect the relevant startup logs and compare required variable names with configured variable names. "
            "Do not print or copy secret values into the report."
        )
        uncertainty = (
            "The supplied evidence does not satisfy the Day 1 rule for this known startup failure. "
            "No root cause is asserted."
        )

    return InvestigationReport(
        incident_id=incident.incident_id,
        title=incident.title,
        status=status,
        root_cause=root_cause,
        evidence=evidence,
        recommended_fix=recommended_fix,
        prevention=_PREVENTION if root_cause else (),
        uncertainty=uncertainty,
    )
