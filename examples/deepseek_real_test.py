#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Real Test — one skill generation with real LLM.
Budget: $0.50 max, 1 request.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.deepseek_adapter import DeepSeekAdapter


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if not api_key:
        print("=" * 60)
        print("ERROR: DEEPSEEK_API_KEY not set!")
        print("=" * 60)
        print("\nSet your key:")
        print("    set DEEPSEEK_API_KEY=sk-your-key-here")
        print("\nGet key: https://platform.deepseek.com")
        return

    print("=" * 60)
    print("DEEPEEK REAL API TEST")
    print("=" * 60)
    print(f"Key: {api_key[:8]}...{api_key[-4:]}")
    print("Budget: $0.50 | Max requests: 1 | Timeout: 30s")
    print("-" * 60)

    adapter = DeepSeekAdapter(
        api_key=api_key,
        model="deepseek-chat",
        max_cost_usd=0.50,
        max_requests_per_min=1,
    )

    gap = {
        "task": "Implement a priority task queue with deadline scheduling",
        "missing_keywords": ["queue", "scheduling", "priority"],
        "suggested_category": "Backend",
    }

    print(f"\n>>> Generating skill: {gap['task']}")
    print("    Calling DeepSeek API... (this may take 10-30 seconds)")

    try:
        skill = adapter.generate_skill(gap)
        print(f"\n✅ SUCCESS!")
        print(f"    Name: {skill['name']}")
        print(f"    Category: {skill['category']}")
        print(f"    Complexity: {skill['complexity']}")
        print(f"    Keywords: {', '.join(skill['keywords'])}")
        print(f"\n--- CODE ({len(skill['code'])} chars) ---")
        print(skill['code'][:500] + ("..." if len(skill['code']) > 500 else ""))
        print(f"\n--- TESTS ({len(skill['tests'])} chars) ---")
        print(skill['tests'][:300] + ("..." if len(skill['tests']) > 300 else ""))

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    stats = adapter.get_stats()
    print(f"\n--- STATS ---")
    print(f"    Cost: ${stats['total_cost_usd']:.6f}")
    print(f"    Remaining: ${stats['remaining_budget_usd']:.2f}")
    print(f"    Model: {stats['model']}")

    adapter.close()
    print("\n" + "=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()