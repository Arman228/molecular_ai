from typing import List, Tuple, Optional

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
        return "\n".join("".join(row) for row in self.buffer)

    def render_frame(self):
        frame = self.draw()
        print(frame)
