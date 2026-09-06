import os

import reflex as rx


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


config = rx.Config(
    app_name="multimind_reflex",
    api_url=os.getenv("MULTIMIND_API_URL", "http://localhost:8000"),
    deploy_url=os.getenv("MULTIMIND_DEPLOY_URL", "http://localhost:3000"),
    cors_allowed_origins=_csv_env(
        "MULTIMIND_CORS_ALLOWED_ORIGINS",
        "http://localhost:3000",
    ),
)
