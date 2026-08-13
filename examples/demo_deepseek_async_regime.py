#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v6.0 + DeepSeek — Async Multi-Agent + ConvergenceRegime Demo.
6 agents with roles -> 800 steps sync -> regime switch ->
6 parallel async LLM calls -> consensus.

LAUNCH (Windows cmd):
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_deepseek_async_regime" "examples\demo_deepseek_async_regime.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_deepseek_async_regime.py

IMPORTANT: If saving via Notepad — choose "All files (*.*)" and type .py manually,
otherwise you get demo_deepseek_async_regime.py.txt
"""

import os
import sys
import random
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime, detect_regime, get_regime_description

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# Agent roles
ROLES = [
    {"name": "Ecologist", "persona": "You are an environmental scientist. Focus on sustainability, green tech, carbon footprint."},
    {"name": "Engineer", "persona": "You are a systems engineer. Focus on efficiency, optimization, automation, scalability."},
    {"name": "Economist", "persona": "You are an economist. Focus on cost, ROI, market viability, scalability."},
    {"name": "Sociologist", "persona": "You are a sociologist. Focus on people, communities, equity, accessibility."},
    {"name": "Futurist", "persona": "You are a futurist. Focus on innovation, AI, bold ideas, emerging tech."},
    {"name": "Critic", "persona": "You are a risk analyst. Focus on risks, limitations, edge cases, reality check."},
]


def build_prompt(agent, orbital, task: str, role: dict) -> str:
    """Build prompt with orbital context + agent role."""
    state = agent.get_state()
    sync_r = 0.0
    if hasattr(orbital, "get_mean_phase"):
        sync_r = orbital.get_mean_phase()

    return f"""=== ORBITAL CONTEXT ===
System sync: r ~ {sync_r:.2f}
Agent {state['agent_id']} | Phase: {state['phase']:.2f} | Mood: {state.get('mood', 0):+.2f} | Spin: {state.get('spin', 0):.2f} | Energy: {state.get('energy', 0):.2f}

=== YOUR ROLE ===
{role['persona']}

=== TASK ===
{task}

