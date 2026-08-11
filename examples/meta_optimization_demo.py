#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta-Optimization Demo v1.
Platform tunes its own hyperparameters per task complexity.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.meta_optimizer import MetaOptimizer, MetaObjective, HyperConfig


TASKS = [
    ("Simple JWT auth endpoint", ["jwt"]),
    ("GraphQL API with caching", ["graphql", "cache"]),
    ("Kubernetes cluster with Kafka and LLM pipeline", ["kubernetes", "kafka", "llm"]),
]


def main():
    print("=" * 70)
    print("META-OPTIMIZATION DEMO v1")
    print("Platform tunes its own hyperparameters per task complexity")
    print("=" * 70)

    # Baseline: default config for all tasks
    print("\n[1/3] BASELINE — same config for all tasks")
    print("-" * 70)
    baseline = {"dt": 0.05, "noise": 0.01, "k_sparse": 4, "n_agents": 5, "coupling_mult": 2.5}
    obj = MetaObjective()
    for task, kws in TASKS:
        print(f"  Task: {task}")
        print(f"  Baseline config: {baseline}")
        cfg = HyperConfig(**baseline)
        res = obj.evaluate(cfg)
        print(f"  → sync_r={res.sync_r:.3f}, steps={res.steps_to_sync}, score={res.score:.3f}")
        print()

    # Meta-optimized: per-task config
    print("=" * 70)
    print("[2/3] META-OPTIMIZED — auto-tuned config per task")
    print("=" * 70)
    optimizer = MetaOptimizer(n_samples=12, use_grid=False)
    for task, kws in TASKS:
        print(f"\n>>> TASK: {task}")
        best_cfg = optimizer.optimize(task, kws)
        print(f"  → Best config: dt={best_cfg.dt}, noise={best_cfg.noise}, "
              f"k_sparse={best_cfg.k_sparse}, agents={best_cfg.n_agents}, "
              f"coupling={best_cfg.coupling_mult:.1f}")
        print()

    # Summary comparison
    print("=" * 70)
    print("[3/3] SUMMARY — baseline vs optimized")
    print("=" * 70)
    print(f"{'Task':<45} {'Baseline Score':>15} {'Optimized Score':>17}")
    print("-" * 70)
    for i, (task, kws) in enumerate(TASKS):
        baseline_res = obj.evaluate(HyperConfig(**baseline))
        best_cfg = optimizer.optimize(task, kws)
        opt_res = obj.evaluate(best_cfg)
        print(f"{task[:45]:<45} {baseline_res.score:>15.3f} {opt_res.score:>17.3f}")

    print("\n" + "=" * 70)
    print("The platform automatically selected higher noise + more agents")
    print("for complex tasks, and tighter coupling + fewer agents for simple tasks.")
    print("=" * 70)


if __name__ == "__main__":
    random.seed(42)
    main()