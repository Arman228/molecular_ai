#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate real Python implementations for all 23 seed skills via DeepSeek LLM.
Budget: ~$0.12 (23 skills × ~$0.005 each). Max: $0.50.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.deepseek_adapter import DeepSeekAdapter


SEED_PATH = "data/seed_skills.json"
OUTPUT_PATH = "data/seed_skills_with_code.json"
BUDGET_USD = 0.50


def main():
    print("=" * 70)
    print("GENERATE SEED IMPLEMENTATIONS via DeepSeek LLM")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] DEEPSEEK_API_KEY not set.")
        print("    set DEEPSEEK_API_KEY=sk-...")
        return

    # Load seed skills
    print(f"\n[1/4] Loading seed skills from {SEED_PATH}...")
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    print(f"    Total seed skills: {len(skills)}")

    # Check which already have code
    todo = [s for s in skills if not s.get("code")]
    done = [s for s in skills if s.get("code")]
    print(f"    Already with code: {len(done)}")
    print(f"    To generate: {len(todo)}")

    if not todo:
        print("\n    All skills already have code. Nothing to do.")
        return

    # Init adapter
    print(f"\n[2/4] Initializing DeepSeek adapter...")
    adapter = DeepSeekAdapter(
        api_key=api_key,
        model="deepseek-chat",
        max_cost_usd=BUDGET_USD,
        max_requests_per_min=10,
    )
    print(f"    Budget: ${BUDGET_USD:.2f}")
    print(f"    Estimated cost: ${len(todo) * 0.005:.3f}")

    # Generate for each missing skill
    print(f"\n[3/4] Generating implementations...")
    print("-" * 70)

    for i, skill in enumerate(todo, 1):
        name = skill["name"]
        print(f"\n>>> {i}/{len(todo)}: {name} ({skill['category']}, complexity={skill['complexity']})")

        gap = {
            "task": f"Implement {name}: {skill['description']}",
            "missing_keywords": skill.get("keywords", [name.lower()]),
            "suggested_category": skill["category"],
        }

        try:
            result = adapter.generate_skill(gap)
            skill["code"] = result.get("code", "")
            skill["tests"] = result.get("tests", "")
            skill["generated"] = True
            skill["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

            code_len = len(skill["code"])
            test_len = len(skill["tests"])
            print(f"    ✅ Code: {code_len} chars | Tests: {test_len} chars")

            # Save incrementally
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"    💾 Saved to {OUTPUT_PATH}")

        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            skill["error"] = str(e)
            continue

        # Show running stats
        stats = adapter.get_stats()
        print(f"    💰 Cost: ${stats['total_cost_usd']:.4f} | Remaining: ${stats['remaining_budget_usd']:.2f}")

        # Budget check
        if stats["remaining_budget_usd"] < 0.01:
            print(f"\n[!] Budget exhausted! Stopping.")
            break

        # Small delay to respect rate limits
        time.sleep(1)

    adapter.close()

    # Final summary
    print(f"\n" + "=" * 70)
    print("[4/4] SUMMARY")
    print("=" * 70)

    with_code = sum(1 for s in skills if s.get("code"))
    with_error = sum(1 for s in skills if s.get("error"))

    print(f"    Total skills:     {len(skills)}")
    print(f"    With code:        {with_code}")
    print(f"    Errors:           {with_error}")
    print(f"    Output:           {OUTPUT_PATH}")

    stats = adapter.get_stats()
    print(f"    Total cost:       ${stats['total_cost_usd']:.4f}")
    print(f"    Remaining budget: ${stats['remaining_budget_usd']:.2f}")

    print(f"\n    Next steps:")
    print(f"    1. Review {OUTPUT_PATH}")
    print(f"    2. Replace {SEED_PATH} with it if satisfied")
    print(f"    3. Run: python examples\\seed_skills_demo.py")


if __name__ == "__main__":
    main()