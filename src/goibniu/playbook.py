"""Agent playbook and capability catalog module.

This module defines the Goibniu development protocol and playbooks for both
AI agents and human developers. It provides:

- Human-readable playbooks (Markdown) describing the development workflow
- Machine-readable playbooks (YAML) for agent automation
- Capability catalogs listing available CLI commands, MCP endpoints, prompts, and personas

The playbook enforces:
1. ADR-compliant design decisions
2. API contract validation before implementation
3. Compliance checking before commits
4. RFE (Request for Enhancement) workflow for conflicts
"""

from __future__ import annotations

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import json
from pathlib import Path

import yaml

# Human-readable playbook in Markdown format
PLAYBOOK_MD = """# Goibniu Playbook (Agent & Human)
This playbook defines the protocol for design-aware, ADR-compliant implementation.

## Protocol (High-Level)
1) **Discover**: Load `.ai-context/system.yaml`, component files, and API specs.
2) **Plan**: Use prompts (`design_review`, `implementation_planner`) to produce an impact note and plan.
3) **Check** — Perform **both**:
   - **Deterministic checks**: Run ADR and API compliance. If conflicts: STOP and create an RFE.
   - **Semantic ADR Audit (LLM-assisted)**: interpret ADRs, derive constraints, assess compliance on the proposed change
4) **Implement**: Only after checks pass or RFE approved. Update tests + OpenAPI.
5) **Document & PR**: Summarize impact; link ADRs/RFEs; ensure CI green.

## When to Consult MCP
- Start of task: `/mcp/playbook`, `/mcp/system`, `/mcp/prompts/design_review`, `/mcp/personas/system_planner_agent`
- Before any HTTP call: `/mcp/apis/{service}` + `goibniu check-api`
- Before coding: `/mcp/adrs` + `goibniu check-compliance`
- On conflict: generate RFE, await human approval

## Semantic ADR Audit (LLM-Assisted Protocol)

**When:** After deterministic checks (ADR/API) and **before** any coding.

**Inputs**  
- System: `.ai-context/system.yaml`  
- Components: `.ai-context/components/*.yaml`  
- API specs: `.ai-context/contracts/*.openapi.yaml`  
- ADRs: `docs/adr/*.md`  
- Proposed change: diff/patch or change summary  
- Prompt: `/mcp/prompts/adr_semantic_compliance`  
- Persona: `/mcp/personas/adr_semantic_auditor`

**Steps**  
1. Extract constraints from ADRs (natural language + structured schema).  
2. Map constraints to affected components/files.  
3. Assess compliance heuristically (imports, call sites, layering, ownership, API usage).  
4. Produce a **JSON first** report:  
   - `constraints`: derived constraints with ADR source  
   - `findings`: evidence (files/lines/snippets)  
   - `violations`: suspected violations, severity, confidence [0..1], rationale  
   - `rfe`: `{required: bool, title?, reason?, adr_ids?}`  
5. Print a short human‑readable brief after the JSON.  

**Stop Conditions**  
- If any violation has `confidence >= 0.6`, set `rfe.required = true` and **STOP** implementation; file an RFE.

**Success/Acceptance**  
- Constraints & evidence are explicit.  
- Either no violations or an RFE exists and is approved.

## Guardrails (stop conditions)
- ADR violations (until RFE approved)
- Calling endpoints not in spec
- Cross-layer / cross-service coupling without approved ADR

## Success / Acceptance
- Named components & interfaces affected
- No ADR/API compliance failures
- Tests + docs updated; CI passing
"""

