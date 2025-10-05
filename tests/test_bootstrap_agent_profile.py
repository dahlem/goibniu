from pathlib import Path

from goibniu.agent_bootstrap import bootstrap_agent_files


def test_repo_override_precedence(tmp_path: Path, monkeypatch):
    # Create repo-root override
    override_dir = tmp_path / "agent_interface"
    override_dir.mkdir()
    (override_dir / "agent_profile_goibniu.md").write_text("OVERRIDE PROFILE\n")

    res = bootstrap_agent_files(base=str(tmp_path))
    content = (tmp_path / "AGENT_ONBOARDING.md").read_text()
    assert "OVERRIDE PROFILE" in content
    assert "agent_interface/agent_profile_goibniu.md" in res["onboarding_source"]
