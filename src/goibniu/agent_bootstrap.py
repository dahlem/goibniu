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
    onboarding.write_text("""# Agent Onboarding (Goibniu)
Read first: docs/goibniu_playbook.md
Query MCP:
- /mcp/playbook
- /mcp/capabilities
- /mcp/system
- /mcp/prompts/design_review
Before coding:
- goibniu check-compliance
- goibniu check-api
If conflicts:
- goibniu generate-rfe <ADR-ID> "<short reason>" (await approval)
""")

    # Return paths to all created files
    return {
        "playbook_md": str(base_path / "docs/goibniu_playbook.md"),
        "playbook_yaml": str(base_path / ".ai-context/goibniu/playbook.yaml"),
        "capabilities_json": str(base_path / ".ai-context/goibniu/capabilities.json"),
        "onboarding": str(onboarding)
    }
