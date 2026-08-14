def test_renderer_init():
    r = Renderer(10, 5)
    assert r.width == 10
    assert r.height == 5

def test_draw_sprite():
    r = Renderer(10, 5)
    r.add_sprite(Sprite(2, 2, "@"))
    frame = r.draw()
    lines = frame.split("\n")
    assert lines[2][2] == "@"
