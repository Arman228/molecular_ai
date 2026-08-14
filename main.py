# main.py
"""
Главный файл запуска Molecular AI v7.0
"""

import os
import sys
import webbrowser
import time
import threading
import os
os.environ["DEEPSEEK_API_KEY"] = "sk-970239abe4a5483797dab13d70dec3f6"

def main():
    print("=" * 70)
    print("  🧬 MOLECULAR AI v7.0 — ULTIMATE SYSTEM")
    print("  Полная система с UI и генерацией кода")
    print("=" * 70)
    print()
    
    # Проверяем наличие Flask
    try:
        import flask
        print("✅ Flask установлен")
    except ImportError:
        print("❌ Flask не установлен!")
        print("Установите: pip install flask flask-cors")
        return
    
    # Проверяем наличие файлов
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Проверяем ui/app.py
    app_file = os.path.join(base_dir, "ui", "app.py")
    if not os.path.exists(app_file):
        print(f"❌ Файл не найден: {app_file}")
        return
    
    # Проверяем ui/templates/index.html
    template_file = os.path.join(base_dir, "ui", "templates", "index.html")
    if not os.path.exists(template_file):
        print(f"❌ Файл не найден: {template_file}")
        return
    
    print("✅ Все файлы найдены")
    print("🚀 Запуск веб-интерфейса...")
    print("📡 Сервер запускается на http://localhost:5000")
    print()
    print("=" * 70)
    print("  💡 ИНСТРУКЦИЯ:")
    print("  1. Откроется браузер с интерфейсом")
    print("  2. Нажмите 'Инициализация' для запуска системы")
    print("  3. Задавайте вопросы или просите написать код")
    print("  4. Сгенерированные файлы сохраняются в output/ultimate_files/")
    print("=" * 70)
    print()
    
    # Открываем браузер через 1 секунду
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open("http://localhost:5000")
        except:
            print("⚠️ Не удалось открыть браузер автоматически")
            print("   Откройте вручную: http://localhost:5000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Запускаем Flask
    try:
        from ui.app import app
        app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        print("Попробуйте запустить вручную: python ui/app.py")

if __name__ == "__main__":
    main()