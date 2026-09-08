"""Token estimation utilities."""


class TokenCounter:
    """Estimate token/call implications before a MultiMind run."""

    # Rough estimate: 1 token ≈ 0.75 words (English) or 2-3 chars (Indonesian)
    TOKENS_PER_WORD = 1.3
    CHARS_PER_TOKEN = 3

    LOW_THRESHOLD = 300
    MEDIUM_THRESHOLD = 700
    HIGH_THRESHOLD = 1000

    @classmethod
    def count(cls, text):
        if not text:
            return 0
        words = len(text.split())
        word_estimate = int(words * cls.TOKENS_PER_WORD)
        chars = len(text)
        char_estimate = chars // cls.CHARS_PER_TOKEN
        return (word_estimate + char_estimate) // 2

    @classmethod
    def estimate_total(
        cls,
        prompt,
        files_count=0,
        mode="coding",
        rounds=3,
        compressor_on=True,
        participants=1,
    ):
        """Estimate bounded deliberation usage from the real call-graph semantics.

        Deliberation currently performs one independent call per participant,
        one critique call per successful participant for each round after round 1,
        and one judge/synthesis utility call. This estimate assumes every selected
        participant remains successful, so it intentionally represents the upper
        normal call count rather than silently underestimating a full panel.
        """
        try:
            participant_count = max(1, int(participants))
        except (TypeError, ValueError):
            participant_count = 1
        try:
            round_count = max(1, min(5, int(rounds)))
        except (TypeError, ValueError):
            round_count = 1

        prompt_tokens = cls.count(prompt)
        if compressor_on:
            prompt_tokens = int(prompt_tokens * 0.4)

        file_tokens = max(0, int(files_count or 0)) * 500
        shared_input_tokens = prompt_tokens + file_tokens

        # Approximate one response as 3x the shared input. Critiques are usually
        # shorter, but they also receive panel context; keep one simple conservative
        # estimate instead of pretending we can price provider-specific contexts here.
        output_tokens = shared_input_tokens * 3
        participant_calls = participant_count * round_count
        judge_calls = 1
        provider_calls_estimate = participant_calls + judge_calls
        total = int((shared_input_tokens + output_tokens) * provider_calls_estimate)

        return {
            "prompt_tokens": prompt_tokens,
            "file_tokens": file_tokens,
            "output_estimate": output_tokens,
            "total_estimate": total,
            "multiplier": float(provider_calls_estimate),
            "participants": participant_count,
            "rounds": round_count,
            "participant_calls_estimate": participant_calls,
            "judge_calls_estimate": judge_calls,
            "provider_calls_estimate": provider_calls_estimate,
        }

    @classmethod
    def get_warning_level(cls, estimated_total):
        if estimated_total < cls.LOW_THRESHOLD:
            return {"level": "low", "icon": "🟢", "color": "green"}
        if estimated_total < cls.MEDIUM_THRESHOLD:
            return {"level": "medium", "icon": "🟡", "color": "orange"}
        return {"level": "high", "icon": "🔴", "color": "red"}

    @classmethod
    def estimate_cost(cls, tokens, agent="deepseek"):
        """Legacy rough cost hint; real provider responses remain authoritative."""
        rates = {
            "deepseek": 0.14 / 1_000_000,
            "gemini": 0,
            "groq": 0,
            "gpt4o": 5.0 / 1_000_000,
        }
        return tokens * rates.get(agent, 0)
