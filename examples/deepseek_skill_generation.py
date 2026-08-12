#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Skill Generation Demo.
Shows how to attach DeepSeek adapter to AutoSkillEngine for real LLM skill generation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_skills import AutoSkillEngine
from adapters.deepseek_adapter import attach_deepseek_to_engine, ALLOWED_IMPORTS, FORBIDDEN_IMPORTS


TASKS = [
    "Implement a priority task queue with deadline scheduling",
    "Create a circuit breaker pattern for HTTP clients",
    "Build an LRU cache with TTL expiration",
]


def main():
    print("=" * 70)
    print("DEEPSEEK SKILL GENERATION DEMO")
    print("Real LLM-generated skills via DeepSeek API")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] DEEPSEEK_API_KEY not set.")
        print("    Get one at: https://platform.deepseek.com")
        print("    Then run: set DEEPSEEK_API_KEY=your-key")
        print("\n    Demo will show adapter structure only.")
        show_structure_only = True
    else:
        show_structure_only = False

    # Initialize engine
    engine = AutoSkillEngine(use_llm=False)

    if show_structure_only:
        print("\n[1/3] Adapter structure (no API key):")
        print("-" * 70)
        from adapters.deepseek_adapter import DeepSeekAdapter

        adapter = DeepSeekAdapter(api_key="dummy", max_cost_usd=0.5, max_requests_per_min=5)
        print(f"    Model: {adapter.model}")
        print(f"    Cost limit: ${adapter.cost_tracker.max_cost_usd:.2f}")
        print(f"    Rate limit: {adapter.rate_limiter.max_requests} req/min")
        print(f"    Circuit breaker threshold: {adapter.circuit.failure_threshold}")
        print(f"    Allowed imports: {len(ALLOWED_IMPORTS)} modules")
        print(f"    Forbidden imports: {len(FORBIDDEN_IMPORTS)} modules")
        adapter.close()

        print("\n[2/3] Safety checks:")
        print("-" * 70)
        print("    ✅ Circuit breaker — stops after 3 failures")
        print("    ✅ Rate limiter — max 5 requests/minute")
        print("    ✅ Cost tracker — stops at $0.50")
        print("    ✅ Import whitelist — only stdlib allowed")
        print("    ✅ Import blacklist — no socket/subprocess/urllib")
        print("    ✅ AST validation — checks generated code")
        print("    ✅ Pytest sandbox — runs tests in temp file")
        print("    ✅ Timeout — 30 sec per API call")
        print("    ✅ Retry — exponential backoff 3 attempts")

        print("\n[3/3] To run with real LLM:")
        print("-" * 70)
        print("    set DEEPSEEK_API_KEY=sk-...")
        print("    python examples\\deepseek_skill_generation.py")
        print("\n    Expected output:")
        print("    >>> TASK: Implement a priority task queue...")
        print("    [Gap] ['queue', 'scheduling']")
        print("    [LLM] Generating skill via DeepSeek...")
        print("    [Val] Score=0.85 (AST + import + pytest)")
        print("    [Vote] Consensus=0.92 → ACCEPTED")

    else:
        # Real LLM mode
        print("\n[1/3] Attaching DeepSeek adapter...")
        adapter = attach_deepseek_to_engine(
            engine,
            api_key=api_key,
            model="deepseek-chat",
            max_cost_usd=1.0,
            max_requests_per_min=10,
        )
        print(f"    Model: {adapter.model}")
        print(f"    Budget: ${adapter.cost_tracker.max_cost_usd:.2f}")

        print("\n[2/3] Generating skills via DeepSeek API...")
        print("-" * 70)

        for i, task in enumerate(TASKS, 1):
            print(f"\n>>> TASK {i}/{len(TASKS)}: {task}")
            try:
                cand = engine.run_lifecycle(task)
                if cand:
                    print(f"    → ACCEPTED: {cand.name} ({cand.category})")
                    print(f"    → Code: {len(cand.code)} chars, Tests: {len(cand.tests)} chars")
                else:
                    print(f"    → No gap or rejected")
            except Exception as e:
                print(f"    → ERROR: {e}")

            stats = adapter.get_stats()
            print(f"    → Cost so far: ${stats['total_cost_usd']:.4f}, Remaining: ${stats['remaining_budget_usd']:.4f}")

        print("\n[3/3] Final stats:")
        print("-" * 70)
        stats = adapter.get_stats()
        for k, v in stats.items():
            print(f"    {k}: {v}")

        adapter.close()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if show_structure_only:
        print("Demo ran in STRUCTURE-ONLY mode (no API key).")
        print("Set DEEPSEEK_API_KEY to generate real skills via LLM.")
    else:
        print(f"Generated skills: {engine.stats['accepted']}")
        print(f"Total cost: ${stats['total_cost_usd']:.4f}")
    print("\nSafety features active:")
    print("  - Circuit breaker (3 failures → 60s cooldown)")
    print("  - Rate limit (10 req/min)")
    print("  - Cost limit ($1.00/session)")
    print("  - Import whitelist (stdlib only)")
    print("  - Import blacklist (no socket/subprocess/urllib)")
    print("  - AST + pytest sandbox validation")


if __name__ == "__main__":
    main()