"""ADR compliance checking module.

This module validates source code against architectural rules embedded in
Architecture Decision Records (ADRs). Rules are defined in YAML blocks within
ADR markdown files and can enforce coding standards, banned patterns, or
required patterns.

The module supports:
- Extracting compliance rules from ADR documents
- Pattern matching (any/all patterns)
- File path filtering (include/exclude globs)
- Repository-wide and single-file validation
- Detailed violation reporting

Example ADR rule:
    ```yaml
    goibniu_rule:
      id: ADR-0001
      description: Prohibit use of eval()
      patterns:
        any: ['eval(']
      paths:
        include: ['**/*.py']
        exclude: ['tests/**']
    ```
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml


def _extract_rules_from_md(md_text: str) -> list[dict[str, Any]]:
    """Extract compliance rules from ADR markdown content.

    Parses YAML code blocks in ADR markdown files looking for 'goibniu_rule'
    sections. Each rule defines patterns to match and file paths to check.

    Args:
        md_text: ADR markdown file content

    Returns:
        list: List of rule dictionaries extracted from YAML blocks

    """
    rules = []

    # Find all YAML code blocks in the markdown
    for block in re.findall(r"```yaml\n(.*?)```", md_text, flags=re.DOTALL):
        try:
            data = yaml.safe_load(block)
            # Look for goibniu_rule sections
            if isinstance(data, dict) and 'goibniu_rule' in data:
                rules.append(data['goibniu_rule'])
        except Exception:
            # Skip malformed YAML blocks
            continue

    return rules


def load_rules(adr_dir: str = 'docs/adr') -> list[dict[str, Any]]:
    """Load all compliance rules from ADR files.

    Scans the ADR directory for markdown files and extracts all embedded
    compliance rules from YAML blocks.

    Args:
        adr_dir: Path to directory containing ADR markdown files.
                Defaults to 'docs/adr'

    Returns:
        list: All compliance rules found across all ADR files

    Example:
        >>> rules = load_rules('docs/adr')
        >>> print(len(rules))
        5
        >>> print(rules[0]['id'])
        ADR-0001

    """
    adr_path = Path(adr_dir)
    rules: list[dict[str, Any]] = []

    # Process all ADR markdown files
    for md in adr_path.glob('ADR-*.md'):
        rules.extend(_extract_rules_from_md(md.read_text(encoding='utf-8')))

    return rules


def _file_matches(root: Path, f: Path, include: list[str], exclude: list[str]) -> bool:
    """Check if a file matches include/exclude glob patterns.

    Args:
        root: Repository root path
        f: File path to check
        include: List of glob patterns to include (e.g., ['**/*.py'])
        exclude: List of glob patterns to exclude (e.g., ['tests/**'])

    Returns:
        bool: True if file matches include patterns and not excluded

    """
    rel = str(f.relative_to(root))

    # Check exclusion patterns first
    if any(fnmatch(rel, pat) for pat in (exclude or [])):
        return False

    # Check inclusion patterns
    if include:
        return any(fnmatch(rel, pat) for pat in include)

    return True


def _violates(text: str, anyp: list[str], allp: list[str]) -> bool:
    """Check if file content violates rule patterns.

    Rules can specify:
    - 'any' patterns: file violates if ANY pattern is found
    - 'all' patterns: file violates if ALL patterns are found

    Args:
        text: File content to check
        anyp: List of 'any' patterns (OR logic)
        allp: List of 'all' patterns (AND logic)

    Returns:
        bool: True if file content violates the rule

    """
    # If 'all' patterns specified, all must be present
    if allp and not all(p in text for p in allp):
        return False

    # If 'any' patterns specified, any match is a violation
    if anyp and any(p in text for p in anyp):
        return True

    # If only 'all' patterns, violation if all present
    return bool(allp) and all(p in text for p in allp)


def check_path(root: str, target: str, rules: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Check a single file for ADR compliance violations.

    Args:
        root: Repository root path
        target: Path to file to check
        rules: Optional list of rules to check against.
               If None, loads rules from docs/adr

    Returns:
        list: List of violation dictionaries, each containing:
              - rule: Rule ID (e.g., 'ADR-0001')
              - description: Rule description
              - file: Path to violating file

    Example:
        >>> violations = check_path('.', 'src/bad.py')
        >>> if violations:
        ...     print(f"Found {len(violations)} violations")

    """
    root_path = Path(root)
    target_path = Path(target)

    # Load rules if not provided
    if rules is None:
        rules = load_rules(str(root_path / 'docs/adr'))

    # Skip non-existent files
    if not target_path.exists():
        return []

    # Read file content
    text = target_path.read_text(encoding='utf-8', errors='ignore')
    out = []

    # Check file against each rule
    for rule in rules:
        pats = rule.get('patterns', {})
        anyp = pats.get('any', []) or []
        allp = pats.get('all', []) or []
        paths = rule.get('paths', {})
        include = paths.get('include', ['**/*.py'])
        exclude = paths.get('exclude', ['tests/**'])

        # Check if file matches path filters and violates patterns
        if _file_matches(root_path, target_path, include, exclude) and _violates(text, anyp, allp):
            out.append({
                'rule': rule.get('id'),
                'description': rule.get('description'),
                'file': str(target_path)
            })

    return out


def check_repo(root: str, rules: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Check entire repository for ADR compliance violations.

    Scans all Python files in the repository (excluding virtual environments)
    and checks them against loaded compliance rules.

    Args:
        root: Repository root path
        rules: Optional list of rules to check against.
               If None, loads rules from docs/adr

    Returns:
        list: List of all violations found across the repository

    Example:
        >>> violations = check_repo('.')
        >>> for v in violations:
        ...     print(f"{v['file']}: {v['description']}")

    """
    root_path = Path(root)

    # Load rules if not provided
    if rules is None:
        rules = load_rules(str(root_path / 'docs/adr'))

    out = []

    # Check all Python files in repository
    for f in root_path.rglob('*.py'):
        # Skip virtual environment directories
        if any(part in {'.venv', 'venv'} for part in f.parts):
            continue

        # Check file and accumulate violations
        out.extend(check_path(root, str(f), rules))

    return out
