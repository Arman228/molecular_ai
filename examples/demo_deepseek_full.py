#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Molecular AI v6.0 + DeepSeek — полное демо.
Синхронизация 6 агентов → живой LLM-вызов → метрики.
DeepSeek API через OpenAI-compatible endpoint.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def build_prompt(agent, orbital, task: str) -> str:
    """Строит промпт с orbital context."""
    state = agent.get_state()
    sync_r = 0.0
    if hasattr(orbital, "get_mean_phase"):
        sync_r = orbital.get_mean_phase()

    return f"""=== ORBITAL CONTEXT ===
System sync: r ≈ {sync_r:.2f}
Agent {state['agent_id']} | Phase: {state['phase']:.2f} | Mood: {state.get('mood', 0):+.2f} | Spin: {state.get('spin', 0):.2f} | Energy: {state.get('energy', 0):.2f}

=== TASK ===
{task}

=== INSTRUCTION ===
You are Agent {state['agent_id']} in a decentralized multi-agent system synchronized via Kuramoto oscillators.
Respond concisely (2-4 sentences) from the perspective of your role.
Maintain compatibility with the orbital state described above."""


def call_deepseek(prompt: str, api_key: str, model: str = "deepseek-chat") -> str:
    """Вызов DeepSeek через OpenAI-compatible API."""
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content


def main():
    print("=" * 70)
    print("  MOLECULAR AI v6.0 + DEEPSEEK — FULL DEMO")
    print("=" * 70)

    # --- 1. API Key ---
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] DEEPSEEK_API_KEY not set.")
        print("    Set it before running:")
        print("    export DEEPSEEK_API_KEY=sk-...")
        return

    if not HAS_OPENAI:
        print("\n[!] openai package not installed. Run: pip install openai")
        return

    print(f"\n[OK] DeepSeek API key loaded: {api_key[:8]}...{api_key[-4:]}")

    # --- 2. Симуляция ---
    print("\n" + "-" * 70)
    print("[PHASE 1] Launching MolecularSystem (6 agents, 4 orbital layers)")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=6,
        dt=0.05,
        noise=0.02,
        sleep_every=300,
        k_sparse=5,
        exc_ratio=0.90,
    )

    # Boost coupling for 6 agents (optimal from AutoTuner)
    for layer in sys.orbital.layers:
        layer.coupling *= 2.0
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.01, 0.01)

    print(f"  Agents: {sys.n}")
    print(f"  Orbital layers: {[l.name for l in sys.orbital.layers]}")
    print(f"  Sparse connections: k={sys.plasticity.k}")
    print(f"  Excitatory ratio: {sum(1 for a in sys.agents if a.excitatory)}/{sys.n}")

    # Warm-up
    print("\n[PHASE 2] Warm-up: 300 steps...")
    for i in range(300):
        sys.step()
        if i % 100 == 99:
            r = sys.order_parameter()
            print(f"    Step {i+1:3d}: r = {r:.3f}")

    r_final = sys.order_parameter()
    print(f"\n  ✅ Warm-up complete: r = {r_final:.3f}")

    # Metrics
    m = sys.get_metrics()
    print(f"  Mean mood: {m['mean_mood']:+.2f}")
    print(f"  Mean energy: {m['mean_energy']:.3f}")
    print(f"  Goals achieved: {m['goals_achieved']}")
    print(f"  Total reward: {m['total_reward']:.2f}")

    # --- 3. LLM вызов ---
    print("\n" + "-" * 70)
    print("[PHASE 3] DeepSeek LLM call via orbital context")
    print("-" * 70)

    # Выбираем агента с лучшим mood
    best_agent = max(sys.agents, key=lambda a: a.mood)
    orbital = sys.orbital.layers[0].orbital

    task = (
        "As a synchronized agent in this multi-agent system, "
        "suggest one concrete improvement for urban transportation in 2030."
    )

    prompt = build_prompt(best_agent, orbital, task)
    print(f"\n  Selected Agent: {best_agent.agent_id} (mood={best_agent.mood:+.2f})")
    print(f"\n--- PROMPT ---")
    print(prompt)
    print(f"--- END PROMPT ---\n")

    print("  Calling DeepSeek API...")
    try:
        response = call_deepseek(prompt, api_key)
        print(f"\n--- DEEPSEEK RESPONSE ---")
        print(response)
        print(f"--- END RESPONSE ---")
    except Exception as e:
        print(f"\n  ❌ LLM call failed: {e}")
        return

    # --- 4. Финальные метрики ---
    print("\n" + "-" * 70)
    print("[PHASE 4] Final system state")
    print("-" * 70)

    m = sys.get_metrics()
    print(f"  Steps: {m['step']}")
    print(f"  Sync r: {m['sync_r']:.3f}")
    print(f"  Mean mood: {m['mean_mood']:+.2f}")
    print(f"  Goals achieved: {m['goals_achieved']}")
    print(f"  Total reward: {m['total_reward']:.2f}")

    # Plasticity snapshot
    W = sys.plasticity.W
    strong = sum(1 for w in W.values() if w > 1.2)
    weak = sum(1 for w in W.values() if w < 0.3)
    print(f"  Plasticity: {len(W)} connections | strong={strong} | weak={weak}")

    # Attention
    attn = m.get("attention", {})
    print(f"  Attention salience: {attn.get('salience', [])}")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()