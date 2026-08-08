#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Molecular AI + NVIDIA NIM — живой LLM.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from adapters.nvidia_adapter import NvidiaAdapter


def main():
    print("=== Molecular AI + NVIDIA NIM Demo ===")

    sys = MolecularSystem(n_agents=6, dt=0.05, noise=0.02)
    sys.run(300)
    print(f"Sync after 300 steps: r = {sys.order_parameter():.3f}")

    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("[!] Set NVIDIA_API_KEY environment variable")
        return

    try:
        adapter = NvidiaAdapter(api_key=api_key, model="meta/llama3-70b-instruct")
    except Exception as e:
        print(f"[!] Failed: {e}")
        return

    agent = sys.agents[0]
    orbital = sys.orbital.layers[0].orbital
    task = "Suggest one concrete improvement for urban transportation in 2030."

    prompt = adapter.build_prompt(agent, orbital, task)
    print("\n--- PROMPT ---")
    print(prompt)
    print("--- END PROMPT ---\n")

    try:
        response = adapter.call_llm(prompt)
        print("--- NVIDIA LLM RESPONSE ---")
        print(response)
        print("--- END RESPONSE ---")
    except Exception as e:
        print(f"[!] LLM call failed: {e}")


if __name__ == "__main__":
    main()