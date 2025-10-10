import time
from typing import Callable, Any
from flask import abort

class RateLimiter:
    def __init__(self, min_call_interval: float = 2.0):
        self.min_call_interval = min_call_interval
        self.last_api_call = 0
    
    def enforce_rate_limit(self):
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            print(f"Waiting {sleep_time:.1f}s for next API call...")
            time.sleep(sleep_time)
        
        self.last_api_call = time.time()
    
    def execute_with_retry(self, operation: Callable, 
                          fallback_value: Any = None,
                          max_attempts: int = 5,
                          min_delay: float = 0.5,
                          max_delay: float = 3.0):
        attempt = 0
        
        while attempt < max_attempts:
            try:
                return operation()
                
            except Exception as e:
                if self._is_rate_limit_error(e):
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                    print(f"[Rate Limit] Attempt {attempt+1}/{max_attempts}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                elif self._is_validation_error(e):
                    abort(422)
                else:
                    print(f"API Error: {e}")
                    return fallback_value
        
        return fallback_value
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        return hasattr(error, 'status_code') and getattr(error, 'status_code') == 429
    
    def _is_validation_error(self, error: Exception) -> bool:
        return hasattr(error, 'status_code') and getattr(error, 'status_code') == 422