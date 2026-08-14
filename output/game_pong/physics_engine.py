from dataclasses import dataclass
from typing import Tuple
import math

@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x / scalar, self.y / scalar)

    def dot(self, other: 'Vector2D') -> float:
        return self.x * other.x + self.y * other.y

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self) -> 'Vector2D':
        length = self.length()
        if length == 0:
            return Vector2D(0, 0)
        return self / length

@dataclass
class Ball:
    position: Vector2D
    velocity: Vector2D
    radius: float

    def move(self, dt: float) -> None:
        self.position += self.velocity * dt

@dataclass
class Paddle:
    position: Vector2D
    width: float
    height: float
    speed: float

    def move_up(self, dt: float) -> None:
        self.position.y -= self.speed * dt

    def move_down(self, dt: float) -> None:
        self.position.y += self.speed * dt

    def get_bounds(self) -> Tuple[float, float, float, float]:
        left = self.position.x - self.width / 2
        right = self.position.x + self.width / 2
        top = self.position.y - self.height / 2
        bottom = self.position.y + self.height / 2
        return left, right, top, bottom

class PhysicsEngine:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def update(self, ball: Ball, paddle_left: Paddle, paddle_right: Paddle, dt: float) -> None:
        """Update ball position and handle collisions with walls and paddles."""
        ball.move(dt)
        self._handle_wall_collision(ball)
        self._handle_paddle_collision(ball, paddle_left)
        self._handle_paddle_collision(ball, paddle_right)

    def _handle_wall_collision(self, ball: Ball) -> None:
        """Bounce ball off top and bottom walls."""
        if ball.position.y - ball.radius < 0:
            ball.position.y = ball.radius
            ball.velocity.y = abs(ball.velocity.y)
        elif ball.position.y + ball.radius > self.height:
            ball.position.y = self.height - ball.radius
            ball.velocity.y = -abs(ball.velocity.y)

    def _handle_paddle_collision(self, ball: Ball, paddle: Paddle) -> None:
        """Detect collision with a paddle and reflect ball velocity."""
        left, right, top, bottom = paddle.get_bounds()
        # Expand paddle bounds by ball radius for collision detection
        expanded_left = left - ball.radius
        expanded_right = right + ball.radius
        expanded_top = top - ball.radius
        expanded_bottom = bottom + ball.radius

        if (expanded_left <= ball.position.x <= expanded_right and
            expanded_top <= ball.position.y <= expanded_bottom):
            # Determine which side of the paddle was hit
            overlap_left = ball.position.x - expanded_left
            overlap_right = expanded_right - ball.position.x
            overlap_top = ball.position.y - expanded_top
            overlap_bottom = expanded_bottom - ball.position.y

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left or min_overlap == overlap_right:
                # Horizontal collision (side of paddle)
                ball.velocity.x = -ball.velocity.x
                # Adjust position to avoid sticking
                if overlap_left < overlap_right:
                    ball.position.x = expanded_left
                else:
                    ball.position.x = expanded_right
            else:
                # Vertical collision (top or bottom of paddle)
                ball.velocity.y = -ball.velocity.y
                if overlap_top < overlap_bottom:
                    ball.position.y = expanded_top
                else:
                    ball.position.y = expanded_bottom

            # Add a small speed boost to keep game interesting (optional)
            # ball.velocity *= 1.01
