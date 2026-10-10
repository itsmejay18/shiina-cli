"""The antigravity model listing's fallback chain.

Regression context: a dead pooled access token makes the direct Code Assist listing return
nothing, so the local CLI is the safety net; and a signed-out CLI prints an error *sentence*
whose first word used to be ingested as a model id.
"""

import subprocess
from types import SimpleNamespace
from typing import Any

import pytest


def _no_token() -> Any:
    """Step 1 (direct API) is skipped: a manager that yields no access token."""
    return SimpleNamespace(get_access_token=lambda: None)


def _stub_cli(monkeypatch, output: str) -> dict:
    """Stub the CLI subprocess in the client module; the box records the argv it ran."""
    from agent import antigravity_client as ac

    seen: dict = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, output, "")

    monkeypatch.setattr(ac.subprocess, "run", fake_run)
    return seen


@pytest.fixture
def bare_home(tmp_path, monkeypatch):
    """A home where nothing is on PATH, so only the per-user candidate list can find a CLI."""
    from agent import antigravity_client as ac

    monkeypatch.setenv("SHIINA_HOME", str(tmp_path / ".shiina"))
    monkeypatch.setattr(ac.Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr(ac.shutil, "which", lambda *args, **kwargs: None)
    monkeypatch.delenv("AGY_BIN", raising=False)
    monkeypatch.delenv("ANTIGRAVITY_BIN", raising=False)
    return tmp_path


def _install_cli(home, *parts):
    cli = home.joinpath(*parts)
    cli.parent.mkdir(parents=True, exist_ok=True)
    cli.write_text("")
    return cli


def test_finds_the_windows_per_user_install(bare_home, monkeypatch):
    """Windows keeps the same CLI at ~/.gemini/bin/agy.exe, off PATH entirely."""
    from agent import antigravity_client as ac

    cli = _install_cli(bare_home, ".gemini", "bin", "agy.exe")
    seen = _stub_cli(monkeypatch, "Fetching available models...\ngemini-9.9-flash-high\tGemini 9.9 Flash (High)\n")

    models = ac.fetch_antigravity_models(timeout=10, token_manager=_no_token())

    assert seen["cmd"][0] == str(cli)
    assert models == ["gemini-9.9-flash-high"]


def test_a_signed_out_cli_never_becomes_a_model_id(bare_home, monkeypatch):
    """`agy models` prints an error sentence when signed out; its first word is not a model."""
    from agent import antigravity_client as ac

    _install_cli(bare_home, ".gemini", "bin", "agy.exe")
    _stub_cli(
        monkeypatch,
        "Fetching available models...\n"
        "Error: Please sign in to view available models. Launch the CLI without arguments to sign in.\n",
    )

    models = ac.fetch_antigravity_models(timeout=10, token_manager=_no_token())

    assert models, "the curated fallback still answers"
    assert not [m for m in models if "Error" in m or ":" in m or " " in m]


def test_parses_the_id_before_the_description_column(bare_home, monkeypatch):
    """`agy models` emits "<id>\\t<description>"; the description must not leak into the id."""
    from agent import antigravity_client as ac

    _install_cli(bare_home, ".local", "bin", "agy")
    _stub_cli(
        monkeypatch,
        "Fetching available models...\n"
        "gemini-3.8-flash-high\tGemini 3.8 Flash (High)\n"
        "gpt-oss-120b-medium\tGPT-OSS 120B (Medium)\n"
        "⠋ spinner\n",
    )

    models = ac.fetch_antigravity_models(timeout=10, token_manager=_no_token())

    assert models == ["gemini-3.8-flash-high", "gpt-oss-120b-medium"]
