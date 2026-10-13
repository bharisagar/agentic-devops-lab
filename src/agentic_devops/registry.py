"""A small allowlisted registry for fixture-backed Day 2 diagnostic tools."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

from .models import DiagnosticEvidence, Incident
from .tools import (
    inspect_container_status,
    inspect_environment_configuration,
    read_container_logs,
)


class ToolInputError(ValueError):
    """Raised when a requested tool or its arguments are not allowed."""


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., DiagnosticEvidence]


class ToolRegistry:
    """Expose only approved diagnostic functions for one validated incident."""

    def __init__(self, incident: Incident) -> None:
        if not isinstance(incident, Incident):
            raise TypeError("ToolRegistry requires a validated Incident object")
        self._incident = incident
        self._definitions = {
            "inspect_container_status": ToolDefinition(
                name="inspect_container_status",
                description="Read the simulated container state, restart count, and exit code.",
                parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
                handler=inspect_container_status,
            ),
            "read_container_logs": ToolDefinition(
                name="read_container_logs",
                description="Read a bounded number of sanitized startup log entries from the fixture.",
                parameters={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of log entries to return (1–100). Defaults to 20.",
                            "minimum": 1,
                            "maximum": 100,
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
                handler=read_container_logs,
            ),
            "inspect_environment_configuration": ToolDefinition(
                name="inspect_environment_configuration",
                description="Compare required and configured variable names without reading values.",
                parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
                handler=inspect_environment_configuration,
            ),
        }

    def describe_tools(self) -> list[dict[str, Any]]:
        """Return provider-neutral JSON-schema-like tool descriptions."""
        return [
            {
                "name": definition.name,
                "description": definition.description,
                "parameters": deepcopy(definition.parameters),
            }
            for definition in self._definitions.values()
        ]

    def execute(self, name: str, arguments: Any) -> DiagnosticEvidence:
        """Validate a tool request before calling its fixture-only handler."""
        if not isinstance(name, str) or name not in self._definitions:
            raise ToolInputError("tool name is not in the approved registry")
        if not isinstance(arguments, dict):
            raise ToolInputError("tool arguments must be an object")

        definition = self._definitions[name]
        allowed = set(definition.parameters["properties"])
        unknown = set(arguments) - allowed
        if unknown:
            raise ToolInputError(f"unsupported argument(s): {', '.join(sorted(map(str, unknown)))}")

        if name == "read_container_logs":
            limit = arguments.get("limit", 20)
            if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
                raise ToolInputError("limit must be an integer between 1 and 100")
            return read_container_logs(self._incident, limit=limit)

        if arguments:
            # The schemas for the remaining tools intentionally accept no fields.
            raise ToolInputError("this tool does not accept arguments")
        return definition.handler(self._incident)


def build_default_registry(incident: Incident) -> ToolRegistry:
    """Create the Day 2 allowlist for one validated simulated incident."""
    return ToolRegistry(incident)
