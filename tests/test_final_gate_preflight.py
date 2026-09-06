from pathlib import Path

from scripts.final_gate_preflight import (
    check_git_secret_ignores,
    validate_environment,
)


ROOT = Path(__file__).resolve().parents[1]


def _base_env():
    return {
        "MULTIMIND_DEPLOY_URL": "https://multimind.example.com",
        "MULTIMIND_API_URL": "https://api.multimind.example.com",
        "MULTIMIND_CORS_ALLOWED_ORIGINS": "https://multimind.example.com",
        "MULTIMIND_DATA_VOLUME": "multimind-data",
        "MULTIMIND_GEMINI_KEY": "sentinel-not-a-real-key",
    }


def _codes(findings):
    return {finding.code for finding in findings}


def test_production_preflight_accepts_complete_non_placeholder_environment():
    findings = validate_environment(
        _base_env(),
        production=True,
        public=True,
        private_dna=False,
        repo_root=ROOT,
    )
    assert findings == []


def test_production_preflight_rejects_localhost_and_placeholder_origins():
    env = _base_env()
    env["MULTIMIND_DEPLOY_URL"] = "http://localhost:3000"
    env["MULTIMIND_API_URL"] = "https://api.example.invalid"
    env["MULTIMIND_CORS_ALLOWED_ORIGINS"] = "http://localhost:3000"
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=False,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "PRODUCTION_LOCALHOST" in codes
    assert "PRODUCTION_PLACEHOLDER" in codes


def test_preflight_rejects_wildcard_and_deploy_origin_mismatch():
    env = _base_env()
    env["MULTIMIND_CORS_ALLOWED_ORIGINS"] = "*,https://other.example.com"
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "CORS_WILDCARD" in codes
    assert "CORS_DEPLOY_MISMATCH" in codes


def test_preflight_requires_at_least_one_usable_provider_path():
    env = _base_env()
    env.pop("MULTIMIND_GEMINI_KEY")
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "NO_PROVIDER_PATH" in codes


def test_remote_provider_base_url_may_include_a_path_prefix():
    env = _base_env()
    env.pop("MULTIMIND_GEMINI_KEY")
    env["MULTIMIND_REMOTE_URL"] = "https://remote.example.com/api/v1"
    findings = validate_environment(
        env,
        production=True,
        public=True,
        private_dna=False,
        repo_root=ROOT,
    )
    assert findings == []


def test_remote_provider_base_url_rejects_query_or_fragment():
    env = _base_env()
    env.pop("MULTIMIND_GEMINI_KEY")
    env["MULTIMIND_REMOTE_URL"] = "https://remote.example.com/api?token=not-a-secret"
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "REMOTE_URL_INVALID" in codes
    assert "NO_PROVIDER_PATH" in codes


def test_cloudflare_key_requires_account_id():
    env = _base_env()
    env.pop("MULTIMIND_GEMINI_KEY")
    env["MULTIMIND_CLOUDFLARE_KEY"] = "sentinel"
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "CLOUDFLARE_ACCOUNT_MISSING" in codes


def test_public_cutover_requires_https():
    env = _base_env()
    env["MULTIMIND_API_URL"] = "http://api.multimind.example.com"
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=False,
            repo_root=ROOT,
        )
    )
    assert "PUBLIC_TLS_REQUIRED" in codes


def test_private_dna_mode_requires_nonempty_token_file(tmp_path):
    env = _base_env()
    env["MULTIMIND_GITHUB_TOKEN_FILE"] = str(tmp_path / "missing-token")
    codes = _codes(
        validate_environment(
            env,
            production=True,
            public=True,
            private_dna=True,
            repo_root=ROOT,
        )
    )
    assert "PRIVATE_DNA_TOKEN_MISSING" in codes


def test_secret_paths_are_git_ignored_but_example_is_trackable():
    assert check_git_secret_ignores(ROOT) == []
