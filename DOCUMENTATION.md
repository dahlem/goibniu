# Goibniu Documentation

## Overview

Goibniu is a design-aware, ADR-compliant development toolset that helps teams build software with architectural governance. It provides CLI tools, MCP (Model Context Protocol) integration, and compliance checking capabilities.

## Core Modules

### adr.py - Architecture Decision Records
Manages ADR (Architecture Decision Record) creation and listing. ADRs document important architectural decisions including context, decision, and consequences.

**Key Functions:**
- `bootstrap_adr(title, status)` - Creates new ADR from template
- `list_adrs()` - Lists all existing ADRs

### component.py - Component Analysis
Performs static analysis on Python codebases to extract architectural information including classes, functions, and dependencies.

**Key Functions:**
- `analyze_components(root)` - Analyzes Python packages and extracts component metadata
- `export_components(output_dir, components)` - Exports component data to YAML files

### api.py - API Documentation Extraction
Automatically generates API documentation from Python source code by analyzing web framework decorators.

**Key Functions:**
- `extract_api_docs(root)` - Extracts API endpoints from decorator patterns
- `export_openapi(output_dir, apis)` - Generates OpenAPI 3.0 specifications

### system.py - System Analysis
Analyzes system-level characteristics including framework detection and service metadata.

**Key Functions:**
- `analyze_system(root)` - Detects frameworks and analyzes system structure
- `export_system_yaml(output_path, system)` - Exports system metadata to YAML

### compliance.py - ADR Compliance Checking
Validates code against ADR-defined rules to ensure architectural compliance.

**Key Functions:**
- `load_rules(adr_dir)` - Loads compliance rules from ADR files
- `check_path(root, target, rules)` - Checks a file against compliance rules
- `check_repo(root, rules)` - Checks entire repository for violations

### api_compliance.py - API Compliance Checking
Validates HTTP client calls against documented OpenAPI specifications to prevent hallucinated endpoints.

**Key Classes:**
- `ApiIndex` - Indexes OpenAPI specs for fast lookup

**Key Functions:**
- `load_specs(spec_dir)` - Loads OpenAPI specifications
- `extract_calls(root)` - Extracts HTTP client calls from code
- `check_api_usage(root, spec_dir)` - Validates calls against specs

### playbook.py - Agent Playbooks
Defines protocols and playbooks for AI agents and human developers to follow.

**Key Functions:**
- `write_playbook_md(md_path)` - Writes human-readable playbook
- `write_playbook_yaml(yaml_path)` - Writes machine-readable playbook
- `build_capabilities(root)` - Builds capability catalog
- `write_capabilities_json(path, caps)` - Exports capabilities

### agent_bootstrap.py - Agent Onboarding
Bootstraps agent files including playbooks, onboarding docs, and capability catalogs.

**Key Functions:**
- `bootstrap_agent_files(base)` - Creates all agent onboarding files

### mcp.py - Model Context Protocol Server
FastAPI-based MCP server providing access to system documentation, components, APIs, and ADRs.

**Key Functions:**
- `create_app(base)` - Creates and configures FastAPI application

**Endpoints:**
- `/mcp/capabilities` - Lists available capabilities
- `/mcp/playbook` - Returns agent playbook
- `/mcp/system` - Returns system metadata
- `/mcp/components/{name}` - Returns component documentation
- `/mcp/apis/{name}` - Returns API specifications
- `/mcp/adrs` - Lists ADRs
- `/mcp/prompts` - Lists available prompts
- `/mcp/personas` - Lists available personas

### cli/__main__.py - Command Line Interface
Click-based CLI providing all Goibniu commands.

**Commands:**
- `bootstrap-agent` - Create playbook and onboarding files
- `bootstrap-adr` - Create new ADR from template
- `capabilities` - Print capability catalog
- `list-prompts` - List available prompts
- `prompt` - Display a prompt
- `check-api` - Validate API calls against specs
- `generate-docs` - Generate all documentation
- `check-compliance` - Check ADR compliance
- `generate-rfe` - Create Request for Enhancement
- `start-mcp` - Start MCP server

## Workflow

### 1. Initialize Project
```bash
goibniu bootstrap-agent --base .
```

### 2. Create ADRs
```bash
goibniu bootstrap-adr "Use PostgreSQL for persistence"
```

### 3. Generate Documentation
```bash
goibniu generate-docs --root . --out .ai-context
```

### 4. Check Compliance
```bash
goibniu check-compliance --root .
goibniu check-api --root . --specdir .ai-context/contracts
```

### 5. Start MCP Server
```bash
goibniu start-mcp --base . --port 8000
```

## Design Principles

1. **ADR-First**: All architectural decisions are documented
2. **Compliance-Driven**: Code is validated against ADRs
3. **Contract-Based**: APIs are spec-first with validation
4. **Agent-Friendly**: Machine-readable formats for AI agents
5. **Human-Readable**: Markdown docs for developers

## File Structure

```
.
├── docs/
│   ├── adr/                    # Architecture Decision Records
│   ├── rfes/                   # Requests for Enhancement
│   └── goibniu_playbook.md     # Human playbook
├── .ai-context/
│   ├── system.yaml             # System metadata
│   ├── components/             # Component documentation
│   ├── contracts/              # OpenAPI specifications
│   └── goibniu/
│       ├── playbook.yaml       # Machine playbook
│       └── capabilities.json   # Capability catalog
└── AGENT_ONBOARDING.md         # Agent quickstart
```

## Testing

The test suite covers:
- API extraction from FastAPI decorators
- MCP endpoint functionality
- Compliance rule detection
- System analysis and framework detection

Run tests with:
```bash
pytest tests/
```

## Author

Dominik Dahlem

## Status

Development
