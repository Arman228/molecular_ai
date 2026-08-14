import pytest
from pong_game_loop import PongGameLoop, GameState, Paddle, Ball

def test_initial_state():
    game = PongGameLoop(width=800, height=600)
    state = game.state
    assert state.left_score == 0
    assert state.right_score == 0
    assert state.game_over is False
    assert state.ball.x == 400
    assert state.ball.y == 300
    assert state.left_paddle.y == 260
    assert state.right_paddle.y == 260

def test_ball_moves():
    game = PongGameLoop()
    initial_x = game.state.ball.x
    initial_y = game.state.ball.y
    game.step()
    assert game.state.ball.x != initial_x or game.state.ball.y != initial_y

def test_paddle_movement():
    game = PongGameLoop()
    initial_y = game.state.left_paddle.y
    game.step(left_up=True)
    assert game.state.left_paddle.y < initial_y
    game.step(left_down=True)
    assert game.state.left_paddle.y == initial_y  # moved back up then down

def test_paddle_clamp():
    game = PongGameLoop()
    # Move left paddle up many times
    for _ in range(100):
        game.step(left_up=True)
    assert game.state.left_paddle.y >= 0
    # Move down many times
    for _ in range(200):
        game.step(left_down=True)
    assert game.state.left_paddle.y <= game.height - game.state.left_paddle.height

def test_ball_bounces_top_bottom():
    game = PongGameLoop()
    # Set ball moving straight up
    game.state.ball.x = 400
    game.state.ball.y = 100
    game.state.ball.vx = 0
    game.state.ball.vy = -10
    for _ in range(20):
        game.step()
    assert game.state.ball.y >= 0
    # Now moving down
    assert game.state.ball.vy > 0

def test_paddle_collision_left():
    game = PongGameLoop()
    # Place ball just left of left paddle, moving right
    game.state.ball.x = game.state.left_paddle.x + game.state.left_paddle.width + game.state.ball.radius + 1
    game.state.ball.y = game.state.left_paddle.y + game.state.left_paddle.height / 2
    game.state.ball.vx = 5
    game.state.ball.vy = 0
    game.step()
    assert game.state.ball.vx < 0  # bounced

def test_paddle_collision_right():
    game = PongGameLoop()
    # Place ball just right of right paddle, moving left
    game.state.ball.x = game.state.right_paddle.x - game.state.ball.radius - 1
    game.state.ball.y = game.state.right_paddle.y + game.state.right_paddle.height / 2
    game.state.ball.vx = -5
    game.state.ball.vy = 0
    game.step()
    assert game.state.ball.vx > 0

def test_scoring_left():
    game = PongGameLoop()
    # Force ball to go past left wall
    game.state.ball.x = 0
    game.state.ball.y = 300
    game.state.ball.vx = -5
    game.state.ball.vy = 0
    game.step()
    assert game.state.right_score == 1
    assert game.state.ball.x == 400  # reset

def test_scoring_right():
    game = PongGameLoop()
    game.state.ball.x = game.width
    game.state.ball.y = 300
    game.state.ball.vx = 5
    game.state.ball.vy = 0
    game.step()
    assert game.state.left_score == 1

def test_game_over():
    game = PongGameLoop(max_score=1)
    game.state.left_score = 0
    game.state.right_score = 0
    # Force right score to win
    game.state.ball.x = 0
    game.state.ball.y = 300
    game.state.ball.vx = -5
    game.state.ball.vy = 0
    game.step()
    assert game.state.game_over is True
    assert game.state.winner == 'right'

def test_game_over_stops_updates():
    game = PongGameLoop(max_score=1)
    game.state.left_score = 1
    game.state.game_over = True
    game.state.winner = 'left'
    initial_ball_x = game.state.ball.x
    game.step(left_up=True)
    assert game.state.ball.x == initial_ball_x
    assert game.state.left_paddle.y == game.state.left_paddle.y  # no movement

def test_reset():
    game = PongGameLoop()
    game.state.left_score = 5
    game.state.ball.x = 100
    game.reset()
    assert game.state.left_score == 0
    assert game.state.ball.x == 400
