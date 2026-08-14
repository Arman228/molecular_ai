# Автоматически сгенерировано Molecular AI v7.0
# Запрос: напиши хороший промт для игры в html человечек ниндзя в форме бегает по препятствия, и напиши код для игры
# Дата: 2026-08-14 12:41:25


import random
import time

def game_ninja_jump():
    print("🐱‍👤 НИНДЗЯ: ПРЫЖОК ЧЕРЕЗ ДЕРЕВЬЯ")
    print("=" * 40)
    print("Правила:")
    print("1. Нажимайте Enter чтобы прыгнуть")
    print("2. Пропустите дерево - получите очко")
    print("3. Врежьтесь в дерево - игра окончена")
    print("=" * 40)
    print()
    
    score = 0
    trees_passed = 0
    game_over = False
    
    # Позиции объектов (упрощенно)
    ninja_pos = 0
    tree_pos = 10
    tree_height = random.randint(1, 3)
    
    print("🐱‍👤 Ниндзя готов!")
    print("🌳 Деревья появляются...")
    print()
    
    while not game_over:
        # Показываем поле
        field = [" "] * 20
        field[ninja_pos] = "🐱‍👤"
        
        if tree_pos < 20:
            field[tree_pos] = "🌳" * tree_height
        
        print("".join(field))
        print(f"Очки: {score} | Деревья пройдено: {trees_passed}")
        print()
        
        # Двигаем ниндзя
        action = input("Нажмите Enter чтобы прыгнуть, или q для выхода: ")
        
        if action.lower() == "q":
            print("Игра окончена!")
            print(f"Ваш результат: {score}")
            break
        
        # Прыжок
        ninja_pos = 0  # Возвращаем на землю
        tree_pos -= 1
        trees_passed += 1
        
        # Проверка столкновения
        if ninja_pos == tree_pos:
            print("💥 БАМ! Ниндзя врезался в дерево!")
            game_over = True
            print(f"Игра окончена! Ваш результат: {score}")
            break
        
        # Проверка перепрыгивания
        if tree_pos < 0:
            score += 1
            tree_pos = random.randint(5, 15)
            tree_height = random.randint(1, 3)
            print(f"✅ +1 очко! Всего: {score}")
        
        time.sleep(0.3)
    
    print()
    print("=" * 40)
    print(f"🏆 Итоговый счет: {score}")
    print("=" * 40)
    return score

if __name__ == "__main__":
    game_ninja_jump()
