from dataclasses import dataclass, field
from typing import Tuple, Optional
import math

@dataclass
class Paddle:
    x: float
    y: float
    width: float = 10.0
    height: float = 80.0
    speed: float = 5.0

    def move_up(self) -> None:
        self.y -= self.speed

    def move_down(self, max_y: float) -> None:
        self.y += self.speed
        if self.y + self.height > max_y:
            self.y = max_y - self.height

    def clamp(self, min_y: float, max_y: float) -> None:
        if self.y < min_y:
            self.y = min_y
        if self.y + self.height > max_y:
            self.y = max_y - self.height

@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 5.0

    def move(self) -> None:
        self.x += self.vx
        self.y += self.vy

    def bounce_vertical(self) -> None:
        self.vy = -self.vy

    def bounce_horizontal(self) -> None:
        self.vx = -self.vx

@dataclass
class GameState:
    width: int
    height: int
    left_paddle: Paddle
    right_paddle: Paddle
    ball: Ball
    left_score: int = 0
    right_score: int = 0
    max_score: int = 10
    game_over: bool = False
    winner: Optional[str] = None

    def reset_ball(self, direction: int = 1) -> None:
        self.ball.x = self.width / 2
        self.ball.y = self.height / 2
        speed = 5.0
        angle = math.radians(45)
        self.ball.vx = direction * speed * math.cos(angle)
        self.ball.vy = speed * math.sin(angle)

    def update(self, left_up: bool, left_down: bool, right_up: bool, right_down: bool) -> None:
        if self.game_over:
            return

        # Move paddles
        if left_up:
            self.left_paddle.move_up()
        if left_down:
            self.left_paddle.move_down(self.height)
        self.left_paddle.clamp(0, self.height)

        if right_up:
            self.right_paddle.move_up()
        if right_down:
            self.right_paddle.move_down(self.height)
        self.right_paddle.clamp(0, self.height)

        # Move ball
        self.ball.move()

        # Top/bottom walls
        if self.ball.y - self.ball.radius < 0:
            self.ball.y = self.ball.radius
            self.ball.bounce_vertical()
        elif self.ball.y + self.ball.radius > self.height:
            self.ball.y = self.height - self.ball.radius
            self.ball.bounce_vertical()

        # Paddle collisions
        self._check_paddle_collision(self.left_paddle, is_left=True)
        self._check_paddle_collision(self.right_paddle, is_left=False)

        # Scoring
        if self.ball.x - self.ball.radius < 0:
            self.right_score += 1
            self._check_win()
            if not self.game_over:
                self.reset_ball(direction=-1)
        elif self.ball.x + self.ball.radius > self.width:
            self.left_score += 1
            self._check_win()
            if not self.game_over:
                self.reset_ball(direction=1)

    def _check_paddle_collision(self, paddle: Paddle, is_left: bool) -> None:
        ball = self.ball
        # Only check if ball is moving towards the paddle
        if is_left and ball.vx >= 0:
            return
        if not is_left and ball.vx <= 0:
            return

        # Check if ball overlaps paddle horizontally
        if is_left:
            if ball.x - ball.radius > paddle.x + paddle.width:
                return
            if ball.x + ball.radius < paddle.x:
                return
        else:
            if ball.x + ball.radius < paddle.x:
                return
            if ball.x - ball.radius > paddle.x + paddle.width:
                return

        # Check vertical overlap
        if ball.y + ball.radius < paddle.y or ball.y - ball.radius > paddle.y + paddle.height:
            return

        # Collision! Reflect and adjust position
        if is_left:
            ball.x = paddle.x + paddle.width + ball.radius
        else:
            ball.x = paddle.x - ball.radius
        ball.bounce_horizontal()

        # Adjust angle based on hit position
        relative_intersect = (ball.y - (paddle.y + paddle.height / 2)) / (paddle.height / 2)
        relative_intersect = max(-1.0, min(1.0, relative_intersect))
        max_angle = math.radians(60)
        angle = relative_intersect * max_angle
        speed = math.hypot(ball.vx, ball.vy)
        ball.vx = speed * math.cos(angle) * (1 if is_left else -1)
        ball.vy = speed * math.sin(angle)

    def _check_win(self) -> None:
        if self.left_score >= self.max_score:
            self.game_over = True
            self.winner = 'left'
        elif self.right_score >= self.max_score:
            self.game_over = True
            self.winner = 'right'

class PongGameLoop:
    """Main game loop controller for Pong."""

    def __init__(self, width: int = 800, height: int = 600, max_score: int = 10):
        self.width = width
        self.height = height
        self.max_score = max_score
        self.state = self._create_initial_state()

    def _create_initial_state(self) -> GameState:
        paddle_width = 10.0
        paddle_height = 80.0
        left_paddle = Paddle(x=20.0, y=(self.height - paddle_height) / 2, width=paddle_width, height=paddle_height)
        right_paddle = Paddle(x=self.width - 20.0 - paddle_width, y=(self.height - paddle_height) / 2, width=paddle_width, height=paddle_height)
        ball = Ball(x=self.width / 2, y=self.height / 2, vx=5.0, vy=0.0)
        state = GameState(width=self.width, height=self.height, left_paddle=left_paddle, right_paddle=right_paddle, ball=ball, max_score=self.max_score)
        state.reset_ball(direction=1)
        return state

    def step(self, left_up: bool = False, left_down: bool = False, right_up: bool = False, right_down: bool = False) -> GameState:
        """Advance the game by one frame."""
        self.state.update(left_up, left_down, right_up, right_down)
        return self.state

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.state = self._create_initial_state()