=== INSTRUCTION ===
Respond as {role['name']}. Give ONE concrete, actionable suggestion (2-4 sentences).
Reference the orbital state (sync, mood, energy) in your reasoning if relevant."""


async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat") -> str:
    """Async DeepSeek call via OpenAI-compatible API."""
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content


async def run_all_calls(prompts: list, api_key: str, model: str = "deepseek-chat") -> list:
    """Parallel launch of all LLM calls via asyncio.gather."""
    tasks = [call_deepseek_async(p, api_key, model) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)


def main():
    print("=" * 70)
    print("  MOLECULAR AI v6.0 + DEEPSEEK — ASYNC + REGIME DEMO")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] DEEPSEEK_API_KEY not set.")
        print("    set DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] Key loaded: {api_key[:8]}...{api_key[-4:]}")

    # --- 1. Simulation ---
    print("\n" + "-" * 70)
    print("[PHASE 1] Launching 6 agents + 4 orbital layers")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=6,
        dt=0.05,
        noise=0.02,
        sleep_every=300,
        k_sparse=5,
        exc_ratio=0.90,
    )
    for layer in sys.orbital.layers:
        layer.coupling *= 2.0
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.01, 0.01)

    print(f"  Agents: {sys.n} | Layers: {[l.name for l in sys.orbital.layers]}")
    print(f"  k_sparse={sys.plasticity.k} | Excitatory: {sum(1 for a in sys.agents if a.excitatory)}/{sys.n}")

    # Warm-up: 800 steps
    print("\n[PHASE 2] Warm-up: 800 steps...")
    for i in range(800):
        sys.step()
        if i % 200 == 199:
            r = sys.order_parameter()
            print(f"    Step {i+1:3d}: r = {r:.3f}")

    r_final = sys.order_parameter()
    print(f"\n  [OK] Warm-up complete: r = {r_final:.3f}")
    m = sys.get_metrics()
    print(f"  Mood: {m['mean_mood']:+.2f} | Energy: {m['mean_energy']:.3f}")
    print(f"  Goals: {m['goals_achieved']} | Reward: {m['total_reward']:.2f}")

    # --- 2. ConvergenceRegime ---
    print("\n" + "-" * 70)
    print("[PHASE 3] ConvergenceRegime switching")
    print("-" * 70)

    current_regime = detect_regime(sys)
    print(f"  Current regime: {current_regime.value} — {get_regime_description(current_regime)}")

    # Switch to CRITICAL for creativity before LLM calls
    print("  Switching to CRITICAL regime (exploration mode)...")
    set_regime(sys, ConvergenceRegime.CRITICAL)

    # 50 steps in CRITICAL regime
    print("  Running 50 steps in CRITICAL mode...")
    for _ in range(50):
        sys.step()
    r_critical = sys.order_parameter()
    print(f"  [OK] After CRITICAL: r = {r_critical:.3f}")

    # --- 3. Async Multi-LLM calls ---
    print("\n" + "-" * 70)
    print("[PHASE 4] Async DeepSeek calls (6 parallel via asyncio.gather)")
    print("-" * 70)

    task = (
        "How should a city redesign its public transportation by 2030 "
        "to be sustainable, efficient, and equitable?"
    )

    orbital = sys.orbital.layers[0].orbital
    prompts = []
    for i, agent in enumerate(sys.agents):
        role = ROLES[i]
        prompt = build_prompt(agent, orbital, task, role)
        prompts.append(prompt)
        print(f"  Agent {i} [{role['name']}] | mood={agent.mood:+.2f} | spin={agent.spin:.2f}")

    print(f"\n  Launching {len(prompts)} parallel API calls...")
    start_time = time.time()
    results = asyncio.run(run_all_calls(prompts, api_key))
    elapsed = time.time() - start_time
    print(f"  [OK] All calls completed in {elapsed:.1f} seconds")

    # Process results
    responses = []
    for i, result in enumerate(results):
        role = ROLES[i]
        agent = sys.agents[i]
        if isinstance(result, Exception):
            print(f"  Agent {i} [{role['name']}]: [X] {result}")
            responses.append({
                "agent_id": i, "role": role['name'],
                "mood": agent.mood, "spin": agent.spin, "phase": agent.phase,
                "response": f"[ERROR: {result}]"
            })
        else:
            print(f"  Agent {i} [{role['name']}]: [OK] {len(result)} chars")
            responses.append({
                "agent_id": i, "role": role['name'],
                "mood": agent.mood, "spin": agent.spin, "phase": agent.phase,
                "response": result
            })

    # --- 4. Output results ---
    print("\n" + "-" * 70)
    print("[PHASE 5] Full responses")
    print("-" * 70)

    for r in responses:
        print(f"\n{'='*60}")
        print(f"Agent {r['agent_id']} — {r['role']}")
        print(f"  mood={r['mood']:+.2f} | spin={r['spin']:.2f} | phase={r['phase']:.2f}")
        print(f"{'-'*60}")
        print(r['response'])

    # --- 5. Consensus ---
    print("\n" + "-" * 70)
    print("[PHASE 6] Orbital consensus")
    print("-" * 70)

    best = max(sys.agents, key=lambda a: a.mood + a.energy)
    best_role = ROLES[best.agent_id]['name']
    print(f"  Best agent by mood+energy: {best.agent_id} ({best_role})")
    print(f"  mood={best.mood:+.2f} | energy={best.energy:.3f}")
    print(f"\n  Winning suggestion:")
    for r in responses:
        if r['agent_id'] == best.agent_id:
            print(f"  {r['response'][:300]}...")

    # --- 6. Final metrics ---
    print("\n" + "-" * 70)
    print("[PHASE 7] Final system state")
    print("-" * 70)
    m = sys.get_metrics()
    print(f"  Steps: {m['step']} | Sync r: {m['sync_r']:.3f}")
    print(f"  Mood: {m['mean_mood']:+.2f} | Goals: {m['goals_achieved']}")
    W = sys.plasticity.W
    strong = sum(1 for w in W.values() if w > 1.2)
    weak = sum(1 for w in W.values() if w < 0.3)
    print(f"  Plasticity: {len(W)} conn | strong={strong} | weak={weak}")
    print(f"  Regime: {detect_regime(sys).value}")

    # --- 7. Save ---
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "deepseek_async_regime_results.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  MOLECULAR AI v6.0 + DEEPSEEK — ASYNC + REGIME RESULTS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Task: {task}\n")
        f.write(f"Final sync r: {m['sync_r']:.3f}\n")
        f.write(f"Mean mood: {m['mean_mood']:+.2f}\n")
        f.write(f"Regime: {detect_regime(sys).value}\n\n")
        for r in responses:
            f.write(f"\n{'='*60}\n")
            f.write(f"Agent {r['agent_id']} — {r['role']}\n")
            f.write(f"  mood={r['mood']:+.2f} | spin={r['spin']:.2f} | phase={r['phase']:.2f}\n")
            f.write(f"{'-'*60}\n")
            f.write(r['response'] + "\n")
    print(f"\n[OK] Results saved to: {out_path}")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()