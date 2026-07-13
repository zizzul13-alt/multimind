"""
Remote Agent - Panggil PythonAnywhere API
"""
import requests

class RemoteAgent:
    """Agent yang panggil API eksternal"""

    def __init__(self, api_url):
        self.api_url = api_url

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=4096):
        """Generate response via API"""
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
                return {
                    "status": "success",
                    "text": data.get("response", ""),
                    "agent": f"Remote ({self.api_url})",
                    "tokens": len(data.get("response", "").split()),
                    "cost": 0
                }
            else:
                return {
                    "status": "error",
                    "text": f"API error: {response.status_code}",
                    "agent": "Remote",
                    "tokens": 0,
                    "cost": 0
                }
        except Exception as e:
            return {
                "status": "error",
                "text": f"Remote error: {str(e)[:100]}",
                "agent": "Remote",
                "tokens": 0,
                "cost": 0
            }
