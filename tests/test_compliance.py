"""Test ADR compliance rule detection and validation."""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from pathlib import Path

from goibniu import compliance


def test_compliance_rule_detection(tmp_path: Path):
    """Test that compliance violations are correctly detected."""
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    f = src_dir / 'bad.py'
    f.write_text("x = eval('1+1')\n")
    rules = compliance.load_rules('docs/adr')
    violations = compliance.check_path(str(tmp_path), str(f), rules)
    assert any(v.get('rule')=='ADR-0001' for v in violations)
