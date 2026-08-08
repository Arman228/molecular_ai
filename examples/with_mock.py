#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример: Molecular AI + Mock LLM (офлайн).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from adapters.factory import create_adapter


def main():
    print("=== Molecular AI + Mock LLM Demo ===")

    # Симуляция
    sys = MolecularSystem(n_agents=6, dt=0.05, noise=0.02)
    sys.run(300)
    print(f"Sync after 300 steps: r = {sys.order_parameter():.3f}")

    # Mock-адаптер (без интернета, без ключей)
    adapter = create_adapter("mock")

    # Отправляем задачу первому агенту
    agent = sys.agents[0]
    orbital = sys.orbital.layers[0].orbital
    task = "Analyze the current state and suggest improvements."

    prompt = adapter.build_prompt(agent, orbital, task)
    print("\n" + "=" * 50)
    print("PROMPT SENT TO LLM:")
    print("=" * 50)
    print(prompt)

    response = adapter.call_llm(prompt)
    print("\n" + "=" * 50)
    print("MOCK LLM RESPONSE:")
    print("=" * 50)
    print(response)
    print("=" * 50)


if __name__ == "__main__":
    main()