"""
Prompt compressor module
"""
from utils.token_counter import TokenCounter

class PromptCompressor:
    """Compress prompts to save tokens"""
    
    @staticmethod
    def should_compress(prompt, config):
        """Check if compression should be applied"""
        if not config.get("enabled", True):
            return False
        
        words = len(prompt.split())
        if words < 15:
            return False  # Already short
        
        return True
    
    @staticmethod
    def compress(prompt, gemini_agent):
        """Compress prompt using Gemini (FREE)"""
        result = gemini_agent.compress_prompt(prompt)
        
        original_tokens = result["original_tokens"]
        compressed_tokens = result["compressed_tokens"]
        
        return {
            "original": prompt,
            "compressed": result["compressed"],
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "saved_tokens": original_tokens - compressed_tokens,
            "saved_percent": round((1 - compressed_tokens/original_tokens) * 100, 1) if original_tokens > 0 else 0
        }
    
    @staticmethod
    def get_compression_tips(prompt_tokens):
        """Get tips for saving tokens"""
        tips = []
        
        if prompt_tokens > 200:
            tips.append("💡 Prompt agak panjang, ringkas 50%")
        if "tolong" in prompt_tokens or "terima kasih" in prompt_tokens:
            tips.append("✂️ Hapus kata basa-basi (tolong, terima kasih)")
        if len(prompt_tokens.split('.')) > 5:
            tips.append("📏 Pecah jadi poin-poin singkat")
        
        return tips