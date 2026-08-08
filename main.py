#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа Molecular AI.
"""

from core.system import MolecularSystem


def main():
    print("=== Molecular AI v5.1 ===")
    sys = MolecularSystem(n_agents=12, dt=0.05, noise=0.02, sleep_every=300)

    print("Warming up 500 steps...")
    sys.run(500)
    print(f"After warm-up: r = {sys.order_parameter():.4f}")

    print("Running 1000 steps...")
    for i in range(10):
        sys.run(100)
        m = sys.get_metrics()
        print(
            f"Step {m['step']:04d} | "
            f"r={m['sync_r']:.3f} | "
            f"mood={m['mean_mood']:+.2f} | "
            f"goals={m['goals_achieved']} | "
            f"reward={m['total_reward']:.2f}"
        )

    print("\nFinal state exported to state.json")
    with open("state.json", "w", encoding="utf-8") as f:
        f.write(sys.export_state())


if __name__ == "__main__":
    main()
