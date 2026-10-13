# Agentic DevOps Lab

Hi, I’m Bhari. This repository is a hands-on learning series for DevOps engineers who want to understand how an AI system can investigate operational incidents using approved tools and evidence.

We’ll build one simulated `orders-api` container-restart investigation over several days. We begin with a deterministic local example, add validated diagnostic tools, and then grow toward model-assisted investigation, runbook retrieval, evaluation, and an optional AWS architecture. Every lesson explains the idea before extending the code.

## Learn one day at a time

- [Day 1: Foundation](days/day-01-foundation/README.md) — understand the incident, system architecture, and the difference between a chatbot, script, and agent.
- [Day 2: Safe tools and clear contracts](days/day-02-safe-tools/README.md) — inspect the tool registry, schemas, argument validation, and evidence screenshot.
- [Full learning roadmap](docs/learning-roadmap.md)

More day folders will be added as each lesson is ready. Shared application code stays under `src/`, synthetic incident fixtures under `scenarios/`, and automated checks under `tests/` so learners can compare how the same project changes from one day to the next.

## Repository map

```text
days/
  day-01-foundation/       Lesson 1: concepts and starting architecture
  day-02-safe-tools/       Lesson 2: schemas, validation, and screenshot
src/agentic_devops/        Shared investigator and approved tools
scenarios/                 Synthetic incidents and expected test findings
tests/                     Unit, behavior, and safety tests
docs/                      Architecture, roadmap, and security notes
agentic-devops-notes/       Longer concept guides and optional advanced lesson
```

## Run the lab

From the repository root, install the project and its development dependency:

```powershell
python -m pip install -e ".[dev]"
```

Run the deterministic example and tests:

```powershell
python examples/investigate_incident.py
python -m pytest
```

The current demo uses only synthetic fixture data. It does not connect to Docker, AWS, an AI model, or an external service. It cannot execute shell commands or change infrastructure.

## Explore the design

- [System architecture](docs/architecture.md)
- [Security model](docs/security-model.md)
- [Agentic DevOps concept notes](agentic-devops-notes/README.md)
