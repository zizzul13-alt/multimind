"""
Release Gates - Quality control sebelum jawaban final
"""
from utils.token_counter import TokenCounter

class ReleaseGate:
    """Quality check sebelum jawaban ditampilkan"""
    
    @staticmethod
    def check(response_text, mode="coding"):
        """
        Cek kualitas jawaban
        Return: (passed, issues, score)
        """
        issues = []
        score = 10  # Start perfect
        
        # Gate 1: Panjang minimum
        if len(response_text) < 50:
            issues.append("❌ Jawaban terlalu pendek (<50 karakter)")
            score -= 5
        
        # Gate 2: Kepotong?
        if response_text.strip()[-1] not in '.!?…)""'')':
            issues.append("⚠️ Jawaban mungkin kepotong")
            score -= 2
        
        # Gate 3: Error message?
        error_keywords = ["error", "sorry", "unable", "cannot", "maaf", "tidak bisa"]
        first_50 = response_text[:50].lower()
        if any(kw in first_50 for kw in error_keywords):
            issues.append("⚠️ Jawaban diawali error message")
            score -= 3
        
        # Gate 4: Coding mode check
        if mode == "coding":
            if "```" not in response_text and "def " not in response_text and "function" not in response_text:
                issues.append("⚠️ Mode coding tapi tidak ada kode")
                score -= 2
        
        # Gate 5: Research mode check
        if mode == "research" and len(response_text) < 200:
            issues.append("⚠️ Mode research tapi terlalu singkat")
            score -= 2
        
        # Gate 6: Thinking mode check
        if mode == "thinking" and "step" not in response_text.lower():
            issues.append("⚠️ Mode thinking tapi tidak ada step")
            score -= 1
        
        passed = score >= 5
        return passed, issues, score
    
    @staticmethod
    def get_badge(score):
        """Dapatkan badge kualitas"""
        if score >= 9:
            return "🟢 Excellent"
        elif score >= 7:
            return "🟡 Good"
        elif score >= 5:
            return "🟠 Fair"
        else:
            return "🔴 Poor"