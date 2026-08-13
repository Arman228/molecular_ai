#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v6.0 + DeepSeek — 30-AGENT MEGA DEMO.
30 agents | DIVERGENT regime | Mars colony 1000-person blueprint |
Async generation + SensorFusion voting consensus.

LAUNCH (Windows cmd):
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_deepseek_30_agents" "examples\demo_deepseek_30_agents.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_deepseek_30_agents.py
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


# 30 Agent roles
ROLES = [
    {"name": "Biologist", "persona": "Astrobiologist. Closed-loop life support, terraforming microbes, radiation-resistant organisms."},
    {"name": "Engineer", "persona": "Aerospace engineer. Habitats, ISRU, 3D printing, structural integrity."},
    {"name": "Economist", "persona": "Space economist. Funding models, resource allocation, cost per kg to Mars."},
    {"name": "Sociologist", "persona": "Space sociologist. Governance, community building, mental health, law."},
    {"name": "Futurist", "persona": "Futurist. Breakthrough tech, AI swarms, quantum comms, bold visions."},
    {"name": "Critic", "persona": "Risk analyst. Failure modes, radiation, budget overruns, reality checks."},
    {"name": "Physicist", "persona": "Plasma physicist. Energy generation, propulsion, radiation shielding."},
    {"name": "Medic", "persona": "Space medicine specialist. Telemedicine, surgery, long-term health effects."},
    {"name": "Architect", "persona": "Space architect. Underground habitats, modular design, human factors."},
    {"name": "Agronomist", "persona": "Space agronomist. Hydroponics, soil synthesis, waste-to-food loops."},
    {"name": "Diplomat", "persona": "Space diplomat. International cooperation, treaties, logistics chains."},
    {"name": "Psychologist", "persona": "Isolation psychologist. Crew selection, morale, team dynamics."},
    {"name": "Lawyer", "persona": "Space lawyer. Martian jurisdiction, property rights, liability, criminal law."},
    {"name": "Ethicist", "persona": "Bioethicist. Genetic modification of colonists, AI rights, end-of-life decisions."},
    {"name": "Artist", "persona": "Space artist. Habitat aesthetics, sensory design, cultural identity, morale through art."},
    {"name": "Journalist", "persona": "Space journalist. Transparency, Earth-Mars communication, documenting history, public trust."},
    {"name": "Chemist", "persona": "Inorganic chemist. Regolith processing, fuel synthesis, atmospheric extraction."},
    {"name": "Roboticist", "persona": "Robotics engineer. Autonomous construction drones, swarm maintenance, human-robot collaboration."},
    {"name": "Geologist", "persona": "Planetary geologist. Site selection, lava tubes, water ice mapping, seismic stability."},
    {"name": "Climatologist", "persona": "Planetary climatologist. Dust storm prediction, thermal management, artificial weather."},
    {"name": "Historian", "persona": "Space historian. Learning from polar expeditions, documenting firsts, preserving human legacy."},
    {"name": "Philosopher", "persona": "Existential philosopher. Meaning of off-world life, human identity, post-Earth ethics."},
    {"name": "Educator", "persona": "Space educator. Training colonists, children curriculum, knowledge preservation, skill transfer."},
    {"name": "Security", "persona": "Security expert. Sabotage prevention, airlock protocols, weapons policy, emergency lockdown."},
    {"name": "Logistician", "persona": "Supply chain expert. Inventory optimization, just-in-time resupply, spare parts forecasting."},
    {"name": "Nutritionist", "persona": "Space nutritionist. Calorie density, food psychology, cultural cuisine, micronutrient balance."},
    {"name": "AI_Researcher", "persona": "AI researcher. Autonomous colony management, predictive maintenance, decision support systems."},
    {"name": "Geneticist", "persona": "Space geneticist. Radiation adaptation, crop engineering, population genetics, gene therapy."},
    {"name": "Urban_Planner", "persona": "Urban planner. Zoning, walkability, public spaces, population density, infrastructure scaling."},
    {"name": "Game_Designer", "persona": "Game designer. Gamification of tasks, VR training simulations, reward systems, engagement loops."},
]

TASK = (
    "Design a comprehensive blueprint for the first 1000-person Mars colony by 2045. "
    "Outline ONE critical subsystem that MUST be operational before the first 100 settlers arrive. "
    "Be specific, cite numbers, and explain why this is the bottleneck."
)


