#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — REAL UI PLATFORM v4 (2026 Trends).
max_tokens=16384 for complete generation.
Focus: Neubrutalism, 3D elements, AI-native interfaces, micro-interactions.

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_ui_platform_v4" "examples\demo_ui_platform_v4.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_ui_platform_v4.py
""" 

import os
import sys
import random
import asyncio
import time
import http.server
import socketserver
import threading
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


ROLES = [
    {"name": "Trend_Analyst", "persona": "2026 UI trends: neubrutalism, 3D, glassmorphism 2.0, AI-native, micro-interactions."},
    {"name": "UX_Researcher", "persona": "UX researcher. Dashboard layout, quick actions, user flows, zero UI."},
    {"name": "UI_Designer", "persona": "UI designer. Component libraries, spacing, visual hierarchy, 3D elements."},
    {"name": "Frontend_Dev", "persona": "Frontend architect. HTML structure, CSS Grid, Flexbox, animations."},
    {"name": "Accessibility", "persona": "Accessibility expert. WCAG 2.1 AA, keyboard nav, ARIA, inclusive design."},
    {"name": "Interaction", "persona": "Interaction designer. Micro-interactions, hover states, modals, gestures."},
    {"name": "Visual_Designer", "persona": "Visual designer. Neubrutalism, bold colors, 3D, glitch effects."},
    {"name": "Mobile_Dev", "persona": "Mobile-first. Responsive, touch targets, collapsible sidebar, gestures."},
    {"name": "Performance", "persona": "Performance engineer. CSS-only animations, 60fps, WebGL optimization."},
    {"name": "AI_Native", "persona": "AI-native UI. Chat interfaces, voice UI, predictive actions, auto-complete."},
]

TASK = (
    "Design ONE critical UI element for an AI collaboration platform that follows 2026 trends. "
    "Name the element, describe behavior, why it improves UX. 2-3 sentences. "
    "Focus on: neubrutalism, 3D, AI-native, micro-interactions."
)

CODE_PROMPT = """Write a COMPLETE single-file HTML/CSS/JS app: AI Collaboration Platform 2026.

REQUIREMENTS — ALL must work:
1. Dark theme with 2026 aesthetics: neubrutalism (bold borders, shadows), 3D elements (transform: perspective), glassmorphism 2.0 (backdrop-filter, border gradients)
2. Sidebar with 3D icons: Dashboard, Projects, Chat, Files, Settings
3. Click sidebar → switch main view with smooth 3D transitions
4. Dashboard: 4 stat cards (3D hover), project table (10 rows with sorting), activity feed
5. Chat: message list + input that ADDS messages on Enter, AI typing indicator
6. Files: folder tree left, file grid right with 3D hover, grid/list toggle with animation
7. Projects: Kanban 3 columns (To Do, In Progress, Done), drag-drop cards with 3D effects
8. Top bar: search (filters projects live with AI suggestions), bell with dropdown, avatar menu with 3D
9. Theme toggle dark/light with CSS variables + localStorage + smooth transition
10. Responsive: sidebar collapses to hamburger below 768px with 3D animation
11. MICRO-INTERACTIONS: hover scaling, click ripple, smooth transitions, loading skeletons
12. AI CHAT: floating AI assistant in bottom-right corner with 3D bubble
13. 3D ELEMENTS: cards with perspective transform, 3D flip animations, depth layers

RULES:
- ONE file, NO external libs (no CDN)
- CSS Grid + Flexbox + 3D transforms
- Inline mock data: 15 projects, 10 messages, 15 files
- All buttons have hover/active states with 3D effects
- Smooth 0.3s transitions
- Use CSS custom properties for theming
- Add neubrutalist elements: thick borders, bold shadows, offset elements

Return ONLY valid HTML starting with <!DOCTYPE html>. Do NOT truncate.

