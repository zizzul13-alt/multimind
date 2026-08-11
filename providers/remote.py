import requests
from providers.base import BaseProvider

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
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.set_availability(True)
                text = data.get("response", "")
                return {
                    "status": "success",
                    "text": text,
                    "agent": f"Remote ({self.api_url})",
                    "tokens": len(text.split()),
                    "cost": 0.0
                }
            else:
                error_msg = f"API error: {response.status_code}"
                self.set_availability(False, error_msg)
                return {
                    "status": "error",
                    "text": error_msg,
                    "agent": "Remote",
                    "tokens": 0,
                    "cost": 0.0
                }
        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"Remote error: {error_msg[:100]}",
                "agent": "Remote",
                "tokens": 0,
                "cost": 0.0
            }
