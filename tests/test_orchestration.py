import pytest

from agentic_devops import orchestration
from agentic_devops.loop import ToolRequest
from agentic_devops.models import Incident
from agentic_devops.orchestration import MAX_GRAPH_SUPERSTEPS, build_investigation_graph
from agentic_devops.registry import build_default_registry


def _run(graph, incident_data, *, thread_id="day-4-test"):
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": MAX_GRAPH_SUPERSTEPS,
    }
    updates = list(graph.stream({"incident_data": incident_data}, config, stream_mode="updates"))
    state = graph.get_state(config).values
    return updates, state, config


def test_graph_runs_named_nodes_and_collects_evidence_before_reporting(incident_data, expected_findings):
    graph = build_investigation_graph()
    updates, state, config = _run(graph, incident_data)
    node_names = [name for update in updates for name in update]

    assert node_names == [
        "triage",
        "collect_evidence",
        "collect_evidence",
        "collect_evidence",
        "diagnosis",
        "verification",
        "report",
    ]
    assert state["triage"]["incident_id"] == "SIM-DOCKER-001"
    assert [step["tool_name"] for step in state["steps"]] == [
        "inspect_container_status",
        "read_container_logs",
        "inspect_environment_configuration",
    ]
    assert state["diagnosis"]["status"] == "diagnosed"
    assert state["diagnosis"]["root_cause"] == expected_findings["expected_root_cause"]
    assert state["verification"]["passed"] is True
    assert state["verification"]["root_cause_verified"] is True
    assert "DATABASE_URL" in state["report_markdown"]
    assert graph.get_state(config).config["configurable"]["thread_id"] == "day-4-test"


def test_graph_routes_healthy_incident_from_evidence_to_diagnosis(incident_data):
    incident_data["container_status"].update(state="running", restart_count=0, exit_code=0)
    incident_data["logs"] = []
    updates, state, _ = _run(build_investigation_graph(), incident_data, thread_id="healthy-case")
    node_names = [name for update in updates for name in update]

    assert node_names == [
        "triage",
        "collect_evidence",
        "collect_evidence",
        "diagnosis",
        "verification",
        "report",
    ]
    assert state["stop_reason"] == "selector_finished"
    assert state["diagnosis"]["status"] == "insufficient_evidence"
    assert state["diagnosis"]["root_cause"] is None
    assert state["verification"]["passed"] is True


def test_graph_honors_smaller_tool_step_limit(incident_data):
    _, state, _ = _run(
        build_investigation_graph(max_tool_steps=2),
        incident_data,
        thread_id="short-budget",
    )

    assert len(state["steps"]) == 2
    assert state["stop_reason"] == "max_steps_reached"
    assert state["diagnosis"]["status"] == "insufficient_evidence"
    assert state["diagnosis"]["root_cause"] is None


@pytest.mark.parametrize("max_tool_steps", [0, 4, True, 1.5, "2"])
def test_graph_rejects_invalid_tool_step_limits(max_tool_steps):
    with pytest.raises(ValueError, match="max_tool_steps must be an integer"):
        build_investigation_graph(max_tool_steps=max_tool_steps)


def test_graph_retries_only_a_transient_connection_failure(monkeypatch, incident_data, incident):
    real_registry = build_default_registry(incident)
    call_count = 0

    class FlakyRegistry:
        def execute(self, name, arguments):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("temporary local test failure")
            return real_registry.execute(name, arguments)

    monkeypatch.setattr(orchestration, "build_default_registry", lambda _: FlakyRegistry())
    _, state, _ = _run(build_investigation_graph(), incident_data, thread_id="retry-case")

    assert call_count == 4  # one retry, then the three unique read-only checks
    assert len(state["steps"]) == 3
    assert state["diagnosis"]["status"] == "diagnosed"


def test_graph_rejects_unapproved_selector_tool(incident_data):
    class UnsafeSelector:
        def select_next(self, incident: Incident, evidence):
            return ToolRequest("run_shell", {"command": "whoami"}, "unsafe request")

    with pytest.raises(ValueError, match="not in the approved registry"):
        _run(
            build_investigation_graph(selector=UnsafeSelector()),
            incident_data,
            thread_id="unsafe-case",
        )
