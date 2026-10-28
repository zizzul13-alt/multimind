import os

import reflex as rx


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


config = rx.Config(
    app_name="multimind_reflex",
    app_module_import="multimind_reflex.mobile_entry",
    api_url=os.getenv("MULTIMIND_API_URL", "http://localhost:4000"),
    deploy_url=os.getenv("MULTIMIND_DEPLOY_URL", "http://localhost:4000"),
    backend_port=int(os.getenv("MULTIMIND_BACKEND_PORT", "4000")),
    cors_allowed_origins=_csv_env(
        "MULTIMIND_CORS_ALLOWED_ORIGINS",
        "http://localhost:3000",
    ),
)
