import time

class GameLoop:
    """Main game loop with FPS control."""
    def __init__(self, fps: int = 60):
        self.fps = fps
        self.dt = 1.0 / fps
        self.running = False
        self.tick = 0

    def start(self, update_fn, render_fn):
        self.running = True
        last = time.time()
        while self.running:
            now = time.time()
            self.dt = now - last
            last = now
            update_fn(self.dt)
            render_fn()
            self.tick += 1
            sleep_time = (1.0 / self.fps) - self.dt
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self.running = False
