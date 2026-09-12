from types import SimpleNamespace
import json

from core.ai_identity import build_identity_providers, infer_ai_identity, runtime_identity_specs
from multimind_reflex.bridge import environment_secrets_source
from providers.openai_compatible import discover_resource_providers, normalize_resource_spec
from utils.provider_resources import parse_user_provider_pools


class FakeModels:
    def list(self):
        return SimpleNamespace(data=[SimpleNamespace(id="claude-sonnet-4"), SimpleNamespace(id="qwen3-coder"), SimpleNamespace(id="mystery-premium")])

class FakeCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(model=kwargs["model"], choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))], usage=SimpleNamespace(total_tokens=7))

class FakeClient:
    def __init__(self, **kwargs):
        self.models=FakeModels(); self.chat=SimpleNamespace(completions=FakeCompletions()); self.kwargs=kwargs


def _spec(): return {"id":"kios-a","label":"Kios A","base_url":"https://kios.example/v1","api_key":"secret"}


def test_discovery_classifies_known_families_but_leaves_unknown_inert():
    routes=discover_resource_providers(_spec(),client_factory=FakeClient)
    assert len(routes)==3
    specs=runtime_identity_specs(routes)
    assert any(route.startswith("resource:kios-a:") for route in specs["claude"].route_order)
    assert any(route.startswith("resource:kios-a:") for route in specs["qwen"].route_order)
    identities=build_identity_providers(routes)
    assert "claude" in identities and "qwen" in identities
    assert all(identity not in identities for identity in ["gpt","grok","kimi"])


def test_provider_declared_identity_is_rechecked_after_generation():
    routes=discover_resource_providers(_spec(),client_factory=FakeClient)
    claude=build_identity_providers(routes)["claude"]
    result=claude.generate("hello",mode="thinking")
    assert result["status"]=="success"
    assert result["effective_identity"]=="claude"
    assert result["identity_provenance"]=="declared_by_provider_catalog"
    assert result["actual_model"]=="claude-sonnet-4"
    assert "secret" not in repr(result)


def test_identity_inference_does_not_guess_unknown_model():
    assert infer_ai_identity(model_id="mystery-premium") is None
    assert infer_ai_identity(model_id="claude-sonnet-4") == "claude"
    assert infer_ai_identity(model_id="openai/gpt-5") == "gpt"


def test_malformed_or_credentialless_resource_fails_closed():
    assert normalize_resource_spec({"id":"x","base_url":"https://x.example/v1","key":""}) is None
    assert normalize_resource_spec({"id":"x","base_url":"file:///tmp/x","key":"secret"}) is None


def test_operator_resource_env_remains_server_side_and_structured():
    env={"MULTIMIND_OPENAI_COMPATIBLE_RESOURCES_JSON":json.dumps([_spec()])}
    source=environment_secrets_source(env)
    item=source["default"]["openai_compatible_resources"][0]
    assert item["api_key"]=="secret"
    assert item["base_url"]=="https://kios.example/v1"


def test_per_user_custom_resource_isolated_from_other_users():
    raw=json.dumps({"izzul":{"openai_compatible":{"default":"kios","resources":{"kios":{"id":"mine","base_url":"https://mine.example/v1","key":"izzul-secret"}}}},"miko":{"openai_compatible":{"default":"kios","resources":{"kios":{"id":"theirs","base_url":"https://theirs.example/v1","key":"miko-secret"}}}}})
    pools=parse_user_provider_pools(raw)
    assert pools["izzul"]["openai_compatible_resources"][0]["api_key"]=="izzul-secret"
    assert pools["miko"]["openai_compatible_resources"][0]["api_key"]=="miko-secret"
    assert "miko-secret" not in repr(pools["izzul"])
