"""Validated data models for simulated Day 1 incidents."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import re


class IncidentValidationError(ValueError):
    """Raised when an incident fixture does not match the expected schema."""


def _text(value: Any, field: str, *, limit: int = 2_000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IncidentValidationError(f"{field} must be a non-empty string")
    if len(value) > limit:
        raise IncidentValidationError(f"{field} must be {limit} characters or fewer")
    return value.strip()


def _name_list(value: Any, field: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value):
        requirement = "a non-empty list" if not allow_empty else "a list"
        raise IncidentValidationError(f"{field} must be {requirement}")
    if len(value) > 200:
        raise IncidentValidationError(f"{field} contains too many entries")
    result: list[str] = []
    for item in value:
        name = _text(item, field, limit=100)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise IncidentValidationError(f"{field} entries must be environment-variable names")
        if name not in result:
            result.append(name)
    return tuple(result)


@dataclass(frozen=True)
class ContainerStatus:
    name: str
    state: str
    restart_count: int
    exit_code: int | None

    @classmethod
    def from_dict(cls, value: Any) -> "ContainerStatus":
        if not isinstance(value, dict):
            raise IncidentValidationError("container_status must be an object")
        name = _text(value.get("name"), "container_status.name", limit=120)
        state = _text(value.get("state"), "container_status.state", limit=40).lower()
        if state not in {"running", "restarting", "exited", "unknown"}:
            raise IncidentValidationError("container_status.state must be running, restarting, exited, or unknown")
        restart_count = value.get("restart_count")
        if isinstance(restart_count, bool) or not isinstance(restart_count, int) or restart_count < 0:
            raise IncidentValidationError("container_status.restart_count must be a non-negative integer")
        exit_code = value.get("exit_code")
        if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
            raise IncidentValidationError("container_status.exit_code must be an integer or null")
        return cls(name=name, state=state, restart_count=restart_count, exit_code=exit_code)


@dataclass(frozen=True)
class LogEntry:
    timestamp: str
    level: str
    message: str

    @classmethod
    def from_dict(cls, value: Any, index: int) -> "LogEntry":
        if not isinstance(value, dict):
            raise IncidentValidationError(f"logs[{index}] must be an object")
        return cls(
            timestamp=_text(value.get("timestamp"), f"logs[{index}].timestamp", limit=80),
            level=_text(value.get("level"), f"logs[{index}].level", limit=20).upper(),
            message=_text(value.get("message"), f"logs[{index}].message", limit=2_000),
        )


@dataclass(frozen=True)
class EnvironmentConfiguration:
    required_variables: tuple[str, ...]
    configured_variables: tuple[str, ...]
    values_included: bool

    @classmethod
    def from_dict(cls, value: Any) -> "EnvironmentConfiguration":
        if not isinstance(value, dict):
            raise IncidentValidationError("environment_configuration must be an object")
        values_included = value.get("values_included")
        if values_included is not False:
            raise IncidentValidationError("environment variable values must not be included in Day 1 fixtures")
        return cls(
            required_variables=_name_list(value.get("required_variables"), "required_variables"),
            configured_variables=_name_list(value.get("configured_variables"), "configured_variables"),
            values_included=False,
        )


@dataclass(frozen=True)
class Incident:
    incident_id: str
    title: str
    service: str
    environment: str
    description: str
    simulated: bool
    container_status: ContainerStatus
    logs: tuple[LogEntry, ...]
    environment_configuration: EnvironmentConfiguration

    @classmethod
    def from_dict(cls, value: Any) -> "Incident":
        if not isinstance(value, dict):
            raise IncidentValidationError("incident must be a JSON object")
        if value.get("simulated") is not True:
            raise IncidentValidationError("Day 1 accepts simulated fixtures only; set simulated to true")
        logs_value = value.get("logs")
        if not isinstance(logs_value, list) or len(logs_value) > 1_000:
            raise IncidentValidationError("logs must be a list with no more than 1000 entries")
        return cls(
            incident_id=_text(value.get("incident_id"), "incident_id", limit=100),
            title=_text(value.get("title"), "title", limit=200),
            service=_text(value.get("service"), "service", limit=120),
            environment=_text(value.get("environment"), "environment", limit=120),
            description=_text(value.get("description"), "description"),
            simulated=True,
            container_status=ContainerStatus.from_dict(value.get("container_status")),
            logs=tuple(LogEntry.from_dict(item, index) for index, item in enumerate(logs_value)),
            environment_configuration=EnvironmentConfiguration.from_dict(value.get("environment_configuration")),
        )


@dataclass(frozen=True)
class DiagnosticEvidence:
    tool_name: str
    summary: str
    details: tuple[str, ...]
    source: str = "simulated fixture"


@dataclass(frozen=True)
class InvestigationReport:
    incident_id: str
    title: str
    status: str
    root_cause: str | None
    evidence: tuple[DiagnosticEvidence, ...]
    recommended_fix: str
    prevention: tuple[str, ...]
    uncertainty: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
