import pytest

from agentic_devops.models import Incident, IncidentValidationError


def test_parses_simulated_incident(incident):
    assert incident.incident_id == "SIM-DOCKER-001"
    assert incident.simulated is True
    assert incident.container_status.restart_count == 4
    assert len(incident.logs) == 3


def test_rejects_non_object_incident():
    with pytest.raises(IncidentValidationError, match="JSON object"):
        Incident.from_dict([])


def test_rejects_non_simulated_incident(incident_data):
    incident_data["simulated"] = False
    with pytest.raises(IncidentValidationError, match="simulated fixtures only"):
        Incident.from_dict(incident_data)


@pytest.mark.parametrize("bad_count", [-1, True, "4"])
def test_rejects_invalid_restart_count(incident_data, bad_count):
    incident_data["container_status"]["restart_count"] = bad_count
    with pytest.raises(IncidentValidationError, match="non-negative integer"):
        Incident.from_dict(incident_data)


def test_rejects_environment_values(incident_data):
    incident_data["environment_configuration"]["values_included"] = True
    with pytest.raises(IncidentValidationError, match="values must not be included"):
        Incident.from_dict(incident_data)


def test_rejects_invalid_environment_variable_name(incident_data):
    incident_data["environment_configuration"]["required_variables"] = ["DATABASE_URL; rm -rf /"]
    with pytest.raises(IncidentValidationError, match="environment-variable names"):
        Incident.from_dict(incident_data)
