from typing import List, Tuple

class PongRenderer:
    """Render a Pong game state as an ASCII string.

    The renderer takes the dimensions of the field, positions of the left and right paddles,
    and the ball position, and produces a string representation with borders and ball/paddle markers.
    Coordinates are zero-based. The ball is represented by 'O', paddles by '|', and empty space by ' '.
    The field includes a top and bottom border of '-' and side borders of '|'.
    """

    def __init__(self, width: int = 40, height: int = 20):
        """Initialize the renderer with field dimensions.

        Args:
            width: Width of the play area (excluding side borders). Must be >= 3.
            height: Height of the play area (excluding top/bottom borders). Must be >= 3.

        Raises:
            ValueError: If width or height are too small.
        """
        if width < 3 or height < 3:
            raise ValueError("Width and height must be at least 3")
        self.width = width
        self.height = height

    def render(self, left_paddle_y: int, right_paddle_y: int, ball_x: int, ball_y: int) -> str:
        """Render the game state as a string.

        Args:
            left_paddle_y: Y-coordinate of the left paddle's top. Must be in [0, height-1].
            right_paddle_y: Y-coordinate of the right paddle's top. Must be in [0, height-1].
            ball_x: X-coordinate of the ball. Must be in [0, width-1].
            ball_y: Y-coordinate of the ball. Must be in [0, height-1].

        Returns:
            A string representing the game field, with lines separated by '\n'.

        Raises:
            ValueError: If any coordinate is out of bounds.
        """
        if not (0 <= left_paddle_y < self.height):
            raise ValueError(f"left_paddle_y out of range: {left_paddle_y}")
        if not (0 <= right_paddle_y < self.height):
            raise ValueError(f"right_paddle_y out of range: {right_paddle_y}")
        if not (0 <= ball_x < self.width):
            raise ValueError(f"ball_x out of range: {ball_x}")
        if not (0 <= ball_y < self.height):
            raise ValueError(f"ball_y out of range: {ball_y}")

        # Build the field as a list of rows (excluding borders)
        rows: List[List[str]] = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Place left paddle (at x=0)
        rows[left_paddle_y][0] = '|'
        # Place right paddle (at x=width-1)
        rows[right_paddle_y][self.width - 1] = '|'
        # Place ball
        rows[ball_y][ball_x] = 'O'

        # Build the output string
        border = '-' * (self.width + 2)
        lines = [border]
        for row in rows:
            lines.append('|' + ''.join(row) + '|')
        lines.append(border)
        return '\n'.join(lines)
