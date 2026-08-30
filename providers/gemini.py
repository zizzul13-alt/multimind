import google.generativeai as genai
from providers.base import BaseProvider
from utils.token_counter import TokenCounter
from utils.config import Config

class GeminiProvider(BaseProvider):
    """Google Gemini AI Provider"""

    def __init__(self, api_key: str):
        super().__init__("Gemini")
        if not api_key or api_key == "":
            self.model = None
            self.model_name = "Gemini (not configured)"
            self.set_availability(False, "API key not configured")
            return
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.model_name = 'gemini-flash-latest'
            self.set_availability(True)
        except Exception as e:
            self.model = None
            self.model_name = "Gemini (init error)"
            self.set_availability(False, str(e))

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2000, **kwargs) -> dict:
        if not self.model:
            return {
                "status": "error",
                "text": "Gemini not configured",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(
                full_prompt,
                request_options={"timeout": Config.API_TIMEOUT}
            )
            text = response.text
            if not isinstance(text, str) or not text.strip():
                self.set_availability(False, "Empty response")
                return self.failure_response("empty_response")
            self.set_availability(True)
            return {
                "status": "success",
                "text": text,
                "agent": f"Gemini ({self.model_name})",
                "tokens": len(text.split()),
                "cost": 0.0
            }
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)

    def compress_prompt(self, original_prompt: str) -> dict:
        return {
            "status": "success",
            "text": original_prompt,
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(original_prompt)
        }
