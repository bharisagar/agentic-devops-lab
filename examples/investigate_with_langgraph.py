"""Run the Day 4 LangGraph workflow on the local simulated incident."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from agentic_devops.orchestration import MAX_GRAPH_SUPERSTEPS, build_investigation_graph

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCIDENT = ROOT / "scenarios" / "container-restart" / "incident.json"


def main() -> int:
    incident_data = json.loads(DEFAULT_INCIDENT.read_text(encoding="utf-8"))
    graph = build_investigation_graph()
    config = {
        "configurable": {"thread_id": f"day-4-{uuid4()}"},
        "recursion_limit": MAX_GRAPH_SUPERSTEPS,
    }

    print("# Day 4 LangGraph execution\n")
    for update in graph.stream({"incident_data": incident_data}, config, stream_mode="updates"):
        for node_name in update:
            print(f"- {node_name}")

    state = graph.get_state(config).values
    print(f"\nInvestigation stop reason: `{state['stop_reason']}`")
    print(f"Verification: `{state['verification']['passed']}`")
    print(f"Tools executed: {len(state['steps'])}\n")
    print(state["report_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
