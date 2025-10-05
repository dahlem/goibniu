# ADR-0001: Establish Goibniu as Architecture Governance & Guardrails

## Status
Accepted

## Context
AI coding assistants accelerate development but can erode architectural integrity if they work without context or guardrails. We need a standardized, queriable way to capture system design, decisions, and API contracts—and to enforce them in local workflows and CI.

## Decision
Adopt Goibniu as the repository’s architecture governance layer:
- Generate system/component/API context under `.ai-context/`
- Encode architecture decisions as ADRs (`docs/adr/*.md`)
- Enforce ADR rules via `goibniu check-compliance`
- Enforce API correctness via `goibniu check-api`
- Provide agent-facing MCP endpoints and prompts/personas

## Consequences
- Positive: Faster, safer iteration; decisions don’t get lost; agents behave responsibly.
- Negative: Slight overhead to keep `.ai-context` and OpenAPI specs current; ADR hygiene required.
