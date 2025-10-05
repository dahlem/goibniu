"""Scaffold module for creating pre-commit and CI configuration files.

This module provides utilities to generate starter configuration files for
pre-commit hooks and GitHub Actions CI workflows that integrate Goibniu
compliance checks.
"""

from __future__ import annotations

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from pathlib import Path

PRE_COMMIT_STUB = """\
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
"""

CI_STUB = """\
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
      - name: Install Goibniu
        run: pip install -e .
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
"""

def _write_file(path: Path, content: str, overwrite: bool) -> tuple[bool, str]:
    """Write content to file with optional overwrite protection.

    Args:
        path: Target file path
        content: Content to write
        overwrite: If False, skip writing if file exists

    Returns:
        tuple: (success: bool, message: str)

    """
    if path.exists() and not overwrite:
        return False, f"exists (skipped): {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True, f"written: {path}"


def write_pre_commit(base: str = ".", overwrite: bool = False) -> tuple[bool, str]:
    """Create .pre-commit-config.yaml with Goibniu hooks.

    Generates a pre-commit configuration that runs:
    - ADR compliance checks on commit
    - API compliance checks on commit
    - Design context generation on push

    Args:
        base: Project root directory
        overwrite: If True, overwrite existing file

    Returns:
        tuple: (success: bool, message: str)

    """
    return _write_file(Path(base) / ".pre-commit-config.yaml", PRE_COMMIT_STUB, overwrite)


def write_ci_workflow(base: str = ".", overwrite: bool = False) -> tuple[bool, str]:
    """Create GitHub Actions workflow for Goibniu CI.

    Generates a CI workflow that:
    - Generates design context
    - Runs ADR compliance checks
    - Runs API compliance checks
    - Executes pytest tests

    Args:
        base: Project root directory
        overwrite: If True, overwrite existing file

    Returns:
        tuple: (success: bool, message: str)

    """
    return _write_file(Path(base) / ".github/workflows/goibniu-ci.yml", CI_STUB, overwrite)
