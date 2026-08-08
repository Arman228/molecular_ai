#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест масштабирования Molecular AI.
Проверяем n=3, 10, 50, 100 агентов.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def test_scale(n_agents, steps=500):
    print(f"\n{'='*50}")
    print(f"Testing n={n_agents} agents, {steps} steps...")
    print(f"{'='*50}")

    start = time.time()
    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.02,
        sleep_every=300,
        k_sparse=min(4, n_agents - 1) if n_agents > 4 else 2,
    )
    sys.run(steps)
    elapsed = time.time() - start

    m = sys.get_metrics()
    print(f"Sync r:        {m['sync_r']:.3f}")
    print(f"Mean mood:     {m['mean_mood']:+.2f}")
    print(f"Goals achieved:{m['goals_achieved']}")
    print(f"Total reward:  {m['total_reward']:.1f}")
    print(f"Time:          {elapsed:.2f} sec")
    print(f"Speed:         {steps/elapsed:.0f} steps/sec")

    return {
        "n": n_agents,
        "r": m["sync_r"],
        "time": elapsed,
        "goals": m["goals_achieved"],
    }


def main():
    print("=== Molecular AI Scaling Test ===")
    print(f"Python: {sys.version.split()[0]}")

    results = []

    # Тест 1: 3 агента (baseline)
    results.append(test_scale(3, steps=500))

    # Тест 2: 10 агентов
    results.append(test_scale(10, steps=500))

    # Тест 3: 50 агентов (если потянет)
    print("\n[Нажмите Enter для теста 50 агентов, или Ctrl+C чтобы пропустить]")
    try:
        input()
        results.append(test_scale(50, steps=500))
    except KeyboardInterrupt:
        print("Пропущено.")

    # Тест 4: 100 агентов (опционально)
    print("\n[Нажмите Enter для теста 100 агентов, или Ctrl+C чтобы пропустить]")
    try:
        input()
        results.append(test_scale(100, steps=500))
    except KeyboardInterrupt:
        print("Пропущено.")

    # Итоговая таблица
    print("\n" + "=" * 60)
    print("RESULTS TABLE")
    print("=" * 60)
    print(f"{'Agents':>8} | {'Sync r':>8} | {'Time(sec)':>10} | {'Goals':>6}")
    print("-" * 60)
    for r in results:
        print(f"{r['n']:>8} | {r['r']:>8.3f} | {r['time']:>10.2f} | {r['goals']:>6}")


if __name__ == "__main__":
    main()