"""Pure diagnostic functions that inspect only validated fixture data."""

from __future__ import annotations

import re

from .models import DiagnosticEvidence, Incident

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|secret|api[_-]?key|authorization|database_url)\s*([=:])\s*([^\s,;]+)"
)
_URI_CREDENTIALS = re.compile(r"(?i)\b(postgres(?:ql)?|mysql|redis)://[^/@\s]+:[^/@\s]+@")


def _require_incident(incident: Incident) -> None:
    if not isinstance(incident, Incident):
        raise TypeError("diagnostic tools accept a validated Incident object")


def _redact(message: str) -> str:
    message = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", message)
    return _URI_CREDENTIALS.sub(lambda match: f"{match.group(1)}://[REDACTED]@", message)


def inspect_container_status(incident: Incident) -> DiagnosticEvidence:
    _require_incident(incident)
    status = incident.container_status
    details = [f"container state is {status.state}", f"restart count is {status.restart_count}"]
    if status.exit_code is not None:
        details.append(f"last exit code is {status.exit_code}")
    return DiagnosticEvidence(
        tool_name="inspect_container_status",
        summary=f"Container {status.name} is {status.state}.",
        details=tuple(details),
    )


def read_container_logs(incident: Incident, *, limit: int | None = None) -> DiagnosticEvidence:
    _require_incident(incident)
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100):
        raise ValueError("limit must be an integer between 1 and 100")
    selected = incident.logs if limit is None else incident.logs[:limit]
    details = tuple(f"{entry.timestamp} — {entry.level} — {_redact(entry.message)}" for entry in selected)
    if not details:
        summary = "No simulated log entries were supplied."
    else:
        count = f"{len(details)} of {len(incident.logs)}" if len(details) < len(incident.logs) else str(len(details))
        summary = f"Read {count} simulated log entr{'y' if len(details) == 1 else 'ies'}."
    return DiagnosticEvidence(tool_name="read_container_logs", summary=summary, details=details)


def inspect_environment_configuration(incident: Incident) -> DiagnosticEvidence:
    _require_incident(incident)
    config = incident.environment_configuration
    configured = set(config.configured_variables)
    missing = tuple(name for name in config.required_variables if name not in configured)
    if missing:
        label = "variable" if len(missing) == 1 else "variables"
        verb = "is" if len(missing) == 1 else "are"
        summary = f"{len(missing)} required environment {label} {verb} not configured."
        details = tuple(f"{name} is required but not configured" for name in missing)
    elif config.required_variables:
        summary = "All listed required environment variables are configured."
        details = (f"Checked {len(config.required_variables)} required variable name(s); values were not read.",)
    else:
        summary = "No required environment variables were listed."
        details = ("Configuration completeness cannot be assessed without a required-variable list.",)
    return DiagnosticEvidence(tool_name="inspect_environment_configuration", summary=summary, details=details)
