#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример: Molecular AI + OpenAI GPT-4o-mini.
"""

import os
import sys

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from adapters.factory import create_adapter


def main():
    # 1. Запускаем симуляцию (без LLM)
    print("=== Molecular AI + OpenAI Demo ===")
    sys = MolecularSystem(n_agents=3, dt=0.05, noise=0.02)
    sys.run(200)
    print(f"Sync after 200 steps: r = {sys.order_parameter():.3f}")

    # 2. Подключаем LLM адаптер
    # Убедитесь, что установлено: pip install openai
    # И задана переменная окружения: OPENAI_API_KEY=sk-...
    try:
        adapter = create_adapter("openai", model="gpt-4o-mini")
    except ImportError as e:
        print(f"[!] {e}")
        print("Install: pip install openai")
        return
    except Exception as e:
        print(f"[!] Failed to create adapter: {e}")
        return

    # 3. Отправляем задачу через первого агента
    agent = sys.agents[0]
    orbital = sys.orbital.layers[0].orbital
    task = "Suggest one improvement for this multi-agent synchronization system."

    prompt = adapter.build_prompt(agent, orbital, task)
    print("\n--- PROMPT ---")
    print(prompt)
    print("--- END PROMPT ---\n")

    try:
        response = adapter.call_llm(prompt)
        print("--- LLM RESPONSE ---")
        print(response)
        print("--- END RESPONSE ---")
    except Exception as e:
        print(f"[!] LLM call failed: {e}")


if __name__ == "__main__":
    main()