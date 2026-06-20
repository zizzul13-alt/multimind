"""
Session memory management
"""
from datetime import datetime
from utils.token_counter import TokenCounter

class SessionMemory:
    """Short-term memory for a session"""
    
    def __init__(self, max_tokens=800):
        self.max_tokens = max_tokens
        self.short_term = []     # Recent chats
        self.long_term = ""      # Summary of old chats
        self.decisions = []      # Key decisions
    
    def add_chat(self, prompt, response):
        """Add chat to memory"""
        entry = {
            "prompt": prompt,
            "response": response[:500],
            "tokens": TokenCounter.count(prompt + response),
            "time": datetime.now().isoformat()
        }
        
        self.short_term.append(entry)
        
        # Move old to long-term
        if len(self.short_term) > 3:
            old = self.short_term.pop(0)
            self._archive(old)
        
        # Track decisions
        if any(kw in prompt.lower() for kw in ["final", "putuskan", "jadi", "pilih"]):
            self.decisions.append({
                "decision": response[:200],
                "time": datetime.now().isoformat()
            })
    
    def _archive(self, entry):
        """Archive old chat to long-term summary"""
        summary = f"- Topic: {entry['prompt'][:100]}... | Result: {entry['response'][:100]}..."
        
        if self.long_term:
            self.long_term += f"\n{summary}"
        else:
            self.long_term = summary
        
        # Keep long-term under limit
        if TokenCounter.count(self.long_term) > 300:
            self.long_term = self.long_term[-500:]  # Simple truncation
    
    def get_context(self):
        """Get context for AI"""
        parts = []
        total = 0
        
        # 1. Key decisions
        if self.decisions:
            dec_text = "KEY DECISIONS:\n" + "\n".join([f"- {d['decision']}" for d in self.decisions[-5:]])
            dec_tokens = TokenCounter.count(dec_text)
            if total + dec_tokens < self.max_tokens * 0.3:
                parts.append(dec_text)
                total += dec_tokens
        
        # 2. Long-term summary
        if self.long_term:
            lt_tokens = TokenCounter.count(self.long_term)
            if total + lt_tokens < self.max_tokens * 0.5:
                parts.append(f"PREVIOUS:\n{self.long_term}")
                total += lt_tokens
        
        # 3. Recent chats
        recent_text = "RECENT:\n"
        for chat in self.short_term:
            chat_text = f"Q: {chat['prompt'][:100]}\nA: {chat['response'][:200]}\n\n"
            chat_tokens = TokenCounter.count(chat_text)
            if total + chat_tokens > self.max_tokens:
                break
            recent_text += chat_text
            total += chat_tokens
        
        parts.append(recent_text)
        return "\n".join(parts)
    
    def get_stats(self):
        """Get memory statistics"""
        context = self.get_context()
        return {
            "short_term_chats": len(self.short_term),
            "decisions": len(self.decisions),
            "context_tokens": TokenCounter.count(context),
            "max_tokens": self.max_tokens,
            "free_percent": round((1 - TokenCounter.count(context)/self.max_tokens) * 100)
        }