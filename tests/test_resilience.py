import time
import pytest
from tools.resilience import retry_with_backoff, CircuitBreaker, CircuitBreakerOpenException, RateLimiter

class TestResilienceRetry:
    def test_immediate_success(self):
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01, jitter=False)
        def succeeds_immediately():
            nonlocal call_count
            call_count += 1
            return "SUCCESS"

        result = succeeds_immediately()
        assert result == "SUCCESS"
        assert call_count == 1

    def test_success_after_retries(self):
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01, jitter=False)
        def fails_twice_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary glitch")
            return "RECOVERED"

        result = fails_twice_then_succeeds()
        assert result == "RECOVERED"
        assert call_count == 3

    def test_max_attempts_exceeded_raises(self):
        call_count = 0

        @retry_with_backoff(max_attempts=2, initial_delay=0.01, jitter=False)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent error")

        with pytest.raises(ValueError, match="Permanent error"):
            always_fails()

        assert call_count == 2


class TestCircuitBreaker:
    def test_trips_when_threshold_exceeded(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2, name="test_breaker")

        @cb
        def faulty_operation():
            raise RuntimeError("API dead")

        # Attempt 1: failure
        with pytest.raises(RuntimeError):
            faulty_operation()
        assert cb.state == "CLOSED"

        # Attempt 2: hits threshold -> trips OPEN
        with pytest.raises(RuntimeError):
            faulty_operation()
        assert cb.state == "OPEN"

        # Attempt 3: fast-fails with CircuitBreakerOpenException without running func
        with pytest.raises(CircuitBreakerOpenException):
            faulty_operation()

    def test_recovers_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05, name="recovery_breaker")
        should_succeed = False

        @cb
        def intermittent_op():
            if not should_succeed:
                raise RuntimeError("Down")
            return "UP"

        with pytest.raises(RuntimeError):
            intermittent_op()
        assert cb.state == "OPEN"

        # Wait for recovery timeout
        time.sleep(0.06)
        should_succeed = True
        
        result = intermittent_op()
        assert result == "UP"
        assert cb.state == "CLOSED"


class TestRateLimiter:
    def test_rate_limiter_throttles(self):
        # 3 calls per 0.1 seconds
        limiter = RateLimiter(max_calls=3, period_seconds=0.1)
        timestamps = []

        @limiter
        def quick_call():
            timestamps.append(time.time())

        for _ in range(4):
            quick_call()

        assert len(timestamps) == 4
        # The 4th call should have been delayed until the 0.1s window elapsed
        time_diff = timestamps[3] - timestamps[0]
        assert time_diff >= 0.08
