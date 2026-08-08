#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест масштабирования v4 — оптимальные параметры.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def test_scale(n_agents, steps=1000):
    print(f"\n{'='*50}")
    print(f"n={n_agents} agents, {steps} steps (optimized)")
    print(f"{'='*50}")

    # Оптимальные параметры под размер
    k_sparse = min(n_agents // 5, 15)  # больше связей
    exc_ratio = 0.95 if n_agents > 20 else 0.85  # меньше ингибиторов
    noise = 0.01 if n_agents > 20 else 0.02  # меньше шума

    start = time.time()
    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=noise,
        sleep_every=500,
        k_sparse=k_sparse,
        exc_ratio=exc_ratio,
    )
    
    # Усиливаем coupling для больших систем
    boost = 1.0 + (n_agents / 20)  # 1.0, 1.5, 3.5, 6.0
    for layer in sys.orbital.layers:
        layer.coupling *= boost
    
    # Реже меняем цели
    sys.goal_generator.min_steps_per_goal = max(200, n_agents * 5)

    sys.run(steps)
    elapsed = time.time() - start

    m = sys.get_metrics()
    print(f"Sync r:        {m['sync_r']:.3f}")
    print(f"Mean mood:     {m['mean_mood']:+.2f}")
    print(f"Goals achieved:{m['goals_achieved']}")
    print(f"Time:          {elapsed:.2f} sec")
    print(f"Speed:         {steps/elapsed:.0f} steps/sec")

    return {"n": n_agents, "r": m["sync_r"], "time": elapsed, "goals": m["goals_achieved"]}


def main():
    print("=== Molecular AI Scaling v4 (Optimized) ===")

    results = []
    for n in [3, 10, 50, 100]:
        results.append(test_scale(n, steps=1000))

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"{'Agents':>8} | {'Sync r':>8} | {'Time':>8} | {'Speed':>10} | {'Goals':>6}")
    print("-" * 60)
    for r in results:
        speed = 1000 / r['time']
        print(f"{r['n']:>8} | {r['r']:>8.3f} | {r['time']:>6.2f}s | {speed:>8.0f} st/s | {r['goals']:>6}")


if __name__ == "__main__":
    main()