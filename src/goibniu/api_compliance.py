"""API compliance checking module.

This module validates HTTP client calls in Python code against OpenAPI specifications
to prevent calling undocumented or hallucinated API endpoints. It ensures that:

1. All HTTP calls match documented endpoints
2. Required query parameters are provided
3. Required request bodies are included

The validation helps prevent:
- Calls to non-existent endpoints
- Missing required parameters
- API contract violations

Supports: requests, httpx (extensible to aiohttp)
"""

from __future__ import annotations

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import ast
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

# Supported HTTP methods
HTTP = {"get", "post", "put", "patch", "delete", "options", "head"}

# HTTP client libraries to check
CLIENT_MODULES = {"requests", "httpx"}  # extend with aiohttp if you use it


class ApiIndex:
    """Index of API operations from OpenAPI specifications.

    Provides fast lookup of API endpoints with normalized path matching
    (e.g., /users/123 matches /users/{id}).

    Attributes:
        ops: Dictionary mapping (method, normalized_path) to operation metadata

    """

    def __init__(self) -> None:
        """Initialize empty API index."""
        # {(method, normalized_path): {"query_required": set(), "body_required": bool}}
        self.ops: dict[tuple[str, str], dict] = {}

    @staticmethod
    def _normalize(p: str) -> str:
        """Normalize API path for matching.

        Converts dynamic path segments to placeholder for comparison:
        - "/users/123" -> "/users/{_}"
        - "/users/{id}" -> "/users/{_}"
        - "/api/v1/items" -> "/api/v1/items"

        Args:
            p: API path string

        Returns:
            str: Normalized path with placeholders for dynamic segments

        """
        # Convert path parameters and IDs to generic placeholder
        return "/" + "/".join(
            "{_}" if s.startswith("{") and s.endswith("}") or re.fullmatch(r"[A-Za-z0-9_\-]+", s) is None else s
            for s in p.strip().split("/") if s
        )

    def add(self, method: str, path: str, query_required: list[str], body_required: bool):
        """Add an API operation to the index.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (may contain parameters like /users/{id})
            query_required: List of required query parameter names
            body_required: Whether a request body is required

        """
        self.ops[(method.upper(), self._normalize(path))] = {
            "query_required": set(query_required or []),
            "body_required": bool(body_required),
        }

    def match(self, method: str, path: str) -> dict | None:
        """Look up API operation by method and path.

        Args:
            method: HTTP method
            path: API path (will be normalized for matching)

        Returns:
            dict or None: Operation metadata if found, None otherwise

        """
        key = (method.upper(), self._normalize(path))
        return self.ops.get(key)


def load_specs(spec_dir: str) -> ApiIndex:
    """Load OpenAPI specifications from a directory into an index.

    Reads all YAML/JSON files in the directory, parses them as OpenAPI specs,
    and builds an index of all defined operations.

    Args:
        spec_dir: Directory containing OpenAPI specification files

    Returns:
        ApiIndex: Indexed API operations for fast lookup

    Example:
        >>> index = load_specs('.ai-context/contracts')
        >>> op = index.match('GET', '/users/123')
        >>> print(op['query_required'])
        {'limit', 'offset'}

    """
    idx = ApiIndex()
    base = Path(spec_dir)

    # Load all YAML and JSON spec files
    for spec_file in list(base.glob("*.yaml")) + list(base.glob("*.yml")) + list(base.glob("*.json")):
        try:
            data = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
        except Exception:
            # Skip malformed files
            continue

        # Extract path operations from OpenAPI spec
        paths = (data or {}).get("paths", {}) or {}
        for path, ops in paths.items():
            for method, op in (ops or {}).items():
                if method.lower() not in HTTP:
                    continue

                # Collect required query parameters
                qreq = []
                for p in (op.get("parameters") or []):
                    if p.get("in") == "query" and p.get("required"):
                        qreq.append(p.get("name"))

                # Check if request body is required
                body_required = bool((op.get("requestBody") or {}).get("required"))

                # Add operation to index
                idx.add(method, path, qreq, body_required)

    return idx


def _literal_or_fstring_to_path(node: ast.AST) -> str | None:
    """Extract path string from AST node.

    Handles both literal strings and f-strings used in HTTP calls:
    - "/v1/users/123"
    - f"/v1/users/{user_id}"

    Args:
        node: AST node representing the path argument

    Returns:
        str or None: Extracted path with {_} placeholders for variables,
                     or None if not extractable

    """
    # Handle literal string constants
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    # Handle f-strings
    if isinstance(node, ast.JoinedStr):
        out = ""
        for part in node.values:
            # Replace formatted values with placeholder
            out += "{_}" if isinstance(part, ast.FormattedValue) else (
                part.value if isinstance(part, ast.Constant) else ""
            )
        return out

    return None

