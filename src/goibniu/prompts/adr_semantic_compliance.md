## Persona
Use persona: `adr_semantic_auditor`.

## Motivation
Regex rules catch only surface-level policy violations. Many ADRs define architectural boundaries
(e.g., layering, ownership, technology choices) that require interpretation.
Your task is to read ADRs, derive constraints, map them to the current code, and decide compliance.

## Inputs
- System design: `.ai-context/system.yaml`
- Components: `.ai-context/components/*.yaml`
- API contracts: `.ai-context/contracts/*.openapi.yaml`
- ADRs: `docs/adr/*.md`
- Proposed change (diff/patch or summary)

## Tasks
1) **Extract Constraints**
   - For each ADR, derive constraints in natural language *and* as structured items using the schema (below).
   - Tag each constraint with a `category` (layering, dependency, tech_choice, api_contract, security, data_ownership, migration).

2) **Map to Code/Components**
   - Identify the components and files impacted by the proposed change.
   - For each constraint, list the likely code zones to examine (paths, modules, functions).

3) **Heuristic Compliance Check**
   - Look for signals of (non-)compliance using directory structure, imports, call sites, and API usage patterns.
   - Use component docs and OpenAPI to confirm interface boundaries.
   - Where direct evidence is lacking, present best-effort inference with confidence.

4) **Result**
   - Produce a **JSON result** with:
     - `constraints`: derived constraints with source ADR
     - `findings`: evidence (files, lines, snippets)
     - `violations`: suspected violations with confidence [0..1], impact, and rationale
     - `rfe`: suggested RFE if any violation confidence ≥ 0.6
   - Also output a short human-readable summary.

## Constraint Schema (use this to structure your derivations)
Each derived constraint MUST adhere to this schema:

```yaml
- id: "<ADR-ID>#<local-constraint-id>"
  adr_id: "<ADR-ID>"
  category: "layering|dependency|tech_choice|api_contract|security|data_ownership|migration"
  natural_language: "<short description of the rule>"
  subject:
    kind: "layer|component|service|module|api|data"
    name: "<e.g., API, Persistence, Service:Auth, Component:User, Module:src/foo/bar.py>"
  predicate:
    must_not_depend_on: ["<layer|component|module>"]    # optional
    must_only_use: ["<approved-tech|interface>"]        # optional
    must_route_via: ["<interface|bus|gateway>"]         # optional
    ownership: "<system_of_record|exclusive|shared>"     # optional
    api_contract: "<must_call_existing|no_undocumented_endpoints|no_breaking_changes>" # optional
  evidence_templates:
    - "Look for imports of sqlalchemy in src/api/**"
    - "Look for direct HTTP calls from service A to service B bypassing gateway"
```

## Acceptance Criteria
- Constraints extracted for every relevant ADR.
- Findings include concrete evidence locations or clear “not found” statements.
- Violations are accompanied by rationale, impact, and confidence.
- If any violation confidence ≥ 0.6, recommend an RFE and STOP coding.

## Output Format (JSON FIRST, then human brief)
**You MUST print a JSON object first**, with keys:
- `constraints`: [Constraint]
- `findings`: [{constraint_id, evidence: [ {file, line?, snippet?} ]}]
- `violations`: [{constraint_id, severity, confidence, rationale, impacted_files: [...]}]
- `rfe`: {required: bool, title?: string, reason?: string, adr_ids?: [string]}

Then, a human-readable summary.


## 3) Optional ADR “Semantics” block (richer than regex)

To help the agent, you can add an **optional structured block** to ADRs (in addition to `goibniu_rule`). The agent will prefer this if present:

```yaml
goibniu_semantics:
  constraints:
    - category: layering
      natural_language: "API layer must not access persistence directly."
      subject: { kind: "layer", name: "API" }
      predicate:
        must_not_depend_on: ["Persistence"]
      evidence_templates:
        - "Find imports of sqlalchemy under src/api/**"
        - "Find DB session usage in API routers"
    - category: api_contract
      natural_language: "Call only documented endpoints."
      predicate:
        api_contract: "no_undocumented_endpoints"
```

