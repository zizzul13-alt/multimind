import requests
from providers.base import BaseProvider
from utils.config import Config
from utils.error_handler import error_logger

class RemoteProvider(BaseProvider):
    """Remote Provider calling PythonAnywhere or similar APIs"""

    def __init__(self, api_url: str):
        super().__init__("Remote")
        self.api_url = api_url
        if not api_url or api_url == "":
            self.set_availability(False, "API URL not configured")
        else:
            self.set_availability(True)

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 4096, **kwargs) -> dict:
        if not self.api_url:
            return {
                "status": "error",
                "text": "Remote API URL not configured.",
                "agent": "Remote",
                "tokens": 0,
                "cost": 0.0
            }

        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "prompt": prompt,
                    "mode": mode,
                    "agent": "gemini"
                },
                timeout=Config.API_TIMEOUT
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    self.set_availability(False, "Malformed response")
                    error_logger.log("PROVIDER_FAILURE", "provider=Remote category=malformed_response")
                    return self.failure_response("malformed_response")
                self.set_availability(True)
                text = data.get("response") if isinstance(data, dict) else None
                if not isinstance(text, str) or not text.strip():
                    self.set_availability(False, "Malformed or empty response")
                    error_logger.log("PROVIDER_FAILURE", "provider=Remote category=malformed_response")
                    return self.failure_response("malformed_response")
                return {
                    "status": "success",
                    "text": text,
                    "agent": f"Remote ({self.api_url})",
                    "tokens": len(text.split()),
                    "cost": 0.0
                }
            else:
                self.set_availability(False, f"HTTP {response.status_code}")
                error_logger.log("PROVIDER_FAILURE", f"provider=Remote category=http_status status_code={response.status_code}")
                return self.failure_response("http_status", status_code=response.status_code)
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            error_logger.log("PROVIDER_FAILURE", f"provider=Remote category=network_or_sdk_exception exception_type={type(e).__name__}")
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)
