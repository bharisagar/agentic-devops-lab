"""Command-line interface for the local, fixture-only investigator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Sequence

from .investigation import investigate
from .models import Incident, IncidentValidationError

DEFAULT_INCIDENT = Path(__file__).resolve().parents[2] / "scenarios" / "container-restart" / "incident.json"


def _safe_markdown_text(value: str) -> str:
    """Keep fixture text inert when a report is opened in a Markdown viewer."""
    escaped = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("`", "&#96;")
    escaped = re.sub(r"([\\*!\[\]])", r"\\\1", escaped)
    return " ".join(escaped.splitlines())


def render_markdown(report) -> str:
    lines = [
        f"# Investigation report: {_safe_markdown_text(report.title)}",
        "",
        f"- **Incident:** `{_safe_markdown_text(report.incident_id)}`",
        f"- **Status:** {_safe_markdown_text(report.status)}",
        "- **Data source:** simulated fixture only",
        "",
        "## Root cause",
        "",
        _safe_markdown_text(report.root_cause or "Not determined from the supplied evidence."),
        "",
        "## Evidence",
        "",
    ]
    for item in report.evidence:
        lines.append(f"### {_safe_markdown_text(item.tool_name)}")
        lines.append("")
        lines.append(_safe_markdown_text(item.summary))
        lines.extend(f"- {_safe_markdown_text(detail)}" for detail in item.details)
        lines.append("")
    lines.extend(["## Recommended next step", "", _safe_markdown_text(report.recommended_fix), "", "## Prevention", ""])
    if report.prevention:
        lines.extend(f"- {_safe_markdown_text(item)}" for item in report.prevention)
    else:
        lines.append("No preventive action is asserted until more evidence is available.")
    lines.extend(["", "## Uncertainty and limitations", "", _safe_markdown_text(report.uncertainty), ""])
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Investigate an explicitly simulated incident fixture.")
    parser.add_argument("--incident", type=Path, default=DEFAULT_INCIDENT, help="Path to a simulated incident JSON file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Report output format")
    args = parser.parse_args(argv)
    try:
        raw = json.loads(args.incident.read_text(encoding="utf-8"))
        incident = Incident.from_dict(raw)
        report = investigate(incident)
    except (OSError, json.JSONDecodeError, IncidentValidationError, TypeError) as exc:
        print(f"Could not investigate incident: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
