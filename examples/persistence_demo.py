#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistence Demo v1.
Platform loads seed skills, evolves them, and persists across sessions.
"""

import os
import sys
import random
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_skills import AutoSkillEngine, attach_to_system
from core.persistence import SkillRegistryPersistence, attach_persistence


# Seed skills — simulating a pre-loaded knowledge base
SEED_SKILLS = {
    "Python": {
        "name": "Python",
        "category": "Programming",
        "description": "Python programming language",
        "complexity": 5,
        "code": "",
        "tests": "",
        "keywords": ["python", "programming"],
        "level": 0.8,
    },
    "Docker": {
        "name": "Docker",
        "category": "DevOps",
        "description": "Containerization platform",
        "complexity": 6,
        "code": "",
        "tests": "",
        "keywords": ["docker", "container"],
        "level": 0.7,
    },
    "JWT": {
        "name": "JWT",
        "category": "Security",
        "description": "JSON Web Token authentication",
        "complexity": 4,
        "code": "",
        "tests": "",
        "keywords": ["jwt", "auth", "token"],
        "level": 0.6,
    },
}


# Tasks: some covered by seed, some requiring new skills
TASKS = [
    "Build Python API with JWT authentication",       # covered by seed
    "Add GraphQL schema with Redis caching",          # gap: GraphQL + Redis
    "Implement WebSocket broadcast for notifications", # gap: WebSocket
]


def main():
    print("=" * 70)
    print("PERSISTENCE DEMO v1")
    print("Platform loads seed skills, detects gaps, evolves, and persists")
    print("=" * 70)

    # Use temp file for demo so we don't clutter real data/
    tmp_dir = tempfile.mkdtemp()
    registry_path = os.path.join(tmp_dir, "skills_registry.json")
    seed_path = os.path.join(tmp_dir, "seed.json")

    # 1. Save seed to JSON
    print(f"\n[1/5] Creating seed file: {seed_path}")
    import json
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump({"skills": list(SEED_SKILLS.values())}, f, indent=2)
    print(f"    Seed: {len(SEED_SKILLS)} skills")

    # 2. Initialize engine with persistence
    print(f"\n[2/5] Initializing engine with persistence...")
    engine = AutoSkillEngine(use_llm=False)

    # Attach persistence + load seed
    pers = SkillRegistryPersistence(filepath=registry_path, autosave=False)
    seed = pers.load_seed(seed_path)
    engine.registry.skills = pers.merge_seed(seed, engine.registry.skills)
    print(f"    Loaded {len(engine.registry.skills)} skills from seed")

    # Update detector with seeded registry
    from core.auto_skills import SkillGapDetector
    engine.detector = SkillGapDetector(engine.registry.skills)

    # 3. Run tasks — some covered, some generate new skills
    print(f"\n[3/5] Running tasks (some covered by seed, some new)...")
    print("-" * 70)
    accepted = []
    for i, task in enumerate(TASKS, 1):
        print(f"\n>>> TASK {i}/{len(TASKS)}: {task}")
        cand = engine.run_lifecycle(task)
        if cand:
            accepted.append(cand.name)
        print("-" * 70)

    # 4. Simulate feedback on all skills (seed + new)
    print(f"\n[4/5] Simulating Hebbian evolution...")
    for name in list(engine.registry.skills.keys()):
        for _ in range(3):
            success = random.random() > 0.2
            engine.evolve_from_feedback(name, success)
        rec = engine.registry.evolution.get(name)
        level = rec.level if rec else engine.registry.skills[name].get("level", 0.1)
        print(f"    {name:20s}: level={level:.2f}")

    # 5. Save to disk
    print(f"\n[5/5] Saving registry to disk...")
    saved_path = pers.save(engine.registry.skills, engine.registry.evolution)
    print(f"    Saved to: {saved_path}")
    stats = pers.get_stats()
    print(f"    Size: {stats['size_bytes']} bytes")

    # 6. Simulate NEW session — reload and verify
    print(f"\n" + "=" * 70)
    print("SIMULATING NEW SESSION — reload from disk")
    print("=" * 70)

    pers2 = SkillRegistryPersistence(filepath=registry_path, autosave=False)
    loaded = pers2.load()
    loaded_registry = loaded.get("registry", {})
    loaded_evolution = loaded.get("evolution", {})

    print(f"\n    Reloaded registry: {len(loaded_registry)} skills")
    print(f"    Reloaded evolution: {len(loaded_evolution)} records")
    print(f"    Saved at: {loaded.get('saved_at', 'unknown')}")

    print(f"\n{'Skill':<20} {'Category':<18} {'Level':>8} {'Status':>10}")
    print("-" * 70)
    for name, info in loaded_registry.items():
        evo = loaded_evolution.get(name, {})
        level = evo.get("level", info.get("level", 0.1))
        is_seed = info.get("seed", False)
        status = "SEED" if is_seed else "AUTO"
        print(f"{name:<20} {info.get('category', '?'):<18} {level:>8.2f} {status:>10}")

    # 7. Cleanup
    print(f"\n[Cleanup] Removing temp files...")
    import shutil
    shutil.rmtree(tmp_dir)
    print(f"    Done.")

    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Seed skills: {len(SEED_SKILLS)}")
    print(f"Auto-generated skills: {len(accepted)}")
    print(f"Total after evolution: {len(engine.registry.skills)}")
    print(f"Persisted to: {registry_path}")
    print(f"\nPlatform now remembers skills between sessions.")
    print(f"Seed skills provide baseline knowledge.")
    print(f"Auto-generated skills fill gaps dynamically.")


if __name__ == "__main__":
    random.seed(42)
    main()