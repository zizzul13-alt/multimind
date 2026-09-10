import pytest

from multimind_reflex.bridge import environment_secrets_source
from utils.config import Config, InvalidUserIdError


def test_deployment_user_receives_only_exact_user_credentials():
    source = environment_secrets_source(
        {
            "MULTIMIND_GEMINI_KEY": "operator-gemini",
            "MULTIMIND_USER_A_ID": "alice",
            "MULTIMIND_USER_A_GEMINI_KEY": "alice-gemini",
            "MULTIMIND_USER_A_GROQ_KEY": "alice-groq",
            "MULTIMIND_USER_B_ID": "bob",
            "MULTIMIND_USER_B_GEMINI_KEY": "bob-gemini",
        }
    )

    alice = Config.get_api_keys("alice", source)
    bob = Config.get_api_keys("bob", source)

    assert alice["gemini_key"] == "alice-gemini"
    assert alice["groq_key"] == "alice-groq"
    assert bob["gemini_key"] == "bob-gemini"
    assert bob.get("groq_key", "") == ""
    assert "bob-gemini" not in repr(alice)
    assert "alice-gemini" not in repr(bob)


def test_unknown_deployment_user_cannot_borrow_operator_default_pool():
    source = environment_secrets_source(
        {
            "MULTIMIND_GEMINI_KEY": "operator-gemini",
            "MULTIMIND_USER_A_ID": "alice",
            "MULTIMIND_USER_A_GEMINI_KEY": "alice-gemini",
        }
    )
    unknown = Config.get_api_keys("charlie", source)
    assert unknown == Config.EMPTY_API_KEYS


def test_explicit_default_identity_can_use_operator_pool():
    source = environment_secrets_source({"MULTIMIND_GEMINI_KEY": "operator-gemini"})
    default = Config.get_api_keys("default", source)
    assert default["gemini_key"] == "operator-gemini"


def test_generic_mapping_preserves_historical_default_fallback():
    source = {"default": {"groq_key": "legacy-default"}}
    assert Config.get_api_keys("alice", source)["groq_key"] == "legacy-default"


def test_explicit_strict_mapping_disables_default_fallback():
    source = {
        "__policy__": {"allow_default_fallback": False},
        "default": {"groq_key": "operator"},
    }
    assert Config.get_api_keys("alice", source) == Config.EMPTY_API_KEYS


def test_multiple_same_provider_resources_are_ordered_and_primary_is_first():
    source = environment_secrets_source(
        {
            "MULTIMIND_USER_A_ID": "alice",
            "MULTIMIND_USER_A_GEMINI_KEY": "g-primary",
            "MULTIMIND_USER_A_GEMINI_KEY_10": "g-ten",
            "MULTIMIND_USER_A_GEMINI_KEY_2": "g-two",
            "MULTIMIND_USER_A_GEMINI_KEY_3": "g-three",
        }
    )
    alice = Config.get_api_keys("alice", source)
    resources = alice["provider_resources"]["gemini"]

    assert alice["gemini_key"] == "g-primary"
    assert [item["credential"] for item in resources] == [
        "g-primary",
        "g-two",
        "g-three",
        "g-ten",
    ]
    assert [item["resource_id"] for item in resources] == ["primary", "2", "3", "4"]


def test_numbered_resource_can_be_primary_when_unnumbered_is_absent():
    source = environment_secrets_source(
        {
            "MULTIMIND_USER_A_ID": "alice",
            "MULTIMIND_USER_A_OPENROUTER_KEY_3": "or-three",
            "MULTIMIND_USER_A_OPENROUTER_KEY_2": "or-two",
        }
    )
    alice = Config.get_api_keys("alice", source)
    assert alice["openrouter_key"] == "or-two"
    assert [r["credential"] for r in alice["provider_resources"]["openrouter"]] == [
        "or-two",
        "or-three",
    ]


def test_cloudflare_account_resources_are_user_scoped_and_deterministic():
    source = environment_secrets_source(
        {
            "MULTIMIND_USER_A_ID": "alice",
            "MULTIMIND_USER_A_CLOUDFLARE_KEY": "cf-key-a",
            "MULTIMIND_USER_A_CLOUDFLARE_ACCOUNT_ID": "cf-account-a",
            "MULTIMIND_USER_B_ID": "bob",
            "MULTIMIND_USER_B_CLOUDFLARE_KEY": "cf-key-b",
            "MULTIMIND_USER_B_CLOUDFLARE_ACCOUNT_ID": "cf-account-b",
        }
    )
    alice = Config.get_api_keys("alice", source)
    bob = Config.get_api_keys("bob", source)
    assert (alice["cloudflare_key"], alice["cloudflare_account_id"]) == (
        "cf-key-a",
        "cf-account-a",
    )
    assert (bob["cloudflare_key"], bob["cloudflare_account_id"]) == (
        "cf-key-b",
        "cf-account-b",
    )


def test_duplicate_user_slot_ids_fail_closed():
    with pytest.raises(ValueError, match="unique"):
        environment_secrets_source(
            {
                "MULTIMIND_USER_A_ID": "alice",
                "MULTIMIND_USER_B_ID": "ALICE",
            }
        )


def test_invalid_user_slot_id_fails_closed():
    with pytest.raises(InvalidUserIdError):
        environment_secrets_source({"MULTIMIND_USER_A_ID": "../alice"})


def test_default_cannot_be_declared_as_named_user_slot():
    with pytest.raises(ValueError, match="non-default"):
        environment_secrets_source({"MULTIMIND_USER_A_ID": "default"})
