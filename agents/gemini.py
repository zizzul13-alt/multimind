"""
Gemini API wrapper - GRATIS!
"""
import google.generativeai as genai
from utils.error_handler import APIError, RateLimitError, retry_with_backoff
from utils.token_counter import TokenCounter

class GeminiAgent:
    """Gemini Flash agent (FREE)"""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.name = "Gemini"
    
    @retry_with_backoff(max_retries=3, delay=2)
    def generate(self, prompt, system_prompt=None, max_tokens=2000):
        """Generate response"""
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
            
            text = response.text
            
            return {
                "status": "success",
                "text": text,
                "agent": self.name,
                "tokens": TokenCounter.count(text),
                "cost": 0  # GRATIS!
            }
        
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "quota" in error_msg:
                raise RateLimitError(f"Gemini rate limit: {e}")
            else:
                raise APIError(f"Gemini error: {e}")
    
    def compress_prompt(self, original_prompt):
        """Compress prompt (FREE)"""
        system = """You are PROMPT COMPRESSOR. Compress user prompt to minimum tokens 
        without losing key information. Use keywords. Remove politeness."""
        
        result = self.generate(
            prompt=f"Compress this:\n{original_prompt}",
            system_prompt=system,
            max_tokens=200
        )
        
        return {
            "original": original_prompt,
            "compressed": result["text"],
            "original_tokens": TokenCounter.count(original_prompt),
            "compressed_tokens": TokenCounter.count(result["text"])
        }
    
    def review_code(self, code, task):
        """Review code (FREE)"""
        system = """You are CODE REVIEWER. Find bugs, security issues, 
        edge cases, and suggest improvements. Be concise."""
        
        result = self.generate(
            prompt=f"Task: {task}\n\nCode:\n{code}\n\nReview:",
            system_prompt=system,
            max_tokens=500
        )
        
        return result
    
    def analyze_image(self, image_file):
        """Analyze image using Gemini Vision (FREE)"""
        try:
            image = genai.upload_file(image_file)
            vision_model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = vision_model.generate_content([
                "Describe this image in detail. Extract all text if any.",
                image
            ])
            
            return {
                "status": "success",
                "text": response.text,
                "tokens": TokenCounter.count(response.text),
                "cost": 0  # GRATIS!
            }
        
        except Exception as e:
            raise APIError(f"Gemini Vision error: {e}")