#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — ORBITAL SYMPHONY GAME v1.
Mini-game showcasing all platform capabilities:
- Kuramoto synchronization (visualized as dancing particles)
- Multi-agent consensus (musical harmony)
- Adaptive difficulty (ConvergenceRegime switching)
- SensorFusion voting (pattern recognition)
- Live LLM integration (creative puzzle generation)

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_orbital_symphony" "examples\demo_orbital_symphony.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_orbital_symphony.py
"""

import os
import sys
import random
import asyncio
import time
import json
import math
import http.server
import socketserver
import threading
import webbrowser
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Game roles - each with specific expertise
GAME_ROLES = [
    {"name": "Rhythm_Master", "persona": "Expert in rhythmic patterns, syncopation, and tempo. Creates engaging beat sequences."},
    {"name": "Melody_Architect", "persona": "Creates memorable melodies. Understands music theory, chord progressions, and harmony."},
    {"name": "Harmony_Expert", "persona": "Specializes in harmonic structures. Knows counterpoint, modulations, and voice leading."},
    {"name": "Puzzle_Designer", "persona": "Designs engaging puzzles. Creates clear rules, progressive difficulty, and satisfying solutions."},
    {"name": "UI_Artist", "persona": "Visual design expert. Creates beautiful, intuitive, and responsive game interfaces."},
    {"name": "Game_Mechanic", "persona": "Gameplay systems designer. Balances challenge, reward, and player engagement."},
    {"name": "Sound_Engineer", "persona": "Audio specialist. Creates satisfying sound effects, ambient layers, and feedback."},
    {"name": "AI_Director", "persona": "Dynamic difficulty adjustment. Monitors player performance and adapts challenge."},
    {"name": "Storyteller", "persona": "Narrative designer. Weaves engaging story elements and progression arcs."},
    {"name": "Performance_Expert", "persona": "Optimization and smooth experience. Ensures 60fps, responsive controls, and polish."},
]

GAME_TASK = (
    "Design ONE core mechanic for 'Orbital Symphony' - a musical puzzle game "
    "where players synchronize orbiting particles to create harmony. "
    "Describe: mechanic name, how it works (2-3 sentences), why it's fun, "
    "and how it demonstrates synchronization or consensus."
)

GAME_PROMPT = """Create a COMPLETE single-file HTML/CSS/JS GAME: "Orbital Symphony"

GAME CONCEPT:
A musical puzzle game where players arrange orbiting particles to create harmonic patterns.
Inspired by Kuramoto synchronization - particles naturally sync up when correctly positioned.

CORE MECHANICS:
1. 10-15 particles orbiting a central point at different speeds
2. Player drags particles to adjust their orbits (radius + speed)
3. Goal: Arrange particles so they synchronize (phase alignment)
4. Visual feedback: particles glow brighter when synced
5. Audio feedback: each particle plays a note when synced
6. Score based on: sync accuracy + speed + creativity

REQUIREMENTS — ALL must work:
1. Canvas-based rendering (no DOM for particles)
2. Physics: each particle has: angle, speed, radius, phase_offset, note
3. Drag interaction: click and drag particle to adjust orbit
4. Sync detection: particles with similar phase → glow + play note
5. Score display: real-time sync score (0-100%)
6. Levels: 3 levels with increasing complexity (3, 5, 7 particles)
7. Visual style: dark space theme with nebula background
8. Particle colors: gradient from blue to purple to pink based on sync
9. Particle trails: 20-frame trailing effect
10. UI: level selector, score, timer, instructions

ADVANCED FEATURES (showcasing platform capabilities):
11. "Synchronization Wave" - when all particles sync, trigger visual/audio celebration
12. "Consensus Mode" - particles vote on which note to play (major/minor chord)
13. "Regime Switch" - player can toggle between LINEAR (stable), CRITICAL (balanced), DIVERGENT (chaotic)
14. "Sensor Fusion" - particles with high confidence have larger glow
15. "Resonance Detection" - highlight particles that are out of sync

