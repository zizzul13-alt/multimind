"""
HuggingFace Inference API - Backup GRATIS!
"""
import requests
import time
from utils.token_counter import TokenCounter

class HuggingFaceAgent:
    """HuggingFace agent (FREE - rate limited)"""

    def __init__(self, api_key):
        if not api_key or api_key == "":
            self.api_key = None
            self.name = "HuggingFace (not configured)"
            return

        self.api_key = api_key
        # Model yang PASTI TERSEDIA di HuggingFace
        self.models = {
            "coding": "Qwen/Qwen2.5-Coder-7B-Instruct",
            "research": "meta-llama/Llama-3.1-8B-Instruct",
            "thinking": "Qwen/Qwen3-4B-Thinking-2507",
            "quick": "mistralai/Mistral-7B-Instruct-v0.3"
        }
        self.name = "HuggingFace (Multi-Model)"

    def generate(self, prompt, system_prompt=None, mode="coding", max_tokens=2048):
        """Generate response - dengan retry"""
        if not self.api_key:
            return {
                "status": "error",
                "text": "HuggingFace not configured.",
                "agent": self.name,
                "tokens": 0,
                "cost": 0
            }

        model = self.models.get(mode, self.models["quick"])

        for attempt in range(3):
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                
                payload = {
                    "inputs": full_prompt[:1000],
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
                    
                    if text and len(text) > 10:
                        return {
                            "status": "success",
                            "text": text,
                            "agent": f"HuggingFace ({model})",
                            "tokens": len(text.split()),
                            "cost": 0
                        }
                
                if response.status_code == 503:
                    time.sleep(3)
                    continue
                
                if response.status_code == 429:
                    time.sleep(5)
                    continue

            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return {
                    "status": "error",
                    "text": f"HF error: {str(e)[:100]}",
                    "agent": self.name,
                    "tokens": 0,
                    "cost": 0
                }

        return {
            "status": "error",
            "text": "HF timeout after 3 retries",
            "agent": self.name,
            "tokens": 0,
            "cost": 0
        }
