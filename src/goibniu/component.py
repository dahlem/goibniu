"""Component analysis module for Python codebases.

This module provides static analysis capabilities to extract architectural
information from Python source code. It analyzes packages and modules to
identify classes, public functions, and dependencies.

The analysis helps with:
- Understanding codebase structure
- Documenting components and their interfaces
- Identifying dependencies between modules
- Generating component diagrams and documentation
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import ast
from pathlib import Path

import yaml


def analyze_components(root: str) -> dict:
    """Analyze Python packages to extract component information.

    Performs static analysis on all Python files in the given directory tree,
    grouping them by package and extracting:
    - Module/package names
    - Public classes defined
    - Public functions (non-underscore prefixed)
    - Top-level imports (dependencies)

    Args:
        root: Root directory path to analyze

    Returns:
        dict: Component analysis results, keyed by package name.
              Each value contains:
              - module: Relative module path
              - classes: List of class names defined
              - functions: List of public function names
              - imports: Sorted list of top-level dependencies

    Example:
        >>> components = analyze_components('src/myapp')
        >>> print(components['models'])
        {
            'module': 'myapp/models',
            'classes': ['User', 'Post'],
            'functions': ['create_user'],
            'imports': ['datetime', 'sqlalchemy']
        }

    """
    root_path = Path(root)
    comps = {}

    # Group Python files by their parent directory (package)
    for pkg in {p.parent for p in root_path.rglob('*.py')}:
        files = list(pkg.glob('*.py'))
        if not files:
            continue

        # Initialize component data structure
        data = {'module': str(pkg.relative_to(root_path)), 'classes': [], 'functions': [], 'imports': []}
        imports = set()

        # Analyze each Python file in the package
        for f in files:
            try:
                tree = ast.parse(f.read_text(encoding='utf-8'))
            except Exception:
                # Skip files that can't be parsed (syntax errors, etc.)
                continue

            # Extract top-level classes and functions
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    data['classes'].append(node.name)
                # Only include public functions (not starting with _)
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    data['functions'].append(node.name)

            # Extract all imports to identify dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # For "import foo.bar", extract "foo"
                    imports.update(n.name.split('.')[0] for n in node.names)
                if isinstance(node, ast.ImportFrom) and node.module:
                    # For "from foo.bar import baz", extract "foo"
                    imports.add(node.module.split('.')[0])

        data['imports'] = sorted(imports)
        comps[pkg.name or 'root'] = data

    return comps


def export_components(output_dir: Path, components: dict):
    """Export component analysis results to YAML files.

    Creates one YAML file per component in the specified output directory.
    Each file contains the component's module path, classes, functions, and imports.

    Args:
        output_dir: Directory where YAML files will be written
        components: Component analysis results from analyze_components()

    Example:
        >>> components = analyze_components('src')
        >>> export_components(Path('.ai-context/components'), components)
        # Creates files like:
        # .ai-context/components/models.yaml
        # .ai-context/components/services.yaml

    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write each component to its own YAML file
    for name, data in components.items():
        (output_dir / f"{name}.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
