"""Model Context Protocol (MCP) server module.

This module implements a FastAPI-based MCP server that provides HTTP endpoints
for AI agents and tools to access project documentation, capabilities, and
architectural artifacts.

The MCP server exposes:
- System metadata (frameworks, dependencies)
- Component documentation (modules, classes, functions)
- API contracts (OpenAPI specifications)
- ADRs (Architecture Decision Records)
- Playbooks (development protocols)
- Prompts (task-specific guidance)
- Personas (agent configurations)
- Capabilities catalog (available commands and endpoints)

All endpoints follow the /mcp/* path convention and return YAML/JSON responses
or file downloads.
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from importlib import resources
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from .playbook import build_capabilities


def _serve_text_from_repo_or_package(path_from_base: Path, package_resource: tuple[str, str]):
    """Try a repo file first; else read from installed package resources.

    package_resource = ("goibniu.prompts", "design_review.md") or ("goibniu.personas", "adr_semantic_auditor.json").

    """
    if path_from_base.exists():
        return FileResponse(str(path_from_base))
    pkg, name = package_resource
    try:
        data = resources.files(pkg).joinpath(name).read_text(encoding="utf-8")
        # Decide media type based on suffix
        media = "application/json" if name.endswith(".json") else "text/markdown"
        return PlainTextResponse(data, media_type=media)
    except Exception as e:
        raise HTTPException(404, f"{name} not found") from e


def create_app(base: str = '.') -> FastAPI:
    """Create and configure the MCP FastAPI application.

    Args:
        base: Project root directory containing .ai-context and docs folders.
              Defaults to current directory.

    Returns:
        FastAPI: Configured application with all MCP endpoints registered

    Example:
        >>> app = create_app('/path/to/project')
        >>> # Start server: uvicorn app:app

    """
    base_path = Path(base)
    app = FastAPI(title='Goibniu MCP')

    @app.get("/mcp/capabilities")
    def capabilities():
        """Get capability catalog listing all available commands, endpoints, prompts, and personas.

        Returns:
            JSONResponse: Catalog with cli_commands, mcp_endpoints, prompts, personas

        """
        caps = build_capabilities(base_path)
        return JSONResponse(caps)

    @app.get("/mcp/playbook")
    def playbook():
        """Get the Goibniu development playbook.

        Returns machine-readable YAML playbook if available, otherwise falls back
        to human-readable Markdown version.

        Returns:
            FileResponse: YAML or Markdown playbook file

        Raises:
            HTTPException: 404 if no playbook found

        """
        # prefer machine-readable playbook; fall back to md
        yaml_p = base_path / ".ai-context/goibniu/playbook.yaml"
        md_p = base_path / "docs/goibniu_playbook.md"
        if yaml_p.exists():
            return FileResponse(str(yaml_p))
        if md_p.exists():
            return FileResponse(str(md_p))
        raise HTTPException(404, "Playbook not found")

    @app.get("/mcp/prompts")
    def list_prompts():
        """List all available Goibniu prompts.

        Returns:
            JSONResponse: List of prompt names (without .md extension)

        """
        pdir = base_path / "src/goibniu/prompts"
        names = sorted([p.stem for p in pdir.glob("*.md")])
        return JSONResponse({"prompts": names})

    @app.get("/mcp/personas")
    def list_personas():
        """List all available Goibniu personas.

        Returns:
            JSONResponse: List of persona names (without .json extension)

        """
        pdir = base_path / "src/goibniu/personas"
        names = sorted([p.stem for p in pdir.glob("*.json")])
        return JSONResponse({"personas": names})

    @app.get('/mcp/system')
    def system():
        """Get system-level metadata (frameworks, dependencies, structure).

        Returns:
            FileResponse: YAML file with system analysis

        Raises:
            HTTPException: 404 if system.yaml not found

        """
        f = base_path / '.ai-context/system.yaml'
        if not f.exists():
            raise HTTPException(404, 'system.yaml not found')
        return FileResponse(str(f))

    @app.get('/mcp/components/{name}')
    def component(name: str):
        """Get component documentation for a specific module.

        Args:
            name: Component/module name (without .yaml extension)

        Returns:
            FileResponse: YAML file with component metadata, classes, functions

        Raises:
            HTTPException: 404 if component not found

        """
        f = base_path / f'.ai-context/components/{name}.yaml'
        if not f.exists():
            raise HTTPException(404, f'{name} component not found')
        return FileResponse(str(f))

    @app.get('/mcp/apis/{name}')
    def apis(name: str):
        """Get OpenAPI specification for a specific API contract.

        Args:
            name: API name (without .openapi.yaml extension)

        Returns:
            FileResponse: OpenAPI 3.0 YAML specification

        Raises:
            HTTPException: 404 if API spec not found

        """
        f = base_path / f'.ai-context/contracts/{name}.openapi.yaml'
        if not f.exists():
            raise HTTPException(404, f'{name} api not found')
        return FileResponse(str(f))

    @app.get('/mcp/adrs')
    def adrs():
        """List all Architecture Decision Records.

        Returns:
            JSONResponse: List of ADR filenames (ADR-*.md)

        """
        adr_dir = base_path / 'docs/adr'
        items = sorted([p.name for p in adr_dir.glob('ADR-*.md')])
        return JSONResponse({'adrs': items})

    @app.get('/mcp/prompts/{name}')
    def prompts(name: str):
        """Get a specific Goibniu prompt template.

        Args:
            name: Prompt name (without .md extension)

        Returns:
            FileResponse: Markdown prompt template

        Raises:
            HTTPException: 404 if prompt not found

        """
        repo_path = base_path / f'src/goibniu/prompts/{name}.md'
        return _serve_text_from_repo_or_package(repo_path, ("goibniu.prompts", f"{name}.md"))

    @app.get('/mcp/personas/{name}')
    def personas(name: str):
        """Get a specific Goibniu persona configuration.

        Args:
            name: Persona name (without .json extension)

        Returns:
            FileResponse: JSON persona configuration

        Raises:
            HTTPException: 404 if persona not found

        """
        repo_path = base_path / f'src/goibniu/personas/{name}.json'
        return _serve_text_from_repo_or_package(repo_path, ("goibniu.personas", f"{name}.json"))

    return app
