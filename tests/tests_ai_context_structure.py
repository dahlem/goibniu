from pathlib import Path


def test_ai_context_structure_exists():
    root = Path(".")
    assert (root / ".ai-context/system.yaml").exists(), "Missing .ai-context/system.yaml"
    assert any((root / ".ai-context/components").glob("*.yaml")), "Missing component docs"
    assert any((root / ".ai-context/contracts").glob("*.openapi.yaml")), "Missing API contracts"
