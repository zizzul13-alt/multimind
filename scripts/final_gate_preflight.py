#!/usr/bin/env python3
"""Fail-closed operator preflight for the MultiMind Final Governor Migration Gate.

This script validates deployment configuration without printing secret values and
without performing a production cutover. It is intentionally presentation- and
provider-implementation independent.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse
from urllib.request import urlopen


PROVIDER_KEY_GROUPS = {
    "gemini": ("MULTIMIND_GEMINI_KEY", "GEMINI_API_KEY"),
    "deepseek": ("MULTIMIND_DEEPSEEK_KEY", "DEEPSEEK_API_KEY"),
    "groq": ("MULTIMIND_GROQ_KEY", "GROQ_API_KEY"),
    "cloudflare": ("MULTIMIND_CLOUDFLARE_KEY", "CLOUDFLARE_API_KEY"),
    "openrouter": ("MULTIMIND_OPENROUTER_KEY", "OPENROUTER_API_KEY"),
    "huggingface": (
        "MULTIMIND_HUGGINGFACE_KEY",
        "HUGGINGFACE_API_KEY",
        "HF_TOKEN",
    ),
}
CLOUDFLARE_ACCOUNT_NAMES = (
    "MULTIMIND_CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_ACCOUNT_ID",
)
REMOTE_URL_NAMES = ("MULTIMIND_REMOTE_URL",)
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
RESERVED_SUFFIXES = (".invalid", ".example", ".test")
SAFE_VOLUME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _first_value(environ: Mapping[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        value = environ.get(name, "").strip()
        if value:
            return value
    return ""


def _origin(value: str, *, variable: str) -> tuple[str, str, int | None]:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{variable} must be an absolute http(s) origin")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"{variable} must not contain credentials, query, or fragment")
    if parsed.path not in {"", "/"}:
        raise ValueError(f"{variable} must be an origin, not a path URL")
    return parsed.scheme.lower(), parsed.hostname.lower(), parsed.port


def _normalized_origin(value: str) -> str:
    scheme, host, port = _origin(value, variable="origin")
    default_port = 443 if scheme == "https" else 80
    suffix = "" if port in {None, default_port} else f":{port}"
    return f"{scheme}://{host}{suffix}"


def validate_environment(
    environ: Mapping[str, str],
    *,
    production: bool,
    public: bool,
    private_dna: bool,
    repo_root: Path,
) -> list[Finding]:
    failures: list[Finding] = []

    deploy_url = environ.get("MULTIMIND_DEPLOY_URL", "").strip()
    api_url = environ.get("MULTIMIND_API_URL", "").strip()
    cors_raw = environ.get("MULTIMIND_CORS_ALLOWED_ORIGINS", "").strip()
    volume_name = environ.get("MULTIMIND_DATA_VOLUME", "multimind-data").strip()

    parsed_origins: dict[str, tuple[str, str, int | None]] = {}
    for variable, value in (
        ("MULTIMIND_DEPLOY_URL", deploy_url),
        ("MULTIMIND_API_URL", api_url),
    ):
        if not value:
            failures.append(Finding("ORIGIN_MISSING", f"{variable} is required"))
            continue
        try:
            parsed_origins[variable] = _origin(value, variable=variable)
        except ValueError as exc:
            failures.append(Finding("ORIGIN_INVALID", str(exc)))

    if not cors_raw:
        failures.append(
            Finding("CORS_MISSING", "MULTIMIND_CORS_ALLOWED_ORIGINS is required")
        )
        cors_values: list[str] = []
    else:
        cors_values = [item.strip() for item in cors_raw.split(",") if item.strip()]
        if "*" in cors_values:
            failures.append(Finding("CORS_WILDCARD", "production CORS must not contain '*'"))
        for value in cors_values:
            if value == "*":
                continue
            try:
                _origin(value, variable="MULTIMIND_CORS_ALLOWED_ORIGINS")
            except ValueError as exc:
                failures.append(Finding("CORS_INVALID", str(exc)))

    if deploy_url and cors_values:
        try:
            deploy_origin = _normalized_origin(deploy_url)
            normalized_cors = {
                _normalized_origin(value) for value in cors_values if value != "*"
            }
            if deploy_origin not in normalized_cors:
                failures.append(
                    Finding(
                        "CORS_DEPLOY_MISMATCH",
                        "the browser-visible MULTIMIND_DEPLOY_URL origin must be allowed by CORS",
                    )
                )
        except ValueError:
            pass

    if production:
        for variable, parsed in parsed_origins.items():
            _, host, _ = parsed
            if host in LOCAL_HOSTS or host.endswith(".localhost"):
                failures.append(
                    Finding("PRODUCTION_LOCALHOST", f"{variable} still points to localhost")
                )
            if host.endswith(RESERVED_SUFFIXES):
                failures.append(
                    Finding(
                        "PRODUCTION_PLACEHOLDER",
                        f"{variable} still uses a reserved placeholder hostname",
                    )
                )

    if public:
        for variable, parsed in parsed_origins.items():
            scheme, _, _ = parsed
            if scheme != "https":
                failures.append(
                    Finding("PUBLIC_TLS_REQUIRED", f"{variable} must use https for public cutover")
                )

    if not volume_name or not SAFE_VOLUME_RE.fullmatch(volume_name):
        failures.append(
            Finding(
                "VOLUME_INVALID",
                "MULTIMIND_DATA_VOLUME must be a non-empty Docker-safe volume name",
            )
        )

    usable_provider_names: list[str] = []
    for provider, names in PROVIDER_KEY_GROUPS.items():
        if _first_value(environ, names):
            usable_provider_names.append(provider)
    remote_url = _first_value(environ, REMOTE_URL_NAMES)
    if remote_url:
        try:
            _origin(remote_url, variable="MULTIMIND_REMOTE_URL")
            usable_provider_names.append("remote")
        except ValueError as exc:
            failures.append(Finding("REMOTE_URL_INVALID", str(exc)))

    cloudflare_key = _first_value(environ, PROVIDER_KEY_GROUPS["cloudflare"])
    cloudflare_account = _first_value(environ, CLOUDFLARE_ACCOUNT_NAMES)
    if cloudflare_key and not cloudflare_account:
        failures.append(
            Finding(
                "CLOUDFLARE_ACCOUNT_MISSING",
                "Cloudflare key is configured but Cloudflare account ID is missing",
            )
        )

    if not usable_provider_names:
        failures.append(
            Finding(
                "NO_PROVIDER_PATH",
                "at least one provider credential or MULTIMIND_REMOTE_URL is required for usable production chat",
            )
        )

    if private_dna:
        token_path = Path(
            environ.get("MULTIMIND_GITHUB_TOKEN_FILE", "./.secrets/github_token")
        )
        if not token_path.is_absolute():
            token_path = repo_root / token_path
        if not token_path.is_file():
            failures.append(
                Finding("PRIVATE_DNA_TOKEN_MISSING", "private-DNA token file does not exist")
            )
        else:
            try:
                if token_path.stat().st_size <= 0:
                    failures.append(
                        Finding("PRIVATE_DNA_TOKEN_EMPTY", "private-DNA token file is empty")
                    )
            except OSError:
                failures.append(
                    Finding("PRIVATE_DNA_TOKEN_UNREADABLE", "private-DNA token file cannot be inspected")
                )

    return failures


def check_git_secret_ignores(repo_root: Path) -> list[Finding]:
    failures: list[Finding] = []
    git = shutil.which("git")
    if not git:
        return [Finding("GIT_MISSING", "git executable is required for ignore-contract preflight")]

    def ignored(path: str) -> bool:
        proc = subprocess.run(
            [git, "check-ignore", "--no-index", "-q", path],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return proc.returncode == 0

    for path in (".env", ".env.production", ".secrets/github_token"):
        if not ignored(path):
            failures.append(Finding("SECRET_NOT_IGNORED", f"{path} is not protected by .gitignore"))
    if ignored(".env.example"):
        failures.append(
            Finding("ENV_EXAMPLE_IGNORED", ".env.example must remain trackable and non-secret")
        )
    return failures


def check_compose_config(
    repo_root: Path, environ: Mapping[str, str], *, private_dna: bool
) -> list[Finding]:
    docker = shutil.which("docker")
    if not docker:
        return [Finding("DOCKER_MISSING", "docker executable is required for deployment preflight")]

    command = [docker, "compose", "-f", "compose.yml"]
    if private_dna:
        command.extend(["-f", "compose.private-dna.yml"])
    command.append("config")

    proc = subprocess.run(
        command,
        cwd=repo_root,
        env=dict(environ),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode != 0:
        return [
            Finding(
                "COMPOSE_CONFIG_FAILED",
                "docker compose config failed; inspect the server configuration without exposing secrets",
            )
        ]
    return []


def check_health(environ: Mapping[str, str]) -> list[Finding]:
    failures: list[Finding] = []
    deploy_url = environ.get("MULTIMIND_DEPLOY_URL", "").rstrip("/") + "/"
    api_url = environ.get("MULTIMIND_API_URL", "").rstrip("/") + "/_health"
    for label, url in (("frontend", deploy_url), ("backend", api_url)):
        try:
            with urlopen(url, timeout=8) as response:  # nosec B310 - operator-supplied http(s) URL is validated separately.
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status}")
        except Exception as exc:  # noqa: BLE001 - preflight must aggregate health failures.
            failures.append(Finding("HEALTH_FAILED", f"{label} health probe failed: {type(exc).__name__}"))
    return failures


def _print_result(failures: list[Finding]) -> int:
    if failures:
        print("FINAL_GATE_PREFLIGHT=FAIL")
        for finding in failures:
            print(f"- {finding.code}: {finding.message}")
        return 1
    print("FINAL_GATE_PREFLIGHT=PASS")
    print("No secret values were printed. This PASS does not authorize production cutover.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production", action="store_true", help="reject localhost and placeholder origins")
    parser.add_argument("--public", action="store_true", help="require HTTPS for public browser/backend origins")
    parser.add_argument("--private-dna", action="store_true", help="require the optional private-DNA token file")
    parser.add_argument("--check-docker", action="store_true", help="validate docker compose configuration")
    parser.add_argument("--health", action="store_true", help="probe configured frontend and backend after deployment")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    environ = dict(os.environ)
    failures = validate_environment(
        environ,
        production=args.production,
        public=args.public,
        private_dna=args.private_dna,
        repo_root=repo_root,
    )
    failures.extend(check_git_secret_ignores(repo_root))
    if args.check_docker:
        failures.extend(check_compose_config(repo_root, environ, private_dna=args.private_dna))
    if args.health and not failures:
        failures.extend(check_health(environ))
    return _print_result(failures)


if __name__ == "__main__":
    sys.exit(main())