# Machine-readable playbook in YAML/dict format for agent consumption
PLAYBOOK_YAML = {
  "protocol": ["discover", "plan", "check", "implement", "document_pr"],
  "consult_mcp": {
    "start": [
      "/mcp/playbook",
      "/mcp/system",
      "/mcp/prompts/design_review",
      "/mcp/personas/system_planner_agent"
    ],
    "before_http": ["/mcp/apis/{service}", "goibniu check-api"],
    "before_code": ["/mcp/adrs", "goibniu check-compliance"],
    "on_conflict": ["goibniu generate-rfe <ADR-ID> '<reason>'"]
  },
  "semantic_adr_audit": {
    "when": "after deterministic checks and before coding",
    "endpoints": [
      "/mcp/adrs",
      "/mcp/system",
      "/mcp/components/*",
      "/mcp/apis/*",
      "/mcp/prompts/adr_semantic_compliance",
      "/mcp/personas/adr_semantic_auditor"
    ],
    "input": ["diff|patch|change_summary"],
    "output_contract": {
      "constraints": "list of derived constraints with ADR sources",
      "findings": "evidence (files/lines/snippets) per constraint_id",
      "violations": "list with severity, confidence [0..1], rationale, impacted_files",
      "rfe": "{required: bool, title?: string, reason?: string, adr_ids?: [string]}"
    },
    "stop_on": {
      "rfe_required": True,
      "min_confidence": 0.6
    }
  },
  "guardrails": ["adr_violation", "unknown_endpoint", "cross_layer_violation"],
  "acceptance_criteria": [
    "components_and_interfaces_named",
    "no_adr_api_violations",
    "tests_docs_updated_ci_green"
  ]
}


def write_playbook_md(md_path: Path):
    """Write human-readable playbook to Markdown file.

    Args:
        md_path: Path where playbook.md will be written

    Example:
        >>> write_playbook_md(Path('docs/goibniu_playbook.md'))

    """
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(PLAYBOOK_MD)


def write_playbook_yaml(yaml_path: Path):
    """Write machine-readable playbook to YAML file.

    Args:
        yaml_path: Path where playbook.yaml will be written

    Example:
        >>> write_playbook_yaml(Path('.ai-context/goibniu/playbook.yaml'))

    """
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(yaml.safe_dump(PLAYBOOK_YAML, sort_keys=False))

def build_capabilities(root: Path) -> dict:
    """Build a catalog of all available Goibniu capabilities.

    Scans the project for available CLI commands, MCP endpoints,
    prompts, and personas to create a comprehensive capability catalog
    for agents and developers.

    Args:
        root: Project root directory

    Returns:
        dict: Capability catalog containing:
              - cli: List of available CLI commands
              - mcp: List of MCP endpoint patterns
              - prompts: List of available prompt names
              - personas: List of available persona names

    Example:
        >>> caps = build_capabilities(Path('.'))
        >>> print(caps['cli'])
        ['goibniu generate-docs', 'goibniu check-compliance', ...]
        >>> print(caps['prompts'])
        ['design_review', 'implementation_planner']

    """
    prompts_dir = root / "src/goibniu/prompts"
    personas_dir = root / "src/goibniu/personas"
    profiles_repo = root / "agent_interface"  # repo-root overrides
    
    # Build capability catalog
    caps = {
        "cli": [
            "goibniu generate-docs",
            "goibniu check-compliance",
            "goibniu check-api",
            "goibniu generate-rfe",
            "goibniu bootstrap-adr",
            "goibniu bootstrap-agent",
            "goibniu capabilities",
            "goibniu list-prompts",
            "goibniu prompt <name>",
            "goibniu init"
        ],
        "mcp": [
            "/mcp/system",
            "/mcp/components/{name}",
            "/mcp/apis/{name}",
            "/mcp/adrs",
            "/mcp/prompts", "/mcp/prompts/{name}",
            "/mcp/personas", "/mcp/personas/{name}",
            "/mcp/playbook",
            "/mcp/capabilities",
            "/mcp/agent_profiles", "/mcp/agent_profiles/{name}"
        ],
        "prompts": sorted([p.stem for p in prompts_dir.glob("*.md")]) if prompts_dir.exists() else [],
        "personas": sorted([p.stem for p in personas_dir.glob("*.json")]) if personas_dir.exists() else [],
        "agent_profiles": sorted([p.stem for p in profiles_repo.glob("*.md")]) or ["agent_profile_goibniu"]
    }
    return caps


def write_capabilities_json(path: Path, caps: dict):
    """Write capability catalog to JSON file.

    Args:
        path: Path where capabilities.json will be written
        caps: Capability catalog from build_capabilities()

    Example:
        >>> caps = build_capabilities(Path('.'))
        >>> write_capabilities_json(Path('.ai-context/goibniu/capabilities.json'), caps)

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(caps, indent=2))
