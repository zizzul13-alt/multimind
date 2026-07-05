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
            
# GANTI JADI:
model_names = [
    'gemini-flash-latest',        # GRATIS (pasti)
    'gemini-flash-lite-latest',   # GRATIS (ringan)
    'gemini-2.0-flash-exp',       # GRATIS (experimental)
    'gemini-1.5-flash',           # GRATIS (standar)
    'models/gemini-1.5-flash',    # Full path
]

self.model = None
for model_name in model_names:
    try:
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        break
    except Exception as e:
        continue
            
            if self.model:
                self.name = f"Gemini ({self.model_name})"
            else:
                self.name = "Gemini (no model)"
                
        except Exception as e:
            print(f"Gemini init error: {e}")
            self.model = None
            self.name = "Gemini (error)"

    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response"""
        if not self.model:
            return {
                "status": "error",
                "text": "Gemini API not configured. Check API key.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )

            text = response.text if response.text else "No response generated"

            return {
                "status": "success",
                "text": text,
                "agent": self.name,
                "tokens": TokenCounter.count(text),
                "cost": 0  # GRATIS!
            }

        except Exception as e:
            error_msg = str(e)
            print(f"Gemini error: {error_msg}")
            return {
                "status": "error",
                "text": f"[Gemini error: {error_msg[:100]}]",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

    def compress_prompt(self, original_prompt):
        """Compress prompt (FREE)"""
        system = "Compress this prompt to minimum tokens without losing key information. Remove politeness. Use keywords."

        result = self.generate(
            prompt=f"Compress:\n{original_prompt}",
            system_prompt=system,
            max_tokens=200
        )

        compressed = result.get("text", original_prompt) if result.get("status") == "success" else original_prompt

        return {
            "status": result.get("status", "error"),
            "text": compressed,
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(compressed)
        }
