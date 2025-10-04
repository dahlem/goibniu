"""API documentation extraction module.

This module provides automated API documentation generation from Python source code.
It analyzes web framework decorators (FastAPI, Flask, etc.) to extract HTTP endpoints
and generates OpenAPI 3.0 specifications.

The module supports:
- Automatic endpoint discovery from decorator patterns
- HTTP method detection (GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD)
- Path parameter extraction
- OpenAPI 3.0 specification generation
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import ast
from pathlib import Path

import yaml

# Supported HTTP methods for endpoint detection
HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'options', 'head'}


def extract_api_docs(root: str) -> dict:
    """Extract API endpoint information from Python source files.

    Scans Python files for web framework decorators (e.g., @app.get, @router.post)
    and extracts endpoint metadata including HTTP method, path, and handler function.

    Supports FastAPI, Flask, and similar frameworks that use decorator patterns
    like @app.METHOD(path).

    Args:
        root: Root directory path to scan for Python files

    Returns:
        dict: API endpoints grouped by source file.
              Keys are relative file paths.
              Values are lists of endpoint dictionaries containing:
              - method: HTTP method (GET, POST, etc.)
              - path: URL path
              - function: Handler function name

    Example:
        >>> apis = extract_api_docs('src/api')
        >>> print(apis['api/routes.py'])
        [
            {'method': 'GET', 'path': '/users', 'function': 'list_users'},
            {'method': 'POST', 'path': '/users', 'function': 'create_user'}
        ]

    """
    root_path = Path(root)
    apis = {}

    # Scan all Python files in the directory tree
    for p in root_path.rglob('*.py'):
        try:
            tree = ast.parse(p.read_text(encoding='utf-8'))
        except Exception:
            # Skip files with syntax errors
            continue

        endpoints = []
        # Walk the AST to find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check each decorator on the function
                for dec in node.decorator_list:
                    # Look for pattern: @app.get(...), @router.post(...), etc.
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        method = dec.func.attr.lower()
                        if method in HTTP_METHODS:
                            # Extract the path argument from the decorator
                            path_arg = None
                            if dec.args and isinstance(dec.args[0], (ast.Str, ast.Constant)):
                                # Handle both Python 3.7 (ast.Str) and 3.8+ (ast.Constant)
                                path_arg = dec.args[0].s if isinstance(dec.args[0], ast.Str) else getattr(dec.args[0], 'value', None)

                            # Default path based on function name if not specified
                            endpoints.append({
                                'method': method.upper(),
                                'path': path_arg or f'/{node.name}',
                                'function': node.name
                            })

        # Only include files that have endpoints
        if endpoints:
            apis[str(p.relative_to(root_path))] = endpoints

    return apis


def export_openapi(output_dir: Path, apis: dict, title: str = 'Extracted API', version: str = '1.0.0'):
    """Export API documentation as OpenAPI 3.0 specifications.

    Converts extracted endpoint information into OpenAPI 3.0 YAML files,
    one per source module. Each specification includes metadata, paths,
    and basic operation definitions.

    Args:
        output_dir: Directory where OpenAPI YAML files will be written
        apis: API endpoint data from extract_api_docs()
        title: API title for the OpenAPI spec. Defaults to 'Extracted API'
        version: API version string. Defaults to '1.0.0'

    Example:
        >>> apis = extract_api_docs('src/api')
        >>> export_openapi(
        ...     Path('.ai-context/contracts'),
        ...     apis,
        ...     title='My Service API',
        ...     version='2.0.0'
        ... )
        # Creates: .ai-context/contracts/routes.openapi.yaml

    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate one OpenAPI spec per source module
    for module_rel, endpoints in apis.items():
        # Initialize OpenAPI 3.0 specification structure
        spec = {
            'openapi': '3.0.0',
            'info': {'title': title, 'version': version},
            'paths': {}
        }

        # Add each endpoint to the spec
        for ep in endpoints:
            path = ep['path']
            method = ep['method'].lower()

            # Ensure path exists in spec
            spec['paths'].setdefault(path, {})

            # Add operation with minimal metadata
            spec['paths'][path][method] = {
                'operationId': ep['function'],
                'responses': {
                    '200': {'description': 'Success'}
                }
            }

        # Write OpenAPI spec to YAML file named after the source module
        (output_dir / f"{Path(module_rel).stem}.openapi.yaml").write_text(
            yaml.safe_dump(spec, sort_keys=False)
        )
