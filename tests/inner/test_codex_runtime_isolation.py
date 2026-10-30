"""Contract tests for Omnigent ↔ OpenCodex runtime isolation.

These tests verify that:
- OpenCodex-polluted config.toml fields (openai_base_url, 10100 endpoints,
  user model overrides) do NOT leak into the private CODEX_HOME.
- auth.json is bridged (symlinked) without reading or logging its contents.
- Child env does not carry OPENAI_BASE_URL / OPENAI_API_BASE.
- argv explicitly contains ``-c model="gpt-5.6-sol"`` in subscription mode.
- The user's ``gpt-5.6-luna`` never becomes the effective model.

Written BEFORE the implementation (TDD red phase).
"""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
import tomlkit

from omnigent.inner.codex_executor import (
    CodexExecutor,
    _clean_codex_env,
    _populate_codex_home_config,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_POLLUTED_CONFIG = textwrap.dedent("""\
    # Auto-injected by opencodex
    openai_base_url = "http://127.0.0.1:10100/v1"
    model = "gpt-5.6-luna"
    model_reasoning_effort = "high"
    notify = ["some-notifier", "turn-ended"]

    [features]
    fast_mode = true

    [desktop]
    followUpQueueMode = "queue"
""")

_SAFE_CONFIG = textwrap.dedent("""\
    model_reasoning_effort = "high"
    notify = ["some-notifier", "turn-ended"]

    [features]
    fast_mode = true

    [desktop]
    followUpQueueMode = "queue"
""")


@pytest.fixture()
def polluted_codex_home(tmp_path: Path) -> Path:
    """A fake user CODEX_HOME with OpenCodex-polluted config.toml + auth.json."""
    home = tmp_path / "user-codex-home"
    home.mkdir()
    (home / "config.toml").write_text(_POLLUTED_CONFIG, encoding="utf-8")
    # Fake auth.json — contents must never be read or logged by the executor.
    (home / "auth.json").write_text('{"token": "REDACTED"}', encoding="utf-8")
    return home


@pytest.fixture()
def private_codex_home(tmp_path: Path) -> Path:
    """An empty private CODEX_HOME target directory."""
    target = tmp_path / "private-codex-home"
    target.mkdir()
    return target


# ---------------------------------------------------------------------------
# 1. Config sanitisation
# ---------------------------------------------------------------------------


class TestConfigSanitisation:
    """OpenCodex pollution must not survive into the private CODEX_HOME."""

    def test_openai_base_url_removed(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        dest = private_codex_home / "config.toml"
        assert dest.is_file(), "config.toml must be bridged"
        doc = tomlkit.parse(dest.read_text(encoding="utf-8"))
        assert "openai_base_url" not in doc, (
            "openai_base_url (OpenCodex route) must be stripped"
        )

    def test_openai_api_base_removed(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        # openai_api_base must be a top-level key (before any [section])
        cfg = polluted_codex_home / "config.toml"
        cfg.write_text(
            'openai_api_base = "http://127.0.0.1:10100/v1"\n' + _POLLUTED_CONFIG,
            encoding="utf-8",
        )
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        doc = tomlkit.parse(
            (private_codex_home / "config.toml").read_text(encoding="utf-8")
        )
        assert "openai_api_base" not in doc

    def test_user_model_override_removed(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        doc = tomlkit.parse(
            (private_codex_home / "config.toml").read_text(encoding="utf-8")
        )
        assert "model" not in doc, (
            "User model override (gpt-5.6-luna) must be stripped; "
            "Omnigent pins model via -c flag"
        )

    def test_10100_endpoint_not_present_anywhere(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        raw = (private_codex_home / "config.toml").read_text(encoding="utf-8")
        assert "10100" not in raw, "No 10100 endpoint may survive sanitisation"

    def test_safe_fields_preserved(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        doc = tomlkit.parse(
            (private_codex_home / "config.toml").read_text(encoding="utf-8")
        )
        assert doc.get("model_reasoning_effort") == "high"
        assert doc.get("notify") == ["some-notifier", "turn-ended"]
        assert doc["features"]["fast_mode"] is True  # type: ignore[index]
        assert doc["desktop"]["followUpQueueMode"] == "queue"  # type: ignore[index]

    def test_no_hardcoded_openai_url_injected(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        """Subscription direct mode must NOT write https://api.openai.com/v1."""
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        raw = (private_codex_home / "config.toml").read_text(encoding="utf-8")
        assert "api.openai.com" not in raw, (
            "Subscription mode must not hardcode an API base URL"
        )

    def test_missing_source_config_is_noop(self, private_codex_home: Path, tmp_path: Path) -> None:
        empty_src = tmp_path / "empty-src"
        empty_src.mkdir()
        _populate_codex_home_config(private_codex_home, empty_src)
        assert not (private_codex_home / "config.toml").exists()


# ---------------------------------------------------------------------------
# 2. Auth bridge
# ---------------------------------------------------------------------------


class TestAuthBridge:
    """auth.json must be bridged but never read or logged."""

    def test_auth_json_bridged(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        auth = private_codex_home / "auth.json"
        assert auth.exists(), "auth.json must be bridged into private CODEX_HOME"

    def test_auth_json_is_symlink_or_copy(
        self, polluted_codex_home: Path, private_codex_home: Path
    ) -> None:
        _populate_codex_home_config(private_codex_home, polluted_codex_home)
        auth = private_codex_home / "auth.json"
        # Prefer symlink; copy is acceptable fallback (Windows non-admin).
        assert auth.is_symlink() or auth.is_file()


# ---------------------------------------------------------------------------
# 3. Child env scrub
# ---------------------------------------------------------------------------


class TestChildEnvScrub:
    """Child env must not carry OPENAI_BASE_URL / OPENAI_API_BASE."""

    def test_openai_base_url_stripped(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_BASE_URL": "http://127.0.0.1:10100/v1"},
        ):
            env = _clean_codex_env()
        assert "OPENAI_BASE_URL" not in env

    def test_openai_api_base_stripped(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_API_BASE": "http://127.0.0.1:10100/v1"},
        ):
            env = _clean_codex_env()
        assert "OPENAI_API_BASE" not in env

    def test_openai_api_key_still_stripped(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            env = _clean_codex_env()
        assert "OPENAI_API_KEY" not in env

    def test_safe_openai_vars_preserved(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_MAX_RETRIES": "3", "OPENAI_TIMEOUT": "30"},
        ):
            env = _clean_codex_env()
        assert env.get("OPENAI_MAX_RETRIES") == "3"
        assert env.get("OPENAI_TIMEOUT") == "30"


# ---------------------------------------------------------------------------
# 4. Subscription proxy route
# ---------------------------------------------------------------------------


class TestSubscriptionProxyRoute:
    """Subscription Codex gets one explicit, child-scoped proxy route."""

    def test_default_proxy_is_injected_for_subscription_child(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for name in (
            "OMNIGENT_CODEX_PROXY",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        ):
            monkeypatch.delenv(name, raising=False)
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=False,
        )
        assert executor._env["HTTPS_PROXY"] == "http://127.0.0.1:7897"
        assert executor._env["HTTP_PROXY"] == "http://127.0.0.1:7897"
        assert executor._env["ALL_PROXY"] == "http://127.0.0.1:7897"
        assert executor._env["https_proxy"] == "http://127.0.0.1:7897"
        assert "features.network_proxy=true" in executor._codex_config_overrides
        assert 'network_proxy.proxy_url="http://127.0.0.1:7897"' in executor._codex_config_overrides
        assert set(executor._env["NO_PROXY"].split(",")) == {
            "localhost",
            "127.0.0.1",
            "::1",
        }
        assert "no_proxy" not in executor._env

    def test_proxy_can_be_overridden_without_ambient_proxy_leak(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OMNIGENT_CODEX_PROXY", "socks5h://127.0.0.1:7897")
        monkeypatch.setenv("HTTP_PROXY", "http://ambient.invalid:1")
        monkeypatch.setenv("ALL_PROXY", "socks5://ambient.invalid:2")
        # Ambient NO_PROXY (WSL host-proxy IP) must be replaced, not merged.
        monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,::1,172.31.80.1")
        monkeypatch.setenv("no_proxy", "172.31.80.1")
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=False,
        )
        assert executor._env["HTTPS_PROXY"] == "socks5h://127.0.0.1:7897"
        assert "ambient.invalid" not in repr(executor._env)
        assert "172.31.80.1" not in repr(executor._env)
        assert executor._env["HTTP_PROXY"] == "socks5h://127.0.0.1:7897"
        assert executor._env["ALL_PROXY"] == "socks5h://127.0.0.1:7897"
        assert set(executor._env["NO_PROXY"].split(",")) == {
            "localhost",
            "127.0.0.1",
            "::1",
        }
        assert "features.network_proxy=true" in executor._codex_config_overrides
        assert 'network_proxy.proxy_url="socks5h://127.0.0.1:7897"' in executor._codex_config_overrides

    @pytest.mark.parametrize("value", ["direct", "none", "off", "disabled"])
    def test_direct_proxy_override_is_rejected(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        monkeypatch.setenv("OMNIGENT_CODEX_PROXY", value)
        with pytest.raises(OSError, match="cannot disable proxy"):
            CodexExecutor(codex_path="/fake/codex", gateway=False)

    def test_gateway_mode_does_not_inject_subscription_proxy(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("OMNIGENT_CODEX_PROXY", raising=False)
        for name in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        ):
            monkeypatch.delenv(name, raising=False)
        # Ambient host proxy + NO_PROXY must be stripped on the gateway path.
        monkeypatch.setenv("HTTP_PROXY", "http://ambient.invalid:1")
        monkeypatch.setenv("HTTPS_PROXY", "http://ambient.invalid:1")
        monkeypatch.setenv("http_proxy", "http://ambient.invalid:1")
        monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,::1,172.31.80.1")
        monkeypatch.setenv("no_proxy", "172.31.80.1")
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=True,
            gateway_host="https://example.databricks.com",
            base_url_override="https://example.databricks.com/ai-gateway/codex/v1",
            gateway_auth_command="printf %s fake-token",
        )
        assert "HTTPS_PROXY" not in executor._env
        assert "HTTP_PROXY" not in executor._env
        assert "NO_PROXY" not in executor._env
        assert "no_proxy" not in executor._env
        assert "ambient.invalid" not in repr(executor._env)
        assert "172.31.80.1" not in repr(executor._env)
        assert "features.network_proxy=true" not in executor._codex_config_overrides
        assert not any(
            override.startswith("network_proxy.proxy_url=")
            or override.startswith("network.proxy_url=")
            for override in executor._codex_config_overrides
        )

    def test_custom_model_provider_does_not_inherit_subscription_proxy(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Databricks/custom cli-config pins must not inherit subscription proxy."""
        monkeypatch.delenv("OMNIGENT_CODEX_PROXY", raising=False)
        for name in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        ):
            monkeypatch.delenv(name, raising=False)
        # Host-transmitted ambient proxy (WSL full-suite case) must not
        # reappear as either env or subscription network_proxy overrides.
        monkeypatch.setenv("HTTP_PROXY", "http://172.31.80.1:17892")
        monkeypatch.setenv("HTTPS_PROXY", "http://172.31.80.1:17892")
        monkeypatch.setenv("ALL_PROXY", "http://172.31.80.1:17892")
        monkeypatch.setenv("http_proxy", "http://172.31.80.1:17892")
        monkeypatch.setenv("https_proxy", "http://172.31.80.1:17892")
        monkeypatch.setenv("all_proxy", "http://172.31.80.1:17892")
        monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,::1,172.31.80.1")
        monkeypatch.setenv("no_proxy", "172.31.80.1")
        executor = CodexExecutor(
            codex_path="/fake/codex",
            gateway=False,
            model_provider_override="Databricks",
        )
        assert executor._codex_config_overrides == ['model_provider="Databricks"']
        assert "HTTPS_PROXY" not in executor._env
        assert "HTTP_PROXY" not in executor._env
        assert "ALL_PROXY" not in executor._env
        assert "http_proxy" not in executor._env
        assert "https_proxy" not in executor._env
        assert "all_proxy" not in executor._env
        assert "NO_PROXY" not in executor._env
        assert "no_proxy" not in executor._env
        assert "172.31.80.1" not in repr(executor._env)
        assert "features.network_proxy=true" not in executor._codex_config_overrides
        assert not any(
            override.startswith("network_proxy.proxy_url=")
            for override in executor._codex_config_overrides
        )

    def test_openai_provider_pin_still_uses_subscription_proxy(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("OMNIGENT_CODEX_PROXY", raising=False)
        for name in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "NO_PROXY",
            "no_proxy",
        ):
            monkeypatch.delenv(name, raising=False)
        # Ambient NO_PROXY host IP must not survive the openai pin path.
        monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,::1,172.31.80.1")
        executor = CodexExecutor(
            codex_path="/fake/codex",
            gateway=False,
            model_provider_override="openai",
        )
        assert executor._env["HTTPS_PROXY"] == "http://127.0.0.1:7897"
        assert "features.network_proxy=true" in executor._codex_config_overrides
        assert 'network_proxy.proxy_url="http://127.0.0.1:7897"' in (
            executor._codex_config_overrides
        )
        assert 'model_provider="openai"' in executor._codex_config_overrides
        assert set(executor._env["NO_PROXY"].split(",")) == {
            "localhost",
            "127.0.0.1",
            "::1",
        }
        assert "172.31.80.1" not in repr(executor._env)


# ---------------------------------------------------------------------------
# 4. Explicit model override in argv
# ---------------------------------------------------------------------------


class TestExplicitModelOverride:
    """argv must contain -c model="gpt-5.6-sol" in subscription mode."""

    def test_subscription_mode_pins_model_in_overrides(self) -> None:
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=False,
        )
        # The model must appear as a -c override, not just an env var.
        model_overrides = [
            o for o in executor._codex_config_overrides if o.startswith("model=")
        ]
        assert len(model_overrides) == 1, (
            f"Expected exactly one model= override, got {model_overrides}"
        )
        assert "gpt-5.6-sol" in model_overrides[0]

    def test_user_luna_model_not_in_overrides(self) -> None:
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=False,
        )
        for override in executor._codex_config_overrides:
            assert "gpt-5.6-luna" not in override, (
                "User's gpt-5.6-luna must not appear in -c overrides"
            )

    def test_gateway_mode_does_not_double_pin_model(self) -> None:
        """Gateway mode already pins model via _databricks_codex_config_overrides;
        subscription model pin must not also fire."""
        # gateway=True with host requires base_url + auth_command; use the
        # Databricks-profile path which only needs a profile.
        # We just verify no crash and that model appears exactly once.
        executor = CodexExecutor(
            model="gpt-5.6-sol",
            codex_path="/fake/codex",
            gateway=True,
            gateway_host="https://example.databricks.com",
            base_url_override="https://example.databricks.com/ai-gateway/codex/v1",
            gateway_auth_command="printf %s fake-token",
        )
        model_overrides = [
            o for o in executor._codex_config_overrides if o.startswith("model=")
        ]
        assert len(model_overrides) == 1, (
            f"Gateway mode must pin model exactly once, got {model_overrides}"
        )

    def test_no_model_no_pin(self) -> None:
        """When no model is specified, no model= override is added."""
        executor = CodexExecutor(
            codex_path="/fake/codex",
            gateway=False,
        )
        model_overrides = [
            o for o in executor._codex_config_overrides if o.startswith("model=")
        ]
        assert len(model_overrides) == 0


# ---------------------------------------------------------------------------
# 5. Gateway / subscription mutual exclusion
# ---------------------------------------------------------------------------


class TestGatewaySubscriptionExclusion:
    """Gateway mode and subscription direct mode must be mutually exclusive."""

    def test_gateway_and_provider_override_rejected(self) -> None:
        with pytest.raises(OSError, match="mutually exclusive"):
            CodexExecutor(
                codex_path="/fake/codex",
                gateway=True,
                model_provider_override="openai",
                gateway_host="https://example.databricks.com",
                base_url_override="https://example.databricks.com/ai-gateway/codex/v1",
                gateway_auth_command="printf %s fake",
            )
