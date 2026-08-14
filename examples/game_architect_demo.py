#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Architect v1 — Molecular AI creates a game via orbital consensus.
Agents: GameLoop, Physics, Renderer, Input, StateManager.
They sync phases, generate modules, vote on API contracts.
"""

import os
import sys
import random
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.auto_skills import AutoSkillEngine, SkillGapDetector
from core.persistence import SkillRegistryPersistence


# Game components as "agents" in orbital space
GAME_COMPONENTS = [
    "GameLoop",          # main loop, FPS, delta-time
    "PhysicsEngine",     # collision, velocity, gravity
    "Renderer",          # draw sprites, backgrounds, HUD
    "InputHandler",      # keyboard, mouse, events
    "StateManager",      # menu, play, pause, game-over
]

# Seed skills for game development
GAME_SEED = {
    "GameLoop": {
        "name": "GameLoop",
        "category": "GameDev",
        "description": "Main game loop with FPS control and delta-time",
        "complexity": 5,
        "code": "",
        "tests": "",
        "keywords": ["game", "loop", "fps", "delta", "tick"],
        "level": 0.8,
        "seed": True,
    },
    "CollisionDetection": {
        "name": "CollisionDetection",
        "category": "GameDev",
        "description": "AABB and circle collision detection for 2D games",
        "complexity": 6,
        "code": "",
        "tests": "",
        "keywords": ["collision", "aabb", "circle", "physics", "2d"],
        "level": 0.7,
        "seed": True,
    },
    "SpriteRenderer": {
        "name": "SpriteRenderer",
        "category": "GameDev",
        "description": "2D sprite rendering with layers and camera",
        "complexity": 7,
        "code": "",
        "tests": "",
        "keywords": ["sprite", "render", "2d", "camera", "layer"],
        "level": 0.6,
        "seed": True,
    },
}


def simulate_component_generation(engine, component: str, game_type: str) -> dict:
    """
    Simulate one game component generation.
    In real mode: would call DeepSeek LLM.
    In demo mode: returns mock implementation.
    """
    task = f"Implement {component} for {game_type} game"

    # Check seed
    cand = engine.run_lifecycle(task)
    if cand:
        return {
            "name": cand.name,
            "code": cand.code,
            "tests": cand.tests,
            "source": "LLM",
        }

    # Fallback: mock implementation
    mocks = {
        "GameLoop": {
            "code": '''import time

class GameLoop:
    """Main game loop with FPS control."""
    def __init__(self, fps: int = 60):
        self.fps = fps
        self.dt = 1.0 / fps
        self.running = False
        self.tick = 0

    def start(self, update_fn, render_fn):
        self.running = True
        last = time.time()
        while self.running:
            now = time.time()
            self.dt = now - last
            last = now
            update_fn(self.dt)
            render_fn()
            self.tick += 1
            sleep_time = (1.0 / self.fps) - self.dt
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self.running = False
''',
            "tests": '''def test_game_loop_init():
    gl = GameLoop(fps=30)
    assert gl.fps == 30
    assert gl.dt == 1.0 / 30

def test_game_loop_stop():
    gl = GameLoop()
    gl.stop()
    assert gl.running is False
''',
        },
        "PhysicsEngine": {
            "code": '''from typing import List, Tuple

class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Body:
    def __init__(self, x, y, w, h, vx=0, vy=0):
        self.pos = Vec2(x, y)
        self.size = Vec2(w, h)
        self.vel = Vec2(vx, vy)

    def rect(self):
        return (self.pos.x, self.pos.y, self.size.x, self.size.y)

class PhysicsEngine:
    """Simple 2D physics with AABB collision."""
    def __init__(self, gravity: float = 980.0):
        self.gravity = gravity
        self.bodies: List[Body] = []

    def add_body(self, body: Body):
        self.bodies.append(body)

    def step(self, dt: float):
        for b in self.bodies:
            b.vel.y += self.gravity * dt
            b.pos.x += b.vel.x * dt
            b.pos.y += b.vel.y * dt

    def check_aabb(self, a: Body, b: Body) -> bool:
        ax, ay, aw, ah = a.rect()
        bx, by, bw, bh = b.rect()
        return (ax < bx + bw and ax + aw > bx and
                ay < by + bh and ay + ah > by)

    def resolve_collisions(self):
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                if self.check_aabb(self.bodies[i], self.bodies[j]):
                    # Simple elastic bounce
                    self.bodies[i].vel.y *= -0.9
                    self.bodies[j].vel.y *= -0.9
''',
            "tests": '''def test_aabb_collision():
    pe = PhysicsEngine()
    a = Body(0, 0, 10, 10)
    b = Body(5, 5, 10, 10)
    pe.add_body(a)
    pe.add_body(b)
    assert pe.check_aabb(a, b) is True

def test_no_collision():
    pe = PhysicsEngine()
    a = Body(0, 0, 10, 10)
    b = Body(100, 100, 10, 10)
    assert pe.check_aabb(a, b) is False
''',
        },
        "Renderer": {
            "code": '''from typing import List, Tuple, Optional

class Sprite:
    def __init__(self, x: float, y: float, char: str, color: str = "white"):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

class Renderer:
    """ASCII renderer for 2D games."""
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.sprites: List[Sprite] = []
        self.buffer = [[" " for _ in range(width)] for _ in range(height)]

    def add_sprite(self, sprite: Sprite):
        self.sprites.append(sprite)

    def clear(self):
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]

    def draw(self):
        self.clear()
        for s in self.sprites:
            x = int(s.x) % self.width
            y = int(s.y) % self.height
            self.buffer[y][x] = s.char
        return "\\n".join("".join(row) for row in self.buffer)

    def render_frame(self):
        frame = self.draw()
        print(frame)
''',
            "tests": '''def test_renderer_init():
    r = Renderer(10, 5)
    assert r.width == 10
    assert r.height == 5

def test_draw_sprite():
    r = Renderer(10, 5)
    r.add_sprite(Sprite(2, 2, "@"))
    frame = r.draw()
    lines = frame.split("\\n")
    assert lines[2][2] == "@"
''',
        },
        "InputHandler": {
            "code": '''from typing import Dict, Callable, Optional
import sys

class InputHandler:
    """Cross-platform input handler (keyboard)."""
    def __init__(self):
        self.bindings: Dict[str, Callable] = {}
        self.pressed: set = set()

    def bind(self, key: str, callback: Callable):
        self.bindings[key.lower()] = callback

    def on_key(self, key: str):
        k = key.lower()
        self.pressed.add(k)
        if k in self.bindings:
            self.bindings[k]()

    def is_pressed(self, key: str) -> bool:
        return key.lower() in self.pressed

    def clear(self):
        self.pressed.clear()

    def get_input(self) -> Optional[str]:
        """Non-blocking input read."""
        try:
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getch().decode("utf-8", errors="ignore")
        except ImportError:
            pass
        return None
''',
            "tests": '''def test_input_binding():
    ih = InputHandler()
    called = False
    def on_space():
        nonlocal called
        called = True
    ih.bind("space", on_space)
    ih.on_key(" ")
    assert called is True

def test_is_pressed():
    ih = InputHandler()
    ih.on_key("a")
    assert ih.is_pressed("A") is True
''',
        },
        "StateManager": {
            "code": '''from typing import Dict, Callable, Optional
from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class StateManager:
    """Finite state machine for game states."""
    def __init__(self):
        self.state = GameState.MENU
        self.transitions: Dict[GameState, Dict[GameState, Callable]] = {}
        self.callbacks: Dict[GameState, Callable] = {}

    def on_enter(self, state: GameState, callback: Callable):
        self.callbacks[state] = callback

    def add_transition(self, from_state: GameState, to_state: GameState, guard: Callable = None):
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        self.transitions[from_state][to_state] = guard or (lambda: True)

    def transition(self, to_state: GameState) -> bool:
        if to_state in self.transitions.get(self.state, {}):
            guard = self.transitions[self.state][to_state]
            if guard():
                self.state = to_state
                cb = self.callbacks.get(to_state)
                if cb:
                    cb()
                return True
        return False

    def is_in(self, state: GameState) -> bool:
        return self.state == state
''',
            "tests": '''def test_state_transition():
    sm = StateManager()
    sm.add_transition(GameState.MENU, GameState.PLAYING)
    assert sm.transition(GameState.PLAYING) is True
    assert sm.is_in(GameState.PLAYING) is True

def test_invalid_transition():
    sm = StateManager()
    assert sm.transition(GameState.PLAYING) is False
    assert sm.is_in(GameState.MENU) is True
''',
        },
    }

    return mocks.get(component, {"code": "# TODO", "tests": "# TODO", "source": "MOCK"})


def main():
    print("=" * 70)
    print("GAME ARCHITECT v1")
    print("Molecular AI creates a game via orbital consensus")
    print("=" * 70)

    game_type = "Pong"
    print(f"\n>>> REQUEST: Create {game_type} game")
    print(f"    Components: {', '.join(GAME_COMPONENTS)}")

    # 1. Orbital sync — agents (components) synchronize
    print("\n[1/5] Orbital synchronization of game agents...")
    mol = MolecularSystem(
        n_agents=len(GAME_COMPONENTS),
        dt=0.05,
        noise=0.02,
        k_sparse=3,
        exc_ratio=0.85,
    )
    for layer in mol.orbital.layers:
        layer.coupling *= 2.0

    for _ in range(300):
        mol.step()
    sync_r = mol.order_parameter()
    print(f"    Sync r = {sync_r:.3f} (agents aligned on architecture)")

    # 2. Initialize engine with game seed
    print("\n[2/5] Loading game development seeds...")
    engine = AutoSkillEngine(use_llm=False)
    engine.registry.skills.update({k: v for k, v in GAME_SEED.items()})
    engine.detector = SkillGapDetector(engine.registry.skills)
    print(f"    Seed skills: {len(GAME_SEED)}")

    # Attach DeepSeek if API key available
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if api_key:
        from adapters.deepseek_adapter import attach_deepseek_to_engine
        attach_deepseek_to_engine(engine, api_key=api_key, max_cost_usd=0.50, max_requests_per_min=5)
        print("    ✅ DeepSeek LLM attached for game generation")
    else:
        print("    ⚠️  No DEEPSEEK_API_KEY — using mock templates")

    # 3. Generate each component
    print("\n[3/5] Generating game components...")
    print("-" * 70)

    game_modules = []
    for i, component in enumerate(GAME_COMPONENTS, 1):
        print(f"\n>>> COMPONENT {i}/{len(GAME_COMPONENTS)}: {component}")

        # Check if covered by seed
        task = f"Implement {component} for {game_type}"
        cand = engine.run_lifecycle(task)

        if cand:
            print(f"    → Generated via platform: {cand.name}")
            module = {
                "name": cand.name,
                "code": cand.code,
                "tests": cand.tests,
                "source": "PLATFORM",
            }
        else:
            print(f"    → Using mock (seed covers or demo mode)")
            module = simulate_component_generation(engine, component, game_type)
            module["name"] = component

        game_modules.append(module)
        print(f"    → Code: {len(module['code'])} chars | Tests: {len(module['tests'])} chars")

    # 4. Orbital consensus — check API compatibility
    print("\n" + "=" * 70)
    print("[4/5] ORBITAL CONSENSUS — API compatibility check")
    print("=" * 70)

    # Simulate consensus voting on interfaces
    votes = []
    for module in game_modules:
        # Check if module has standard interface markers
        has_init = "__init__" in module["code"]
        has_update = "update" in module["code"] or "step" in module["code"]
        has_draw = "draw" in module["code"] or "render" in module["code"]

        score = 0.0
        if has_init:
            score += 0.4
        if has_update:
            score += 0.3
        if has_draw:
            score += 0.3

        accepted = score >= 0.6
        votes.append((module["name"], score, accepted))
        status = "ACCEPTED" if accepted else "REJECTED"
        print(f"    {module['name']:<20} score={score:.2f} → {status}")

    accepted_modules = [m for m, (_, s, a) in zip(game_modules, votes) if a]
    print(f"\n    Consensus: {len(accepted_modules)}/{len(game_modules)} modules accepted")

    # 5. Assemble game
    print("\n" + "=" * 70)
    print("[5/5] ASSEMBLING GAME")
    print("=" * 70)

    # Write assembled game
    output_dir = "output/game_pong"
    os.makedirs(output_dir, exist_ok=True)

    for module in accepted_modules:
        filepath = os.path.join(output_dir, f"{module['name'].lower()}.py")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(module["code"])
        print(f"    💾 {filepath} ({len(module['code'])} chars)")

    # Write tests
    test_dir = os.path.join(output_dir, "tests")
    os.makedirs(test_dir, exist_ok=True)
    for module in accepted_modules:
        filepath = os.path.join(test_dir, f"test_{module['name'].lower()}.py")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(module["tests"])
        print(f"    💾 {filepath} ({len(module['tests'])} chars)")

    # Write main.py — glue code
    main_py = '''#!/usr/bin/env python3
"""Pong game assembled by Molecular AI Game Architect."""

import time
import os
import sys

# Add components to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gameloop import GameLoop
from physicsengine import PhysicsEngine, Body
from renderer import Renderer, Sprite
from inputhandler import InputHandler
from statemanager import StateManager, GameState


class PongGame:
    """Assembled Pong game."""
    def __init__(self):
        self.loop = GameLoop(fps=30)
        self.physics = PhysicsEngine(gravity=0.0)
        self.renderer = Renderer(width=40, height=20)
        self.input = InputHandler()
        self.state = StateManager()

        # Create paddles and ball
        self.paddle_left = Body(2, 8, 1, 4)
        self.paddle_right = Body(37, 8, 1, 4)
        self.ball = Body(20, 10, 1, 1, vx=20, vy=15)

        self.physics.add_body(self.paddle_left)
        self.physics.add_body(self.paddle_right)
        self.physics.add_body(self.ball)

        # Sprites
        self.renderer.add_sprite(Sprite(2, 8, "[", "white"))
        self.renderer.add_sprite(Sprite(37, 8, "]", "white"))
        self.renderer.add_sprite(Sprite(20, 10, "O", "white"))

        # State machine
        self.state.add_transition(GameState.MENU, GameState.PLAYING)
        self.state.add_transition(GameState.PLAYING, GameState.PAUSED)
        self.state.add_transition(GameState.PAUSED, GameState.PLAYING)
        self.state.add_transition(GameState.PLAYING, GameState.GAME_OVER)

        # Input
        self.input.bind("w", self.move_left_up)
        self.input.bind("s", self.move_left_down)
        self.input.bind("o", self.move_right_up)
        self.input.bind("l", self.move_right_down)
        self.input.bind("q", self.quit)

        self.score_left = 0
        self.score_right = 0

    def move_left_up(self):
        self.paddle_left.vel.y = -30

    def move_left_down(self):
        self.paddle_left.vel.y = 30

    def move_right_up(self):
        self.paddle_right.vel.y = -30

    def move_right_down(self):
        self.paddle_right.vel.y = 30

    def quit(self):
        self.loop.stop()

    def update(self, dt):
        self.physics.step(dt)
        self.physics.resolve_collisions()

        # Ball bounce off top/bottom
        if self.ball.pos.y <= 0 or self.ball.pos.y >= 19:
            self.ball.vel.y *= -1

        # Score
        if self.ball.pos.x <= 0:
            self.score_right += 1
            self.reset_ball()
        elif self.ball.pos.x >= 39:
            self.score_left += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball.pos.x = 20
        self.ball.pos.y = 10
        self.ball.vel.x *= -1

    def render(self):
        # Update sprite positions
        self.renderer.sprites[0].y = self.paddle_left.pos.y
        self.renderer.sprites[1].y = self.paddle_right.pos.y
        self.renderer.sprites[2].x = self.ball.pos.x
        self.renderer.sprites[2].y = self.ball.pos.y

        frame = self.renderer.draw()
        print(f"\\nScore: {self.score_left} - {self.score_right}")
        print(frame)

    def run(self):
        print("PONG by Molecular AI")
        print("Controls: W/S = left, O/L = right, Q = quit")
        self.state.transition(GameState.PLAYING)
        self.loop.start(self.update, self.render)


if __name__ == "__main__":
    game = PongGame()
    # Demo: run 10 frames
    for i in range(10):
        game.update(0.033)
        game.render()
        time.sleep(0.1)
    print("\\nGame Architect Demo Complete!")
'''

    main_path = os.path.join(output_dir, "main.py")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_py)
    print(f"    💾 {main_path} ({len(main_py)} chars)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"    Game: {game_type}")
    print(f"    Components: {len(accepted_modules)}")
    print(f"    Total code: {sum(len(m['code']) for m in accepted_modules)} chars")
    print(f"    Total tests: {sum(len(m['tests']) for m in accepted_modules)} chars")
    print(f"    Output: {output_dir}/")
    print(f"\n    To run: cd {output_dir} && python main.py")
    print("\n    The game was created by:")
    print("    - 5 agents synchronized via Kuramoto orbital consensus")
    print("    - Seed skills provided game architecture patterns")
    print("    - Orbital consensus voted on API compatibility")
    print("    - AutoSkillEngine generated missing components")


if __name__ == "__main__":
    random.seed(42)
    main()
