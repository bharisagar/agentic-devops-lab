import pytest

from agentic_devops.registry import ToolInputError, build_default_registry


def test_registry_exposes_only_three_read_only_tools(incident):
    registry = build_default_registry(incident)
    descriptions = registry.describe_tools()

    assert {item["name"] for item in descriptions} == {
        "inspect_container_status",
        "read_container_logs",
        "inspect_environment_configuration",
    }
    assert all(item["parameters"]["additionalProperties"] is False for item in descriptions)


def test_registry_validates_arguments_and_limits_log_output(incident):
    registry = build_default_registry(incident)

    evidence = registry.execute("read_container_logs", {"limit": 1})

    assert len(evidence.details) == 1
    assert "1 of 3" in evidence.summary


@pytest.mark.parametrize("arguments", [None, [], "{}"])
def test_registry_rejects_non_object_arguments(incident, arguments):
    with pytest.raises(ToolInputError, match="must be an object"):
        build_default_registry(incident).execute("inspect_container_status", arguments)


@pytest.mark.parametrize("limit", [0, 101, True, 1.5, "2"])
def test_registry_rejects_invalid_log_limits(incident, limit):
    with pytest.raises(ToolInputError, match="limit must be an integer"):
        build_default_registry(incident).execute("read_container_logs", {"limit": limit})


def test_registry_rejects_unknown_arguments(incident):
    with pytest.raises(ToolInputError, match="unsupported argument"):
        build_default_registry(incident).execute("inspect_container_status", {"command": "docker ps"})


@pytest.mark.parametrize("name", ["run_shell", "docker_exec", "terraform_apply", ""])
def test_registry_rejects_tools_outside_allowlist(incident, name):
    with pytest.raises(ToolInputError, match="not in the approved registry"):
        build_default_registry(incident).execute(name, {})


def test_registry_requires_validated_incident(incident_data):
    with pytest.raises(TypeError, match="validated Incident"):
        build_default_registry(incident_data)
