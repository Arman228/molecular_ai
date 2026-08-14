#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — Real Project: AI Collaboration Platform UI.
15 UI/UX experts -> DIVERGENT -> async generation -> SensorFusion voting ->
winning agent writes complete HTML/CSS/JS -> localhost server.

LAUNCH (Windows cmd):
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_ui_platform" "examples\demo_ui_platform.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_ui_platform.py

Then open http://localhost:8000 in your browser.
"""

import os
import sys
import random
import asyncio
import json
import time
import http.server
import socketserver
import threading
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime, detect_regime
from core.sensor_fusion import SensorFusionLayer

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# 15 UI/UX Expert roles
ROLES = [
    {"name": "UX_Researcher", "persona": "You are a UX researcher. Focus on user flows, mental models, personas, journey maps, usability testing."},
    {"name": "UI_Designer", "persona": "You are a UI designer. Focus on layout, component libraries, design systems, Figma-ready specs."},
    {"name": "Frontend_Dev", "persona": "You are a frontend architect. Focus on React/Vue/HTML structure, component hierarchy, state management."},
    {"name": "Accessibility", "persona": "You are an accessibility expert. Focus on WCAG 2.1 AA, screen readers, keyboard nav, color contrast."},
    {"name": "Interaction", "persona": "You are an interaction designer. Focus on micro-interactions, hover states, feedback loops, gestures."},
    {"name": "Visual_Designer", "persona": "You are a visual designer. Focus on spacing, visual hierarchy, whitespace, grid systems."},
    {"name": "Motion_Designer", "persona": "You are a motion designer. Focus on transitions, loading states, page animations, easing curves."},
    {"name": "Typography", "persona": "You are a typography expert. Focus on font pairing, readability, hierarchy, system fonts."},
    {"name": "Color_Specialist", "persona": "You are a color specialist. Focus on accessible palettes, dark mode, semantic colors, contrast ratios."},
    {"name": "Info_Architect", "persona": "You are an information architect. Focus on navigation, content structure, findability, taxonomies."},
    {"name": "Mobile_Dev", "persona": "You are a mobile-first developer. Focus on responsive design, touch targets, swipe gestures, PWA."},
    {"name": "Performance", "persona": "You are a performance engineer. Focus on lazy loading, code splitting, Core Web Vitals, bundle size."},
    {"name": "Security_UI", "persona": "You are a security UX expert. Focus on auth flows, 2FA, privacy controls, secure patterns."},
    {"name": "Content", "persona": "You are a content strategist. Focus on microcopy, empty states, error messages, tone of voice."},
    {"name": "QA_Tester", "persona": "You are a QA usability tester. Focus on edge cases, confusion points, broken flows, consistency."},
]

TASK = (
    "Design a modern AI-powered collaboration platform UI. "
    "The platform includes: dashboard, project workspace, chat sidebar, file manager, user profile. "
    "Your task: describe ONE critical UI decision (layout, component, pattern, or feature) "
    "that makes this platform exceptionally user-friendly. Be specific, cite examples."
)

CODE_TASK = (
    "You are now the lead frontend architect. Using the winning design decisions below, "
    "write a COMPLETE, runnable single-file HTML/CSS/JS prototype. "
    "Requirements:\n"
    "- Modern dark theme with glassmorphism accents\n"
    "- Responsive sidebar + main workspace layout\n"
    "- Dashboard with stats cards, project list, activity feed\n"
    "- Chat sidebar with message list and input\n"
    "- File manager with folder tree and grid view\n"
    "- User profile dropdown\n"
    "- Smooth CSS transitions and hover states\n"
    "- No external dependencies (pure HTML/CSS/JS in one file)\n"
    "- Use CSS Grid and Flexbox\n"
    "- Include mock data so it looks alive immediately\n"
    "\nReturn ONLY the complete HTML code between <!-- START --> and <!-- END --> markers."
)


def build_gen_prompt(agent, orbital, task: str, role: dict) -> str:
    state = agent.get_state()
    sync_r = 0.0
    if hasattr(orbital, "get_mean_phase"):
        sync_r = orbital.get_mean_phase()
    return f"""=== ORBITAL CONTEXT ===
