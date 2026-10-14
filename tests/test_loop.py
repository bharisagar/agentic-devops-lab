import pytest

from agentic_devops.loop import (
    MAX_INVESTIGATION_STEPS,
    ToolRequest,
    investigate_with_loop,
)
from agentic_devops.registry import ToolInputError
from agentic_devops.models import Incident


def test_loop_selects_tools_from_evidence_and_diagnoses_known_incident(incident, expected_findings):
    result = investigate_with_loop(incident)

    assert [step.tool_name for step in result.steps] == [
        "inspect_container_status",
        "read_container_logs",
        "inspect_environment_configuration",
    ]
    assert "restart count" in result.steps[1].rationale.lower()
    assert "configuration" in result.steps[2].rationale
    assert result.stop_reason == "max_steps_reached"
    assert result.report.status == "diagnosed"
    assert result.report.root_cause == expected_findings["expected_root_cause"]
    assert len(result.steps) <= MAX_INVESTIGATION_STEPS


def test_healthy_status_stops_before_collecting_unneeded_evidence(incident_data):
    incident_data["container_status"].update(state="running", restart_count=0, exit_code=0)
    incident_data["logs"] = []
    result = investigate_with_loop(Incident.from_dict(incident_data))

    assert [step.tool_name for step in result.steps] == ["inspect_container_status"]
    assert result.stop_reason == "selector_finished"
    assert result.report.status == "insufficient_evidence"
    assert result.report.root_cause is None


def test_step_limit_produces_partial_report_without_inventing_a_cause(incident):
    result = investigate_with_loop(incident, max_steps=2)

    assert len(result.steps) == 2
    assert result.stop_reason == "max_steps_reached"
    assert result.report.status == "insufficient_evidence"
    assert result.report.root_cause is None
    assert all(item.tool_name != "inspect_environment_configuration" for item in result.report.evidence)


@pytest.mark.parametrize("max_steps", [0, 4, True, 1.5, "2"])
def test_loop_rejects_invalid_step_limits(incident, max_steps):
    with pytest.raises(ValueError, match="max_steps must be an integer"):
        investigate_with_loop(incident, max_steps=max_steps)


def test_loop_stops_if_a_selector_repeats_a_completed_tool(incident):
    class RepeatingSelector:
        def select_next(self, incident, evidence):
            return ToolRequest("inspect_container_status", {}, "repeat for test")

    result = investigate_with_loop(incident, selector=RepeatingSelector())

    assert len(result.steps) == 1
    assert result.stop_reason == "repeated_tool_request"


def test_registry_rejects_unapproved_tool_proposed_by_selector(incident):
    class UnsafeSelector:
        def select_next(self, incident, evidence):
            if not evidence:
                return ToolRequest("run_shell", {"command": "whoami"}, "unsafe test request")
            return None

    with pytest.raises(ToolInputError, match="not in the approved registry"):
        investigate_with_loop(incident, selector=UnsafeSelector())


def test_loop_rejects_selector_return_type_outside_contract(incident):
    class InvalidSelector:
        def select_next(self, incident, evidence):
            return {"name": "inspect_container_status"}

    with pytest.raises(TypeError, match="ToolRequest or None"):
        investigate_with_loop(incident, selector=InvalidSelector())
