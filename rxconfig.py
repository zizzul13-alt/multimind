import os

import reflex as rx


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


config = rx.Config(
    app_name="multimind_reflex",
    app_module_import="multimind_reflex.mobile_entry",
    api_url=os.getenv("MULTIMIND_API_URL", "http://localhost:8000"),
    deploy_url=os.getenv("MULTIMIND_DEPLOY_URL", "http://localhost:3000"),
    cors_allowed_origins=_csv_env(
        "MULTIMIND_CORS_ALLOWED_ORIGINS",
        "http://localhost:3000",
    ),
    # The hand-built theme previews ship in the private DNA repo and are copied
    # into the image at /app/preview. Without this Reflex only serves
    # .web/build/client, so every /preview/... path 404s.
    custom_statics={
        "preview": "preview",
    },
)
