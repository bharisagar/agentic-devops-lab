import json
from pathlib import Path

import pytest

from agentic_devops.models import Incident

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "scenarios" / "container-restart"


@pytest.fixture
def incident_data():
    return json.loads((SCENARIO / "incident.json").read_text(encoding="utf-8"))


@pytest.fixture
def incident(incident_data):
    return Incident.from_dict(incident_data)


@pytest.fixture
def expected_findings():
    return json.loads((SCENARIO / "expected-findings.json").read_text(encoding="utf-8"))
