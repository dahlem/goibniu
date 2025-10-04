"""Architecture Decision Record (ADR) management module.

This module provides utilities for creating and managing Architecture Decision Records
following the ADR pattern. ADRs document important architectural decisions made during
software development, including context, decision, and consequences.

The module supports:
- Creating new ADR documents from templates
- Auto-numbering ADRs sequentially
- Embedding optional compliance rules in YAML format
- Listing existing ADRs
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from pathlib import Path

# Default directory for storing ADR markdown files
ADR_DIR = Path('docs/adr')


def bootstrap_adr(title: str, status: str = 'Proposed') -> Path:
    """Create a new Architecture Decision Record from a template.

    This function generates a new ADR markdown file with auto-incremented ID,
    following the ADR template structure with sections for context, decision,
    and consequences. Optionally includes a YAML rule block for compliance checks.

    Args:
        title: The title of the ADR (e.g., "Use PostgreSQL for persistence")
        status: The initial status of the ADR. Defaults to 'Proposed'.
                Common values: 'Proposed', 'Accepted', 'Deprecated', 'Superseded'

    Returns:
        Path: The path to the newly created ADR file

    Example:
        >>> adr_path = bootstrap_adr("Use FastAPI framework", status="Accepted")
        >>> print(adr_path)
        docs/adr/ADR-0001-use-fastapi-framework.md

    """
    # Ensure the ADR directory exists
    ADR_DIR.mkdir(parents=True, exist_ok=True)

    # Generate URL-friendly slug from title
    slug = title.lower().replace(' ', '-')

    # Calculate next ADR ID by counting existing ADRs
    next_id = len(list(ADR_DIR.glob('ADR-*.md'))) + 1

    # Construct filename: ADR-NNNN-slug.md
    fn = ADR_DIR / f"ADR-{next_id:04d}-{slug}.md"

    # Build ADR content from template
    content = (
        f"# ADR-{next_id:04d}: {title}\n\n"
        f"## Status\n{status}\n\n"
        "## Context\nDescribe the forces at play and constraints.\n\n"
        "## Decision\nState the decision clearly.\n\n"
        "## Consequences\n- Positive:\n- Negative:\n\n"
        "## Rule (optional)\n"
        "```yaml\n"
        f"goibniu_rule:\n  id: ADR-{next_id:04d}\n  description: Optional rule.\n  patterns:\n    any: []\n    all: []\n  paths:\n    include: ['**/*.py']\n    exclude: ['tests/**']\n"
        "```\n"
    )
    # Write ADR content to file
    fn.write_text(content)
    return fn


def list_adrs():
    """List all existing ADR files in chronological order.

    Returns:
        list[Path]: Sorted list of paths to ADR markdown files.
                   Files are sorted alphabetically by filename, which corresponds
                   to chronological order due to the ADR-NNNN prefix.

    Example:
        >>> adrs = list_adrs()
        >>> for adr in adrs:
        ...     print(adr.name)
        ADR-0001-use-fastapi-framework.md
        ADR-0002-adopt-postgresql.md

    """
    return sorted(ADR_DIR.glob('ADR-*.md'))
