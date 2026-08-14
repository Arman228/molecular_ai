import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Класс игрока (мальчик)
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.is_jumping = False
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True

    def update(self):
        # Применяем гравитацию
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Проверка на землю
        if self.y >= SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.is_jumping = False

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        # Рисуем мальчика (простой прямоугольник с головой)
        pygame.draw.rect(screen, BLUE, self.rect)
        # Голова
        pygame.draw.circle(screen, BLUE, (self.x + self.width // 2, self.y - 10), 15)

# Класс препятствия
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.passed = False

    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

    def off_screen(self):
        return self.x + self.width < 0

# Класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Бегущий мальчик")
        self.clock = pygame.time.Clock()
        self.player = Player(100, SCREEN_HEIGHT - 60)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.speed = 5
        self.spawn_timer = 0

    def spawn_obstacle(self):
        # Случайная высота препятствия
        height = random.randint(30, 60)
        y = SCREEN_HEIGHT - height
        width = random.randint(20, 40)
        obstacle = Obstacle(SCREEN_WIDTH, y, width, height)
        self.obstacles.append(obstacle)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.jump()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        if not self.game_over:
            # Обновляем игрока
            self.player.update()

            # Спавним препятствия
            self.spawn_timer += 1
            if self.spawn_timer > random.randint(60, 120):
                self.spawn_obstacle()
                self.spawn_timer = 0

            # Обновляем препятствия
            for obstacle in self.obstacles[:]:
                obstacle.update(self.speed)
                if obstacle.off_screen():
                    self.obstacles.remove(obstacle)
                    self.score += 1

                # Проверка столкновения
                if self.player.rect.colliderect(obstacle.rect):
                    self.game_over = True

            # Увеличиваем сложность
            self.speed = 5 + self.score // 20

    def draw(self):
        self.screen.fill(WHITE)

        # Рисуем землю
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

        # Рисуем игрока
        self.player.draw(self.screen)

        # Рисуем препятствия
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Отображаем счёт
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Счёт: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        # Отображаем конец игры
        if self.game_over:
            game_over_text = font.render("Игра окончена! Нажми R для рестарта", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def reset_game(self):
        # Сброс всех параметров
        self.player = Player(100, SCREEN_HEIGHT - 60)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.speed = 5
        self.spawn_timer = 0

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Точка входа
if __name__ == "__main__":
    game = Game()
    game.run()
