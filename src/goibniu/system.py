"""System-level analysis module.

This module analyzes Python projects at the system level to extract metadata
including service name, web frameworks used, and interaction patterns.

The analysis helps with:
- Framework detection (FastAPI, Flask, Django)
- Service identification
- System architecture documentation
- Dependency mapping
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import ast
from pathlib import Path

import yaml


def _detect_frameworks(py_files):
    """Detect web frameworks used in Python files.

    Analyzes import statements to identify which web frameworks are in use.
    Currently detects: FastAPI, Flask, Django.

    Args:
        py_files: List of Python file paths to analyze

    Returns:
        list: Sorted list of framework names detected

    """
    frameworks = set()

    # Scan each Python file for framework imports
    for p in py_files:
        try:
            tree = ast.parse(Path(p).read_text(encoding='utf-8'))
        except Exception:
            # Skip files with syntax errors
            continue

        # Check all import statements
        for node in ast.walk(tree):
            # Check "import fastapi" style imports
            if isinstance(node, ast.Import):
                for n in node.names:
                    if n.name.startswith('fastapi'):
                        frameworks.add('fastapi')
                    if n.name.startswith('flask'):
                        frameworks.add('flask')
                    if n.name.startswith('django'):
                        frameworks.add('django')

            # Check "from fastapi import ..." style imports
            if isinstance(node, ast.ImportFrom) and node.module:
                m = node.module
                if m.startswith('fastapi'):
                    frameworks.add('fastapi')
                if m.startswith('flask'):
                    frameworks.add('flask')
                if m.startswith('django'):
                    frameworks.add('django')

    return sorted(frameworks)


def analyze_system(root: str) -> dict:
    """Analyze system-level characteristics of a Python project.

    Scans the project to extract high-level metadata including service name,
    frameworks used, and version. Excludes virtual environment files.

    Args:
        root: Root directory of the project to analyze

    Returns:
        dict: System metadata containing:
              - version: Metadata format version
              - service: Service name (from directory name)
              - frameworks: List of detected frameworks
              - interactions: List of system interactions (empty for now)

    Example:
        >>> system = analyze_system('src/myservice')
        >>> print(system)
        {
            'version': '1.0',
            'service': 'myservice',
            'frameworks': ['fastapi'],
            'interactions': []
        }

    """
    root_path = Path(root)

    # Find all Python files, excluding virtual environments
    py_files = [str(p) for p in root_path.rglob('*.py') if '.venv' not in str(p)]

    # Detect frameworks from imports
    frameworks = _detect_frameworks(py_files)

    # Build system metadata
    return {
        'version': '1.0',
        'service': root_path.name,
        'frameworks': frameworks,
        'interactions': []  # Placeholder for future interaction mapping
    }


def export_system_yaml(output_path: Path, system: dict):
    """Export system metadata to a YAML file.

    Args:
        output_path: Path where system.yaml will be written
        system: System metadata dict from analyze_system()

    Example:
        >>> system = analyze_system('src')
        >>> export_system_yaml(Path('.ai-context/system.yaml'), system)

    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write system metadata as YAML
    output_path.write_text(yaml.safe_dump(system, sort_keys=False))
