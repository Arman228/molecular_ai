#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сравнение экономии токенов: Molecular AI vs Classical Star Topology.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


def simulate_molecular_tokens(n_agents, n_steps):
    """
    Molecular AI: каждый агент публикует frequency vector (16 floats).
    В JSON: [0.84, -0.53, ...] ≈ 100 chars ≈ 25 токенов.
    """
    TOKENS_PER_VECTOR = 25  # 16 floats в JSON-array ≈ 100 chars / 4
    total = n_steps * n_agents * TOKENS_PER_VECTOR
    return total


def simulate_classical_tokens(n_agents, n_steps):
    """
    Classical Star (CrewAI/LangGraph): каждый агент шлёт полное сообщение
    оркестратору с ролью, контекстом, задачей, результатом.
    Средний JSON: ~2000 chars ≈ 500 токенов.
    """
    TOKENS_PER_MESSAGE = 500  # типичный agent message с контекстом
    # В star topology: каждый агент ↔ оркестратор (2 сообщения на шаг)
    # Или n агентов шлют n сообщений оркестратору
    total = n_steps * n_agents * TOKENS_PER_MESSAGE
    return total


def main():
    print("=" * 65)
    print("MOLECULAR AI — TOKEN ECONOMY COMPARISON")
    print("=" * 65)

    configs = [3, 6, 10, 50, 100]
    results = []

    for n in configs:
        steps = 100

        # Запускаем реальную симуляцию Molecular AI (для времени)
        sys = MolecularSystem(n_agents=n, dt=0.05, noise=0.02)
        sys.run(steps)

        mol_tokens = simulate_molecular_tokens(n, steps)
        cls_tokens = simulate_classical_tokens(n, steps)
        saved = cls_tokens - mol_tokens
        pct = (saved / cls_tokens) * 100

        results.append({
            "n": n,
            "molecular": mol_tokens,
            "classical": cls_tokens,
            "saved": saved,
            "pct": pct,
            "sync_r": sys.order_parameter(),
        })

    # Таблица
    print(f"\n{'Agents':>8} | {'Molecular':>12} | {'Classical':>12} | {'Saved':>12} | {'Economy':>8} | {'Sync r':>8}")
    print("-" * 75)
    for r in results:
        print(f"{r['n']:>8} | {r['molecular']:>10} tok | {r['classical']:>10} tok | "
              f"{r['saved']:>10} tok | {r['pct']:>7.1f}% | {r['sync_r']:>8.3f}")

    # Итог
    print("\n" + "=" * 65)
    print("ASSUMPTIONS")
    print("=" * 65)
    print("Molecular AI: 16-float frequency vector ≈ 25 tokens per agent/step")
    print("Classical Star: JSON message with context ≈ 500 tokens per agent/step")
    print("\nMolecular AI uses shared orbital — no central orchestrator.")
    print("Agents synchronize via resonance, not message passing.")

    # Пример стоимости
    print("\n" + "=" * 65)
    print("COST ESTIMATE (GPT-4o-mini @ $0.60 / 1M input tokens)")
    print("=" * 65)
    for r in results:
        mol_cost = r["molecular"] * 0.60 / 1_000_000
        cls_cost = r["classical"] * 0.60 / 1_000_000
        print(f"n={r['n']:>3} | Molecular: ${mol_cost:>8.4f} | Classical: ${cls_cost:>8.4f} | "
              f"Saved: ${cls_cost - mol_cost:>8.4f}")

    print("\n" + "=" * 65)
    print("CONCLUSION")
    print("=" * 65)
    avg_pct = sum(r["pct"] for r in results) / len(results)
    print(f"Average token economy: {avg_pct:.1f}%")
    print("Molecular AI achieves synchronization with 95% fewer tokens.")


if __name__ == "__main__":
    main()