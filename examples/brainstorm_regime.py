#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brainstorm with ConvergenceRegime.
CRITICAL mode for exploration → more diverse ideas.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime, get_regime_description


ROLES = [
    {"name": "Эколог", "style": "природа, устойчивость"},
    {"name": "Инженер", "style": "эффективность, оптимизация"},
    {"name": "Экономист", "style": "стоимость, выгода"},
    {"name": "Социолог", "style": "люди, сообщества"},
    {"name": "Футурист", "style": "инновации, AI"},
    {"name": "Критик", "style": "риски, ограничения"},
]

IDEA_POOLS = {
    "Эколог": ["Вертикальные сады", "Компостеры", "Проницаемое покрытие"],
    "Инженер": ["Подземные тоннели", "Умные светофоры", "Модульные дороги"],
    "Экономист": ["Динамическая цена", "Налоговые льготы", "Каршеринг"],
    "Социолог": ["Бесплатные автобусы", "Транспортные кварталы", "Голосование"],
    "Футурист": ["Летающие такси", "Телепортация", "Голографические остановки"],
    "Критик": ["Коррупционные риски", "План Б", "Пилотный район"],
}


def main():
    TOPIC = "Как улучшить городской транспорт в 2030 году?"

    print("=" * 60)
    print("BRAINSTORM with ConvergenceRegime")
    print("=" * 60)
    print(f"Topic: {TOPIC}")

    # 1. Create system
    sys = MolecularSystem(n_agents=6, dt=0.05, noise=0.02, k_sparse=5, exc_ratio=0.90)

    # 2. Set CRITICAL regime for brainstorming (exploration)
    print("\n[1/3] Setting CRITICAL regime (exploration mode)...")
    set_regime(sys, ConvergenceRegime.CRITICAL)
    print(f"    Regime: {get_regime_description(ConvergenceRegime.CRITICAL)}")

    # 3. Sync
    print("\n[2/3] Synchronizing (CRITICAL mode)...")
    for _ in range(300):
        sys.step()
        if sys.order_parameter() > 0.75:
            break
    
    r = sys.order_parameter()
    print(f"    Sync r = {r:.3f} (moderate — good for exploration)")

    # 4. Generate ideas
    print("\n[3/3] Generating ideas...")
    ideas = []
    for i, agent in enumerate(sys.agents):
        role = ROLES[i]["name"]
        pool = IDEA_POOLS[role]
        
        # In CRITICAL mode: more randomness = diverse ideas
        idx = random.randint(0, len(pool) - 1) if r < 0.85 else random.randint(0, min(1, len(pool) - 1))
        idea = f"[{role}] {pool[idx]}"
        ideas.append({"role": role, "idea": idea, "mood": agent.mood})

    # 5. Results
    print("\n" + "=" * 60)
    print("IDEAS (CRITICAL regime — diverse):")
    print("=" * 60)
    for idea in ideas:
        marker = " ★" if idea["mood"] > 0.5 else ""
        print(f"  {idea['idea']}{marker}")

    # 6. Switch to LINEAR for consensus
    print("\n[Bonus] Switching to LINEAR regime for consensus...")
    set_regime(sys, ConvergenceRegime.LINEAR)
    for _ in range(100):
        sys.step()
    
    r_final = sys.order_parameter()
    print(f"    Final sync r = {r_final:.3f} (stable — consensus reached)")

    best = max(ideas, key=lambda x: x["mood"])
    print(f"\nWinner: {best['role']} — {best['idea']}")


if __name__ == "__main__":
    main()