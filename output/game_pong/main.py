#!/usr/bin/env python3
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
        print(f"\nScore: {self.score_left} - {self.score_right}")
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
    print("\nGame Architect Demo Complete!")
