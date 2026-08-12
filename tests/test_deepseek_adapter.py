#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for adapters.deepseek_adapter — safety components.
Tests circuit breaker, rate limiter, cost tracker, and prompt safety.
"""

import pytest
import time

from adapters.deepseek_adapter import (
    CircuitBreaker,
    RateLimiter,
    CostTracker,
    ALLOWED_IMPORTS,
    FORBIDDEN_IMPORTS,
    SAFETY_PROMPT,
)


class TestCircuitBreaker:
    def test_success_resets_failures(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        cb.call(lambda: 42)
        assert cb._failures == 0

    def test_failure_counts(self):
        cb = CircuitBreaker(failure_threshold=3)

        def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            cb.call(fail)
        assert cb._failures == 1

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2)

        def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            cb.call(fail)
        with pytest.raises(RuntimeError):
            cb.call(fail)
        assert cb._open is True
        with pytest.raises(RuntimeError, match="OPEN"):
            cb.call(lambda: 42)

    def test_recovery_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            cb.call(fail)
        assert cb._open is True
        time.sleep(0.15)
        result = cb.call(lambda: 42)
        assert result == 42
        assert cb._open is False


class TestRateLimiter:
    def test_allows_under_limit(self):
        rl = RateLimiter(max_requests=3, window_sec=60.0)
        rl.acquire()
        rl.acquire()
        rl.acquire()
        assert len(rl._timestamps) == 3

    def test_blocks_over_limit(self):
        rl = RateLimiter(max_requests=2, window_sec=60.0)
        rl.acquire()
        rl.acquire()
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            rl.acquire()

    def test_window_slides(self):
        rl = RateLimiter(max_requests=1, window_sec=0.1)
        rl.acquire()
        time.sleep(0.15)
        rl.acquire()
        assert len(rl._timestamps) == 1


class TestCostTracker:
    def test_tracks_cost(self):
        ct = CostTracker(max_cost_usd=1.0)
        ct.add("deepseek-chat", 1000, 500)
        assert ct._cost > 0

    def test_remaining(self):
        ct = CostTracker(max_cost_usd=1.0)
        ct.add("deepseek-chat", 1000000, 500000)
        assert ct.remaining >= 0

    def test_check_raises(self):
        ct = CostTracker(max_cost_usd=0.01)
        ct.add("deepseek-chat", 1000000, 500000)
        with pytest.raises(RuntimeError, match="Cost limit exceeded"):
            ct.check()


class TestSafetyConfig:
    def test_allowed_not_empty(self):
        assert len(ALLOWED_IMPORTS) > 20

    def test_forbidden_not_empty(self):
        assert len(FORBIDDEN_IMPORTS) > 5

    def test_no_overlap(self):
        overlap = ALLOWED_IMPORTS & FORBIDDEN_IMPORTS
        assert overlap == set()

    def test_safety_prompt_contains_rules(self):
        assert "CRITICAL SAFETY RULES" in SAFETY_PROMPT
        assert "NEVER import" in SAFETY_PROMPT
        assert "exec()" in SAFETY_PROMPT
        assert "eval()" in SAFETY_PROMPT

    def test_forbidden_contains_dangerous(self):
        assert "socket" in FORBIDDEN_IMPORTS
        assert "subprocess" in FORBIDDEN_IMPORTS
        assert "urllib.request" in FORBIDDEN_IMPORTS
        assert "os.system" in FORBIDDEN_IMPORTS


class TestDeepSeekAdapterStructure:
    def test_init_without_key(self):
        from adapters.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter(api_key="")
        assert adapter.api_key == ""
        adapter.close()

    def test_init_with_key(self):
        from adapters.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter(api_key="sk-test", max_cost_usd=0.5)
        assert adapter.api_key == "sk-test"
        assert adapter.cost_tracker.max_cost_usd == 0.5
        adapter.close()

    def test_stats_structure(self):
        from adapters.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter(api_key="sk-test")
        stats = adapter.get_stats()
        assert "model" in stats
        assert "total_cost_usd" in stats
        assert "remaining_budget_usd" in stats
        assert "circuit_failures" in stats
        assert "circuit_open" in stats
        adapter.close()

    def test_call_api_raises_without_key(self):
        from adapters.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter(api_key="")
        with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY not set"):
            adapter._call_api([{"role": "user", "content": "test"}])
        adapter.close()