"""Test API extraction from FastAPI decorators."""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from goibniu import api


def test_api_extraction():
    """Test that API endpoints are correctly extracted from example service."""
    apis = api.extract_api_docs('examples/example_service')
    assert any(len(v) > 0 for v in apis.values())
