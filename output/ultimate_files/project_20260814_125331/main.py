"""
Ninja Jump - игра про ниндзя, который прыгает по деревьям
Файл: main.html (переименован из main.py)
Запуск: открыть в браузере
"""

import random
import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_POWER = -12
GROUND_Y = 500

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Ninja:
    """Класс ниндзя"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_y = 0
        self.on_ground = True
        self.color = BLUE
        
    def jump(self):
        """Прыжок ниндзя"""
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            
    def update(self):
        """Обновление позиции"""
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Проверка земли
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
            
    def draw(self, screen):
        """Отрисовка ниндзя"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Глаза
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 15), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 15), 5)
        # Пояс
        pygame.draw.rect(screen, RED, (self.x, self.y + 35, self.width, 5))

class Tree:
    """Класс дерева"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 100
        # Ствол
        self.trunk_color = BROWN
        # Крона
        self.leaf_color = GREEN
        
    def draw(self, screen):
        """Отрисовка дерева"""
        # Ствол
        pygame.draw.rect(screen, self.trunk_color, (self.x, self.y, self.width, self.height))
        # Крона
        pygame.draw.circle(screen, self.leaf_color, (self.x + 30, self.y - 20), 40)

class Obstacle:
    """Класс препятствия"""
    def __init__(self, x):
        self.x = x
        self.y = GROUND_Y - 30
        self.width = 30
        self.height = 30
        self.color = RED
        
    def draw(self, screen):
        """Отрисовка препятствия"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ninja Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.ninja = Ninja(100, GROUND_Y - 60)
        self.trees = []
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.speed = 5
        
        # Создание начальных деревьев
        for i in range(5):
            x = 200 + i * 150
            y = GROUND_Y - 100
            self.trees.append(Tree(x, y))
            
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.ninja.jump()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
    def update(self):
        """Обновление игровой логики"""
        if self.game_over:
            return
            
        # Обновление ниндзя
        self.ninja.update()
        
        # Обновление препятствий
        for obstacle in self.obstacles[:]:
            obstacle.x -= self.speed
            if obstacle.x < -50:
                self.obstacles.remove(obstacle)
                self.score += 10
                
        # Создание новых препятствий
        if random.randint(1, 50) == 1:
            self.obstacles.append(Obstacle(SCREEN_WIDTH))
            
        # Обновление деревьев
        for tree in self.trees:
            tree.x -= self.speed / 2
            if tree.x < -100:
                tree.x = SCREEN_WIDTH + 100
                
        # Проверка столкновений
        self.check_collisions()
        
        # Увеличение скорости
        self.speed += 0.001
        
    def check_collisions(self):
        """Проверка столкновений"""
        ninja_rect = pygame.Rect(self.ninja.x, self.ninja.y, 
                                 self.ninja.width, self.ninja.height)
        
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y,
                                       obstacle.width, obstacle.height)
            if ninja_rect.colliderect(obstacle_rect):
                self.game_over = True
                
    def draw(self):
        """Отрисовка игры"""
        self.screen.fill(WHITE)
        
        # Отрисовка неба
        pygame.draw.rect(self.screen, (135, 206, 235), (0, 0, SCREEN_WIDTH, GROUND_Y))
        
        # Отрисовка земли
        pygame.draw.rect(self.screen, GREEN, (0, GROUND_Y, SCREEN_WIDTH, 
                                             SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, BLACK, (0, GROUND_Y), 
                        (SCREEN_WIDTH, GROUND_Y), 3)
        
        # Отрисовка деревьев
        for tree in self.trees:
            tree.draw(self.screen)
            
        # Отрисовка препятствий
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Отрисовка ниндзя
        self.ninja.draw(self.screen)
        
        # Отрисовка счёта
        score_text = self.font.render(f"Счёт: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Отрисовка скорости
        speed_text = self.font.render(f"Скорость: {self.speed:.1f}", True, BLACK)
        self.screen.blit(speed_text, (10, 50))
        
        # Отрисовка сообщения о конце игры
        if self.game_over:
            game_over_text = self.font.render("ИГРА ОКОНЧЕНА!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 
                                                            SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)
            
            restart_text = self.font.render("Нажмите ПРОБЕЛ для рестарта", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 
                                                        SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)
            
    def reset_game(self):
        """Сброс игры"""
        self.ninja = Ninja(100, GROUND_Y - 60)
        self.obstacles = []
        self.score = 0
        self.speed = 5
        self.game_over = False
        
    def run(self):
        """Главный игровой цикл"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
