"""
DeepSeek API wrapper - MURAH!
"""
from openai import OpenAI
from utils.error_handler import APIError, RateLimitError, retry_with_backoff
from utils.token_counter import TokenCounter

class DeepSeekAgent:
    """DeepSeek agent (CHEAP)"""
    
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.name = "DeepSeek"
    
    @retry_with_backoff(max_retries=3, delay=2)
    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            text = response.choices[0].message.content
            
            return {
                "status": "success",
                "text": text,
                "agent": self.name,
                "tokens": response.usage.total_tokens if response.usage else TokenCounter.count(text),
                "cost": self._calculate_cost(
                    response.usage.prompt_tokens if response.usage else 0,
                    response.usage.completion_tokens if response.usage else 0
                )
            }
        
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg:
                raise RateLimitError(f"DeepSeek rate limit: {e}")
            else:
                raise APIError(f"DeepSeek error: {e}")
    
    def _calculate_cost(self, input_tokens, output_tokens):
        """Calculate cost (DeepSeek pricing)"""
        input_cost = input_tokens * 0.14 / 1_000_000   # $0.14/1M
        output_cost = output_tokens * 0.28 / 1_000_000  # $0.28/1M
        return input_cost + output_cost
    
    def generate_code(self, task, context=""):
        """Generate code solution"""
        system = """You are EXPERT CODER. Write clean, efficient code with 
        error handling and comments. Output code only with brief explanation."""
        
        prompt = f"Task: {task}\n"
        if context:
            prompt += f"Context:\n{context}\n"
        prompt += "\nCode solution:"
        
        return self.generate(prompt, system_prompt=system, max_tokens=1500)