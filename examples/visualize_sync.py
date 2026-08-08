#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Визуализация синхронизации Molecular AI.
Графики: фазы, order parameter, mood, energy.
"""

import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from core.system import MolecularSystem
from core.utils import order_parameter


def run_and_collect(n_agents=6, steps=500):
    """
    Запускает симуляцию и собирает историю для графиков.
    """
    print(f"=== Visualization: {n_agents} agents, {steps} steps ===")

    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.02,
        sleep_every=300,
        k_sparse=min(6, n_agents - 1),
        exc_ratio=0.88,
    )

    # Усиливаем coupling для лучшей синхронизации
    for layer in sys.orbital.layers:
        layer.coupling *= 2.0

    # Хранилище истории
    history = {
        "steps": [],
        "phases": [[] for _ in range(n_agents)],
        "r": [],
        "mood": [],
        "energy": [],
        "goal": [],
    }

    for step in range(steps):
        sys.step()

        history["steps"].append(step)
        history["r"].append(sys.order_parameter())
        history["mood"].append(sum(a.mood for a in sys.agents) / n_agents)
        history["energy"].append(sum(a.energy for a in sys.agents) / n_agents)
        history["goal"].append(sys.goal_phase)

        for i, agent in enumerate(sys.agents):
            # Нормализуем фазу в [0, 2*pi] для красоты
            ph = agent.phase % (2 * math.pi)
            if ph < 0:
                ph += 2 * math.pi
            history["phases"][i].append(ph)

    print(f"Final sync: r = {history['r'][-1]:.3f}")
    return history


def plot_results(history, n_agents):
    """
    Строит 4 графика в одном окне.
    """
    steps = history["steps"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("Molecular AI v6.0 — Synchronization Visualization", fontsize=14)

    # 1. Фазы агентов во времени
    ax = axes[0, 0]
    colors = plt.cm.tab10(range(n_agents))
    for i in range(n_agents):
        ax.plot(steps, history["phases"][i], color=colors[i], alpha=0.8, linewidth=1.2, label=f"Agent {i}")
    ax.set_title("Agent Phases over Time")
    ax.set_xlabel("Step")
    ax.set_ylabel("Phase (rad)")
    ax.set_ylim(0, 2 * math.pi)
    ax.legend(loc="upper right", fontsize=7)
    ax.grid(True, alpha=0.3)

    # 2. Order Parameter r(t)
    ax = axes[0, 1]
    ax.plot(steps, history["r"], color="crimson", linewidth=2)
    ax.axhline(0.9, color="green", linestyle="--", alpha=0.5, label="r = 0.9 (strong sync)")
    ax.axhline(0.5, color="orange", linestyle="--", alpha=0.5, label="r = 0.5 (weak)")
    ax.set_title("Order Parameter r(t)")
    ax.set_xlabel("Step")
    ax.set_ylabel("Sync r")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Средний Mood
    ax = axes[1, 0]
    ax.plot(steps, history["mood"], color="blue", linewidth=2)
    ax.axhline(0, color="black", linestyle="-", alpha=0.2)
    ax.fill_between(steps, history["mood"], 0, alpha=0.2, color="blue")
    ax.set_title("Mean Mood")
    ax.set_xlabel("Step")
    ax.set_ylabel("Mood [-1, 1]")
    ax.set_ylim(-1.1, 1.1)
    ax.grid(True, alpha=0.3)

    # 4. Средняя Energy + Goal Phase
    ax = axes[1, 1]
    ax.plot(steps, history["energy"], color="purple", linewidth=2, label="Mean Energy")
    ax2 = ax.twinx()
    ax2.plot(steps, history["goal"], color="gray", linestyle=":", alpha=0.6, label="Goal Phase")
    ax.set_title("Energy & Goal Phase")
    ax.set_xlabel("Step")
    ax.set_ylabel("Energy", color="purple")
    ax2.set_ylabel("Goal (rad)", color="gray")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("sync_visualization.png", dpi=150, bbox_inches="tight")
    print("\nSaved: sync_visualization.png")
    plt.show()


def main():
    history = run_and_collect(n_agents=6, steps=500)
    plot_results(history, n_agents=6)


if __name__ == "__main__":
    main()