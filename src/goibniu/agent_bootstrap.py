"""Agent bootstrapping module.

This module creates all necessary files for agent onboarding including:
- Human-readable playbook (Markdown)
- Machine-readable playbook (YAML)
- Capability catalog (JSON)
- Quick-start onboarding document

Used by the `goibniu bootstrap-agent` CLI command to initialize a project
for AI agent collaboration.
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from pathlib import Path

from .playbook import (
    build_capabilities,
    write_capabilities_json,
    write_playbook_md,
    write_playbook_yaml,
)

ONBOARDING_MD = """# Agent Onboarding (Goibniu)
You are operating in a Goibniu-governed repository.

## Always start here
- GET /mcp/capabilities
- GET /mcp/playbook

## Protocol (from Playbook)
1) Discover → read .ai-context/system.yaml, components, contracts
2) Plan → use prompts: design_review, implementation_planner
3) Check → deterministic (goibniu check-compliance, goibniu check-api)
           → semantic ADR audit (prompt: adr_semantic_compliance; persona: adr_semantic_auditor)
           → STOP & RFE if violations or confidence ≥ 0.6
4) Implement → only after checks pass or RFE approved
5) Document & PR → impact summary; link ADRs/RFEs; CI green

## MCP you must consult
- /mcp/system, /mcp/components/{name}, /mcp/apis/{name}, /mcp/adrs
- /mcp/prompts/{name}: design_review, implementation_planner, adr_semantic_compliance
- /mcp/personas/{name}: system_planner_agent, implementation_agent, adr_semantic_auditor

## Definition of Done
- Affected components/APIs named; plan explicit
- Deterministic checks pass; semantic audit JSON shows no violations or approved RFE
- Tests + OpenAPI updated; CI green; .ai-context/ refreshed and committed
"""

def bootstrap_agent_files(base: str = ".") -> dict:
    """Bootstrap all agent onboarding files in a project.

    Creates the complete set of files needed for AI agent onboarding:
    - docs/goibniu_playbook.md - Human-readable workflow
    - .ai-context/goibniu/playbook.yaml - Machine-readable protocol
    - .ai-context/goibniu/capabilities.json - Capability catalog
    - AGENT_ONBOARDING.md - Quick-start guide

    Args:
        base: Project root directory. Defaults to current directory.

    Returns:
        dict: Paths to all created files

    Example:
        >>> result = bootstrap_agent_files('.')
        >>> print(result['onboarding'])
        ./AGENT_ONBOARDING.md

    """
    base_path = Path(base)

    # Create human-readable playbook for developers
    write_playbook_md(base_path / "docs" / "goibniu_playbook.md")

    # Create machine-readable playbook for agents
    write_playbook_yaml(base_path / ".ai-context" / "goibniu" / "playbook.yaml")

    # Create capability catalog
    caps = build_capabilities(base_path)
    write_capabilities_json(base_path / ".ai-context" / "goibniu" / "capabilities.json", caps)

    # Create quick-start onboarding document
    onboarding = base_path / "AGENT_ONBOARDING.md"
    onboarding.write_text(ONBOARDING_MD)

    # Return paths to all created files
    return {
        "playbook_md": str(base_path / "docs/goibniu_playbook.md"),
        "playbook_yaml": str(base_path / ".ai-context/goibniu/playbook.yaml"),
        "capabilities_json": str(base_path / ".ai-context/goibniu/capabilities.json"),
        "onboarding": str(onboarding)
    }
