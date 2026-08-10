#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Skill Evolution v1.
Molecular AI creates its own skills: detect gap → generate → validate → vote → evolve.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.auto_skills import AutoSkillEngine, attach_to_system


# Tasks that require skills NOT in the initial empty registry
TASKS = [
    "Build GraphQL API with type-safe resolvers for user management",
    "Add real-time WebSocket broadcast for live notifications",
    "Implement Redis cache layer with TTL for API responses",
    "Add token-bucket rate limiter per user for REST endpoints",
    "Create GraphQL schema with caching and rate limiting",  # reuse + combo
]


def simulate_task_execution(skill_name: str) -> bool:
    """
    Simulate whether a task succeeds using the generated skill.
    Higher complexity = slightly lower success rate (mimics real world).
    """
    base = 0.85
    if skill_name in ("GraphQL", "WebSocket"):
        base = 0.90
    elif skill_name in ("RedisCache", "RateLimiter"):
        base = 0.80
    return random.random() < base


def main():
    print("=" * 70)
    print("AUTO SKILL EVOLUTION v1")
    print("Platform creates its own skills: gap → gen → validate → vote → evolve")
    print("=" * 70)

    # 1. Orbital sync (5 agents: 3 voters + 2 observers)
    print("\n[1/5] Orbital synchronization...")
    mol = MolecularSystem(
        n_agents=5,
        dt=0.05,
        noise=0.01,
        k_sparse=4,
        exc_ratio=0.90,
    )
    for layer in mol.orbital.layers:
        layer.coupling *= 2.5

    for _ in range(400):
        mol.step()
    sync_r = mol.order_parameter()
    print(f"    Sync r = {sync_r:.3f}")

    # 2. Attach AutoSkillEngine
    print("\n[2/5] Attaching AutoSkillEngine...")
    engine = attach_to_system(mol, use_llm=False)
    print(f"    Registry size: {len(engine.registry.skills)}")
    print(f"    Agents: {len(mol.agents)}")

    # 3. Run lifecycle for each task
    print("\n[3/5] Running skill evolution lifecycle...")
    print("-" * 70)

    accepted_skills = []
    for i, task in enumerate(TASKS, 1):
        print(f"\n>>> TASK {i}/{len(TASKS)}: {task}")
        candidate = engine.run_lifecycle(task)
        if candidate:
            accepted_skills.append(candidate.name)
        print("-" * 70)

    # 4. Simulate execution feedback (Hebbian learning)
    print("\n[4/5] Simulating task execution feedback (Hebbian LTP/LTD)...")
    for name in accepted_skills:
        for trial in range(5):
            success = simulate_task_execution(name)
            engine.evolve_from_feedback(name, success)
        record = engine.registry.evolution[name]
        print(f"    {name:20s}: level={record.level:.2f}  uses={record.usage_count}")

    # 5. Sleep consolidation (prune weak skills)
    print("\n[5/5] Sleep consolidation (pruning weak skills)...")
    # Artificially age one skill by not using it
    if "GraphQL" in engine.registry.evolution:
        engine.registry.evolution["GraphQL"].last_used -= 400  # force old
        engine.registry.evolution["GraphQL"].level = 0.03       # force weak

    pruned = engine.sleep()
    if pruned:
        print(f"    Pruned: {', '.join(pruned)}")
    else:
        print("    No skills pruned (all healthy)")

    # 6. Final registry state
    print("\n" + "=" * 70)
    print("FINAL REGISTRY")
    print("=" * 70)
    print(f"{'Skill':<20} {'Category':<18} {'Level':>8} {'Uses':>6} {'Status':>10}")
    print("-" * 70)

    for name, info in engine.registry.skills.items():
        rec = engine.registry.evolution.get(name)
        level = rec.level if rec else info.get("level", 0.1)
        uses = rec.usage_count if rec else 0
        status = "PRUNED" if rec and rec.pruned else "ACTIVE"
        print(f"{name:<20} {info['category']:<18} {level:>8.2f} {uses:>6} {status:>10}")

    # 7. Skill retrieval demo
    print("\n" + "=" * 70)
    print("SKILL RETRIEVAL")
    print("=" * 70)
    queries = [
        "I need a GraphQL endpoint with caching",
        "Add WebSocket for real-time updates",
        "Rate limit my API",
    ]
    for q in queries:
        found = engine.registry.get_skill_for_task(q)
        print(f"  Query: {q[:50]}...")
        print(f"  → Best skill: {found or 'NONE (create new)'}")
        print()

    # 8. Stats
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    for key, val in engine.stats.items():
        print(f"  {key:<20s}: {val}")
    print(f"  {'registry_size':<20s}: {len(engine.registry.skills)}")
    print(f"  {'sync_r':<20s}: {sync_r:.3f}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("The platform detected missing capabilities, generated skills,")
    print("validated them via AST + import + pytest, voted via orbital consensus,")
    print("and evolved levels through Hebbian feedback + sleep pruning.")
    print(f"\nAccepted skills: {accepted_skills}")
    print(f"Final registry: {len(engine.registry.skills)} active skills")


if __name__ == "__main__":
    random.seed(42)
    main()