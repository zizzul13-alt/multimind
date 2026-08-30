import os

from google import genai
from google.genai import types
from providers.base import BaseProvider
from utils.token_counter import TokenCounter
from utils.config import Config

class GeminiProvider(BaseProvider):
    """Google Gemini AI Provider"""

    IMAGE_MIME_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
    }

    def __init__(self, api_key: str):
        super().__init__("Gemini")
        self.client = None
        self.model = None
        if not api_key or api_key == "":
            self.model_name = "Gemini (not configured)"
            self.set_availability(False, "API key not configured")
            return
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-flash-latest'
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "Gemini (init error)"
            self.set_availability(False, str(e))

    def generate(self, prompt: str, system_prompt: str = None, mode: str = "coding", max_tokens: int = 2000, **kwargs) -> dict:
        if not self.client:
            return {
                "status": "error",
                "text": "Gemini not configured",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self._request_config(),
            )
            return self._normalise_response(response)
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)

    def analyze_image(self, file) -> dict:
        """Describe an S4-validated image using Gemini vision."""
        if not self.client:
            return {
                "status": "error",
                "text": "Gemini not configured",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0,
            }

        filename = getattr(file, "name", "")
        extension = os.path.splitext(filename)[1].lower()
        mime_type = self.IMAGE_MIME_TYPES.get(extension)
        if mime_type is None:
            return self.failure_response("invalid_image_type")

        try:
            original_position = file.tell()
            try:
                file.seek(0)
                image_bytes = file.read()
            finally:
                file.seek(original_position)
            if not image_bytes:
                return self.failure_response("empty_image")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    "Describe the image accurately and extract any relevant visible text.",
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
                config=self._request_config(),
            )
            return self._normalise_response(response)
        except Exception as e:
            self.set_availability(False, type(e).__name__)
            return self.failure_response("network_or_sdk_exception", exception_type=type(e).__name__)

    @staticmethod
    def _request_config():
        """Apply the existing app-level request timeout to the Google SDK."""
        return types.GenerateContentConfig(
            http_options=types.HttpOptions(timeout=Config.API_TIMEOUT * 1000)
        )

    def _normalise_response(self, response):
        text = getattr(response, "text", None)
        if not isinstance(text, str) or not text.strip():
            self.set_availability(False, "Empty response")
            return self.failure_response("empty_response")
        self.set_availability(True)
        return {
            "status": "success",
            "text": text,
            "agent": f"Gemini ({self.model_name})",
            "tokens": len(text.split()),
            "cost": 0.0,
        }

    def compress_prompt(self, original_prompt: str) -> dict:
        return {
            "status": "success",
            "text": original_prompt,
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(original_prompt)
        }
