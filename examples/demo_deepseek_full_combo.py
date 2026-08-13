#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v6.0 + DeepSeek — FULL COMBO DEMO.
12 agents | DIVERGENT regime | Mars colony task |
Async generation + SensorFusion voting consensus.

LAUNCH (Windows cmd):
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_deepseek_full_combo" "examples\demo_deepseek_full_combo.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_deepseek_full_combo.py
"""

import os
import sys
import random
import asyncio
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime, detect_regime, get_regime_description
from core.sensor_fusion import SensorFusionLayer

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# 12 Agent roles
ROLES = [
    {"name": "Biologist", "persona": "You are an astrobiologist. Focus on closed-loop life support, terraforming microbes, radiation-resistant organisms."},
    {"name": "Engineer", "persona": "You are a aerospace engineer. Focus on habitats, ISRU, 3D printing, structural integrity."},
    {"name": "Economist", "persona": "You are a space economist. Focus on funding models, resource allocation, cost per kg to Mars."},
    {"name": "Sociologist", "persona": "You are a space sociologist. Focus on governance, community building, mental health, law."},
    {"name": "Futurist", "persona": "You are a futurist. Focus on breakthrough tech, AI swarms, quantum comms, bold visions."},
    {"name": "Critic", "persona": "You are a risk analyst. Focus on failure modes, radiation, budget overruns, reality checks."},
    {"name": "Physicist", "persona": "You are a plasma physicist. Focus on energy generation, propulsion, radiation shielding."},
    {"name": "Medic", "persona": "You are a space medicine specialist. Focus on telemedicine, surgery, long-term health effects."},
    {"name": "Architect", "persona": "You are a space architect. Focus on underground habitats, modular design, human factors."},
    {"name": "Agronomist", "persona": "You are a space agronomist. Focus on hydroponics, soil synthesis, waste-to-food loops."},
    {"name": "Diplomat", "persona": "You are a space diplomat. Focus on international cooperation, treaties, logistics chains."},
    {"name": "Psychologist", "persona": "You are an isolation psychologist. Focus on crew selection, morale, team dynamics."},
]

TASK = (
    "How can humanity establish a self-sustaining Mars colony by 2040? "
    "Outline ONE critical subsystem or strategy (2-4 sentences). Be specific."
)


def build_gen_prompt(agent, orbital, task: str, role: dict) -> str:
    """Generation prompt with orbital context."""
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
Respond as {role['name']}. Give ONE concrete, actionable proposal (2-4 sentences).
Reference the orbital state if relevant."""


def build_vote_prompt(role: dict, proposals: list) -> str:
    """Voting prompt: agent rates all 12 proposals."""
    lines = ["Here are 12 proposals for Mars colony critical subsystems:\n"]
    for i, prop in enumerate(proposals):
        text = prop['response'].replace('\n', ' ')[:200]
        lines.append(f"[{i}] {prop['role']}: {text}...")
    lines.append("\nAs an expert " + role['name'] + ", rate EACH proposal on 3 criteria (1-10):")
    lines.append("- Feasibility: can this be built by 2040?")
    lines.append("- Innovation: how novel is this approach?")
    lines.append("- Safety: how well does this protect colonists?")
    lines.append("\nReturn ONLY valid JSON: {\"ratings\": [[f,i,s], [f,i,s], ...]}")
    lines.append("Index 0 = Proposal 0, etc. No extra text.")
    return "\n".join(lines)


async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat", max_tokens: int = 512) -> str:
    """Async DeepSeek call."""
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


async def run_all_calls(prompts: list, api_key: str, max_tokens: int = 512) -> list:
    """Parallel async calls."""
    tasks = [call_deepseek_async(p, api_key, max_tokens=max_tokens) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)


def parse_vote_json(text: str) -> list:
    """Parse JSON ratings from LLM response."""
    try:
        data = json.loads(text)
        if "ratings" in data:
            return data["ratings"]
    except json.JSONDecodeError:
        pass
    # Fallback: try to extract JSON from markdown
    try:
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception:
        pass
    return None


