"""
Multi-agent debate orchestrator
"""
import time
from datetime import datetime
from utils.token_counter import TokenCounter
from utils.error_handler import error_logger, APIError, RateLimitError

class DebateOrchestrator:
    """Orchestrate multi-agent debate"""
    
    def __init__(self, gemini_agent, deepseek_agent):
        self.gemini = gemini_agent
        self.deepseek = deepseek_agent
    
    def debate(self, prompt, context="", mode="coding", rounds=3, agents=None):
        """
        Run multi-agent debate
        
        Returns: dict with results and token tracking
        """
        if not agents:
            agents = ["deepseek", "gemini"]
        
        debate_log = {
            "prompt": prompt,
            "context": context,
            "mode": mode,
            "rounds": rounds,
            "agents": agents,
            "responses": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "start_time": datetime.now().isoformat()
        }
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTASK:\n{prompt}"
            
            # Round 1: Solution Provider
            if "deepseek" in agents:
                round1 = self._round_creator(full_prompt, mode)
                debate_log["responses"].append(round1)
                debate_log["total_tokens"] += round1.get("tokens", 0)
                debate_log["total_cost"] += round1.get("cost", 0)
            
            # Round 2: Critic (Gemini - FREE)
            if "gemini" in agents and rounds >= 2:
                solution = round1.get("text", "") if round1.get("status") == "success" else ""
                round2 = self._round_critic(full_prompt, solution, mode)
                debate_log["responses"].append(round2)
                debate_log["total_tokens"] += round2.get("tokens", 0)
                # Gemini is FREE
            
            # Round 3: Refiner (if needed)
            if "deepseek" in agents and rounds >= 3:
                critique = round2.get("text", "") if round2.get("status") == "success" else ""
                round3 = self._round_refiner(full_prompt, round1.get("text", ""), critique)
                debate_log["responses"].append(round3)
                debate_log["total_tokens"] += round3.get("tokens", 0)
                debate_log["total_cost"] += round3.get("cost", 0)
            
            # Synthesize final answer (Gemini - FREE)
            final = self._synthesize(full_prompt, debate_log["responses"])
            debate_log["final_answer"] = final.get("text", "No response generated")
            debate_log["total_tokens"] += final.get("tokens", 0)
            
            debate_log["status"] = "success"
            debate_log["end_time"] = datetime.now().isoformat()
            
        except RateLimitError as e:
            debate_log["status"] = "rate_limit"
            debate_log["error"] = str(e)
            debate_log["final_answer"] = self._fallback_response(prompt)
            error_logger.log("RATE_LIMIT", str(e))
        
        except APIError as e:
            debate_log["status"] = "api_error"
            debate_log["error"] = str(e)
            debate_log["final_answer"] = self._fallback_response(prompt)
            error_logger.log("API_ERROR", str(e))
        
        except Exception as e:
            debate_log["status"] = "error"
            debate_log["error"] = str(e)
            debate_log["final_answer"] = f"Error: {str(e)[:200]}. Please try again."
            error_logger.log("DEBATE_ERROR", str(e))
        
        return debate_log
    
    def _round_creator(self, prompt, mode):
        """Round 1: Create solution"""
        system_prompts = {
            "coding": "You are EXPERT CODER. Write clean, working code with explanation.",
            "research": "You are RESEARCHER. Provide comprehensive analysis with sources.",
            "thinking": "You are SYSTEMS THINKER. Break down complex problems step-by-step."
        }
        system = system_prompts.get(mode, system_prompts["coding"])
        
        return self.deepseek.generate_code(prompt) if mode == "coding" else \
               self.deepseek.generate(prompt, system_prompt=system)
    
    def _round_critic(self, task, solution, mode):
        """Round 2: Critique solution (Gemini - FREE)"""
        system = "You are CODE REVIEWER. Find bugs, edge cases, and improvements."
        if mode != "coding":
            system = "You are CRITICAL THINKER. Challenge assumptions and find flaws."
        
        return self.gemini.generate(
            prompt=f"Task: {task}\n\nSolution:\n{solution[:2000]}\n\nCritique:",
            system_prompt=system,
            max_tokens=500
        )
    
    def _round_refiner(self, task, solution, critique):
        """Round 3: Refine based on critique"""
        system = "You are EXPERT. Improve the solution based on the critique provided."
        
        return self.deepseek.generate(
            prompt=f"Task: {task}\n\nOriginal:\n{solution[:1000]}\n\nCritique:\n{critique[:500]}\n\nRefined solution:",
            system_prompt=system
        )
    
    def _synthesize(self, task, responses):
        """Synthesize final answer (Gemini - FREE)"""
        discussion = "\n\n".join([
            f"[{r.get('agent', 'Unknown')}]: {r.get('text', '')[:500]}"
            for r in responses if r.get("status") == "success"
        ])
        
        return self.gemini.generate(
            prompt=f"Task: {task}\n\nDiscussion:\n{discussion[:2000]}\n\nSynthesize the best final answer:",
            system_prompt="You are SYNTHESIZER. Combine all inputs into one clear, comprehensive answer.",
            max_tokens=1000
        )
    
    def _fallback_response(self, prompt):
        """Simple fallback when all agents fail"""
        return f"I apologize, but I'm having trouble processing your request right now. Please try again in a moment.\n\nYour question: {prompt[:200]}..."