System sync: r ~ {sync_r:.2f}
Agent {state['agent_id']} | Phase: {state['phase']:.2f} | Mood: {state.get('mood', 0):+.2f} | Spin: {state.get('spin', 0):.2f}

=== YOUR ROLE ===
{role['persona']}

=== TASK ===
{task}

=== INSTRUCTION ===
Respond as {role['name']}. Give ONE concrete UI/UX recommendation (3-5 sentences).
Include specific design patterns, tools, or metrics. Reference orbital state if relevant."""


def build_vote_prompt(role: dict, proposals: list) -> str:
    lines = [f"Here are {len(proposals)} UI/UX proposals for an AI collaboration platform:\n"]
    for i, prop in enumerate(proposals):
        text = prop['response'].replace('\n', ' ')[:120]
        lines.append(f"[{i}] {prop['role']}: {text}...")
    lines.append(f"\nAs {role['name']}, rate EACH proposal on 3 criteria (1-10):")
    lines.append("- Usability: how much does this improve user experience?")
    lines.append("- Feasibility: can this be built with modern web tech?")
    lines.append("- Impact: how critical is this for a collaboration platform?")
    lines.append(f"\nReturn ONLY valid JSON: {{\"ratings\": [[u,f,i], [u,f,i], ...]}}")
    lines.append(f"Array must have exactly {len(proposals)} triplets. No extra text.")
    return "\n".join(lines)


def build_code_prompt(winning_proposals: list, all_proposals: list) -> str:
    lines = [CODE_TASK]
    lines.append("\n=== WINNING DESIGN DECISIONS (incorporate these) ===")
    for p in winning_proposals:
        lines.append(f"\n[{p['role']}]: {p['response']}")
    lines.append("\n=== OTHER NOTABLE IDEAS (reference if useful) ===")
    for p in all_proposals[:5]:
        if p not in winning_proposals:
            lines.append(f"[{p['role']}]: {p['response'][:150]}...")
    return "\n".join(lines)


async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat", max_tokens: int = 1024) -> str:
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


async def run_all_calls(prompts: list, api_key: str, max_tokens: int = 1024) -> list:
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


def extract_html(text: str) -> str:
    start = text.find("<!-- START -->")
    end = text.find("<!-- END -->")
    if start != -1 and end != -1:
        return text[start + len("<!-- START -->"):end].strip()
    if "<!DOCTYPE html>" in text or "<html" in text:
        html_start = text.find("<!DOCTYPE html>")
        if html_start == -1:
            html_start = text.find("<html")
        return text[html_start:].strip()
    return text


def start_server(port: int = 8000, directory: str = "."):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def main():
    print("=" * 70)
    print("  MOLECULAR AI v7.0 — REAL PROJECT: AI PLATFORM UI")
    print("  15 UI/UX experts -> DIVERGENT -> SensorFusion -> Live HTML")
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
    print("[PHASE 1] Launching 15 UI/UX agents + 4 orbital layers")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=15,
        dt=0.05,
        noise=0.015,
        sleep_every=400,
        k_sparse=5,
        exc_ratio=0.88,
    )
    for layer in sys.orbital.layers:
        layer.coupling *= 2.5
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.02, 0.02)

    print(f"  Agents: {sys.n} | Layers: {[l.name for l in sys.orbital.layers]}")
    print(f"  k_sparse={sys.plasticity.k} | Excitatory: {sum(1 for a in sys.agents if a.excitatory)}/{sys.n}")

    # Warm-up
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
    print("[PHASE 3] DIVERGENT regime (maximum creativity)")
    print("-" * 70)
    set_regime(sys, ConvergenceRegime.DIVERGENT)
    for _ in range(100):
        sys.step()
    print(f"  [OK] After DIVERGENT: r = {sys.order_parameter():.3f}")

    # --- 3. Generation round ---
    print("\n" + "-" * 70)
    print("[PHASE 4] UI/UX generation — 15 parallel async calls")
    print("-" * 70)

    orbital = sys.orbital.layers[0].orbital
    gen_prompts = []
    for i, agent in enumerate(sys.agents):
        prompt = build_gen_prompt(agent, orbital, TASK, ROLES[i])
        gen_prompts.append(prompt)
        print(f"  Agent {i:2d} [{ROLES[i]['name']:14s}] | mood={agent.mood:+.2f} | spin={agent.spin:+.2f}")

    print(f"\n  Launching {len(gen_prompts)} generation calls...")
    t0 = time.time()
    gen_results = asyncio.run(run_all_calls(gen_prompts, api_key, max_tokens=1024))
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
    print("[PHASE 5] SensorFusion voting — 15 parallel evaluations")
    print("-" * 70)

    vote_prompts = [build_vote_prompt(ROLES[i], proposals) for i in range(len(sys.agents))]
    print(f"  Launching {len(vote_prompts)} voting calls...")
    t0 = time.time()
    vote_results = asyncio.run(run_all_calls(vote_prompts, api_key, max_tokens=2048))
    print(f"  [OK] Voting done in {time.time()-t0:.1f}s")

    ratings_matrix = []
    n_props = len(proposals)
    for i, res in enumerate(vote_results):
        parsed = parse_vote_json(res, n_props) if not isinstance(res, Exception) else None
        if parsed:
            ratings_matrix.append(parsed)
            print(f"  Voter {i:2d} [{ROLES[i]['name']:14s}]: parsed {len(parsed)} ratings")
        else:
            print(f"  Voter {i:2d} [{ROLES[i]['name']:14s}]: [X] parse failed, neutral")
            ratings_matrix.append([[5, 5, 5]] * n_props)

    # --- 5. SensorFusion consensus ---
    print("\n" + "-" * 70)
    print("[PHASE 6] SensorFusion consensus")
    print("-" * 70)

    n_voters = len(ratings_matrix)
    measurements = []
    for voter_idx in range(n_voters):
        row = []
        for prop_idx in range(n_props):
            u, f, imp = ratings_matrix[voter_idx][prop_idx]
            row.append((u + f + imp) / 3.0)
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

    indexed = [(i, consensus_scores[i]) for i in range(n_props)]
    indexed.sort(key=lambda x: x[1], reverse=True)

    print(f"  Top 5 consensus scores:")
    for rank, (idx, score) in enumerate(indexed[:5], 1):
        marker = " <<< WINNER" if rank == 1 else ""
        print(f"    #{rank} [{proposals[idx]['role']:14s}]: {score:.2f}{marker}")

    top3 = [proposals[idx] for idx, _ in indexed[:3]]
    print(f"\n  Top 3 winners will guide code generation.")

    # --- 6. Code generation ---
    print("\n" + "-" * 70)
    print("[PHASE 7] Generating complete HTML/CSS/JS prototype")
    print("-" * 70)

    code_prompt = build_code_prompt(top3, proposals)
    print(f"  Prompt size: {len(code_prompt)} chars")
    print(f"  Calling DeepSeek for code (max_tokens=4096)...")

    t0 = time.time()
    try:
        code_response = asyncio.run(call_deepseek_async(code_prompt, api_key, max_tokens=4096))
        html_code = extract_html(code_response)
        print(f"  [OK] Code generated in {time.time()-t0:.1f}s ({len(html_code)} chars)")
    except Exception as e:
        print(f"  [X] Code generation failed: {e}")
        return

    # --- 7. Save & serve ---
    print("\n" + "-" * 70)
    print("[PHASE 8] Saving and launching localhost server")
    print("-" * 70)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "platform_ui.html")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"  [OK] Saved to: {html_path}")

    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    port = 8000
    try:
        httpd = start_server(port, output_dir)
        print(f"\n  🚀 SERVER RUNNING at http://localhost:{port}/platform_ui.html")
        print(f"  🚀 Or open: http://localhost:{port}/index.html")
        print(f"\n  Press Ctrl+C to stop")

        try:
            webbrowser.open(f"http://localhost:{port}/platform_ui.html")
            print(f"  [OK] Browser opened automatically")
        except:
            pass

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  [OK] Server stopped")
    except OSError:
        print(f"\n  [!] Port {port} busy. Trying {port+1}...")
        httpd = start_server(port+1, output_dir)
        print(f"  🚀 SERVER RUNNING at http://localhost:{port+1}/platform_ui.html")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()