#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест масштабирования с автонастройкой.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.tuning import AutoTuner


def test_scale(n_agents, steps=1000):
    print(f"\n{'='*50}")
    print(f"n={n_agents} agents | AUTO-TUNED")
    print(f"{'='*50}")

    # Автонастройка
    cfg = AutoTuner.tune(n_agents)
    print(f"Config: k={cfg['k_sparse']}, exc={cfg['exc_ratio']:.0%}, "
          f"noise={cfg['noise']}, boost={cfg['coupling_boost']:.1f}x")

    start = time.time()
    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=cfg["noise"],
        sleep_every=cfg["sleep_every"],
        k_sparse=cfg["k_sparse"],
        exc_ratio=cfg["exc_ratio"],
    )

    # Применяем boost
    for layer in sys.orbital.layers:
        layer.coupling *= cfg["coupling_boost"]

    sys.goal_generator.min_steps_per_goal = cfg["goal_interval"]
    sys.goal_generator.threshold = cfg["goal_threshold"]
    sys.run(steps)
    elapsed = time.time() - start

    m = sys.get_metrics()
    print(f"Sync r:        {m['sync_r']:.3f}")
    print(f"Mean mood:     {m['mean_mood']:+.2f}")
    print(f"Goals achieved:{m['goals_achieved']}")
    print(f"Time:          {elapsed:.2f} sec")

    return {"n": n_agents, "r": m["sync_r"], "time": elapsed, "goals": m["goals_achieved"]}


def main():
    print("=== Molecular AI Scaling (Auto-Tuned) ===")

    results = []
    for n in [3, 6, 12, 20, 50, 100]:
        results.append(test_scale(n, steps=1000))

    print("\n" + "=" * 65)
    print("AUTO-TUNED RESULTS")
    print("=" * 65)
    print(f"{'Agents':>8} | {'Sync r':>8} | {'Time':>8} | {'Goals':>6} | {'Verdict':>10}")
    print("-" * 65)
    for r in results:
        verdict = "EXCELLENT" if r['r'] > 0.85 else "GOOD" if r['r'] > 0.70 else "FAIR" if r['r'] > 0.50 else "WEAK"
        print(f"{r['n']:>8} | {r['r']:>8.3f} | {r['time']:>6.2f}s | {r['goals']:>6} | {verdict:>10}")


if __name__ == "__main__":
    main()