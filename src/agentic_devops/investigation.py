"""Deterministic Day 1 incident analysis."""

from __future__ import annotations

from .models import DiagnosticEvidence, Incident, InvestigationReport
from .tools import inspect_container_status, inspect_environment_configuration, read_container_logs

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

    evidence: tuple[DiagnosticEvidence, ...] = (
        inspect_container_status(incident),
        read_container_logs(incident),
        inspect_environment_configuration(incident),
    )
    log_text = " ".join(evidence[1].details).lower()
    configuration = incident.environment_configuration
    configured = set(configuration.configured_variables)
    database_missing = "DATABASE_URL" in configuration.required_variables and "DATABASE_URL" not in configured
    log_confirms_missing = "database_url" in log_text and any(
        marker in log_text for marker in ("missing", "not set", "not configured")
    )
    restart_evidence = incident.container_status.state == "restarting" and incident.container_status.restart_count > 0

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
