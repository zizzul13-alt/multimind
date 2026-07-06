"""
Coze API wrapper - GPT-4o GRATIS! (Credit-based)
"""
from openai import OpenAI
from utils.token_counter import TokenCounter

class CozeAgent:
    """Coze agent (FREE credits)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.client = None
            self.name = "Coze (not configured)"
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
            self.name = "Coze (GPT-4o mini)"
        except Exception as e:
            print(f"Coze init error: {e}")
            self.client = None
            self.name = "Coze (error)"

    def detect_complexity(self, prompt):
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

    def generate(self, prompt, system_prompt=None, complexity=1, max_tokens=2048):
        """Generate response - auto-pilih model sesuai kompleksitas"""
        if not self.client:
            return {
                "status": "error",
                "text": "Coze not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        # Auto-pilih model
        if complexity >= 5:
            model = self.models["ultra"]    # GPT-5!
            used_credits = 2
        elif complexity >= 4:
            model = self.models["heavy"]    # Claude 3.5 Sonnet
            used_credits = 1
        elif complexity >= 3:
            model = self.models["medium"]   # GPT-4o
            used_credits = 1
        else:
            model = self.models["light"]    # GPT-4o mini (AMAN)
            used_credits = 0  # 100x/hari, ga dihitung

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

            return {
                "status": "success",
                "text": text,
                "agent": f"Coze ({model})",
                "tokens": response.usage.total_tokens if response.usage else len(text.split()),
                "cost": used_credits,
                "complexity": complexity
            }

        except Exception as e:
            return {
                "status": "error",
                "text": f"Coze error: {str(e)[:150]}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
