# Goibniu 🛠️

**Pronounced:** **GOV‑new** (IPA: **/ˈɡɪv.nʲu/**)

> Goibniu is the mythic **Irish god of the forge**, famed for crafting tools
> that never failed. This project adopts that spirit: precise tooling that keeps
> engineering work aligned with architectural intent—**even when AI coding
> assistants help build it.**

---

## Abstract

### 1) Big picture motivation

AI coding assistants are getting good at writing code, but they don't
automatically understand your **architecture**, **APIs**, or **decisions**.
Teams need a way to **retain architectural integrity** and **prevent
drift**—without blocking the speed benefits of automation.

### 2) Specifics of the problem/opportunity

Common failure modes:

* **Decision entropy**: architectural choices get lost across time/teams.
* **Interface drift**: code changes break implicit boundaries.
* **Hallucinated APIs**: agents call endpoints that don't exist.
* **Missing context**: agents don't know where to look for design/ADRs.

Opportunity: centralize design context and guardrails in a **standard, queriable
format**. Use it to guide both humans and agents—locally, in CI, and via a
simple HTTP interface.

### 3) Approach to tackle it

Goibniu integrates four pillars:

1. **Documentation extraction** → Generate system, component, and API docs into
   `.ai-context/`.
2. **Decision enforcement** → Encode **ADR** rules (lightweight YAML) and **fail
   fast** on violations.
3. **API compliance** → Statically check HTTP client calls against **OpenAPI**;
   block hallucinated endpoints.
4. **Agent‑ready interfaces** → **MCP** endpoints + **prompts/personas** +
   **playbook** to instruct agents when/how to consult context and guardrails.

### 4) Reintegration with the big picture

With Goibniu in the loop, teams get **fast iterations** without surrendering
**architecture, safety, and coherence**. Humans remain in control (RFE/human
review gates), while agents become **reliable, context‑aware collaborators**.

---

## What this repository provides (technical overview)

* **CLI**: `goibniu` with subcommands:

  * `generate-docs` → extract **system**, **components**, **OpenAPI** → `.ai-context/`
  * `check-compliance` → check **ADR** rules (from `docs/adr/*.md`)
  * `check-api` → static **API compliance** against `.ai-context/contracts/*.openapi.yaml`
  * `bootstrap-adr` → create a new ADR skeleton
  * `generate-rfe` → create **RFE** file when ADRs are (or may be) violated
  * `bootstrap-agent` → create **playbook**, **capabilities** catalog, and **agent onboarding** doc
  * `capabilities`, `list-prompts`, `prompt` → discover & view Goibniu content
* **MCP server** (`start-mcp`) to serve design context and guidance to agents:

  * `/mcp/system`, `/mcp/components/{name}`, `/mcp/apis/{name}`
  * `/mcp/adrs`, `/mcp/prompts`, `/mcp/personas`
  * `/mcp/playbook`, `/mcp/capabilities`
* **Prompts & personas**: agent‑ready instructions with **motivation**,
  **checklists**, and **acceptance criteria**.
* **ADR rules**: ADRs can embed **machine‑checkable** policies using a simple
  `goibniu_rule` block.
* **CI hooks**: GitHub Actions & **pre‑commit** examples to enforce guardrails
  automatically.

---

## Quick start (maintainer's checklist)

> Requires Python **3.12+**.

```bash
# 1) Install Goibniu in this repo (dev mode recommended)
pip install -e .

# 2) Generate design context (system, components, API)
goibniu generate-docs --root . --out .ai-context

# 3) Enforce ADRs (fails if rules are violated)
goibniu check-compliance --root .

# 4) Enforce API correctness (prevents hallucinated endpoints)
goibniu check-api --root . --specdir .ai-context/contracts

# 5) Optional: expose MCP endpoints for agents
goibniu start-mcp --base . --host 0.0.0.0 --port 8000
```

---

## The playbook and agent onboarding

**Why?** Agents need to know *when* to look up design, *when* to check ADRs, and
*when* to stop and request human review.

Create a **queriable playbook** + onboarding files:

```bash
goibniu bootstrap-agent --base .
```

This generates:

* `docs/goibniu_playbook.md` (human-readable playbook)
* `.ai-context/goibniu/playbook.yaml` (machine-readable playbook)
* `.ai-context/goibniu/capabilities.json` (CLI, MCP, prompts, personas)
* `AGENT_ONBOARDING.md` (agent-friendly quickstart)

**Agents should:**

1. Query `/mcp/capabilities` and `/mcp/playbook` (understand tools & guardrails)
2. Read `/mcp/system`, `/mcp/prompts/design_review`
3. Run `check-compliance` & `check-api`
4. If an ADR is at risk: **STOP**, `generate-rfe`, wait for human approval

---

## ADRs: how to create and enforce

### Create an ADR (skeleton)

```bash
goibniu bootstrap-adr "Use FastAPI for internal APIs"
# -> docs/adr/ADR-000X-use-fastapi-for-internal-apis.md
```

### Add a machine‑checkable rule (optional, recommended)

Inside the ADR's markdown, add a fenced YAML block:

```yaml
goibniu_rule:
  id: ADR-0001
  description: Avoid python eval() in application code
  patterns:
    any: ["eval("]      # flag if ANY appear
    all: []             # flag only if ALL appear (advanced)
  paths:
    include: ["**/*.py"]
    exclude: ["tests/**"]
```

### Enforce ADRs (local + CI)

```bash
goibniu check-compliance --root .
```

If a proposal conflicts with an ADR:

```bash
goibniu generate-rfe ADR-0001 "Allow dynamic expressions only in admin ETL jobs"
# -> docs/rfes/RFE-ADR-0001-allow-dynamic-expressions-only-in-admin-etl-jobs.md
# Hand off to human reviewers and update ADRs accordingly if approved.
```

---

## API compliance: block hallucinated endpoints

Goibniu statically scans `requests`/`httpx` calls and checks them against your
**OpenAPI** specs in `.ai-context/contracts/`.

```bash
# Generate/refresh contracts (via goibniu generate-docs or your own build)
goibniu generate-docs --root . --out .ai-context

# Verify client calls match documented endpoints
goibniu check-api --root . --specdir .ai-context/contracts
```

It flags:

* **Unknown endpoint** (method+path not in spec)
* **Missing required query params**
* **Missing request body** where the spec requires one

> Tip: Keep your OpenAPI specs up to date (FastAPI apps can emit them with
> `app.openapi()`).

---

## MCP endpoints (for agents)

Start the server:

```bash
goibniu start-mcp --base . --host 0.0.0.0 --port 8000
```

Useful endpoints:

* `GET /mcp/playbook` → the protocol and guardrails (YAML or MD)
* `GET /mcp/capabilities` → what Goibniu offers (CLI, MCP, prompts, personas)
* `GET /mcp/system` → system design snapshot
* `GET /mcp/components/{name}` → component doc
* `GET /mcp/apis/{name}` → OpenAPI for a module/service
* `GET /mcp/adrs` → list of ADR files
* `GET /mcp/prompts`, `GET /mcp/prompts/{name}` → prompts with checklists & acceptance criteria
* `GET /mcp/personas`, `GET /mcp/personas/{name}` → agent personas

Agents can adapt behavior as the playbook and capabilities evolve in this repo.

---

## GitHub Actions (CI) and pre‑commit

### CI (recommended)

Add to `.github/workflows/goibniu-ci.yml`:

```yaml
name: Goibniu CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e .
      - name: Generate design context
        run: goibniu generate-docs --root . --out .ai-context
      - name: ADR compliance
        run: goibniu check-compliance --root .
      - name: API compliance
        run: goibniu check-api --root . --specdir .ai-context/contracts
      - name: Run tests
        run: |
          pip install pytest
          pytest -q
```

### pre‑commit (local developer guardrails)

Create **`.pre-commit-config.yaml`** at repo root:

```yaml
repos:
  - repo: local
    hooks:
      - id: goibniu-adr
        name: Goibniu ADR compliance
        entry: goibniu
        args: ["check-compliance", "--root", "."]
        language: system
        pass_filenames: false
        stages: [commit]
      - id: goibniu-api
        name: Goibniu API compliance
        entry: goibniu
        args: ["check-api", "--root", ".", "--specdir", ".ai-context/contracts"]
        language: system
        pass_filenames: false
        stages: [commit]
      - id: goibniu-generate
        name: Goibniu generate design context
        entry: goibniu
        args: ["generate-docs", "--root", ".", "--out", ".ai-context"]
        language: system
        pass_filenames: false
        stages: [push]
```

Then:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

> Note: If `generate-docs` updates `.ai-context/`, the push is blocked until you
> stage and commit the changes—by design.

---

## What to commit to the repo

* `docs/adr/*.md` (and `docs/rfes/*.md` as created)
* `.ai-context/**` (generated design/context; keep it versioned so agents and
  reviewers share the same truth)
* `.pre-commit-config.yaml`, `.github/workflows/*`
* `AGENT_ONBOARDING.md`, `docs/goibniu_playbook.md` (from `bootstrap-agent`)

---

## Design philosophy (name & origins)

**Goibniu** (GOV‑new) is the **Irish god of craftsmanship**, whose tools and feasts sustained the Tuatha Dé Danann in battle. The metaphor is intentional:
- *Forge precise tools* → CLI, compliance checks, MCP.
- *Enduring craftsmanship* → ADRs and contracts persist beyond individuals and
  sprints.
- *Feeding the effort* → Prompts, personas, and a queriable playbook “feed”
  agents the right information and timing.

We apply this philosophy to modern engineering:
- *Why*: Preserve architectural integrity without sacrificing speed.
- *What*: A coherent system to encode decisions, expose design, and verify behavior.
- *How*: Static analysis + ADR rules + OpenAPI checks + agent‑ready interfaces.
- *So what*: Reliable autonomy and learnable change, at the pace of modern teams.

---

## Troubleshooting

- **“Unknown endpoint” in `check-api`** Ensure
  `.ai-context/contracts/*.openapi.yaml` are up to date. If you're changing an
  API, update the spec (or propose one via RFE) before implementing callers.

- **Compliance keeps failing on a new pattern** Create an RFE with `goibniu
  generate-rfe ...`, discuss, and—if accepted—**update or add an ADR** with a
  corresponding `goibniu_rule`.

- **Pre‑commit blocks a push** Stage and commit the updated `.ai-context/`
  files—that's the point: design context stays versioned with code.

---

## License

MIT

---

**Ready to use Goibniu?**
Run `goibniu bootstrap-agent`, commit the playbook, and let your agents query
`/mcp/capabilities` and `/mcp/playbook`. From there, they'll know *when* to
consult design, *how* to plan, and *when* to pause for human judgment.
