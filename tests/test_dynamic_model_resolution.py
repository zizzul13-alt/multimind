from providers.model_registry import REGISTRY, ModelCandidate, openai_catalog, resolve_model


def test_discovery_selects_only_bounded_same_provider_candidate():
    result=resolve_model("groq","coding",discover=lambda:["other/model","openai/gpt-oss-20b"])
    assert result.model_id=="openai/gpt-oss-20b"
    assert result.provider=="groq"
    assert result.source=="discovered"


def test_discovery_failure_degrades_to_registry_candidate():
    def broken(): raise TimeoutError("catalog unavailable")
    result=resolve_model("groq","research",discover=broken)
    assert result.model_id=="openai/gpt-oss-20b"
    assert result.source=="registry_fallback"


def test_authoritative_catalog_missing_candidate_fails_instead_of_calling_stale_id():
    result=resolve_model("groq","coding",discover=lambda:["replacement/model"])
    assert result is None


def test_paid_optional_model_is_not_implicitly_eligible():
    assert resolve_model("deepseek","thinking") is None
    explicit=resolve_model("deepseek","thinking",allow_paid=True)
    assert explicit.model_id=="deepseek-v4-flash"
    assert explicit.free_class=="paid_optional"


def test_openrouter_uses_dynamic_free_router_instead_of_stale_per_mode_ids():
    ids={resolve_model("openrouter",mode).model_id for mode in ("coding","research","thinking")}
    assert ids=={"openrouter/free"}


def test_resolution_is_deterministic_for_same_state():
    catalog=["openai/gpt-oss-20b","something-else"]
    first=resolve_model("groq","coding",discover=lambda:catalog)
    second=resolve_model("groq","coding",discover=lambda:list(reversed(catalog)))
    assert first==second


def test_registry_policy_has_no_scattered_openrouter_mode_map():
    assert [item.model_id for item in REGISTRY["openrouter"]]==["openrouter/free"]


def test_openai_catalog_handles_sdk_page_shape():
    class Item:
        def __init__(self,value): self.id=value
    class Page:
        data=[Item("a"),Item("b")]
    class Models:
        def list(self): return Page()
    class Client:
        models=Models()
    assert openai_catalog(Client())==("a","b")
