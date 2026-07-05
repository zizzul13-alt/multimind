"""
Gemini API wrapper - GRATIS!
"""
import google.generativeai as genai
from utils.token_counter import TokenCounter

class GeminiAgent:
    """Gemini agent (FREE)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.model = None
            self.name = "Gemini (not configured)"
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.model_name = 'gemini-flash-latest'
            self.name = "Gemini (gemini-flash-latest)"
        except Exception as e:
            self.model = None
            self.name = "Gemini (init error)"

    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response"""
        if not self.model:
            return {
                "status": "error",
                "text": "Gemini API not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            text = response.text if response.text else "No response"

            return {
                "status": "success",
                "text": text,
                "agent": self.name,
                "tokens": len(text.split()),
                "cost": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "text": f"Gemini error: {str(e)[:200]}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

    def compress_prompt(self, original_prompt):
        """Compress prompt"""
        return {
            "status": "success",
            "text": original_prompt,
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(original_prompt)
        }
