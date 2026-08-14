# ui/app.py
"""
Flask приложение для UI.
"""

import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS
except ImportError:
    print("❌ Ошибка: Flask не установлен!")
    print("Установите: pip install flask flask-cors")
    sys.exit(1)

from ui.controller import UltimateController

app = Flask(__name__)
CORS(app)

controller = UltimateController()

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>Ошибка загрузки шаблона</h1><p>{e}</p>"

@app.route('/api/init', methods=['POST'])
def init_system():
    data = request.json or {}
    result = controller.init_system(
        n_agents=data.get('n_agents', 10),
        dt=data.get('dt', 0.02),
        noise=data.get('noise', 0.03)
    )
    return jsonify(result)

@app.route('/api/step', methods=['POST'])
def step():
    data = request.json or {}
    metrics = controller.step(data.get('n_steps', 1))
    return jsonify(metrics)

@app.route('/api/run', methods=['POST'])
def run():
    data = request.json or {}
    controller.run_async(data.get('n_steps', 100))
    return jsonify({"status": "started"})

@app.route('/api/stop', methods=['POST'])
def stop():
    controller.stop()
    return jsonify({"status": "stopped"})

@app.route('/api/state', methods=['GET'])
def state():
    return jsonify(controller.get_state())

@app.route('/api/mode', methods=['POST'])
def set_mode():
    data = request.json or {}
    result = controller.set_mode(data.get('mode', 'mixed'))
    return jsonify(result)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json or {}
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"})
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(controller.ask_question(question))
        loop.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify({"projects": controller.get_projects()})

@app.route('/api/download/<path:filepath>')
def download_file(filepath):
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/system_info', methods=['GET'])
def system_info():
    return jsonify({
        "name": "Ultimate System v7.0",
        "version": "7.0",
        "features": [
            "Самосознание",
            "Генерация кода",
            "Создание файлов",
            "3 режима: Факты, Интерпретации, Смешанный",
            "Вопросы только при необходимости",
            "Маркеры уверенности"
        ]
    })

if __name__ == '__main__':
    print("🚀 Запуск Flask сервера на http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')