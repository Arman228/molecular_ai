"""
Мини-игра "Угадай число"
Игрок должен угадать случайное число от 1 до 100 за ограниченное количество попыток.
"""

import random
import sys
from typing import Optional


class NumberGuessingGame:
    """Класс, реализующий игру 'Угадай число'."""
    
    def __init__(self, min_number: int = 1, max_number: int = 100, max_attempts: int = 10) -> None:
        """
        Инициализация игры.
        
        Args:
            min_number: Минимальное значение загаданного числа
            max_number: Максимальное значение загаданного числа
            max_attempts: Максимальное количество попыток
        """
        self.min_number = min_number
        self.max_number = max_number
        self.max_attempts = max_attempts
        self.secret_number: Optional[int] = None
        self.attempts: int = 0
        self.is_playing: bool = False
    
    def start_new_game(self) -> None:
        """Начинает новую игру."""
        self.secret_number = random.randint(self.min_number, self.max_number)
        self.attempts = 0
        self.is_playing = True
        print(f"\n🎮 Новая игра!")
        print(f"🔢 Я загадал число от {self.min_number} до {self.max_number}")
        print(f"💪 У тебя {self.max_attempts} попыток, чтобы угадать его!")
    
    def check_guess(self, guess: int) -> str:
        """
        Проверяет предположение игрока.
        
        Args:
            guess: Предполагаемое число
            
        Returns:
            Строка с результатом проверки
        """
        if guess < self.secret_number:
            return "📈 Слишком маленькое число! Попробуй больше."
        elif guess > self.secret_number:
            return "📉 Слишком большое число! Попробуй меньше."
        else:
            return "🎉 Поздравляю! Ты угадал!"
    
    def play_turn(self, guess: int) -> bool:
        """
        Выполняет один ход игры.
        
        Args:
            guess: Предполагаемое число
            
        Returns:
            True если игра продолжается, False если игра окончена
        """
        if not self.is_playing:
            print("⚠️ Игра не начата. Начни новую игру!")
            return False
        
        self.attempts += 1
        
        if guess < self.min_number or guess > self.max_number:
            print(f"⚠️ Число должно быть от {self.min_number} до {self.max_number}!")
            return True
        
        result = self.check_guess(guess)
        print(f"Попытка {self.attempts}/{self.max_attempts}: {result}")
        
        if "Поздравляю" in result:
            print(f"✨ Ты справился за {self.attempts} попыток!")
            self.is_playing = False
            return False
        
        if self.attempts >= self.max_attempts:
            print(f"😔 Игра окончена! Загаданное число было: {self.secret_number}")
            self.is_playing = False
            return False
        
        return True
    
    def play(self) -> None:
        """Запускает основной игровой цикл."""
        self.start_new_game()
        
        while self.is_playing:
            try:
                guess_input = input("\n🔍 Введите число: ").strip()
                
                if guess_input.lower() == 'exit':
                    print("👋 Спасибо за игру! До встречи!")
                    sys.exit(0)
                
                guess = int(guess_input)
                
                if not self.play_turn(guess):
                    self.show_menu()
                    break
                    
            except ValueError:
                print("❌ Ошибка! Введите целое число или 'exit' для выхода.")
    
    def show_menu(self) -> None:
        """Показывает меню после окончания игры."""
        while True:
            choice = input("\n🔄 Хочешь сыграть ещё раз? (y/n): ").strip().lower()
            
            if choice in ('y', 'yes', 'да', 'д'):
                self.play()
                break
            elif choice in ('n', 'no', 'нет', 'н'):
                print("👋 Спасибо за игру! До встречи!")
                sys.exit(0)
            else:
                print("⚠️ Пожалуйста, введите 'y' (да) или 'n' (нет)")


def main() -> None:
    """Главная функция запуска игры."""
    print("=" * 50)
    print("🎯 Добро пожаловать в игру 'Угадай число'!")
    print("=" * 50)
    
    # Создаем игру с настраиваемыми параметрами
    game = NumberGuessingGame(
        min_number=1,
        max_number=100,
        max_attempts=10
    )
    
    # Запускаем игру
    try:
        game.play()
    except KeyboardInterrupt:
        print("\n\n👋 Игра прервана пользователем. До встречи!")
        sys.exit(0)


if __name__ == "__main__":
    main()
