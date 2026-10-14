"""Run the Day 3 bounded investigation loop on a simulated fixture."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_devops.cli import render_markdown
from agentic_devops.loop import investigate_with_loop
from agentic_devops.models import Incident

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCIDENT = ROOT / "scenarios" / "container-restart" / "incident.json"


def main() -> int:
    raw = json.loads(DEFAULT_INCIDENT.read_text(encoding="utf-8"))
    result = investigate_with_loop(Incident.from_dict(raw))

    print("# Day 3 investigation trace\n")
    for step in result.steps:
        print(f"{step.number}. **{step.tool_name}**")
        print(f"   - Why: {step.rationale}")
        print(f"   - Evidence: {step.evidence_summary}")
    print(f"\nStopped: `{result.stop_reason}`\n")
    print(render_markdown(result.report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
