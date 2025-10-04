"""Test system-level analysis and framework detection."""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from goibniu import system


def test_system_analysis():
    """Test that system metadata is correctly extracted."""
    d = system.analyze_system('examples/example_service')
    assert 'service' in d
