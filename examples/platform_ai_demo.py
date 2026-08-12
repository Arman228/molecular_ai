#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platform AI Demo v1 — full autonomous pipeline:
seed → gap detect → DeepSeek/mock generate → validate → vote → save.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_skills import AutoSkillEngine, SkillGapDetector
from core.persistence import SkillRegistryPersistence, attach_persistence


TASKS = [
    "Find structural patterns in this codebase using AST analysis",
    "Design state transitions for distributed system with orbital sync",
    "Build a real-time WebSocket notification system with Redis pub/sub",
    "Implement JWT authentication with rate limiting for API endpoints",
    "Trace root cause of error cascade through call graph",
]


def main():
    print("=" * 70)
    print("PLATFORM AI DEMO v1")
    print("Full pipeline: seed → gap detect → generate → validate → vote → save")
    print("=" * 70)

    # 1. Load seed skills (with real DeepSeek-generated code)
    print("\n[1/5] Loading seed skills...")
    pers = SkillRegistryPersistence(filepath="data/skills_registry.json", autosave=False)
    seed = pers.load_seed("data/seed_skills.json")
    print(f"    Loaded {len(seed)} seed skills from data/seed_skills.json")

    # 2. Initialize engine
    print("\n[2/5] Initializing AutoSkillEngine...")
    engine = AutoSkillEngine(use_llm=False)
    engine.registry.skills = pers.merge_seed(seed, engine.registry.skills, overwrite=False)
    engine.detector = SkillGapDetector(engine.registry.skills)
    print(f"    Registry: {len(engine.registry.skills)} skills")

    # 3. Attach DeepSeek if API key available
    print("\n[3/5] Checking DeepSeek API...")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    use_deepseek = False

    if api_key:
        print(f"    API key found: {api_key[:8]}...{api_key[-4:]}")
        try:
            from adapters.deepseek_adapter import attach_deepseek_to_engine
            attach_deepseek_to_engine(
                engine,
                api_key=api_key,
                max_cost_usd=0.50,
                max_requests_per_min=5,
            )
            use_deepseek = True
            print("    ✅ DeepSeek LLM mode ACTIVE")
            print("    Budget: $0.50 | Rate: 5 req/min")
        except Exception as e:
            print(f"    ⚠️  Failed to attach DeepSeek: {e}")
            print("    Fallback to mock generation")
    else:
        print("    ⚠️  DEEPSEEK_API_KEY not set")
        print("    Fallback to mock generation (4 templates)")
        print("    To use real LLM: set DEEPSEEK_API_KEY=sk-...")

    # 4. Run tasks through pipeline
    print("\n" + "=" * 70)
    print("[4/5] RUNNING TASKS THROUGH PLATFORM")
    print("=" * 70)

    for i, task in enumerate(TASKS, 1):
        print(f"\n>>> TASK {i}/{len(TASKS)}")
        print(f"    {task}")
        print("    " + "-" * 60)

        start = time.time()
        try:
            cand = engine.run_lifecycle(task)
        except Exception as e:
            print(f"    ❌ Pipeline error: {e}")
            continue
        elapsed = time.time() - start

        if cand:
            print(f"\n    ✅ NEW SKILL: '{cand.name}'")
            print(f"       Category: {cand.category}")
            print(f"       Complexity: {cand.complexity}")
            print(f"       Code: {len(cand.code)} chars")
            print(f"       Tests: {len(cand.tests)} chars")
            print(f"       Validation: {cand.validation_score:.2f}")
            print(f"       Source: {'DeepSeek LLM' if use_deepseek else 'Mock template'}")
        else:
            print(f"\n    ✅ COVERED BY SEED — no generation needed")

        print(f"    Time: {elapsed:.2f}s")
        print("    " + "-" * 60)

        # Small delay between tasks
        if use_deepseek and i < len(TASKS):
            time.sleep(2)

    # 5. Summary
    print("\n" + "=" * 70)
    print("[5/5] SUMMARY")
    print("=" * 70)

    print(f"\n    Tasks processed:      {len(TASKS)}")
    print(f"    Gaps detected:        {engine.stats['gaps_detected']}")
    print(f"    New skills generated: {engine.stats['generated']}")
    print(f"    Accepted by vote:     {engine.stats['accepted']}")
    print(f"    Total registry:       {len(engine.registry.skills)}")

    # Save registry
    saved = pers.save(engine.registry.skills, engine.registry.evolution)
    print(f"\n    💾 Registry saved: {saved}")

    # Show final registry
    print(f"\n    {'Skill':<30} {'Category':<20} {'Level':>8} {'Source':>10}")
    print("    " + "-" * 70)
    for name, info in sorted(engine.registry.skills.items(), key=lambda x: x[1].get("category", "")):
        level = info.get("level", 0.5)
        src = "SEED" if info.get("seed") else "AUTO"
        print(f"    {name:<30} {info.get('category', '?'):<20} {level:>8.2f} {src:>10}")

    # DeepSeek stats
    if use_deepseek and hasattr(engine, "deepseek"):
        stats = engine.deepseek.get_stats()
        print(f"\n    💰 DeepSeek cost: ${stats['total_cost_usd']:.4f}")
        print(f"    💰 Remaining: ${stats['remaining_budget_usd']:.2f}")

    print("\n" + "=" * 70)
    print("The platform autonomously decided:")
    print("  - Which tasks are covered by existing knowledge (seed)")
    print("  - Which require new skill generation (gap → LLM/mock)")
    print("  - Validated, voted, and persisted all results.")
    print("=" * 70)


if __name__ == "__main__":
    main()