Make it look like a 2026 platform: futuristic, AI-native, 3D, bold colors, neubrutalism."""
def build_gen_prompt(agent, orbital, task: str, role: dict) -> str:
    state = agent.get_state()
    sync_r = 0.0
    if hasattr(orbital, "get_mean_phase"):
        sync_r = orbital.get_mean_phase()
    return f"Sync r={sync_r:.2f} | {role['name']} | Mood={state.get('mood', 0):+.2f}\n{task}\n2-3 sentences, specific."

async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat", max_tokens: int = 1024) -> str:
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,  # Higher creativity for 2026 trends
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

async def run_all_calls(prompts: list, api_key: str, max_tokens: int = 1024) -> list:
    tasks = [call_deepseek_async(p, api_key, max_tokens=max_tokens) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)

def start_server(port: int = 8000, directory: str = "."):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def main():
    print("=" * 70)
    print("  MOLECULAR AI v7.0 — REAL UI PLATFORM v4 (2026 Trends)")
    print("  max_tokens=16384 | 10 experts | 2026 UI trends")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] set DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] Key: {api_key[:8]}...{api_key[-4:]}")

    # Simulation with more agents for diversity
    print("\n[PHASE 1] 10 agents + warm-up 800 steps...")
    sys = MolecularSystem(n_agents=10, dt=0.05, noise=0.015, sleep_every=400, k_sparse=4, exc_ratio=0.88)
    for layer in sys.orbital.layers:
        layer.coupling *= 3.0  # Stronger coupling for better sync
    for agent in sys.agents:
        agent.omega = 1.0 + random.uniform(-0.03, 0.03)

    for i in range(800):
        sys.step()
        if i % 200 == 199:
            print(f"    Step {i+1}: r={sys.order_parameter():.3f}")

    print(f"\n  Warm-up: r={sys.order_parameter():.3f}")

    # DIVERGENT for creativity
    print("\n[PHASE 2] DIVERGENT regime for creativity...")
    set_regime(sys, ConvergenceRegime.DIVERGENT)
    for _ in range(150):  # More steps for diversity
        sys.step()
    print(f"  After DIVERGENT: r={sys.order_parameter():.3f}")

    # Generation
    print("\n[PHASE 3] 10 parallel generation calls...")
    orbital = sys.orbital.layers[0].orbital
    gen_prompts = [build_gen_prompt(sys.agents[i], orbital, TASK, ROLES[i]) for i in range(10)]

    for i in range(10):
        print(f"  Agent {i} [{ROLES[i]['name']:14s}] mood={sys.agents[i].mood:+.2f}")

    t0 = time.time()
    gen_results = asyncio.run(run_all_calls(gen_prompts, api_key, max_tokens=1024))
    print(f"\n  Done in {time.time()-t0:.1f}s")

    proposals = []
    for i, res in enumerate(gen_results):
        if isinstance(res, Exception):
            print(f"  Agent {i}: [X]")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": "3D card with neubrutalist style.", "mood": sys.agents[i].mood})
        else:
            print(f"  Agent {i}: [OK] {len(res)} chars")
            proposals.append({"agent_id": i, "role": ROLES[i]['name'], "response": res, "mood": sys.agents[i].mood})

    # Orbital consensus with weighted scoring
    print("\n[PHASE 4] Orbital consensus (mood+energy+creativity)...")
    ranked = sorted(enumerate(sys.agents), key=lambda x: x[1].mood + x[1].energy + random.uniform(0, 0.2), reverse=True)
    top4_indices = [idx for idx, _ in ranked[:4]]  # Use top 4 for more diversity
    for rank, idx in enumerate(top4_indices, 1):
        a = sys.agents[idx]
        print(f"  #{rank} [{ROLES[idx]['name']:14s}] mood={a.mood:+.2f} energy={a.energy:.3f}")

    # Code generation — 16384 tokens for complete 2026 UI!
    print("\n[PHASE 5] Generating HTML/CSS/JS (max_tokens=16384)...")
    code_prompt = CODE_PROMPT + "\n\n2026 DESIGN INPUT FROM EXPERTS:\n"
    for i, idx in enumerate(top4_indices, 1):
        p = proposals[idx]
        code_prompt += f"{i}. [{p['role']}]: {p['response']}\n"
    
    code_prompt += "\nADDITIONAL 2026 TRENDS:\n"
    code_prompt += "- Neubrutalism: thick borders, bold shadows, offset elements\n"
    code_prompt += "- 3D elements: transform: perspective(), rotateX/Y, depth\n"
    code_prompt += "- Glassmorphism 2.0: border gradients, backdrop-filter\n"
    code_prompt += "- AI-native: predictive UI, auto-complete, context-aware\n"
    code_prompt += "- Micro-interactions: ripple effects, hover scaling, smooth transitions\n"
    code_prompt += "- Bold colors: neon accents, gradients, color combinations\n"

    print(f"  Prompt: {len(code_prompt)} chars")
    t0 = time.time()
    try:
        code_response = asyncio.run(call_deepseek_async(code_prompt, api_key, max_tokens=16384))
        html_code = code_response.strip()
        
        # Extract HTML if wrapped in markdown
        if "```html" in html_code:
            start = html_code.find("```html") + 7
            end = html_code.find("```", start)
            if end != -1:
                html_code = html_code[start:end].strip()
        elif "```" in html_code:
            start = html_code.find("```") + 3
            end = html_code.find("```", start)
            if end != -1:
                html_code = html_code[start:end].strip()
        elif not html_code.startswith("<"):
            start = html_code.find("<!DOCTYPE")
            if start != -1:
                html_code = html_code[start:]
        
        # Check completion quality
        if len(html_code) < 15000:
            print(f"\n  [!] WARNING: Code only {len(html_code)} chars — may be truncated!")
            print(f"      Expected ~20KB for complete 2026 UI.")
            if "</html>" not in html_code[-2000:]:
                print(f"  [!] Missing </html> — definitely truncated!")
            else:
                print(f"  [!] Code seems short but has </html> — might be compressed.")
        elif "</html>" not in html_code[-2000:]:
            print(f"\n  [!] WARNING: Missing </html> — code may be truncated!")
            print(f"      Last 500 chars: {html_code[-500:]}")
        else:
            print(f"  [OK] Complete code: {len(html_code)} chars in {time.time()-t0:.1f}s")
            
        # Check for key features
        if "neubrutal" in html_code.lower() or "brutal" in html_code.lower():
            print(f"  [OK] Neubrutalism detected")
        if "3d" in html_code.lower() or "perspective" in html_code.lower():
            print(f"  [OK] 3D elements detected")
        if "glass" in html_code.lower() or "backdrop-filter" in html_code.lower():
            print(f"  [OK] Glassmorphism detected")
            
    except Exception as e:
        print(f"  [X] Failed: {e}")
        return

    # Save
    print("\n[PHASE 6] Saving & serving...")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, "platform_ui_2026.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"  [OK] Saved: {html_path}")

    # Design log with details
    design_path = os.path.join(output_dir, "ui_design_decisions_2026.txt")
    with open(design_path, "w", encoding="utf-8") as f:
        f.write("UI DESIGN DECISIONS (2026 Trends)\n" + "=" * 50 + "\n\n")
        f.write("TRENDS IMPLEMENTED:\n")
        f.write("- Neubrutalism: bold borders, heavy shadows, offset elements\n")
        f.write("- 3D Elements: perspective transforms, depth layers\n")
        f.write("- Glassmorphism 2.0: border gradients, backdrop blur\n")
        f.write("- AI-Native: predictive UI, context-aware components\n")
        f.write("- Micro-interactions: ripple, hover, transitions\n\n")
        
        f.write("TOP 4 EXPERT CONTRIBUTIONS:\n")
        f.write("-" * 40 + "\n")
        for i, idx in enumerate(top4_indices, 1):
            p = proposals[idx]
            f.write(f"#{i} [{p['role']}] (mood={p['mood']:+.2f})\n{p['response']}\n\n")

        f.write("\nALL EXPERT RESPONSES:\n")
        f.write("-" * 40 + "\n")
        for i, p in enumerate(proposals):
            f.write(f"[{i}] {p['role']}\n{p['response']}\n\n")
            
    print(f"  [OK] Log: {design_path}")

    # Server
    port = 8000
    try:
        httpd = start_server(port, output_dir)
        print(f"\n  🚀 http://localhost:{port}/platform_ui_2026.html")
        print(f"  🚀 http://localhost:{port}/index.html")
        print(f"\n  Press Ctrl+C to stop")
        try:
            webbrowser.open(f"http://localhost:{port}/platform_ui_2026.html")
        except:
            pass
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopped")
    except OSError:
        httpd = start_server(port+1, output_dir)
        print(f"\n  🚀 http://localhost:{port+1}/platform_ui_2026.html")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()