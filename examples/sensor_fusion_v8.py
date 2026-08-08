#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Эксперимент v8: Iterative Robust Consensus.
Шаг 1: Вычисляем медиану omega через orbital.
Шаг 2: Отбрасываем агентов с |omega - median| > 3*MAD.
Шаг 3: Пересчитываем консенсус из оставшихся.
"""

import os
import sys
import random
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def median(values):
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def mad(values):
    """Median Absolute Deviation."""
    m = median(values)
    deviations = [abs(v - m) for v in values]
    return median(deviations)


def run_experiment(
    true_value=23.5,
    noise_std=1.5,
    n_agents=12,
    outlier_fraction=0.20,
    outlier_bias=10.0,
    steps=600,
):
    print("=" * 60)
    print("EXPERIMENT v8: Iterative Robust Consensus (Median + MAD)")
    print("=" * 60)
    print(f"True value:     {true_value}°C")
    print(f"Agents:         {n_agents}")
    print(f"Outliers:       {int(n_agents * outlier_fraction)} ({outlier_fraction*100:.0f}%)")
    print("-" * 60)

    measurements = []
    agent_types = []
    for i in range(n_agents):
        if random.random() < outlier_fraction:
            m = true_value + outlier_bias + random.gauss(0, noise_std * 2)
            agent_types.append("OUTLIER")
        else:
            m = true_value + random.gauss(0, noise_std)
            agent_types.append("normal")
        measurements.append(m)

    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.01,
        k_sparse=min(4, n_agents - 1),
        exc_ratio=0.85,
    )

    min_m, max_m = min(measurements), max(measurements)
    for i, agent in enumerate(sys.agents):
        norm = 0.5 + (measurements[i] - min_m) / (max_m - min_m) if max_m > min_m else 1.0
        agent.omega = norm

    for layer in sys.orbital.layers:
        layer.coupling *= 1.5

    for step in range(steps):
        sys.step()

    # Собираем omega всех агентов
    omegas = [a.omega for a in sys.agents]

    # Итеративная фильтрация
    remaining = list(range(n_agents))
    for iteration in range(3):
        vals = [omegas[i] for i in remaining]
        med = median(vals)
        m = mad(vals)
        threshold = max(m * 3, 0.05)  # минимальный threshold

        new_remaining = []
        for i in remaining:
            if abs(omegas[i] - med) <= threshold:
                new_remaining.append(i)
            else:
                pass  # отброшен

        if len(new_remaining) == len(remaining):
            break
        remaining = new_remaining

    # Консенсус из оставшихся
    consensus_omega = sum(omegas[i] for i in remaining) / len(remaining)
    final = min_m + (consensus_omega - 0.5) * (max_m - min_m)
    final_r = sys.order_parameter()

    simple_mean = sum(measurements) / len(measurements)
    normal = [m for m, t in zip(measurements, agent_types) if t == "normal"]
    normal_mean = sum(normal) / len(normal) if normal else 0
    median_val = median(measurements)

    print("\nRESULTS:")
    print(f"  True value:           {true_value:.2f}°C")
    print(f"  Simple mean (all):    {simple_mean:.2f}°C  (error: {abs(simple_mean - true_value):.2f})")
    print(f"  Normal mean only:     {normal_mean:.2f}°C  (error: {abs(normal_mean - true_value):.2f})")
    print(f"  Median:               {median_val:.2f}°C  (error: {abs(median_val - true_value):.2f})")
    print(f"  Robust consensus:     {final:.2f}°C  (error: {abs(final - true_value):.2f})")
    print(f"  Agents kept:        {len(remaining)}/{n_agents}")
    print(f"  Final sync r:         {final_r:.3f}")

    print("\nAGENT STATE:")
    for i in range(n_agents):
        marker = " <-- OUTLIER" if agent_types[i] == "OUTLIER" else ""
        kept = "KEEP" if i in remaining else "DROP"
        val = min_m + (sys.agents[i].omega - 0.5) * (max_m - min_m)
        print(f"  Agent {i:2d}: {kept:4s}  omega={val:6.2f}°C  "
              f"mood={sys.agents[i].mood:+.2f}{marker}")

    print("\n" + "=" * 60)
    if abs(final - true_value) < abs(simple_mean - true_value):
        print("✅ Robust consensus BEATS simple mean")
    else:
        print("⚠️  Simple mean was better")
    print("=" * 60)

    return final, final_r


def main():
    random.seed(42)

    print("\n" + "🔥" * 30)
    r1 = run_experiment(true_value=23.5, noise_std=1.5, n_agents=12,
                       outlier_fraction=0.20, outlier_bias=10.0, steps=600)

    print("\n" + "🔥" * 30)
    r2 = run_experiment(true_value=23.5, noise_std=2.0, n_agents=20,
                       outlier_fraction=0.40, outlier_bias=15.0, steps=800)

    print("\n" + "=" * 60)
    print("SUMMARY v8")
    print("=" * 60)
    print("Median + MAD = robust outlier detection.")
    print("Iterative trimming converges to clean consensus.")


if __name__ == "__main__":
    main()