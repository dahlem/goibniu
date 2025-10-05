"""Goibniu command-line interface.

This module provides the Click-based CLI for Goibniu, offering commands for:
- Bootstrapping ADRs and agent onboarding files
- Generating documentation (system, components, APIs)
- Checking compliance against ADR rules and API contracts
- Managing prompts and capabilities
- Starting the MCP server
- Creating RFEs (Request for Enhancement) for ADR conflicts

All commands operate on the current directory by default but can be configured
with --root or --base options.
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

import sys
from pathlib import Path

import click
import uvicorn

from goibniu import api, compliance, component, system
from goibniu.mcp import create_app


@click.group()
def main():
    """Goibniu CLI - ADR-compliant development toolset.

    Provides commands for architecture decision management, code compliance
    checking, documentation generation, and AI agent integration.

    """

@main.command("init")
@click.option("--root", default=".", help="Repository root to analyze for docs generation")
@click.option("--out", default=".ai-context", help="Output directory for design context")
@click.option("--pre-commit/--no-pre-commit", default=False, help="Create .pre-commit-config.yaml stub")
@click.option("--ci/--no-ci", default=False, help="Create GitHub Actions CI stub")
@click.option("--adr", default=None, help="Create an initial ADR with given title")
@click.option("--overwrite/--no-overwrite", default=False, help="Overwrite existing files if present")
@click.option("--skip-docs/--no-skip-docs", default=False, help="Skip generating .ai-context/ design docs")
@click.option("--dry-run/--no-dry-run", default=False, help="Print actions without writing files")
def init_cmd(root, out, pre_commit, ci, adr, overwrite, skip_docs, dry_run):
    """Initialize a repository with Goibniu.

    - Generate design context (.ai-context/)
    - Bootstrap agent artifacts (playbook + onboarding)
    - (Optional) drop pre-commit and CI stubs
    - (Optional) create a first ADR

    """
    from pathlib import Path

    import click

    from goibniu import adr as adrmod
    from goibniu import api, component, system
    from goibniu.agent_bootstrap import bootstrap_agent_files
    from goibniu.scaffold import write_ci_workflow, write_pre_commit

    root_path = Path(root)
    actions = []

    if not skip_docs:
        actions.append(f"generate-docs --root {root} --out {out}")
    actions.append("bootstrap-agent --base .")
    if adr:
        actions.append(f"bootstrap-adr '{adr}'")
    if pre_commit:
        actions.append("write .pre-commit-config.yaml")
    if ci:
        actions.append("write .github/workflows/goibniu-ci.yml")

    click.echo("Goibniu init plan:")
    for a in actions:
        click.echo(f" - {a}")

    if dry_run:
        click.echo("Dry run complete. No changes made.")
        return

    # 1) Generate docs (unless skipped)
    if not skip_docs:
        out_path = Path(out)
        out_path.mkdir(parents=True, exist_ok=True)
        sys_data = system.analyze_system(root)
        system.export_system_yaml(out_path / "system.yaml", sys_data)
        comp_data = component.analyze_components(root)
        component.export_components(out_path / "components", comp_data)
        apis = api.extract_api_docs(root)
        api.export_openapi(out_path / "contracts", apis, title=f"API for {root_path.name}")
        click.echo(f"✅ Generated design context in {out}/")

    # 2) Bootstrap agent artifacts
    res = bootstrap_agent_files(base=".")
    click.echo("✅ Bootstrapped agent artifacts:")
    for k, v in res.items():
        click.echo(f"   - {k}: {v}")

    # 3) Optional ADR
    if adr:
        path = adrmod.bootstrap_adr(adr, status="Proposed")
        click.echo(f"📝 Created ADR: {path}")

    # 4) Optional stubs
    if pre_commit:
        ok, msg = write_pre_commit(base=".", overwrite=overwrite)
        click.echo(("✅ " if ok else "ℹ️  ") + msg)
    if ci:
        ok, msg = write_ci_workflow(base=".", overwrite=overwrite)
        click.echo(("✅ " if ok else "ℹ️  ") + msg)

    click.echo("🎉 Goibniu init complete.")

@main.command("bootstrap-agent")
@click.option("--base", default=".", help="Repo root")
def bootstrap_agent(base):
    """Create playbook, onboarding, and capability catalog.

    Generates all files needed for AI agent onboarding:
    - docs/goibniu_playbook.md (human-readable workflow)
    - .ai-context/goibniu/playbook.yaml (machine-readable protocol)
    - .ai-context/goibniu/capabilities.json (capability catalog)
    - AGENT_ONBOARDING.md (quick-start guide)

    """
    from goibniu.agent_bootstrap import bootstrap_agent_files
    out = bootstrap_agent_files(base=base)
    click.echo("✅ Bootstrapped agent files:")
    for k,v in out.items():
        click.echo(f" - {k}: {v}")

@main.command("bootstrap-adr")
@click.argument("title")
@click.option("--status", default="Proposed")
def bootstrap_adr_cmd(title, status):
    """Create a new ADR skeleton from template.

    Generates an Architecture Decision Record with standard sections:
    - Title and metadata
    - Context (problem description)
    - Decision (chosen solution)
    - Consequences (trade-offs and implications)

    The ADR is created in docs/adr/ with auto-incremented ID.

    """
    from goibniu.adr import bootstrap_adr
    path = bootstrap_adr(title, status=status)
    click.echo(f"📝 Created {path}")

@main.command("capabilities")
@click.option("--base", default=".", help="Repo root")
def capabilities_cmd(base):
    """Print a capability catalog for humans/agents.

    Outputs JSON catalog of available:
    - CLI commands (with descriptions and parameters)
    - MCP endpoints (with paths and purposes)
    - Prompts (task-specific templates)
    - Personas (agent configurations)

    """
    import json

    from goibniu.playbook import build_capabilities
    caps = build_capabilities(Path(base))
    click.echo(json.dumps(caps, indent=2))

@main.command("list-prompts")
def list_prompts_cmd():
    """List available Goibniu prompts.

    Displays names of all prompt templates in src/goibniu/prompts/
    that can be used with the 'prompt' command.

    """
    from pathlib import Path
    pdir = Path(__file__).resolve().parent.parent / "prompts"
    names = sorted([p.stem for p in pdir.glob("*.md")])
    for n in names:
        click.echo(n)

@main.command("prompt")
@click.argument("name")
def prompt_cmd(name):
    """Print a Goibniu prompt to stdout (for piping to agents).

    Outputs the full content of a prompt template, useful for:
    - Piping to AI agents: goibniu prompt design_review | claude
    - Viewing prompt content: goibniu prompt code_review
    - Integration with automation tools

    """
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "prompts" / f"{name}.md"
    if not p.exists():
        raise click.ClickException(f"Prompt not found: {name}")
    click.echo(p.read_text())

@main.command("check-api")
@click.option("--root", default=".", help="Repo to scan for HTTP calls")
@click.option("--specdir", default=".ai-context/contracts", help="Directory with OpenAPI specs")
def check_api_cmd(root, specdir):
    """Check that HTTP client calls match documented API (prevents hallucinated endpoints).

    Validates that all HTTP client calls (requests.get, httpx.post, etc.) correspond
    to endpoints defined in OpenAPI specifications. Detects:
    - Unknown/undocumented endpoints
    - Missing required request bodies
    - Missing required query parameters

    Exits with code 1 if violations found, 0 if compliant.

    """
    from goibniu.api_compliance import check_api_usage
    issues = check_api_usage(root, specdir)
    if issues:
        click.echo("🚨 API compliance failures:")
        for i in issues:
            where = f"{i['file']}:{i.get('line')}"
            t = i['type']
            if t == "unknown-endpoint":
                click.echo(f" - {where} -> {i['method']} {i['path']} is not in spec")
            elif t == "missing-body":
                click.echo(f" - {where} -> {i['method']} {i['path']} requires a body (json= or data=)")
            elif t == "missing-query-params":
                click.echo(f" - {where} -> {i['method']} {i['path']} missing query params {i['required']}")
        raise SystemExit(1)
    click.echo("✅ API calls comply with documented endpoints.")

@main.command('generate-docs')
@click.option('--root', default='.', help='Repository root to analyze')
@click.option('--out', default='.ai-context', help='Output directory for context')
def generate_docs(root, out):
    """Generate complete AI context documentation.

    Performs static analysis and generates:
    - system.yaml: Framework detection, dependencies, project structure
    - components/*.yaml: Module analysis with classes, functions, imports
    - contracts/*.openapi.yaml: API endpoint documentation

    Output is written to .ai-context/ by default and can be served via MCP.

    """
    root_path = Path(root)
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    sys_data = system.analyze_system(root)
    system.export_system_yaml(out_path / 'system.yaml', sys_data)
    comp_data = component.analyze_components(root)
    component.export_components(out_path / 'components', comp_data)
    apis = api.extract_api_docs(root)
    api.export_openapi(out_path / 'contracts', apis, title=f'API for {root_path.name}')
    click.echo(f'Generated context in {out}/')

@main.command('check-compliance')
@click.argument('target', required=False)
@click.option('--root', default='.', help='Repository root')
def check_compliance_cmd(target, root):
    """Check code compliance against ADR rules.

    Validates source code against architectural rules defined in ADR YAML blocks.
    Can check a specific file/directory (TARGET) or entire repository.

    Rules are extracted from docs/adr/ADR-*.md files and can enforce:
    - Banned patterns (e.g., no eval(), no subprocess.call())
    - Required patterns (e.g., must use logging module)
    - File-specific rules via include/exclude globs

    Exits with code 1 if violations found, 0 if compliant.

    """
    if target:
        violations = compliance.check_path(root, target)
    else:
        violations = compliance.check_repo(root)
    if violations:
        click.echo('ADR Violations:')
        for v in violations:
            click.echo(f" - {v['rule']}: {v['description']} -> {v['file']}")
        sys.exit(1)
    else:
        click.echo('No ADR violations detected.')

@main.command('generate-rfe')
@click.argument('adr_id')
@click.argument('description')
def generate_rfe(adr_id, description):
    """Generate a Request for Enhancement (RFE) for an ADR conflict.

    Creates an RFE document when proposed changes conflict with existing ADRs.
    The RFE provides a structured way to request architectural changes through
    formal review process.

    Generated RFE includes:
    - Context and justification
    - Proposed change description
    - Reviewer checklist
    - Decision placeholder

    File is created in docs/rfes/ as RFE-{ADR_ID}-{slug}.md

    """
    rfedir = Path('docs/rfes')
    rfedir.mkdir(parents=True, exist_ok=True)
    slug = description.lower().replace(' ', '-')[:60]
    fn = rfedir / f'RFE-{adr_id}-{slug}.md'
    fn.write_text('# RFE for ' + adr_id + '\n\n## Context\n\n## Proposed Change\n' + description + '\n\n## Justification\n\n## Reviewers\n- [ ] Engineering Lead\n- [ ] Architecture Owner\n\n## Decision\nPending review.\n')
    click.echo(f'Created {fn}')

@main.command('start-mcp')
@click.option('--base', default='.', help='Base path containing .ai-context and docs/adr')
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8000, type=int)
def start_mcp(base, host, port):
    """Start the Model Context Protocol (MCP) server.

    Launches a FastAPI server providing HTTP endpoints for AI agents to access
    project documentation, ADRs, API specs, and capabilities.

    Available endpoints:
    - GET /mcp/system - System metadata
    - GET /mcp/components/{name} - Component docs
    - GET /mcp/apis/{name} - OpenAPI specs
    - GET /mcp/adrs - List ADRs
    - GET /mcp/playbook - Development protocol
    - GET /mcp/capabilities - Capability catalog
    - GET /mcp/prompts - List prompts
    - GET /mcp/prompts/{name} - Get prompt
    - GET /mcp/personas - List personas
    - GET /mcp/personas/{name} - Get persona

    Server runs until interrupted (Ctrl+C).

    """
    app = create_app(base=base)
    click.echo(f'Starting MCP on http://{host}:{port}')
    uvicorn.run(app, host=host, port=port)
