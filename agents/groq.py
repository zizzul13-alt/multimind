"""
Groq API wrapper - GRATIS & SUPER CEPAT!
"""
from openai import OpenAI
from utils.token_counter import TokenCounter

class GroqAgent:
    """Groq agent (FREE - 500 tok/detik!)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.client = None
            self.name = "Groq (not configured)"
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.1-70b-versatile"
            self.name = "Groq (Llama 3.1 70B)"
        except Exception as e:
            print(f"Groq init error: {e}")
            self.client = None
            self.name = "Groq (error)"

    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response - SUPER CEPAT!"""
        if not self.client:
            return {
                "status": "error",
                "text": "Groq API not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            text = response.choices[0].message.content

            return {
    "status": "success",
    "text": text,
    "agent": self.name,
    "tokens": response.usage.total_tokens if response.usage else len(text.split()),
    "cost": 0
}

        except Exception as e:
            error_msg = str(e)
            print(f"Groq error: {error_msg}")
            return {
                "status": "error",
                "text": f"[Groq unavailable: {error_msg[:100]}]",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
