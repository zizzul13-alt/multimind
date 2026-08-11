import google.generativeai as genai
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

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
            response = self.model.generate_content(full_prompt)
            text = response.text if response.text else "No response"
            self.set_availability(True)
            return {
                "status": "success",
                "text": text,
                "agent": f"Gemini ({self.model_name})",
                "tokens": len(text.split()),
                "cost": 0.0
            }
        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"Gemini error: {error_msg[:200]}",
                "agent": f"Gemini ({self.model_name})",
                "tokens": 0,
                "cost": 0.0
            }

    def compress_prompt(self, original_prompt: str) -> dict:
        return {
            "status": "success",
            "text": original_prompt,
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(original_prompt)
        }
