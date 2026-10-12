import json
from pathlib import Path

from agentic_devops.cli import main, render_markdown
from agentic_devops.investigation import investigate
from agentic_devops.models import Incident


def test_identifies_known_root_cause_and_expected_evidence(incident, expected_findings):
    report = investigate(incident)
    evidence_text = " ".join(detail for item in report.evidence for detail in item.details)
    assert report.status == "diagnosed"
    assert report.root_cause == expected_findings["expected_root_cause"]
    for expected in expected_findings["required_evidence"]:
        assert expected in evidence_text
    assert "secret-management" in report.recommended_fix
    assert report.prevention == tuple(expected_findings["preventive_measures"])


def test_does_not_assert_a_root_cause_when_logs_do_not_confirm_it(incident_data):
    incident_data["logs"] = [{"timestamp": "now", "level": "ERROR", "message": "Application failed to start"}]
    report = investigate(Incident.from_dict(incident_data))
    assert report.status == "insufficient_evidence"
    assert report.root_cause is None
    assert not report.prevention


def test_does_not_assert_a_root_cause_without_restart_evidence(incident_data):
    incident_data["container_status"]["state"] = "running"
    incident_data["container_status"]["restart_count"] = 0
    report = investigate(Incident.from_dict(incident_data))
    assert report.status == "insufficient_evidence"
    assert report.root_cause is None


def test_markdown_report_contains_finding_evidence_and_limits(incident):
    report_text = render_markdown(investigate(incident))
    assert "DATABASE_URL" in report_text
    assert "simulated fixture" in report_text
    assert "Uncertainty and limitations" in report_text


def test_cli_prints_readable_report(capsys):
    assert main([]) == 0
    output = capsys.readouterr().out
    assert "Investigation report" in output
    assert "DATABASE_URL" in output


def test_cli_supports_json_output(capsys):
    assert main(["--format", "json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "diagnosed"
    assert output["incident_id"] == "SIM-DOCKER-001"


def test_cli_rejects_invalid_input_with_nonzero_status(tmp_path: Path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text('{"simulated": false}', encoding="utf-8")
    assert main(["--incident", str(path)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "simulated fixtures only" in captured.err
