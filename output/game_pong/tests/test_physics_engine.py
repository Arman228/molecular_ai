import math
from physics_engine import PhysicsEngine, Ball, Paddle, Vector2D

def test_ball_moves():
    ball = Ball(Vector2D(0, 0), Vector2D(1, 0), 1)
    ball.move(1.0)
    assert ball.position.x == 1.0
    assert ball.position.y == 0.0

def test_wall_collision_top():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 0), Vector2D(0, -1), 1)
    engine._handle_wall_collision(ball)
    assert ball.position.y == 1
    assert ball.velocity.y == 1

def test_wall_collision_bottom():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 50), Vector2D(0, 1), 1)
    engine._handle_wall_collision(ball)
    assert ball.position.y == 49
    assert ball.velocity.y == -1

def test_paddle_collision_left_side():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(10, 25), Vector2D(-1, 0), 1)
    paddle = Paddle(Vector2D(10, 25), 4, 20, 5)
    engine._handle_paddle_collision(ball, paddle)
    assert ball.velocity.x == 1
    assert ball.position.x == 10 - 2 - 1  # left edge minus radius

def test_paddle_collision_right_side():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(90, 25), Vector2D(1, 0), 1)
    paddle = Paddle(Vector2D(90, 25), 4, 20, 5)
    engine._handle_paddle_collision(ball, paddle)
    assert ball.velocity.x == -1
    assert ball.position.x == 90 + 2 + 1

def test_paddle_collision_top():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 10), Vector2D(0, -1), 1)
    paddle = Paddle(Vector2D(50, 10), 20, 4, 5)
    engine._handle_paddle_collision(ball, paddle)
    assert ball.velocity.y == 1
    assert ball.position.y == 10 - 2 - 1

def test_paddle_collision_bottom():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 40), Vector2D(0, 1), 1)
    paddle = Paddle(Vector2D(50, 40), 20, 4, 5)
    engine._handle_paddle_collision(ball, paddle)
    assert ball.velocity.y == -1
    assert ball.position.y == 40 + 2 + 1

def test_update_no_collision():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 25), Vector2D(1, 0), 1)
    paddle_left = Paddle(Vector2D(0, 25), 4, 20, 5)
    paddle_right = Paddle(Vector2D(100, 25), 4, 20, 5)
    engine.update(ball, paddle_left, paddle_right, 1.0)
    assert ball.position.x == 51
    assert ball.position.y == 25

def test_update_wall_bounce():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(50, 1), Vector2D(0, -1), 1)
    paddle_left = Paddle(Vector2D(0, 25), 4, 20, 5)
    paddle_right = Paddle(Vector2D(100, 25), 4, 20, 5)
    engine.update(ball, paddle_left, paddle_right, 1.0)
    assert ball.position.y == 1
    assert ball.velocity.y == 1

def test_update_paddle_bounce():
    engine = PhysicsEngine(100, 50)
    ball = Ball(Vector2D(10, 25), Vector2D(-1, 0), 1)
    paddle_left = Paddle(Vector2D(10, 25), 4, 20, 5)
    paddle_right = Paddle(Vector2D(90, 25), 4, 20, 5)
    engine.update(ball, paddle_left, paddle_right, 1.0)
    assert ball.velocity.x == 1

def test_vector_operations():
    v1 = Vector2D(1, 2)
    v2 = Vector2D(3, 4)
    assert v1 + v2 == Vector2D(4, 6)
    assert v1 - v2 == Vector2D(-2, -2)
    assert v1 * 2 == Vector2D(2, 4)
    assert v1 / 2 == Vector2D(0.5, 1)
    assert v1.dot(v2) == 11
    assert v1.length() == math.sqrt(5)
    assert v1.normalized() == Vector2D(1/math.sqrt(5), 2/math.sqrt(5))

def test_paddle_move():
    paddle = Paddle(Vector2D(0, 25), 4, 20, 5)
    paddle.move_up(1.0)
    assert paddle.position.y == 20
    paddle.move_down(1.0)
    assert paddle.position.y == 25

def test_paddle_bounds():
    paddle = Paddle(Vector2D(10, 25), 4, 20, 5)
    left, right, top, bottom = paddle.get_bounds()
    assert left == 8
    assert right == 12
    assert top == 15
    assert bottom == 35
