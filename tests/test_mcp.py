"""Test MCP (Model Context Protocol) server endpoints."""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from pathlib import Path

from starlette.testclient import TestClient

from goibniu.mcp import create_app


def test_mcp_endpoints(tmp_path: Path):
    """Test that MCP endpoints correctly serve system, component, and API docs."""
    out = tmp_path / '.ai-context'
    out.mkdir()
    (out/'system.yaml').write_text('service: test\n')
    (out/'components').mkdir()
    (out/'components'/'root.yaml').write_text('module: root\n')
    (out/'contracts').mkdir()
    (out/'contracts'/'root.openapi.yaml').write_text('openapi: 3.0.0\n')
    app = create_app(base=str(tmp_path))
    client = TestClient(app)
    assert client.get('/mcp/system').status_code == 200
    assert client.get('/mcp/components/root').status_code == 200
    assert client.get('/mcp/apis/root').status_code == 200