def build_gen_prompt(agent, orbital, task: str, role: dict) -> str:
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
Respond as {role['name']}. Give ONE concrete, actionable proposal (3-5 sentences).
Include specific numbers, timelines, or metrics. Reference the orbital state if relevant."""


def build_vote_prompt(role: dict, proposals: list) -> str:
    lines = [f"Here are {len(proposals)} proposals for Mars colony critical subsystems:\n"]
    for i, prop in enumerate(proposals):
        text = prop['response'].replace('\n', ' ')[:100]
        lines.append(f"[{i}] {prop['role']}: {text}...")
    lines.append(f"\nAs an expert {role['name']}, rate EACH of the {len(proposals)} proposals on 3 criteria (1-10):")
    lines.append("- Feasibility: can this be built by 2045?")
    lines.append("- Innovation: how novel is this approach?")
    lines.append("- Criticality: how essential is this BEFORE the first 100 settlers?")
    lines.append(f"\nReturn ONLY valid JSON: {{\"ratings\": [[f,i,c], [f,i,c], ...]}}")
    lines.append(f"Array must have exactly {len(proposals)} triplets. No extra text.")
    return "\n".join(lines)


async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat", max_tokens: int = 512) -> str:
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


async def run_all_calls(prompts: list, api_key: str, max_tokens: int = 512) -> list:
    tasks = [call_deepseek_async(p, api_key, max_tokens=max_tokens) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)


def parse_vote_json(text: str, expected_len: int) -> list:
    try:
        data = json.loads(text)
        if "ratings" in data and len(data["ratings"]) == expected_len:
            return data["ratings"]
    except json.JSONDecodeError:
        pass
    try:
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            arr = json.loads(text[start:end+1])
            if len(arr) == expected_len:
                return arr
    except Exception:
        pass
    return None


def main():
    print("=" * 70)
    print("  MOLECULAR AI v6.0 + DEEPSEEK — 30-AGENT MEGA DEMO")
    print("  30 agents | DIVERGENT regime | SensorFusion voting")
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
    print("[PHASE 1] Launching 30 agents + 4 orbital layers")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=30,
        dt=0.05,
        noise=0.01,
        sleep_every=500,
        k_sparse=6,
        exc_ratio=0.90,
    )
    # AutoTuner boost for 30 agents
    for layer in sys.orbital.layers:
        layer.coupling *= 3.0
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.02, 0.02)

    print(f"  Agents: {sys.n} | Layers: {[l.name for l in sys.orbital.layers]}")
    print(f"  k_sparse={sys.plasticity.k} | Excitatory: {sum(1 for a in sys.agents if a.excitatory)}/{sys.n}")

    # Warm-up: 1200 steps
    print("\n[PHASE 2] Warm-up: 1200 steps...")
    for i in range(1200):
        sys.step()
        if i % 300 == 299:
            r = sys.order_parameter()
            print(f"    Step {i+1:4d}: r = {r:.3f}")

    print(f"\n  [OK] Warm-up: r = {sys.order_parameter():.3f}")
    m = sys.get_metrics()
    print(f"  Mood: {m['mean_mood']:+.2f} | Energy: {m['mean_energy']:.3f}")

    # --- 2. DIVERGENT regime ---
    print("\n" + "-" * 70)
    print("[PHASE 3] DIVERGENT regime (maximum chaos/creativity)")
    print("-" * 70)

    print(f"  Current: {detect_regime(sys).value}")
    set_regime(sys, ConvergenceRegime.DIVERGENT)
    print("  Running 150 steps in DIVERGENT mode...")
    for _ in range(150):
        sys.step()
    print(f"  [OK] After DIVERGENT: r = {sys.order_parameter():.3f}")

    # --- 3. Generation round ---
    print("\n" + "-" * 70)
    print(f"[PHASE 4] Generation round — {len(ROLES)} parallel async calls")
    print("-" * 70)

    orbital = sys.orbital.layers[0].orbital
    gen_prompts = []
    for i, agent in enumerate(sys.agents):
        prompt = build_gen_prompt(agent, orbital, TASK, ROLES[i])
        gen_prompts.append(prompt)
        print(f"  Agent {i:2d} [{ROLES[i]['name']:14s}] | mood={agent.mood:+.2f} | spin={agent.spin:+.2f}")

    print(f"\n  Launching {len(gen_prompts)} generation calls...")
    t0 = time.time()
    gen_results = asyncio.run(run_all_calls(gen_prompts, api_key))
    print(f"  [OK] Generation done in {time.time()-t0:.1f}s")

    proposals = []
    for i, res in enumerate(gen_results):
        if isinstance(res, Exception):
            print(f"  Agent {i:2d}: [X] {str(res)[:60]}")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": "[ERROR]"})
        else:
            print(f"  Agent {i:2d}: [OK] {len(res)} chars")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": res})

    # --- 4. Voting round ---
    print("\n" + "-" * 70)
    print(f"[PHASE 5] SensorFusion voting — {len(ROLES)} parallel async evaluations")
    print("-" * 70)

    vote_prompts = [build_vote_prompt(ROLES[i], proposals) for i in range(len(sys.agents))]
    print(f"  Launching {len(vote_prompts)} voting calls (max_tokens=2048)...")
    t0 = time.time()
    vote_results = asyncio.run(run_all_calls(vote_prompts, api_key, max_tokens=2048))
    print(f"  [OK] Voting done in {time.time()-t0:.1f}s")

    # Parse ratings
    ratings_matrix = []
    n_props = len(proposals)
    for i, res in enumerate(vote_results):
        parsed = parse_vote_json(res, n_props) if not isinstance(res, Exception) else None
        if parsed:
            ratings_matrix.append(parsed)
            print(f"  Voter {i:2d} [{ROLES[i]['name']:14s}]: parsed {len(parsed)} ratings")
        else:
            print(f"  Voter {i:2d} [{ROLES[i]['name']:14s}]: [X] parse failed, using neutral")
            ratings_matrix.append([[5, 5, 5]] * n_props)

    # --- 5. SensorFusion consensus ---
    print("\n" + "-" * 70)
    print("[PHASE 6] SensorFusion robust consensus")
    print("-" * 70)

    n_voters = len(ratings_matrix)
    measurements = []
    for voter_idx in range(n_voters):
        row = []
        for prop_idx in range(n_props):
            f, i, c = ratings_matrix[voter_idx][prop_idx]
            row.append((f + i + c) / 3.0)
        measurements.append(row)

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

    print(f"  Top 10 consensus scores (median-filtered):")
    indexed = [(i, consensus_scores[i]) for i in range(n_props)]
    indexed.sort(key=lambda x: x[1], reverse=True)
    for rank, (idx, score) in enumerate(indexed[:10], 1):
        marker = " <<< WINNER" if rank == 1 else ""
        print(f"    #{rank:2d} Proposal {idx:2d} [{proposals[idx]['role']:14s}]: {score:.2f}{marker}")

    best_idx = indexed[0][0]
    best = proposals[best_idx]
    print(f"\n  [WINNER] Proposal {best_idx} — {best['role']}")
    print(f"  Score: {consensus_scores[best_idx]:.2f}")

    avg_rep = [sum(reputation[i]) / len(reputation[i]) for i in range(n_voters)]
    top_voter = max(range(n_voters), key=lambda i: avg_rep[i])
    print(f"  Most reliable voter: {ROLES[top_voter]['name']} (avg rep: {avg_rep[top_voter]:.2f})")

    # --- 6. Full responses (top 5) ---
    print("\n" + "-" * 70)
    print("[PHASE 7] Top 5 proposals")
    print("-" * 70)
    for rank, (idx, score) in enumerate(indexed[:5], 1):
        p = proposals[idx]
        print(f"\n{'='*60}")
        print(f"#{rank} [{idx}] {p['role']} | consensus: {score:.2f}")
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
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "deepseek_30_agents_results.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  MOLECULAR AI v6.0 + DEEPSEEK — 30-AGENT MEGA RESULTS\n")
        f.write("  30 agents | DIVERGENT | SensorFusion voting\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Task: {TASK}\n")
        f.write(f"Final sync r: {m['sync_r']:.3f}\n")
        f.write(f"Mean mood: {m['mean_mood']:+.2f}\n")
        f.write(f"Regime: {detect_regime(sys).value}\n")
        f.write(f"Winner: Proposal {best_idx} — {best['role']} (score: {consensus_scores[best_idx]:.2f})\n\n")
        for rank, (idx, score) in enumerate(indexed, 1):
            p = proposals[idx]
            f.write(f"\n{'='*60}\n")
            f.write(f"#{rank} [{idx}] {p['role']} | consensus: {score:.2f}\n")
            f.write(f"{'-'*60}\n")
            f.write(p['response'] + "\n")
    print(f"\n[OK] Saved to: {out_path}")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()