def main():
    print("=" * 70)
    print("  MOLECULAR AI v6.0 + DEEPSEEK — FULL COMBO DEMO")
    print("  12 agents | DIVERGENT regime | SensorFusion voting")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] DEEPSEEK_API_KEY not set.\n    set DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] Key loaded: {api_key[:8]}...{api_key[-4:]}")

    # --- 1. Simulation ---
    print("\n" + "-" * 70)
    print("[PHASE 1] Launching 12 agents + 4 orbital layers")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=12,
        dt=0.05,
        noise=0.015,
        sleep_every=400,
        k_sparse=5,
        exc_ratio=0.92,
    )
    # AutoTuner boost for 12 agents
    for layer in sys.orbital.layers:
        layer.coupling *= 2.5
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.02, 0.02)

    print(f"  Agents: {sys.n} | Layers: {[l.name for l in sys.orbital.layers]}")
    print(f"  k_sparse={sys.plasticity.k} | Excitatory: {sum(1 for a in sys.agents if a.excitatory)}/{sys.n}")

    # Warm-up: 800 steps
    print("\n[PHASE 2] Warm-up: 800 steps...")
    for i in range(800):
        sys.step()
        if i % 200 == 199:
            r = sys.order_parameter()
            print(f"    Step {i+1:3d}: r = {r:.3f}")

    print(f"\n  [OK] Warm-up: r = {sys.order_parameter():.3f}")
    m = sys.get_metrics()
    print(f"  Mood: {m['mean_mood']:+.2f} | Energy: {m['mean_energy']:.3f}")

    # --- 2. DIVERGENT regime ---
    print("\n" + "-" * 70)
    print("[PHASE 3] DIVERGENT regime (maximum chaos/creativity)")
    print("-" * 70)

    print(f"  Current: {detect_regime(sys).value}")
    set_regime(sys, ConvergenceRegime.DIVERGENT)
    print("  Running 100 steps in DIVERGENT mode...")
    for _ in range(100):
        sys.step()
    print(f"  [OK] After DIVERGENT: r = {sys.order_parameter():.3f}")

    # --- 3. Generation round ---
    print("\n" + "-" * 70)
    print("[PHASE 4] Generation round — 12 parallel async calls")
    print("-" * 70)

    orbital = sys.orbital.layers[0].orbital
    gen_prompts = []
    for i, agent in enumerate(sys.agents):
        prompt = build_gen_prompt(agent, orbital, TASK, ROLES[i])
        gen_prompts.append(prompt)
        print(f"  Agent {i:2d} [{ROLES[i]['name']:12s}] | mood={agent.mood:+.2f} | spin={agent.spin:+.2f}")

    print(f"\n  Launching {len(gen_prompts)} generation calls...")
    t0 = time.time()
    gen_results = asyncio.run(run_all_calls(gen_prompts, api_key))
    print(f"  [OK] Generation done in {time.time()-t0:.1f}s")

    proposals = []
    for i, res in enumerate(gen_results):
        if isinstance(res, Exception):
            print(f"  Agent {i}: [X] {res}")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": "[ERROR]"})
        else:
            print(f"  Agent {i}: [OK] {len(res)} chars")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": res})

    # --- 4. Voting round ---
    print("\n" + "-" * 70)
    print("[PHASE 5] SensorFusion voting — 12 parallel async evaluations")
    print("-" * 70)

    vote_prompts = [build_vote_prompt(ROLES[i], proposals) for i in range(len(sys.agents))]
    print(f"  Launching {len(vote_prompts)} voting calls...")
    t0 = time.time()
    vote_results = asyncio.run(run_all_calls(vote_prompts, api_key, max_tokens=1024))
    print(f"  [OK] Voting done in {time.time()-t0:.1f}s")

    # Parse ratings
    ratings_matrix = []  # [voter][proposal] = [f, i, s]
    for i, res in enumerate(vote_results):
        parsed = parse_vote_json(res) if not isinstance(res, Exception) else None
        if parsed and len(parsed) == len(proposals):
            ratings_matrix.append(parsed)
            print(f"  Voter {i:2d} [{ROLES[i]['name']:12s}]: parsed {len(parsed)} ratings")
        else:
            print(f"  Voter {i:2d} [{ROLES[i]['name']:12s}]: [X] parse failed, using neutral")
            ratings_matrix.append([[5, 5, 5]] * len(proposals))

    # --- 5. SensorFusion consensus ---
    print("\n" + "-" * 70)
    print("[PHASE 6] SensorFusion robust consensus")
    print("-" * 70)

    # Build measurements: [voter][proposal] = avg(f,i,s)
    n_voters = len(ratings_matrix)
    n_props = len(proposals)
    measurements = []
    for voter_idx in range(n_voters):
        row = []
        for prop_idx in range(n_props):
            f, i, s = ratings_matrix[voter_idx][prop_idx]
            row.append((f + i + s) / 3.0)
        measurements.append(row)

    # SensorFusionLayer with 12 dimensions (proposals)
    dimensions = [{"name": f"Proposal_{i}", "unit": "score"} for i in range(n_props)]
    fusion = SensorFusionLayer(
        n_agents=n_voters,
        dimensions=dimensions,
        threshold=2.0,
        min_rep=0.5,
        reputation_window=50,
    )

    consensus_scores = fusion.process_round(measurements)
    reputation = fusion.get_reputation_matrix()

    print(f"  Consensus scores (median-filtered):")
    for i, score in enumerate(consensus_scores):
        print(f"    Proposal {i:2d} [{proposals[i]['role']:12s}]: {score:.2f}")

    # Best proposal
    best_idx = max(range(n_props), key=lambda i: consensus_scores[i])
    best = proposals[best_idx]
    print(f"\n  [WINNER] Proposal {best_idx} — {best['role']}")
    print(f"  Score: {consensus_scores[best_idx]:.2f}")

    # Most reliable voters
    avg_rep = [sum(reputation[i]) / len(reputation[i]) for i in range(n_voters)]
    top_voter = max(range(n_voters), key=lambda i: avg_rep[i])
    print(f"  Most reliable voter: {ROLES[top_voter]['name']} (avg rep: {avg_rep[top_voter]:.2f})")

    # --- 6. Full responses ---
    print("\n" + "-" * 70)
    print("[PHASE 7] All proposals")
    print("-" * 70)
    for i, p in enumerate(proposals):
        marker = " <<< WINNER" if i == best_idx else ""
        print(f"\n{'='*60}")
        print(f"[{i}] {p['role']}{marker}")
        print(f"{'-'*60}")
        print(p['response'])

    # --- 7. Final metrics ---
    print("\n" + "-" * 70)
    print("[PHASE 8] Final system state")
    print("-" * 70)
    m = sys.get_metrics()
    print(f"  Steps: {m['step']} | Sync r: {m['sync_r']:.3f}")
    print(f"  Mood: {m['mean_mood']:+.2f} | Goals: {m['goals_achieved']}")
    W = sys.plasticity.W
    strong = sum(1 for w in W.values() if w > 1.2)
    weak = sum(1 for w in W.values() if w < 0.3)
    print(f"  Plasticity: {len(W)} conn | strong={strong} | weak={weak}")
    print(f"  Regime: {detect_regime(sys).value}")

    # --- 8. Save ---
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "deepseek_full_combo_results.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  MOLECULAR AI v6.0 + DEEPSEEK — FULL COMBO RESULTS\n")
        f.write("  12 agents | DIVERGENT | SensorFusion voting\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Task: {TASK}\n")
        f.write(f"Final sync r: {m['sync_r']:.3f}\n")
        f.write(f"Mean mood: {m['mean_mood']:+.2f}\n")
        f.write(f"Regime: {detect_regime(sys).value}\n")
        f.write(f"Winner: Proposal {best_idx} — {best['role']} (score: {consensus_scores[best_idx]:.2f})\n\n")
        for i, p in enumerate(proposals):
            f.write(f"\n{'='*60}\n")
            f.write(f"[{i}] {p['role']} | consensus: {consensus_scores[i]:.2f}\n")
            f.write(f"{'-'*60}\n")
            f.write(p['response'] + "\n")
    print(f"\n[OK] Saved to: {out_path}")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()