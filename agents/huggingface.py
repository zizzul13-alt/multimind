"""
HuggingFace Inference API - Backup GRATIS!
"""
import requests
from utils.token_counter import TokenCounter

class HuggingFaceAgent:
    """HuggingFace agent (FREE - rate limited)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.api_key = None
            self.name = "HuggingFace (not configured)"
            return

        self.api_key = api_key
        self.models = {
            "coding": "Qwen/Qwen2.5-1.5B-Instruct",      # Lebih ringan
            "research": "google/gemma-2b",                # Ringan
            "thinking": "microsoft/phi-2",                # Ringan
            "quick": "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # Paling ringan
        }
        self.name = "HuggingFace (Multi-Model)"

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=2048):
        """Generate response"""
        if not self.api_key:
            return {
                "status": "error",
                "text": "HuggingFace not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        model = self.models.get(mode, self.models["quick"])

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            payload = {
                "inputs": full_prompt[:2000],
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }

            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                else:
                    text = str(result)
                
                return {
                    "status": "success",
                    "text": text,
                    "agent": f"HuggingFace ({model})",
                    "tokens": len(text.split()),
                    "cost": 0
                }
            else:
                return {
                    "status": "error",
                    "text": f"HF error {response.status_code}: {response.text[:100]}",
                    "agent": self.name,
                    "tokens": 0,
                    "cost": 0
                }

        except Exception as e:
            return {
                "status": "error",
                "text": f"HF error: {str(e)[:150]}",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }
