import time
import random
import functools
import threading
from typing import Callable, Tuple, Type, Any
from config.logger import setup_logger

logger = setup_logger("resilience")

class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""
    pass

class CircuitBreaker:
    """
    Circuit breaker implementation to prevent repeated calls to failing remote endpoints.
    States:
      - CLOSED: Normal operation. Errors increment failure counter.
      - OPEN: Fast failure without calling remote resource.
      - HALF_OPEN: Probing state after cooldown period to test recovery.
    """
    def __init__(self, failure_threshold: int = 4, recovery_timeout: float = 30.0, name: str = "default"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with self._lock:
                now = time.time()
                if self.state == "OPEN":
                    if now - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"[CircuitBreaker:{self.name}] Entering HALF_OPEN state. Probing endpoint...")
                    else:
                        raise CircuitBreakerOpenException(
                            f"Circuit '{self.name}' is OPEN. Fast-failing request."
                        )

            try:
                result = func(*args, **kwargs)
                with self._lock:
                    if self.state in ["HALF_OPEN", "OPEN"]:
                        logger.info(f"[CircuitBreaker:{self.name}] Probe succeeded. Resetting circuit to CLOSED.")
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
            except Exception as e:
                with self._lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(
                            f"[CircuitBreaker:{self.name}] Threshold {self.failure_threshold} reached. "
                            f"Tripping circuit to OPEN for {self.recovery_timeout}s."
                        )
                raise e
        return wrapper

class RateLimiter:
    """
    Sliding-window token bucket rate limiter to prevent API quota exhaustion.
    """
    def __init__(self, max_calls: int, period_seconds: float = 1.0):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = []
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.time()
            # Remove calls older than the sliding window period
            self.calls = [t for t in self.calls if now - t < self.period]
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            self.calls.append(time.time())

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)
        return wrapper

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 15.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable:
    """
    Decorator that retries a function with exponential backoff and optional jitter.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"[{func.__name__}] Failed after {attempt} attempts. Final error: {str(e)}"
                        )
                        raise

                    sleep_time = current_delay
                    if jitter:
                        sleep_time += random.uniform(0.1, 0.5 * current_delay)
                    sleep_time = min(sleep_time, max_delay)

                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt}/{max_attempts} failed with {type(e).__name__}: {str(e)}. "
                        f"Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
                    attempt += 1
                    current_delay = min(current_delay * backoff_factor, max_delay)
        return wrapper
    return decorator
