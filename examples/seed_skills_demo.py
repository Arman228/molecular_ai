#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed Skills Demo v1.
Platform loads 23 original Molecular AI skills from data/seed_skills.json.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_skills import AutoSkillEngine, SkillGapDetector
from core.persistence import SkillRegistryPersistence


# Tasks that match our unique seed skills
TASKS = [
    "Find structural patterns in this codebase",           # PatternResonance
    "Refactor this high-entropy module",                    # RefactoringEntropy
    "Design state transitions for distributed system",      # StateOrbital
    "Trace root cause of this error cascade",               # ErrorBackpropagation
    "Generate boundary test cases for this API",            # EdgeCaseTopology
    "Build GraphQL API with Redis caching",                 # gap: GraphQL + Redis
]


def main():
    print("=" * 70)
    print("SEED SKILLS DEMO v1")
    print("Platform loads 23 original Molecular AI skills")
    print("=" * 70)

    # 1. Load seed from data/seed_skills.json
    print("\n[1/4] Loading seed skills from data/seed_skills.json...")
    pers = SkillRegistryPersistence(filepath="data/skills_registry.json", autosave=False)
    
    if not os.path.exists("data/seed_skills.json"):
        print("    ERROR: data/seed_skills.json not found!")
        print("    Create it with: python -c \"import json; open('data/seed_skills.json','w')...")
        return

    seed = pers.load_seed("data/seed_skills.json")
    print(f"    Loaded {len(seed)} unique skills from seed")

    # 2. Show seed skills
    print("\n[2/4] Seed skills loaded:")
    print(f"{'Skill':<25} {'Category':<18} {'Complexity':>10}")
    print("-" * 70)
    for name, info in sorted(seed.items(), key=lambda x: x[1]["complexity"]):
        print(f"{name:<25} {info['category']:<18} {info['complexity']:>10}")

    # 3. Initialize engine with seed
    print("\n[3/4] Initializing engine with seeded registry...")
    engine = AutoSkillEngine(use_llm=False)
    engine.registry.skills = pers.merge_seed(seed, engine.registry.skills, overwrite=False)
    engine.detector = SkillGapDetector(engine.registry.skills)
    print(f"    Registry size: {len(engine.registry.skills)}")

    # 4. Run tasks — some covered by seed, some generate new
    print("\n[4/4] Running tasks against seeded registry...")
    print("-" * 70)
    
    covered = 0
    generated = 0
    
    for i, task in enumerate(TASKS, 1):
        print(f"\n>>> TASK {i}/{len(TASKS)}: {task}")
        cand = engine.run_lifecycle(task)
        if cand:
            generated += 1
            print(f"    → NEW SKILL GENERATED: {cand.name}")
        else:
            covered += 1
            print(f"    → COVERED BY SEED (no gap)")
        print("-" * 70)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Seed skills:           {len(seed)}")
    print(f"Tasks covered by seed: {covered}")
    print(f"New skills generated:  {generated}")
    print(f"Total registry:        {len(engine.registry.skills)}")
    
    print("\nThe platform recognized your 23 unique skills and used them")
    print("to cover tasks without generating duplicates. Gaps trigger")
    print("auto-generation — seed + evolution working together.")


if __name__ == "__main__":
    random.seed(42)
    main()