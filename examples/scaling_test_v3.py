#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест масштабирования v3 — настраиваемые параметры.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def test_scale(n_agents, steps=500, coupling_boost=1.0, goal_interval=200):
    print(f"\n{'='*50}")
    print(f"n={n_agents} | boost={coupling_boost}x | goal_interval={goal_interval}")
    print(f"{'='*50}")

    start = time.time()
    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.02,
        sleep_every=300,
        k_sparse=min(6, n_agents - 1),
    )
    
    # Усиливаем coupling для больших систем
    if coupling_boost > 1.0:
        for layer in sys.orbital.layers:
            layer.coupling *= coupling_boost
    
    # Увеличиваем интервал смены целей
    sys.goal_generator.min_steps_per_goal = goal_interval

    sys.run(steps)
    elapsed = time.time() - start

    m = sys.get_metrics()
    print(f"Sync r:        {m['sync_r']:.3f}")
    print(f"Mean mood:     {m['mean_mood']:+.2f}")
    print(f"Goals achieved:{m['goals_achieved']}")
    print(f"Time:          {elapsed:.2f} sec")

    return {"n": n_agents, "r": m["sync_r"], "time": elapsed, "goals": m["goals_achieved"]}


def main():
    print("=== Molecular AI Scaling v3 (Tuned) ===")

    # Тест 1: Малая система (стандартно)
    r1 = test_scale(3, steps=500, coupling_boost=1.0, goal_interval=50)

    # Тест 2: Средняя система (усиленный coupling, реже цели)
    r2 = test_scale(10, steps=500, coupling_boost=1.5, goal_interval=150)

    # Тест 3: Большая система (сильный coupling, редкие цели)
    r3 = test_scale(50, steps=500, coupling_boost=2.5, goal_interval=300)

    # Тест 4: Огромная система
    r4 = test_scale(100, steps=500, coupling_boost=3.0, goal_interval=400)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"{'Agents':>8} | {'Sync r':>8} | {'Time':>8} | {'Goals':>6}")
    print("-" * 60)
    for r in [r1, r2, r3, r4]:
        print(f"{r['n']:>8} | {r['r']:>8.3f} | {r['time']:>6.2f}s | {r['goals']:>6}")


if __name__ == "__main__":
    main()