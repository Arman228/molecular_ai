def test_game_loop_init():
    gl = GameLoop(fps=30)
    assert gl.fps == 30
    assert gl.dt == 1.0 / 30

def test_game_loop_stop():
    gl = GameLoop()
    gl.stop()
    assert gl.running is False