INTERACTION:
- Click particle → select it
- Drag left/right → change orbit radius
- Drag up/down → change speed
- Double-click → reset particle to random position
- Keyboard: Space to pause/resume

RULES:
- ONE file, NO external libs
- Use Canvas API, no DOM for game objects
- Smooth 60fps with requestAnimationFrame
- Inline all data, no external assets
- Responsive: works on different screen sizes
- Clean, commented code

Return ONLY valid HTML starting with <!DOCTYPE html>. Do NOT truncate.

Make it immersive, beautiful, and truly showcase synchronized intelligence."""

def build_gen_prompt(agent, orbital, task: str, role: dict) -> str:
    """Build generation prompt with orbital context."""
    state = agent.get_state()
    sync_r = 0.0
    if hasattr(orbital, "get_mean_phase"):
        sync_r = orbital.get_mean_phase()
    
    return f"""SYNC CONTEXT:
Orbital sync: r={sync_r:.3f}
Agent: {role['name']} (mood={state.get('mood', 0):+.2f}, energy={state.get('energy', 0):.2f})

GAME MECHANIC TASK:
{task}

Provide 2-3 sentences describing your mechanic. Be specific and creative."""

async def call_deepseek_async(prompt: str, api_key: str, model: str = "deepseek-chat", max_tokens: int = 2048) -> str:
    """Async call to DeepSeek API."""
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,  # Higher for creative game design
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

async def run_all_calls(prompts: list, api_key: str, max_tokens: int = 2048) -> list:
    """Run multiple LLM calls in parallel."""
    tasks = [call_deepseek_async(p, api_key, max_tokens=max_tokens) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)

def start_server(port: int = 8000, directory: str = "."):
    """Start simple HTTP server for serving the game."""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def simulate_orbital_sync(agents: List, steps: int = 500) -> Dict:
    """Simulate orbital synchronization for game inspiration."""
    history = []
    for i in range(steps):
        if hasattr(agents[0], 'step'):
            for agent in agents:
                if hasattr(agent, 'step'):
                    agent.step()
        if i % 20 == 0:
            r = 0.0
            if hasattr(agents[0], 'orbital'):
                r = agents[0].orbital.get_mean_phase()
            history.append(r)
    return {
        'final_r': history[-1] if history else 0.0,
        'history': history,
        'steps': steps
    }

def main():
    print("=" * 70)
    print("  MOLECULAR AI v7.0 — ORBITAL SYMPHONY GAME")
    print("  Showcasing all platform capabilities through gameplay")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] set DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] API Key: {api_key[:8]}...{api_key[-4:]}")

    # Initialize system with agents
    print("\n[PHASE 1] Initializing 10 game designer agents...")
    system = MolecularSystem(
        n_agents=10, 
        dt=0.05, 
        noise=0.02, 
        sleep_every=400, 
        k_sparse=4, 
        exc_ratio=0.85
    )
    
    # Enhanced coupling for better creative sync
    for layer in system.orbital.layers:
        layer.coupling *= 2.8
    
    # Diverse initial frequencies
    for agent in system.agents:
        agent.omega = 1.0 + random.uniform(-0.04, 0.04)

    # Warm-up for creative alignment
    print("\n[PHASE 2] Warm-up: 800 steps of orbital synchronization...")
    for i in range(800):
        system.step()
        if i % 200 == 199:
            r = system.order_parameter()
            print(f"    Step {i+1}: r={r:.3f}")

    sync_r = system.order_parameter()
    print(f"\n  Warm-up complete: r={sync_r:.3f}")

    # Switch to divergent regime for maximum creativity
    print("\n[PHASE 3] DIVERGENT regime: unlocking creativity...")
    set_regime(system, ConvergenceRegime.DIVERGENT)
    for i in range(200):
        system.step()
        if i % 50 == 49:
            r = system.order_parameter()
            print(f"    Divergent step {i+1}: r={r:.3f}")

    print(f"  Divergent complete: r={system.order_parameter():.3f}")

    # Generate game mechanics
    print("\n[PHASE 4] Generating 10 game mechanics in parallel...")
    orbital = system.orbital.layers[0].orbital
    gen_prompts = [
        build_gen_prompt(system.agents[i], orbital, GAME_TASK, GAME_ROLES[i]) 
        for i in range(10)
    ]

    # Show agent states
    for i in range(10):
        agent_state = system.agents[i].get_state()
        print(f"  Agent {i} [{GAME_ROLES[i]['name']:16s}] mood={agent_state.get('mood', 0):+.2f} energy={agent_state.get('energy', 0):.2f}")

    # Parallel LLM calls
    t0 = time.time()
    gen_results = asyncio.run(run_all_calls(gen_prompts, api_key, max_tokens=2048))
    elapsed = time.time() - t0
    print(f"\n  Generation complete: {elapsed:.1f}s")

    # Process results
    mechanics = []
    for i, res in enumerate(gen_results):
        if isinstance(res, Exception):
            print(f"  Agent {i}: [X] {str(res)[:50]}")
            mechanics.append({
                "agent_id": i,
                "role": GAME_ROLES[i]['name'],
                "mechanic": "Orbital Resonance: Particles sync when aligned",
                "mood": system.agents[i].mood,
                "error": True
            })
        else:
            print(f"  Agent {i}: [OK] {len(res)} chars")
            mechanics.append({
                "agent_id": i,
                "role": GAME_ROLES[i]['name'],
                "mechanic": res.strip(),
                "mood": system.agents[i].mood,
                "error": False
            })

    # Orbital consensus to pick top mechanics
    print("\n[PHASE 5] Orbital consensus: selecting top 4 mechanics...")
    ranked = sorted(
        enumerate(system.agents), 
        key=lambda x: x[1].mood + x[1].energy + random.uniform(0, 0.3), 
        reverse=True
    )
    top_indices = [idx for idx, _ in ranked[:4]]
    
    print("  Top selected mechanics:")
    for rank, idx in enumerate(top_indices, 1):
        m = mechanics[idx]
        print(f"    #{rank} [{m['role']:16s}] mood={m['mood']:+.2f} → {m['mechanic'][:60]}...")

    # Build design brief for game
    print("\n[PHASE 6] Generating complete game (max_tokens=16384)...")
    design_brief = GAME_PROMPT + "\n\nTOP MECHANICS TO INCORPORATE:\n"
    for i, idx in enumerate(top_indices, 1):
        m = mechanics[idx]
        design_brief += f"{i}. {m['role']}: {m['mechanic']}\n"
    
    design_brief += "\nADDITIONAL INSPIRATION FROM ALL AGENTS:\n"
    for i, m in enumerate(mechanics[:3]):  # Include top 3 more for diversity
        if not m['error']:
            design_brief += f"- {m['role']}: {m['mechanic'][:100]}...\n"

    print(f"  Design brief: {len(design_brief)} chars")
    
    # Generate the game
    t0 = time.time()
    try:
        game_response = asyncio.run(call_deepseek_async(
            design_brief, 
            api_key, 
            max_tokens=16384
        ))
        game_code = game_response.strip()
        
        # Extract HTML if wrapped
        if "```html" in game_code:
            start = game_code.find("```html") + 7
            end = game_code.find("```", start)
            if end != -1:
                game_code = game_code[start:end].strip()
        elif "```" in game_code:
            start = game_code.find("```") + 3
            end = game_code.find("```", start)
            if end != -1:
                game_code = game_code[start:end].strip()
        elif not game_code.startswith("<"):
            start = game_code.find("<!DOCTYPE")
            if start != -1:
                game_code = game_code[start:]
        
        # Quality checks
        print(f"\n  Game code: {len(game_code)} chars in {time.time()-t0:.1f}s")
        
        if len(game_code) < 5000:
            print(f"    [!] WARNING: Game seems incomplete (expected 15-25KB)")
            print(f"    [!] Last 200 chars: {game_code[-200:]}")
        elif "</html>" not in game_code[-2000:]:
            print(f"    [!] WARNING: Missing closing </html> tag")
        else:
            print(f"    [OK] Complete game generated!")
            
        # Check for key features
        features = {
            "canvas": "canvas" in game_code.lower(),
            "particles": "particle" in game_code.lower(),
            "orbit": "orbit" in game_code.lower(),
            "sync": "sync" in game_code.lower(),
            "score": "score" in game_code.lower(),
        }
        print("    Features detected:")
        for feature, present in features.items():
            print(f"      {'✓' if present else '✗'} {feature}")
            
    except Exception as e:
        print(f"  [X] Game generation failed: {e}")
        return

    # Save game
    print("\n[PHASE 7] Saving and serving the game...")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Main game file
    game_path = os.path.join(output_dir, "orbital_symphony.html")
    with open(game_path, "w", encoding="utf-8") as f:
        f.write(game_code)

    # Also save as index
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(game_code)

    print(f"  [OK] Game saved: {game_path}")

    # Save design log
    log_path = os.path.join(output_dir, "game_design_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("ORBITAL SYMPHONY - GAME DESIGN LOG\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("PLATFORM CAPABILITIES DEMONSTRATED:\n")
        f.write("- Kuramoto Synchronization: Particle phase alignment\n")
        f.write("- Multi-Agent Consensus: Harmonic note selection\n")
        f.write("- SensorFusion: Confidence-based glow effects\n")
        f.write("- ConvergenceRegime: LINEAR/CRITICAL/DIVERGENT modes\n")
        f.write("- Live LLM: Generated creative mechanics\n\n")
        
        f.write("TOP 4 MECHANICS (Orbital Consensus):\n")
        f.write("-" * 40 + "\n")
        for i, idx in enumerate(top_indices, 1):
            m = mechanics[idx]
            f.write(f"#{i} {m['role']} (mood={m['mood']:+.2f})\n")
            f.write(f"{m['mechanic']}\n\n")
        
        f.write("ALL GENERATED MECHANICS:\n")
        f.write("-" * 40 + "\n")
        for i, m in enumerate(mechanics):
            f.write(f"[{i}] {m['role']}\n")
            if m.get('error'):
                f.write("  [ERROR]\n")
            else:
                f.write(f"  {m['mechanic']}\n")
            f.write("\n")
        
        f.write("ORBITAL SYNCHRONIZATION DATA:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Final sync r: {sync_r:.3f}\n")
        f.write(f"Number of agents: 10\n")
        f.write(f"Warm-up steps: 800\n")
        f.write(f"Divergent steps: 200\n\n")
        
        f.write("2026 GAME TRENDS INCORPORATED:\n")
        f.write("- Immersive audio-visual experience\n")
        f.write("- AI-generated content\n")
        f.write("- Adaptive difficulty\n")
        f.write("- Social/competitive elements\n")
        f.write("- Beautiful visual design\n")

    print(f"  [OK] Design log: {log_path}")

    # Start server
    port = 8000
    print(f"\n  🚀 Serving game at http://localhost:{port}/orbital_symphony.html")
    print(f"  🚀 Also available at http://localhost:{port}/index.html")
    
    try:
        httpd = start_server(port, output_dir)
        try:
            webbrowser.open(f"http://localhost:{port}/orbital_symphony.html")
        except:
            pass
        
        print(f"\n  🎮 Game ready! Press Ctrl+C to stop")
        print(f"  📊 Design decisions logged in: {log_path}")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopping server...")
    except OSError:
        port = 8001
        httpd = start_server(port, output_dir)
        print(f"\n  Port 8000 busy, using {port}")
        webbrowser.open(f"http://localhost:{port}/orbital_symphony.html")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()