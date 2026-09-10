import json

from multimind_reflex.bridge import (
    default_credentials_allowed_for_users,
    environment_secrets_source,
)
from utils.config import Config
from utils.provider_resources import parse_user_provider_pools


def _pool(**providers):
    return providers


def test_two_users_with_same_provider_get_distinct_selected_resources():
    raw = json.dumps({
        "izzul": _pool(gemini={"default": "personal", "resources": {"personal": "izzul-g", "other": "unused"}}),
        "miko": _pool(gemini={"default": "personal", "resources": {"personal": "miko-g"}}),
    })
    pools = parse_user_provider_pools(raw)
    assert pools["izzul"]["gemini_key"] == "izzul-g"
    assert pools["miko"]["gemini_key"] == "miko-g"
    assert pools["izzul"]["gemini_key"] != pools["miko"]["gemini_key"]


def test_multiple_same_provider_resources_do_not_auto_rotate():
    raw = json.dumps({
        "izzul": _pool(groq={
            "default": "primary",
            "resources": {"primary": "groq-a", "secondary": "groq-b"},
        })
    })
    pools = parse_user_provider_pools(raw)
    assert pools["izzul"]["groq_key"] == "groq-a"
    assert "groq-b" not in pools["izzul"].values()


def test_cloudflare_resource_requires_paired_key_and_account_id():
    good = json.dumps({
        "izzul": _pool(cloudflare={
            "default": "primary",
            "resources": {"primary": {"key": "cf-key", "account_id": "cf-account"}},
        })
    })
    bad = json.dumps({
        "izzul": _pool(cloudflare={
            "default": "primary",
            "resources": {"primary": {"key": "cf-key"}},
        })
    })
    assert parse_user_provider_pools(good)["izzul"]["cloudflare_account_id"] == "cf-account"
    assert "izzul" not in parse_user_provider_pools(bad)


def test_malformed_json_and_malformed_resource_fail_closed():
    assert parse_user_provider_pools("{not-json") == {}
    assert parse_user_provider_pools(json.dumps({"izzul": {"gemini": {"resources": {"x": "secret"}}}})) == {}


def test_reserved_default_user_cannot_override_operator_pool():
    env = {
        "MULTIMIND_GEMINI_KEY": "operator-key",
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": json.dumps({
            "default": _pool(gemini={"default": "x", "resources": {"x": "attacker-key"}})
        }),
    }
    source = environment_secrets_source(env)
    assert source["default"]["gemini_key"] == "operator-key"


def test_missing_user_does_not_inherit_default_in_strict_mode():
    source = {
        "izzul": {"gemini_key": "izzul-key"},
        "default": {"gemini_key": "operator-key"},
    }
    strict = Config.get_api_keys("miko", source, allow_default=False)
    assert strict == Config.EMPTY_API_KEYS


def test_legacy_generic_default_fallback_remains_available():
    source = {"default": {"groq_key": "operator-groq"}}
    assert Config.get_api_keys("alice", source)["groq_key"] == "operator-groq"


def test_default_policy_is_migration_safe_until_user_pool_is_configured():
    assert default_credentials_allowed_for_users({}) is True
    assert default_credentials_allowed_for_users({"MULTIMIND_USER_PROVIDER_POOLS_JSON": ""}) is True
    assert default_credentials_allowed_for_users({
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": json.dumps({"izzul": {}})
    }) is False
    # Nonblank malformed configuration still activates strict isolation. It must
    # fail closed rather than silently falling back to operator credentials.
    assert default_credentials_allowed_for_users({"MULTIMIND_USER_PROVIDER_POOLS_JSON": "{bad"}) is False


def test_explicit_default_policy_overrides_migration_inference():
    assert default_credentials_allowed_for_users({
        "MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS": "false"
    }) is False
    assert default_credentials_allowed_for_users({
        "MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS": "true",
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": "{bad",
    }) is True
    assert default_credentials_allowed_for_users({
        "MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS": "false",
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": "",
    }) is False


def test_environment_source_combines_user_pools_and_operator_default_without_cross_user_merge():
    env = {
        "MULTIMIND_GEMINI_KEY": "operator-gemini",
        "MULTIMIND_GROQ_KEY": "operator-groq",
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": json.dumps({
            "izzul": _pool(gemini={"default": "p", "resources": {"p": "izzul-gemini"}}),
            "miko": _pool(groq={"default": "p", "resources": {"p": "miko-groq"}}),
        }),
    }
    source = environment_secrets_source(env)
    assert source["izzul"]["gemini_key"] == "izzul-gemini"
    assert source["izzul"]["groq_key"] == ""
    assert source["miko"]["groq_key"] == "miko-groq"
    assert source["miko"]["gemini_key"] == ""
    assert source["default"]["gemini_key"] == "operator-gemini"


def test_strict_user_lookup_and_explicit_fallback_are_deterministic():
    env = {
        "MULTIMIND_GEMINI_KEY": "operator-gemini",
        "MULTIMIND_USER_PROVIDER_POOLS_JSON": json.dumps({
            "izzul": _pool(gemini={"default": "p", "resources": {"p": "izzul-gemini"}})
        }),
    }
    source = environment_secrets_source(env)
    assert Config.get_api_keys("izzul", source, allow_default=False)["gemini_key"] == "izzul-gemini"
    assert Config.get_api_keys("miko", source, allow_default=False) == Config.EMPTY_API_KEYS
    assert Config.get_api_keys("miko", source, allow_default=True)["gemini_key"] == "operator-gemini"
