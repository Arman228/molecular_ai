import pygame
import random
import sys
from enum import Enum
from collections import namedtuple

# Константы игры
BLOCK_SIZE = 20
SPEED = 10
FONT_SIZE = 24
FONT_SIZE_BIG = 48

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Направления движения
class Direction(Enum):
    """Направления движения змеи."""
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Структура для координат
Point = namedtuple('Point', 'x, y')

class SnakeGame:
    """Основной класс игры Змейка."""
    
    def __init__(self, width=640, height=480):
        """Инициализация игры."""
        pygame.init()
        self.width = width
        self.height = height
        
        # Настройка окна
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Змейка')
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.font = pygame.font.SysFont('arial', FONT_SIZE)
        self.font_big = pygame.font.SysFont('arial', FONT_SIZE_BIG)
        
        # Начальное состояние
        self.reset()
        
    def reset(self):
        """Сброс игры к начальному состоянию."""
        # Начальное направление
        self.direction = Direction.RIGHT
        
        # Начальная позиция змеи (3 блока в центре)
        self.head = Point(self.width // 2, self.height // 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)
        ]
        
        # Очки и скорость
        self.score = 0
        self.speed = SPEED
        
        # Создание еды
        self.food = None
        self._place_food()
        
        # Флаг игры
        self.game_over = False
        
    def _place_food(self):
        """Размещение еды на свободной клетке."""
        while True:
            x = random.randint(0, (self.width // BLOCK_SIZE) - 1) * BLOCK_SIZE
            y = random.randint(0, (self.height // BLOCK_SIZE) - 1) * BLOCK_SIZE
            self.food = Point(x, y)
            
            # Проверка, что еда не на змее
            if self.food not in self.snake:
                break
                
    def _move_snake(self):
        """Перемещение змеи в текущем направлении."""
        # Определение новой головы
        head = self.head
        
        if self.direction == Direction.RIGHT:
            new_head = Point(head.x + BLOCK_SIZE, head.y)
        elif self.direction == Direction.LEFT:
            new_head = Point(head.x - BLOCK_SIZE, head.y)
        elif self.direction == Direction.UP:
            new_head = Point(head.x, head.y - BLOCK_SIZE)
        elif self.direction == Direction.DOWN:
            new_head = Point(head.x, head.y + BLOCK_SIZE)
            
        # Вставка новой головы
        self.snake.insert(0, new_head)
        self.head = new_head
        
        # Проверка съедания еды
        if self.head == self.food:
            self.score += 1
            self.speed = min(self.speed + 1, 25)  # Увеличение скорости
            self._place_food()
        else:
            # Удаление хвоста, если еда не съедена
            self.snake.pop()
            
    def _check_collision(self):
        """Проверка столкновений."""
        # Столкновение со стенами
        if (self.head.x < 0 or self.head.x >= self.width or
            self.head.y < 0 or self.head.y >= self.height):
            return True
            
        # Столкновение с телом змеи
        if self.head in self.snake[1:]:
            return True
            
        return False
        
    def _draw_grid(self):
        """Рисование фоновой сетки."""
        for x in range(0, self.width, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (x, 0), (x, self.height))
        for y in range(0, self.height, BLOCK_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (0, y), (self.width, y))
            
    def _draw_snake(self):
        """Рисование змеи с градиентом цвета."""
        # Рисование тела змеи
        for i, segment in enumerate(self.snake):
            # Цвет сегмента: от зеленого к голубому
            color_value = min(255, 150 + i * 10)
            color = (0, color_value, 100 + i * 5) if i < len(self.snake) // 2 else \
                   (color_value, 200, 100)
            
            # Прямоугольник сегмента
            rect = pygame.Rect(segment.x, segment.y, BLOCK_SIZE, BLOCK_SIZE)
            
            # Рисование с закругленными углами
            pygame.draw.rect(self.display, color, rect, border_radius=4)
            
            # Добавление блика для 3D эффекта
            if i == 0:  # Голова
                pygame.draw.rect(self.display, WHITE, 
                               (segment.x + 5, segment.y + 5, 4, 4), border_radius=2)
                pygame.draw.rect(self.display, BLACK, 
                               (segment.x + 12, segment.y + 10, 3, 3), border_radius=1)
        
    def _draw_food(self):
        """Рисование еды с анимированным эффектом."""
        # Пульсирующий эффект
        pulse = (pygame.time.get_ticks() // 100) % 5
        size = BLOCK_SIZE - pulse * 2
        
        # Рисование основной части еды
        pygame.draw.circle(self.display, RED, 
                          (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2),
                          size // 2)
        
        # Рисование блика на еде
        pygame.draw.circle(self.display, YELLOW,
                          (self.food.x + BLOCK_SIZE // 2 - 2, self.food.y + BLOCK_SIZE // 2 - 2),
                          size // 6)
        
        # Добавление листиков
        pygame.draw.circle(self.display, GREEN,
                          (self.food.x + BLOCK_SIZE // 2 - 6, self.food.y + BLOCK_SIZE // 2 - 4),
                          3)
        
    def _draw_score(self):
        """Отображение счета."""
        score_text = self.font.render(f'Счёт: {self.score}', True, WHITE)
        self.display.blit(score_text, (10, 10))
        
    def _draw_game_over(self):
        """Отображение экрана проигрыша."""
        # Затемнение фона
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.display.blit(overlay, (0, 0))
        
        # Текст проигрыша
        game_over_text = self.font_big.render('Игра окончена!', True, RED)
        text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.display.blit(game_over_text, text_rect)
        
        # Текст с результатом
        score_text = self.font.render(f'Ваш счёт: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.display.blit(score_text, score_rect)
        
        # Подсказка
        hint_text = self.font.render('Нажмите R для перезапуска или Q для выхода', True, CYAN)
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.display.blit(hint_text, hint_rect)
        
    def play_step(self):
        """Один игровой шаг."""
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_q and self.game_over:
                    pygame.quit()
                    sys.exit()
        
        # Перемещение змеи, если игра активна
        if not self.game_over:
            self._move_snake()
            self.game_over = self._check_collision()
        
        # Обновление экрана
        self.display.fill(BLACK)
        self._draw_grid()
        self._draw_snake()
        self._draw_food()
        self._draw_score()
        
        # Если игра окончена, показать экран проигрыша
        if self.game_over:
            self._draw_game_over()
            
        pygame.display.flip()
        
        # Контроль скорости
        self.clock.tick(self.speed)
        
        return self.game_over
        
    def run(self):
        """Запуск игрового цикла."""
        while True:
            self.play_step()

def main():
    """Главная функция запуска игры."""
    game = SnakeGame()
    game.run()

if __name__ == '__main__':
    main()
