from agentic_devops.models import Incident, IncidentValidationError
from agentic_devops.tools import (
    inspect_container_status,
    inspect_environment_configuration,
    read_container_logs,
)
import pytest


def test_status_tool_returns_structured_simulated_evidence(incident):
    evidence = inspect_container_status(incident)
    assert evidence.tool_name == "inspect_container_status"
    assert evidence.source == "simulated fixture"
    assert "container state is restarting" in evidence.details
    assert "restart count is 4" in evidence.details


def test_log_tool_handles_missing_entries(incident_data):
    incident_data["logs"] = []
    evidence = read_container_logs(Incident.from_dict(incident_data))
    assert evidence.details == ()
    assert "No simulated log entries" in evidence.summary


def test_configuration_tool_handles_missing_configuration(incident_data):
    incident_data["environment_configuration"]["required_variables"] = []
    incident_data["environment_configuration"]["configured_variables"] = []
    evidence = inspect_environment_configuration(Incident.from_dict(incident_data))
    assert "cannot be assessed" in evidence.details[0]


def test_configuration_tool_reports_names_but_never_values(incident):
    evidence = inspect_environment_configuration(incident)
    assert "DATABASE_URL is required but not configured" in evidence.details
    assert all("=" not in detail for detail in evidence.details)


def test_log_tool_redacts_secret_assignments(incident_data):
    incident_data["logs"] = [{
        "timestamp": "2026-10-12T09:15:00Z",
        "level": "ERROR",
        "message": "database_url=postgres://learner:do-not-print@localhost/orders",
    }]
    evidence = read_container_logs(Incident.from_dict(incident_data))
    rendered = " ".join(evidence.details)
    assert "do-not-print" not in rendered
    assert "[REDACTED]" in rendered


def test_shell_and_html_looking_log_text_is_inert_and_escaped(incident_data, tmp_path):
    marker = tmp_path / "should-not-exist"
    command_text = f"$(touch {marker}) <script>alert(1)</script>"
    incident_data["logs"] = [{"timestamp": "now", "level": "ERROR", "message": command_text}]
    incident = Incident.from_dict(incident_data)
    evidence = read_container_logs(incident)
    assert not marker.exists()
    assert "$(touch" in evidence.details[0]

    from agentic_devops.investigation import investigate
    from agentic_devops.cli import render_markdown

    report = render_markdown(investigate(incident))
    assert "&lt;script&gt;" in report
    assert "<script>" not in report
    assert not marker.exists()


def test_tools_reject_unvalidated_input():
    with pytest.raises(TypeError, match="validated Incident"):
        inspect_container_status({"state": "restarting"})


def test_environment_model_rejects_malformed_config(incident_data):
    incident_data["environment_configuration"]["configured_variables"] = "APP_ENV"
    with pytest.raises(IncidentValidationError, match="must be a list"):
        Incident.from_dict(incident_data)
