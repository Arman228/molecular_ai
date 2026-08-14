import pytest
from pong_renderer import PongRenderer

def test_render_basic():
    r = PongRenderer(width=5, height=3)
    out = r.render(left_paddle_y=0, right_paddle_y=2, ball_x=2, ball_y=1)
    expected = (
        "-------\n"
        "| | O |\n"
        "|  O  |\n"
        "|    | |\n"
        "-------"
    )
    assert out == expected

def test_render_ball_on_paddle():
    r = PongRenderer(width=3, height=3)
    out = r.render(left_paddle_y=1, right_paddle_y=1, ball_x=0, ball_y=1)
    # Ball and paddle overlap; ball should be drawn (O) at that position
    expected = (
        "-----\n"
        "|   |\n"
        "|O  |\n"
        "|   |\n"
        "-----"
    )
    assert out == expected

def test_render_corners():
    r = PongRenderer(width=4, height=4)
    out = r.render(left_paddle_y=0, right_paddle_y=3, ball_x=3, ball_y=0)
    expected = (
        "------\n"
        "| | O|\n"
        "|    |\n"
        "|    |\n"
        "|   | |\n"
        "------"
    )
    assert out == expected

def test_invalid_dimensions():
    with pytest.raises(ValueError):
        PongRenderer(width=2, height=5)
    with pytest.raises(ValueError):
        PongRenderer(width=5, height=2)

def test_invalid_coordinates():
    r = PongRenderer(width=5, height=5)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=-1, right_paddle_y=0, ball_x=0, ball_y=0)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=0, right_paddle_y=5, ball_x=0, ball_y=0)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=0, right_paddle_y=0, ball_x=-1, ball_y=0)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=0, right_paddle_y=0, ball_x=5, ball_y=0)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=0, right_paddle_y=0, ball_x=0, ball_y=-1)
    with pytest.raises(ValueError):
        r.render(left_paddle_y=0, right_paddle_y=0, ball_x=0, ball_y=5)

def test_render_default_size():
    r = PongRenderer()
    out = r.render(left_paddle_y=10, right_paddle_y=10, ball_x=20, ball_y=10)
    lines = out.split('\n')
    assert len(lines) == 22  # height + 2 borders
    assert len(lines[0]) == 42  # width + 2 borders
    assert lines[0] == '-' * 42
    assert lines[-1] == '-' * 42
    assert lines[11][0] == '|' and lines[11][-1] == '|'
    assert lines[11][21] == 'O'  # ball at x=20, y=10 -> row 11, col 21 (1-based)
