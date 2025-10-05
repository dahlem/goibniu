# ADR-0003: Version the Design Context Under `.ai-context/`

## Status
Accepted

## Context
Agents and reviewers need a **shared, versioned source of truth** for system
design, component structure, and API contracts. When this context is generated
locally but not versioned, it drifts from the code; agents operate on stale
assumptions and reviewers can’t see how design evolves alongside implementation.

## Decision
- We will generate **system**, **component**, and **API** documentation into a
  **versioned** directory: `.ai-context/`.
- This directory will be **committed to the repository** and refreshed as part
  of routine workflows (pre‑commit on push and in CI).
- Agents will read from `.ai-context/` (or MCP endpoints backed by it) as the
  canonical design context.

### Required contents
At minimum:
- `.ai-context/system.yaml` — service‑level summary
- `.ai-context/components/*.yaml` — per‑component docs
- `.ai-context/contracts/*.openapi.yaml` — OpenAPI contracts used for API
  compliance

## Consequences
**Positive**
- Shared truth for humans and agents
- Diffable design evolution in PRs
- Reliable inputs for ADR and API compliance checks

**Negative**
- Slight maintenance overhead to refresh context
- Spec hygiene is required (OpenAPI kept up to date)

## Operational practice
- **Local**: `goibniu generate-docs --root . --out .ai-context`
- **Pre‑commit (push stage)**: regenerate `.ai-context/` and commit if changed
- **CI**: regenerate and run `goibniu check-compliance` + `goibniu check-api`

## Rule (machine-checkable)
> Prevent ignoring `.ai-context/` in `.gitignore`.

```yaml
goibniu_rule:
  id: ADR-0003
  description: Do not ignore .ai-context/ in .gitignore (context must be versioned)
  patterns:
    any: [".ai-context"]
    all: []
  paths:
    include: [".gitignore"]
    exclude: []
```

## Validation
- `goibniu generate-docs --root . --out .ai-context produces files as above`
- `goibniu check-compliance --root . passes`
- `goibniu check-api --root . --specdir .ai-context/contracts passes`

## Related
- ADR‑0001: Establish Goibniu as Architecture Governance & Guardrails
- ADR‑0005: Enforce API Correctness with OpenAPI + Static Client Checks
- ADR‑0009: Prompts & Personas are Source‑of‑Truth and Queried via MCP
