"""
Prompt compressor module
"""
from utils.token_counter import TokenCounter

class PromptCompressor:
    """Compress prompts to save tokens"""
    
    @staticmethod
    def should_compress(prompt, config):
        if not config.get("enabled", True):
            return False
        words = len(prompt.split())
        if words < 15:
            return False
        return True
    
    @staticmethod
    def compress(prompt, gemini_agent):
        result = gemini_agent.compress_prompt(prompt)
        original_tokens = result.get("original_tokens", 0)
        compressed_tokens = result.get("compressed_tokens", 0)
        return {
            "original": prompt,
            "compressed": result.get("text", prompt),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "saved_tokens": original_tokens - compressed_tokens,
            "saved_percent": round((1 - compressed_tokens/original_tokens) * 100, 1) if original_tokens > 0 else 0
        }
    
    @staticmethod
    def get_compression_tips(prompt_tokens):
        tips = []
        if prompt_tokens > 200:
            tips.append("💡 Prompt agak panjang, ringkas 50%")
        if "tolong" in prompt_tokens or "terima kasih" in prompt_tokens:
            tips.append("✂️ Hapus kata basa-basi")
        if len(prompt_tokens.split('.')) > 5:
            tips.append("📏 Pecah jadi poin-poin singkat")
        return tips
