#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск оптимальных параметров для 6 агентов.
Тестируем комбинации и выбираем лучшую по sync_r.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def test_config(omega_spread, coupling_boost, k_sparse, noise, steps=500, seed=42):
    """Один тест с фиксированными параметрами."""
    random.seed(seed)
    
    sys = MolecularSystem(n_agents=6, dt=0.05, noise=noise, sleep_every=300, k_sparse=k_sparse, exc_ratio=0.90)
    
    # Переопределяем omega вручную
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-omega_spread/2, omega_spread/2)
    
    # Усиливаем coupling
    for layer in sys.orbital.layers:
        layer.coupling *= coupling_boost
    
    sys.run(steps)
    
    m = sys.get_metrics()
    return {
        "r": m["sync_r"],
        "goals": m["goals_achieved"],
        "mood": m["mean_mood"],
        "time": steps,  # упрощённо
    }


def main():
    print("=== Parameter Search for 6 Agents ===\n")
    
    # Сетка параметров
    spreads = [0.02, 0.05, 0.10, 0.20]
    boosts = [1.0, 2.0, 3.0, 4.0]
    k_values = [3, 5, 10]  # 10 = полносвязная
    noises = [0.01, 0.02]
    
    results = []
    total = len(spreads) * len(boosts) * len(k_values) * len(noises)
    tested = 0
    
    for spread in spreads:
        for boost in boosts:
            for k in k_values:
                for noise in noises:
                    tested += 1
                    cfg = test_config(spread, boost, k, noise)
                    results.append({
                        "spread": spread,
                        "boost": boost,
                        "k": k,
                        "noise": noise,
                        "r": cfg["r"],
                        "goals": cfg["goals"],
                        "mood": cfg["mood"],
                    })
                    print(f"[{tested}/{total}] spread={spread} boost={boost} k={k} noise={noise} | "
                          f"r={cfg['r']:.3f} goals={cfg['goals']} mood={cfg['mood']:+.2f}")
    
    # Сортируем по sync_r
    results.sort(key=lambda x: x["r"], reverse=True)
    
    print("\n" + "=" * 70)
    print("TOP 5 CONFIGURATIONS")
    print("=" * 70)
    print(f"{'Rank':>4} | {'Spread':>6} | {'Boost':>5} | {'k':>3} | {'Noise':>5} | {'r':>6} | {'Goals':>5} | {'Mood':>6}")
    print("-" * 70)
    for i, r in enumerate(results[:5], 1):
        print(f"{i:>4} | {r['spread']:>6.2f} | {r['boost']:>5.1f} | {r['k']:>3} | {r['noise']:>5.2f} | "
              f"{r['r']:>6.3f} | {r['goals']:>5} | {r['mood']:>+6.2f}")
    
    best = results[0]
    print(f"\n>>> BEST: omega_spread={best['spread']}, coupling_boost={best['boost']}, "
          f"k_sparse={best['k']}, noise={best['noise']}")
    print(f">>> Expected: r ≈ {best['r']:.3f}, goals ≈ {best['goals']}, mood ≈ {best['mood']:+.2f}")


if __name__ == "__main__":
    main()