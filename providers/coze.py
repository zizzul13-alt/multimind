from openai import OpenAI
from providers.base import BaseProvider
from utils.token_counter import TokenCounter

class CozeProvider(BaseProvider):
    """Coze API Provider (GPT-4o FREE credits)"""

    def __init__(self, api_key: str):
        super().__init__("Coze")
        if not api_key or api_key == "":
            self.client = None
            self.model_name = "Coze (not configured)"
            self.set_availability(False, "API key not configured")
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.coze.com/v1"
            )
            self.models = {
                "light": "gpt-4o-mini",      # 100x/hari - AMAN!
                "medium": "gpt-4o",           # 10x/hari
                "heavy": "claude-3.5-sonnet", # 5x/hari
                "ultra": "gpt-5"              # 5x/hari - PALING PINTAR!
            }
            self.model_name = "Coze (GPT-4o mini)"
            self.set_availability(True)
        except Exception as e:
            self.client = None
            self.model_name = "Coze (error)"
            self.set_availability(False, str(e))

    def detect_complexity(self, prompt: str) -> int:
        """Deteksi kompleksitas prompt (1-5)"""
        length = len(prompt.split())
        keywords_complex = ["arsitektur", "design pattern", "optimasi", "analisis mendalam",
                            "research", "paper", "skripsi", "tesis", "disertasi", "jurnal"]
        keywords_simple = ["halo", "apa itu", "contoh", "cara", "definisi", "tutorial"]

        score = 1  # Default simple

        # Length scoring
        if length > 500:
            score += 2
        elif length > 200:
            score += 1

        # Keyword scoring
        for kw in keywords_complex:
            if kw in prompt.lower():
                score += 2
                break

        for kw in keywords_simple:
            if kw in prompt.lower():
                score -= 1
                break

        return max(1, min(5, score))  # Clamp 1-5

    def generate(self, prompt: str, system_prompt: str = None, complexity: int = 1, max_tokens: int = 2048, mode: str = "coding", **kwargs) -> dict:
        """Generate response - auto-pilih model sesuai kompleksitas"""
        if not self.client:
            return {
                "status": "error",
                "text": "Coze not configured.",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }

        try:
            complexity_val = int(complexity)
        except Exception:
            complexity_val = 1

        # Auto-pilih model
        if complexity_val >= 5:
            model = self.models["ultra"]    # GPT-5!
            used_credits = 2.0
        elif complexity_val >= 4:
            model = self.models["heavy"]    # Claude 3.5 Sonnet
            used_credits = 1.0
        elif complexity_val >= 3:
            model = self.models["medium"]   # GPT-4o
            used_credits = 1.0
        else:
            model = self.models["light"]    # GPT-4o mini (AMAN)
            used_credits = 0.0  # 100x/hari, ga dihitung

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            text = response.choices[0].message.content
            self.set_availability(True)

            return {
                "status": "success",
                "text": text,
                "agent": f"Coze ({model})",
                "tokens": response.usage.total_tokens if response.usage else len(text.split()),
                "cost": used_credits,
                "complexity": complexity_val
            }

        except Exception as e:
            error_msg = str(e)
            self.set_availability(False, error_msg)
            return {
                "status": "error",
                "text": f"Coze error: {error_msg[:150]}",
                "agent": self.model_name,
                "tokens": 0,
                "cost": 0.0
            }