def _extract_url_path(url: str) -> str:
    """Extract path component from URL.

    Handles both absolute URLs (http://api.com/path) and relative paths (/path).

    Args:
        url: Full URL or relative path

    Returns:
        str: Path component of URL

    """
    parsed = urlparse(url)
    # If URL has a scheme (http://...), extract path; otherwise use as-is
    return parsed.path if parsed.scheme else url


def _kw_bool(call: ast.Call, names: list[str]) -> bool:
    """Check if function call has any of the specified keyword arguments.

    Args:
        call: AST Call node
        names: List of keyword argument names to check for

    Returns:
        bool: True if any keyword argument name is present

    """
    return any(kw.arg in names for kw in call.keywords or [])


def extract_calls(root: str) -> list[dict]:
    """Extract all HTTP client calls from Python source code.

    Scans Python files for HTTP client library calls (requests, httpx)
    and extracts metadata about each call including method, path, and
    whether parameters/body are provided.

    Args:
        root: Root directory to scan for Python files

    Returns:
        list: List of call dictionaries, each containing:
              - file: Source file path
              - line: Line number
              - method: HTTP method (GET, POST, etc.)
              - path: URL path
              - has_params: Whether params keyword arg is present
              - has_body: Whether json/data keyword arg is present

    Example:
        >>> calls = extract_calls('src')
        >>> print(calls[0])
        {
            'file': 'src/client.py',
            'line': 42,
            'method': 'POST',
            'path': '/api/users',
            'has_params': False,
            'has_body': True
        }

    """
    calls = []

    # Scan all Python files
    for py in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except Exception:
            # Skip files with syntax errors
            continue

        # Find all function calls in the file
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func
            # Match patterns: requests.get(...), httpx.post(...), httpx.Client().get(...)
            if isinstance(func, ast.Attribute):
                method = func.attr.lower()
                if method not in HTTP:
                    continue

                # Identify the HTTP client library being used
                base = func.value
                modname = None
                if isinstance(base, ast.Name):
                    # Direct call: requests.get(...)
                    modname = base.id
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                    # Chained call: httpx.Client().get(...)
                    modname = base.value.id

                if modname not in CLIENT_MODULES:
                    continue

                # Extract URL from first argument
                if node.args:
                    url_node = node.args[0]
                    s = _literal_or_fstring_to_path(url_node)
                    if s:
                        path = _extract_url_path(s)
                        calls.append({
                            "file": str(py),
                            "line": getattr(node, "lineno", None),
                            "method": method.upper(),
                            "path": path,
                            "has_params": _kw_bool(node, ["params"]),
                            "has_body": _kw_bool(node, ["json", "data"]),
                        })

    return calls


def check_api_usage(root: str, spec_dir: str) -> list[dict]:
    """Validate HTTP client calls against OpenAPI specifications.

    Checks all HTTP calls in the codebase to ensure they:
    1. Match documented endpoints
    2. Include required query parameters
    3. Include required request bodies

    Args:
        root: Root directory to scan for Python files
        spec_dir: Directory containing OpenAPI specifications

    Returns:
        list: List of compliance violations, each containing:
              - type: Violation type ('unknown-endpoint', 'missing-body', 'missing-query-params')
              - file: Source file
              - line: Line number
              - method: HTTP method
              - path: URL path
              - required: (for missing-query-params) List of missing parameters

    Example:
        >>> issues = check_api_usage('src', '.ai-context/contracts')
        >>> for issue in issues:
        ...     if issue['type'] == 'unknown-endpoint':
        ...         print(f"{issue['file']}:{issue['line']} calls undefined {issue['path']}")

    """
    # Load and index all OpenAPI specifications
    idx = load_specs(spec_dir)
    results = []

    # Check each HTTP call found in the code
    for c in extract_calls(root):
        # Look up the call in the API specification
        spec = idx.match(c["method"], c["path"])

        if spec is None:
            # Call to undocumented/unknown endpoint
            results.append({"type": "unknown-endpoint", **c})
            continue

        # Check if required body is missing
        if spec["body_required"] and not c["has_body"]:
            results.append({"type": "missing-body", **c})

        # Check if required query params are missing
        if spec["query_required"] and not c["has_params"]:
            results.append({
                "type": "missing-query-params",
                "required": list(spec["query_required"]),
                **c
            })

    return results
