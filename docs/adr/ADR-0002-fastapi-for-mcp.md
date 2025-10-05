# ADR-0002: Use FastAPI for the MCP (Model Context Protocol) Server

## Status
Accepted

## Context
The repository exposes design and governance context to agents over HTTP. We
need a lightweight, typed, well-supported framework with great developer
ergonomics.

## Decision
Use **FastAPI** for the MCP server in `src/goibniu/mcp.py`.

## Consequences
- Positive: Simple, fast, typed endpoints; easy testing (Starlette TestClient).
- Negative: Another framework in the toolchain; contributors must be familiar
  with FastAPI.

## Rule (optional)
```yaml
goibniu_rule:
  id: ADR-0002
  description: Avoid alternate HTTP frameworks for the MCP server
  patterns:
    any: ["import flask", "from flask", "import aiohttp", "from aiohttp", "import bottle", "from bottle"]
    all: []
  paths:
    include: ["src/goibniu/mcp.py"]
    exclude: []
