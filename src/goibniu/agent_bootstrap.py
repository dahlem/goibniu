"""Agent bootstrapping module.

This module creates all necessary files for agent onboarding including:
- Human-readable playbook (Markdown)
- Machine-readable playbook (YAML)
- Capability catalog (JSON)
- Quick-start onboarding document

Used by the `goibniu bootstrap-agent` CLI command to initialize a project
for AI agent collaboration. Supports profile customization via repo-root
overrides in agent_interface/.
"""

from __future__ import annotations

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from importlib import resources
from pathlib import Path

from .playbook import (
    build_capabilities,
    write_capabilities_json,
    write_playbook_md,
    write_playbook_yaml,
)

# Fallback text only used if neither repo override nor packaged profile can be read.
_DEFAULT_ONBOARDING = """# Agent Onboarding (Goibniu)
You are operating in a Goibniu-governed repository.

## Start
- GET /mcp/capabilities
- GET /mcp/playbook

## Protocol
1) Discover → read .ai-context/system.yaml, components, contracts
2) Plan → prompts: design_review, implementation_planner
3) Check → deterministic (goibniu check-compliance, goibniu check-api)
           → semantic ADR audit (prompt: adr_semantic_compliance; persona: adr_semantic_auditor)
           → STOP & RFE if violations or confidence ≥ 0.6
4) Implement → after checks pass/RFE approved; update tests + OpenAPI
5) Document & PR → impact summary; link ADRs/RFEs; CI green
"""

def _read_packaged_text(package: str, name: str) -> str | None:
    """Read a text resource from an installed package (works in wheels/zip installs)."""
    try:
        return resources.files(package).joinpath(name).read_text(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        try:
            # Backward/alt path for some environments
            return resources.read_text(package, name, encoding="utf-8")  # type: ignore[arg-type]
        except Exception:
            return None

def _select_agent_profile(base_path: Path, profile_name: str = "agent_profile_goibniu.md") -> tuple[str, str]:
    """Select onboarding profile content and report its source.

    Precedence:
      1) Repo override at: <repo-root>/agent_interface/<profile_name>
      2) Packaged default at: goibniu/agent_interface/<profile_name>
      3) Built-in minimal fallback text

    Returns:
        tuple: (content, source_str)

    """
    # 1) Repo override (maintainer local)
    override_path = base_path / "agent_interface" / profile_name
    if override_path.exists():
        try:
            return override_path.read_text(encoding="utf-8"), str(override_path)
        except Exception:
            pass

    # 2) Packaged default
    pkg_content = _read_packaged_text("goibniu.agent_interface", profile_name)
    if pkg_content is not None:
        return pkg_content, f"package:goibniu.agent_interface/{profile_name}"

    # 3) Minimal fallback
    return _DEFAULT_ONBOARDING, "<builtin-default>"

def bootstrap_agent_files(
    base: str = ".",
    profile_name: str = "agent_profile_goibniu.md",
) -> dict[str, str]:
    """Create agent-facing artifacts in the target repo.

    Generated files:
    - docs/goibniu_playbook.md                 (human-readable playbook)
    - .ai-context/goibniu/playbook.yaml        (machine-readable playbook)
    - .ai-context/goibniu/capabilities.json    (catalog of CLI/MCP/prompts/personas)
    - AGENT_ONBOARDING.md                      (agent system profile)

    The onboarding file is sourced from:
      repo override: ./agent_interface/<profile_name>
      else packaged: goibniu/agent_interface/<profile_name>
      else fallback text in this module.

    Args:
        base: Project root directory
        profile_name: Agent profile filename to use

    Returns:
        dict: Paths to all created files

    """
    base_path = Path(base)

    # 1) Playbook (MD + YAML) + Capabilities
    write_playbook_md(base_path / "docs" / "goibniu_playbook.md")
    write_playbook_yaml(base_path / ".ai-context" / "goibniu" / "playbook.yaml")
    caps = build_capabilities(base_path)
    write_capabilities_json(base_path / ".ai-context" / "goibniu" / "capabilities.json", caps)

    # 2) Agent onboarding (profile selection with override precedence)
    content, source_str = _select_agent_profile(base_path, profile_name=profile_name)
    onboarding = base_path / "AGENT_ONBOARDING.md"
    onboarding.write_text(content, encoding="utf-8")

    return {
        "playbook_md": str(base_path / "docs/goibniu_playbook.md"),
        "playbook_yaml": str(base_path / ".ai-context/goibniu/playbook.yaml"),
        "capabilities_json": str(base_path / ".ai-context/goibniu/capabilities.json"),
        "onboarding": str(onboarding),
        "onboarding_source": source_str,
    }
