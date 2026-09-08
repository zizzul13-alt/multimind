"""Regression assertions for intentional prompt-normalization evolution.

These complement older exact-string routing tests without weakening upload/persistence
boundaries: runtime prompts must now contain the common task specification while the
raw prompt remains separately persisted as application truth.
"""
from core.product_semantics import PromptNormalizer


def test_normalized_prompt_retains_raw_task_as_terminal_section():
    normalized = PromptNormalizer().normalize("original user prompt", "coding")["normalized_prompt"]
    assert normalized.startswith("MULTIMIND COMMON TASK SPECIFICATION")
    assert normalized.endswith("USER TASK (preserve intent and literal constraints):\n\noriginal user prompt")


def test_research_normalization_is_not_cosmetic_coding_alias():
    normalizer = PromptNormalizer()
    research = normalizer.normalize("original", "research")["normalized_prompt"]
    coding = normalizer.normalize("original", "coding")["normalized_prompt"]
    assert "TASK MODE: RESEARCH" in research
    assert "evidence-oriented research" in research
    assert research != coding
