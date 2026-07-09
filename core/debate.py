"""
Multi-agent debate orchestrator - DEBUG VERSION
"""
import streamlit as st

class DebateOrchestrator:
    """Orchestrate multi-agent debate"""

    def __init__(self, gemini_agent, deepseek_agent=None, groq_agent=None, cloudflare_agent=None, openrouter_agent=None, huggingface_agent=None, coze_agent=None):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
        self.groq = groq_agent
        self.cloudflare = cloudflare_agent
        self.openrouter = openrouter_agent
        self.huggingface = huggingface_agent
        self.coze = coze_agent

    def debate(self, prompt, context="", mode="coding", rounds=1, agents=None):
        """DEBUG: Return hardcoded response"""
        result = {
            "prompt": prompt,
            "responses": [
                {"agent": "TEST Cloudflare", "status": "success", "text": "Test cloudflare response", "tokens": 3, "cost": 0},
                {"agent": "TEST Gemini", "status": "success", "text": "Test gemini response", "tokens": 3, "cost": 0},
                {"agent": "TEST Groq", "status": "error", "text": "Rate limit", "tokens": 0, "cost": 0},
            ],
            "final_answer": "TEST FINAL ANSWER - HARDCODE",
            "total_tokens": 6,
            "total_cost": 0.0,
            "status": "success"
        }
        return result

    def _draft_prompt(self, mode):
        return "Be brief."

    def _full_prompt(self, mode):
        return "Be complete."
