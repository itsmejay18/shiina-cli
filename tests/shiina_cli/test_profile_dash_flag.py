"""`shiina --<profile>` shorthand expansion (`main._expand_profile_aliases`)."""

from pathlib import Path

import pytest

from shiina_cli.main import _expand_profile_aliases


@pytest.fixture()
def profile_env(tmp_path, monkeypatch):
    home = tmp_path / ".shiina"
    (home / "profiles").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SHIINA_HOME", str(home))
    return home


def _make_profile(home: Path, name: str) -> Path:
    d = home / "profiles" / name
    d.mkdir(parents=True)
    (d / "config.yaml").write_text("model: {}\n", encoding="utf-8")
    return d


def test_dash_profile_flag_expands_to_profile_flag(profile_env):
    _make_profile(profile_env, "pharmashield")
    assert _expand_profile_aliases(["--pharmashield", "chat"]) == ["--profile", "pharmashield", "chat"]


def test_dash_token_naming_no_profile_is_left_alone(profile_env):
    assert _expand_profile_aliases(["--notaprofile", "chat"]) == ["--notaprofile", "chat"]


def test_real_flag_wins_over_same_named_profile(profile_env):
    """A live profile called `cli` must not turn the `--cli` flag into a profile selector."""
    _make_profile(profile_env, "cli")
    assert _expand_profile_aliases(["--cli", "chat"]) == ["--cli", "chat"]


def test_expansion_stops_at_double_dash(profile_env):
    _make_profile(profile_env, "pharmashield")
    assert _expand_profile_aliases(["mcp", "add", "x", "--", "--pharmashield"]) == [
        "mcp", "add", "x", "--", "--pharmashield",
    ]
