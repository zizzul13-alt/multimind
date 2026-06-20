"""
Error handling utilities
"""
import traceback
import functools
import time
from datetime import datetime
from collections import defaultdict

class MultiMindError(Exception):
    """Base error"""
    pass

class APIError(MultiMindError):
    """API provider error"""
    pass

class RateLimitError(MultiMindError):
    """Rate limit reached"""
    pass

class TokenBudgetError(MultiMindError):
    """Token budget exceeded"""
    pass

class DatabaseError(MultiMindError):
    """Database error"""
    pass

class FileError(MultiMindError):
    """File handling error"""
    pass

class ErrorLogger:
    """Simple error logger"""
    
    def __init__(self):
        self.errors = defaultdict(int)
        self.recent = []
    
    def log(self, error_type, message, user_id=None, details=None):
        entry = {
            "time": datetime.now().isoformat(),
            "type": error_type,
            "message": str(message)[:200],
            "user": user_id
        }
        self.errors[error_type] += 1
        self.recent.insert(0, entry)
        self.recent = self.recent[:20]
        
        # Print for Streamlit Cloud logs
        print(f"[{error_type}] User:{user_id} - {message}")
        
        if details:
            print(details[:500])
    
    def get_stats(self):
        return {
            "total": sum(self.errors.values()),
            "by_type": dict(self.errors),
            "recent": self.recent[:5]
        }

# Global logger
error_logger = ErrorLogger()

def handle_api_errors(func):
    """Decorator for API error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            error_logger.log("RATE_LIMIT", str(e))
            return {"status": "rate_limit", "message": str(e), "retry_after": 60}
        except APIError as e:
            error_logger.log("API_ERROR", str(e))
            return {"status": "api_error", "message": str(e)}
        except Exception as e:
            error_logger.log("UNKNOWN", str(e), details=traceback.format_exc())
            return {"status": "error", "message": "Unexpected error occurred"}
    return wrapper

def retry_with_backoff(max_retries=3, delay=2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError:
                    if attempt < max_retries - 1:
                        wait = delay * (2 ** attempt)
                        time.sleep(wait)
                        continue
                    raise
                except APIError as e:
                    if "timeout" in str(e).lower():
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                            continue
                    raise
            raise last_error
        return wrapper
    return decorator