#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Molecular AI + DeepSeek Chat — живой LLM.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from adapters.factory import create_adapter


def main():
    print("=== Molecular AI + DeepSeek Demo ===")

    # 1. Симуляция
    sys = MolecularSystem(n_agents=6, dt=0.05, noise=0.02)
    sys.run(300)
    print(f"Sync after 300 steps: r = {sys.order_parameter():.3f}")

    # 2. Подключаем DeepSeek
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("[!] Set DEEPSEEK_API_KEY environment variable")
        print("    Example: set DEEPSEEK_API_KEY=sk-...")
        return

    try:
        adapter = create_adapter("deepseek", model="deepseek-chat", api_key=api_key)
    except Exception as e:
        print(f"[!] Failed to create adapter: {e}")
        return

    # 3. Задача
    agent = sys.agents[0]
    orbital = sys.orbital.layers[0].orbital
    task = "Suggest one concrete improvement for urban transportation in 2030."

    prompt = adapter.build_prompt(agent, orbital, task)
    print("\n--- PROMPT ---")
    print(prompt)
    print("--- END PROMPT ---\n")

    # 4. Живой ответ
    try:
        response = adapter.call_llm(prompt)
        print("--- DEEPSEEK RESPONSE ---")
        print(response)
        print("--- END RESPONSE ---")
    except Exception as e:
        print(f"[!] LLM call failed: {e}")


if __name__ == "__main__":
    main()