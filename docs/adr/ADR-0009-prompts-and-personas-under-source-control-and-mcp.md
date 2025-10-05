
# ADR-0009: Prompts & Personas Are Source‑Controlled and Queried via MCP

## Status
Accepted

## Context
AI coding assistants depend on stable instructions. Untracked or ad‑hoc prompts
lead to inconsistent agent behavior and architectural drift. We need **versioned
prompts/personas** that agents can **query consistently**.

## Decision
- Store **prompts** under `src/goibniu/prompts/*.md` and **personas** under
  `src/goibniu/personas/*.json`.
- Expose them via MCP endpoints:
  - `GET /mcp/prompts` and `GET /mcp/prompts/{name}`
  - `GET /mcp/personas` and `GET /mcp/personas/{name}`
  - `GET /mcp/playbook` and `GET /mcp/capabilities` for overall guidance
- Agents must query the playbook and relevant prompts/personas **before planning
  and implementation**.

## Consequences
**Positive**
- Predictable, reviewable agent behavior (prompts in PRs)
- Easier to evolve guidance with code changes
- Shared language for humans and agents

**Negative**
- Requires maintaining prompt/persona quality and versioning
- Agents need to re‑sync when prompts change (intended)

## Operational Practice
- Bootstrap and refresh agent guidance:
  ```bash
  goibniu bootstrap-agent --base .
  ```

This creates:
`docs/goibniu_playbook.md`
`.ai-context/goibniu/playbook.yaml`
`.ai-context/goibniu/capabilities.json`
`AGENT_ONBOARDING.md`

Serve to agents:
```bash
goibniu start-mcp --base . --host 0.0.0.0 --port 8000
# Agents query /mcp/playbook and /mcp/capabilities first.
```

## Validation
- `/mcp/prompts`, `/mcp/personas`, `/mcp/playbook`, and `/mcp/capabilities`
  respond successfully in local and CI environments.
- Prompt/persona changes are reviewed in PRs alongside code.
