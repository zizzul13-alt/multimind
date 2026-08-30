"""Deterministic resilience contracts for provider/network failures."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import app

from agents.router import ModelRouter, TERMINAL_PROVIDER_FAILURE_TEXT
from agents.unified_agent import UnifiedAgent
from core.debate import DebateOrchestrator
from providers.base import BaseProvider
from providers.gemini import GeminiProvider
from providers.groq import GroqProvider
from providers.openrouter import OpenRouterProvider
from providers.deepseek import DeepSeekProvider
from providers.cloudflare import CloudflareProvider
from providers.huggingface import HuggingFaceProvider
from providers.remote import RemoteProvider
from core.memory import SessionMemory
from utils.config import Config


class FakeProvider(BaseProvider):
    def __init__(self, name, result=None, exception=None):
        super().__init__(name)
        self.model_name = name
        self.result = result or {
            "status": "success", "text": "usable response", "agent": name,
            "tokens": 1, "cost": 0.0,
        }
        self.exception = exception
        self.calls = []

    def generate(self, *args, **kwargs):
        self.calls.append(kwargs if kwargs else {"args": args})
        if self.exception:
            raise self.exception
        return dict(self.result)


def _error_result(name="failed"):
    return {
        "status": "error", "text": "Provider temporarily unavailable. Trying another provider.",
        "agent": name, "tokens": 0, "cost": 0.0, "failure_category": "timeout",
    }


def test_router_falls_back_for_timeout_and_preserves_context():
    first = FakeProvider("First", result=_error_result("First"))
    second = FakeProvider("Second")

    result = ModelRouter([first, second]).generate("prompt", "system", mode="research", max_tokens=77)

    assert result["agent"] == "Second"
    assert len(first.calls) == len(second.calls) == 1
    assert second.calls[0] == {
        "prompt": "prompt", "system_prompt": "system", "mode": "research", "max_tokens": 77,
    }


def test_router_blank_success_falls_back_and_success_stops_chain():
    blank = FakeProvider("Blank", result={"status": "success", "text": "  ", "agent": "Blank", "tokens": 0, "cost": 0.0})
    healthy = FakeProvider("Healthy")
    unused = FakeProvider("Unused")

    result = ModelRouter([blank, healthy, unused]).generate("prompt")

    assert result["agent"] == "Healthy"
    assert len(blank.calls) == len(healthy.calls) == 1
    assert unused.calls == []


def test_router_exception_diagnostics_do_not_include_raw_sentinel(monkeypatch):
    messages = []
    monkeypatch.setattr("agents.router.error_logger.log", lambda _kind, message, **_kwargs: messages.append(message))
    provider = FakeProvider("Explosive", exception=RuntimeError("SUPER_SECRET_PROVIDER_INTERNAL_ERROR"))

    result = ModelRouter([provider]).generate("prompt")

    assert result["text"] == TERMINAL_PROVIDER_FAILURE_TEXT
    assert all("SUPER_SECRET_PROVIDER_INTERNAL_ERROR" not in message for message in messages)
    assert any("exception_type=RuntimeError" in message for message in messages)


def test_unified_all_fail_is_terminal_and_sanitized():
    unified = UnifiedAgent({})
    first = FakeProvider("First", result=_error_result("First"))
    second = FakeProvider("Second", result=_error_result("Second"))
    unified.providers = [{"name": "First", "agent": first}, {"name": "Second", "agent": second}]
    unified.stats = {
        "First": {"success": 0, "error": 0, "rate_limited": False, "last_error": ""},
        "Second": {"success": 0, "error": 0, "rate_limited": False, "last_error": ""},
    }

    result = unified.generate("prompt")

    assert result["status"] == "error"
    assert result["text"] == TERMINAL_PROVIDER_FAILURE_TEXT
    assert len(first.calls) == len(second.calls) == 1
    assert "SUPER_SECRET_PROVIDER_INTERNAL_ERROR" not in result["text"]


def test_unified_fallback_preserves_request_and_stops_after_usable_success():
    class RecordingProvider:
        def __init__(self, response):
            self.response = response
            self.calls = []

        def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
            self.calls.append({
                "prompt": prompt,
                "system_prompt": system_prompt,
                "mode": mode,
                "max_tokens": max_tokens,
            })
            return dict(self.response)

    first = RecordingProvider(_error_result("Cloudflare"))
    second = RecordingProvider({
        "status": "success", "text": "usable response", "agent": "Groq",
        "tokens": 1, "cost": 0.0,
    })
    unused = RecordingProvider({
        "status": "success", "text": "must not be used", "agent": "Unused",
        "tokens": 1, "cost": 0.0,
    })
    unified = UnifiedAgent({})
    unified.providers = [
        {"name": "☁️ Cloudflare", "agent": first},
        {"name": "⚡ Groq", "agent": second},
        {"name": "🔍 Gemini", "agent": unused},
    ]
    unified.stats = {
        provider["name"]: {"success": 0, "error": 0, "rate_limited": False, "last_error": ""}
        for provider in unified.providers
    }

    result = unified.generate("prompt", "system", mode="research", max_tokens=77)

    expected_request = {
        "prompt": "prompt", "system_prompt": "system", "mode": "research", "max_tokens": 77,
    }
    assert result["text"] == "usable response"
    assert first.calls == [expected_request]
    assert second.calls == [expected_request]
    assert unused.calls == []


@pytest.mark.parametrize(
    ("provider_class", "module_name"),
    [
        (GroqProvider, "providers.groq"),
        (OpenRouterProvider, "providers.openrouter"),
        (DeepSeekProvider, "providers.deepseek"),
    ],
)
def test_openai_compatible_clients_receive_timeout_and_no_retries(monkeypatch, provider_class, module_name):
    captured = {}

    class Client:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(f"{module_name}.OpenAI", Client)
    provider_class("key")

    assert captured["timeout"] == Config.API_TIMEOUT
    assert captured["max_retries"] == 0


def test_gemini_request_receives_timeout(monkeypatch):
    provider = GeminiProvider("")
    captured = {}
    provider.model_name = "Gemini"
    provider.client = SimpleNamespace(models=SimpleNamespace(
        generate_content=lambda **kwargs: captured.update(kwargs) or SimpleNamespace(text="usable response")
    ))

    result = provider.generate("prompt")

    assert result["status"] == "success"
    assert captured["model"] == "Gemini"
    assert captured["contents"] == "prompt"
    assert captured["config"].http_options.timeout == Config.API_TIMEOUT * 1000


@pytest.mark.parametrize(
    ("provider_factory", "post_target", "response"),
    [
        (
            lambda: CloudflareProvider("key", "account"),
            "providers.cloudflare.requests.post",
            SimpleNamespace(ok=True, status_code=200, json=lambda: {"success": True, "result": {"response": "usable"}}),
        ),
        (
            lambda: HuggingFaceProvider("key"),
            "providers.huggingface.requests.post",
            SimpleNamespace(status_code=200, json=lambda: [{"generated_text": "usable"}]),
        ),
        (
            lambda: RemoteProvider("https://remote.example"),
            "providers.remote.requests.post",
            SimpleNamespace(status_code=200, json=lambda: {"response": "usable"}),
        ),
    ],
    ids=["cloudflare", "huggingface", "remote"],
)
def test_requests_providers_pass_configured_timeout(monkeypatch, provider_factory, post_target, response):
    captured = {}

    def post(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return response

    monkeypatch.setattr(post_target, post)

    result = provider_factory().generate("prompt")

    assert result["status"] == "success"
    assert captured["kwargs"]["timeout"] == Config.API_TIMEOUT


def test_remote_malformed_response_is_not_success(monkeypatch):
    provider = RemoteProvider("https://remote.example")
    monkeypatch.setattr(
        "providers.remote.requests.post",
        lambda *args, **kwargs: SimpleNamespace(status_code=200, json=lambda: {"response": "  "}),
    )

    result = provider.generate("prompt")

    assert result["status"] == "error"
    assert "remote.example" not in result["text"]


@pytest.mark.parametrize("status", [401, 403, 400])
def test_huggingface_nonretryable_4xx_is_attempted_once(monkeypatch, status):
    provider = HuggingFaceProvider("key")
    calls = []
    monkeypatch.setattr("providers.huggingface.time.sleep", lambda _seconds: None)
    monkeypatch.setattr(
        "providers.huggingface.requests.post",
        lambda *args, **kwargs: calls.append(1) or SimpleNamespace(status_code=status, json=lambda: {}),
    )

    result = provider.generate("prompt")

    assert result["status"] == "error"
    assert len(calls) == 1


@pytest.mark.parametrize("status", [429, 503, 500])
def test_huggingface_retryable_statuses_remain_bounded(monkeypatch, status):
    provider = HuggingFaceProvider("key")
    calls = []
    monkeypatch.setattr("providers.huggingface.time.sleep", lambda _seconds: None)
    monkeypatch.setattr(
        "providers.huggingface.requests.post",
        lambda *args, **kwargs: calls.append(1) or SimpleNamespace(status_code=status, json=lambda: {}),
    )

    result = provider.generate("prompt")

    assert result["status"] == "error"
    assert len(calls) == 3


def test_zero_usable_debate_candidates_is_terminal_failure():
    failed = FakeProvider("Failed", result=_error_result("Failed"))
    result = DebateOrchestrator(gemini_agent=None, cloudflare_agent=failed).debate(
        "prompt", agents=["cloudflare"]
    )

    assert result["status"] == "error"
    assert result["final_answer"] == TERMINAL_PROVIDER_FAILURE_TEXT


def test_valid_candidate_survives_exhausted_judge_routes():
    candidate = "A short but usable candidate."
    class CandidateThenFailProvider(FakeProvider):
        def generate(self, *args, **kwargs):
            self.calls.append(kwargs if kwargs else {"args": args})
            if len(self.calls) <= 3:
                return {
                    "status": "success", "text": candidate, "agent": self.name,
                    "tokens": 1, "cost": 0.0,
                }
            return _error_result(self.name)

    provider = CandidateThenFailProvider("Provider")
    judge_failure = FakeProvider("Judge", result=_error_result("Judge"))
    result = DebateOrchestrator(
        gemini_agent=None, cloudflare_agent=provider, groq_agent=judge_failure
    ).debate("prompt", agents=["cloudflare", "cloudflare", "cloudflare", "groq"])

    assert result["status"] == "success"
    assert candidate in result["final_answer"]
    assert len(provider.calls) == 4
    assert len(judge_failure.calls) == 1
    assert result["responses"][-1]["status"] == "error"


def _terminal_app_state(active_agents, memory):
    class SessionState(SimpleNamespace):
        def get(self, key, default=None):
            return getattr(self, key, default)

    return SessionState(
        user_id="test-user",
        compressor_enabled=False,
        current_session={"id": "session-1", "mode": "coding"},
        active_agents=active_agents,
        debate_rounds=1,
        selected_skill="default",
        memories={"session-1": memory},
    )


def _assert_process_chat_terminal_failure(monkeypatch, agents, active_agents):
    sentinel = SessionMemory()
    sentinel.add_chat("sentinel prompt", "sentinel response")
    original_short_term = list(sentinel.short_term)
    original_long_term = sentinel.long_term
    original_decisions = list(sentinel.decisions)
    ui = SimpleNamespace(
        session_state=_terminal_app_state(active_agents, sentinel),
        error=Mock(),
        success=Mock(),
        warning=Mock(),
        rerun=Mock(),
    )
    persist = Mock()
    get_db = Mock()
    monkeypatch.setattr(app, "st", ui)
    monkeypatch.setattr(app, "get_agents", lambda _user_id: agents)
    monkeypatch.setattr(app, "persist_chat_and_update_memory", persist)
    monkeypatch.setattr(app, "get_db_manager", get_db)

    app.process_chat("prompt", [], "standalone")

    ui.error.assert_called_once_with(TERMINAL_PROVIDER_FAILURE_TEXT)
    ui.success.assert_not_called()
    persist.assert_not_called()
    get_db.assert_not_called()
    assert all(
        "SUPER_SECRET_PROVIDER_INTERNAL_ERROR" not in str(call)
        for call in (*ui.error.call_args_list, *persist.call_args_list)
    )
    assert ui.session_state.memories["session-1"] is sentinel
    assert sentinel.short_term == original_short_term
    assert sentinel.long_term == original_long_term
    assert sentinel.decisions == original_decisions


def test_process_chat_unified_terminal_failure_skips_persistence(monkeypatch):
    unified = SimpleNamespace(generate=lambda **_kwargs: {
        "status": "error", "text": "SUPER_SECRET_PROVIDER_INTERNAL_ERROR",
        "agent": "Unified", "tokens": 0, "cost": 0.0,
    })
    agents = {name: None for name in ("remote", "gemini", "deepseek", "groq", "cloudflare", "openrouter", "huggingface")}
    agents["unified"] = unified

    _assert_process_chat_terminal_failure(monkeypatch, agents, ["unified"])


def test_process_chat_remote_terminal_failure_skips_persistence(monkeypatch):
    remote = SimpleNamespace(generate=lambda **_kwargs: {
        "status": "error", "text": "SUPER_SECRET_PROVIDER_INTERNAL_ERROR",
        "agent": "Remote", "tokens": 0, "cost": 0.0,
    })
    agents = {name: None for name in ("unified", "gemini", "deepseek", "groq", "cloudflare", "openrouter", "huggingface")}
    agents["remote"] = remote

    _assert_process_chat_terminal_failure(monkeypatch, agents, ["remote"])


def test_process_chat_zero_candidate_debate_skips_persistence(monkeypatch):
    failed = FakeProvider("Cloudflare", result={
        "status": "error", "text": "SUPER_SECRET_PROVIDER_INTERNAL_ERROR",
        "agent": "Cloudflare", "tokens": 0, "cost": 0.0,
        "failure_category": "timeout",
    })
    agents = {name: None for name in ("unified", "remote", "gemini", "deepseek", "groq", "openrouter", "huggingface")}
    agents["cloudflare"] = failed

    _assert_process_chat_terminal_failure(monkeypatch, agents, ["cloudflare"])
