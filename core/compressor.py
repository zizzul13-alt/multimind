"""Prompt compression utility with preservation guards."""
from __future__ import annotations

import re


class PromptCompressor:
    """Compress a normalized task without silently changing task-critical literals."""

    CODE_BLOCK = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    NUMBER = re.compile(r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?%?|0x[0-9a-fA-F]+)(?!\w)")
    PATH = re.compile(r"(?:[A-Za-z]:\\[^\s]+|(?:\.?\.?/|/)[\w.\-/\\]+|[\w.-]+\.(?:py|js|ts|tsx|jsx|json|ya?ml|toml|ini|md|txt|csv|sql|db))")
    CONSTRAINT_LINE = re.compile(r"(?im)^.*\b(?:MUST|MUST NOT|DO NOT|NEVER|REQUIRED|ERROR|EXCEPTION|SOURCE|EVIDENCE)\b.*$")

    @staticmethod
    def should_compress(prompt, config):
        if not config.get("enabled", True):
            return False
        return len(str(prompt or "").split()) >= 15

    @classmethod
    def critical_fragments(cls, prompt):
        text = str(prompt or "")
        fragments = []
        for pattern in (cls.CODE_BLOCK, cls.CONSTRAINT_LINE, cls.PATH, cls.NUMBER):
            fragments.extend(match.group(0).strip() for match in pattern.finditer(text))
        # Stable de-duplication avoids making validation dependent on set ordering.
        return [fragment for fragment in dict.fromkeys(fragments) if fragment]

    @classmethod
    def preserves_critical_content(cls, original, compressed):
        compressed = str(compressed or "")
        return all(fragment in compressed for fragment in cls.critical_fragments(original))

    @classmethod
    def compress(cls, prompt, utility_agent):
        """Call an explicit utility agent and reject lossy compression.

        The caller owns utility-agent selection. This method never routes/falls back.
        """
        if utility_agent is None or not hasattr(utility_agent, "compress_prompt"):
            return {
                "original": prompt,
                "compressed": prompt,
                "applied": False,
                "fallback_reason": "utility_unavailable",
                "original_tokens": 0,
                "compressed_tokens": 0,
                "saved_tokens": 0,
                "saved_percent": 0,
            }

        result = utility_agent.compress_prompt(prompt)
        candidate = result.get("text", prompt) if isinstance(result, dict) else prompt
        original_tokens = result.get("original_tokens", 0) if isinstance(result, dict) else 0
        compressed_tokens = result.get("compressed_tokens", 0) if isinstance(result, dict) else 0
        preserved = cls.preserves_critical_content(prompt, candidate)
        if not preserved:
            candidate = prompt
            compressed_tokens = original_tokens

        saved_tokens = max(0, original_tokens - compressed_tokens)
        return {
            "original": prompt,
            "compressed": candidate,
            "applied": preserved and candidate != prompt,
            "fallback_reason": None if preserved else "preservation_guard",
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "saved_tokens": saved_tokens,
            "saved_percent": round((saved_tokens / original_tokens) * 100, 1) if original_tokens > 0 else 0,
        }

    @staticmethod
    def get_compression_tips(prompt):
        text = str(prompt or "")
        tips = []
        if len(text.split()) > 200:
            tips.append("💡 Prompt agak panjang, ringkas 50%")
        lowered = text.lower()
        if "tolong" in lowered or "terima kasih" in lowered:
            tips.append("✂️ Hapus kata basa-basi")
        if len(text.split('.')) > 5:
            tips.append("📏 Pecah jadi poin-poin singkat")
        return tips
