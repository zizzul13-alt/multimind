"""
Token estimation utilities
"""
import re

class TokenCounter:
    """Estimate token count for prompts"""
    
    # Rough estimate: 1 token ≈ 0.75 words (English) or 2-3 chars (Indonesian)
    TOKENS_PER_WORD = 1.3
    CHARS_PER_TOKEN = 3
    
    # Thresholds for warnings
    LOW_THRESHOLD = 300
    MEDIUM_THRESHOLD = 700
    HIGH_THRESHOLD = 1000
    
    # Debate multipliers
    DEBATE_MULTIPLIERS = {
        "coding": 4,
        "research": 3,
        "thinking": 5,
        "custom": 3
    }
    
    @classmethod
    def count(cls, text):
        """Count estimated tokens in text"""
        if not text:
            return 0
        
        # Method 1: Word-based
        words = len(text.split())
        word_estimate = int(words * cls.TOKENS_PER_WORD)
        
        # Method 2: Character-based
        chars = len(text)
        char_estimate = chars // cls.CHARS_PER_TOKEN
        
        # Average both methods
        return (word_estimate + char_estimate) // 2
    
    @classmethod
    def estimate_total(cls, prompt, files_count=0, mode="coding", rounds=3, compressor_on=True):
        """Estimate total tokens for a chat session"""
        
        # Input tokens
        prompt_tokens = cls.count(prompt)
        
        if compressor_on:
            prompt_tokens = int(prompt_tokens * 0.4)  # Compressor saves ~60%
        
        # File tokens (rough estimate)
        file_tokens = files_count * 500  # Average 500 tokens per file
        
        # Output estimate (usually 2-4x input)
        output_tokens = (prompt_tokens + file_tokens) * 3
        
        # Debate multiplier
        multiplier = cls.DEBATE_MULTIPLIERS.get(mode, 3)
        multiplier *= (rounds / 3)
        
        total = int((prompt_tokens + file_tokens + output_tokens) * multiplier)
        
        return {
            "prompt_tokens": prompt_tokens,
            "file_tokens": file_tokens,
            "output_estimate": output_tokens,
            "total_estimate": total,
            "multiplier": round(multiplier, 1)
        }
    
    @classmethod
    def get_warning_level(cls, estimated_total):
        """Get warning level based on estimated tokens"""
        if estimated_total < cls.LOW_THRESHOLD:
            return {"level": "low", "icon": "🟢", "color": "green"}
        elif estimated_total < cls.MEDIUM_THRESHOLD:
            return {"level": "medium", "icon": "🟡", "color": "orange"}
        else:
            return {"level": "high", "icon": "🔴", "color": "red"}
    
    @classmethod
    def estimate_cost(cls, tokens, agent="deepseek"):
        """Estimate cost in USD"""
        rates = {
            "deepseek": 0.14 / 1_000_000,   # $0.14 per 1M tokens
            "gemini": 0,                      # FREE
            "groq": 0,                        # FREE
            "gpt4o": 5.0 / 1_000_000          # $5 per 1M tokens
        }
        return tokens * rates.get(agent, 0)