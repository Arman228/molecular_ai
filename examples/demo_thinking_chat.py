#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — ИНТЕРАКТИВНЫЙ МЫСЛЯЩИЙ ПРОЦЕСС
Чат-интерфейс для вопросов к коллективному разуму.

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_thinking_chat" "examples\demo_thinking_chat.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_thinking_chat.py
"""

import os
import sys
import random
import asyncio
import time
import json
import threading
import webbrowser
import http.server
import socketserver
from datetime import datetime
from typing import List, Dict, Any
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ================================================================
# РОЛИ АГЕНТОВ
# ================================================================
THINKING_ROLES = [
    {"name": "Аналитик", "persona": "Анализирует проблему с разных сторон, ищет логические связи."},
    {"name": "Креативщик", "persona": "Генерирует нестандартные идеи, предлагает креативные решения."},
    {"name": "Критик", "persona": "Находит слабые места, подвергает сомнению, проверяет на прочность."},
    {"name": "Эмпат", "persona": "Учитывает человеческий фактор, эмоции, потребности людей."},
    {"name": "Стратег", "persona": "Видит общую картину, планирует долгосрочные решения."},
    {"name": "Эксперт", "persona": "Обладает глубокими знаниями в конкретной области."},
    {"name": "Философ", "persona": "Рассматривает этические и философские аспекты."},
    {"name": "Прагматик", "persona": "Фокусируется на практических решениях и реализации."},
    {"name": "Инноватор", "persona": "Ищет новые парадигмы, предлагает прорывные идеи."},
    {"name": "Синтезатор", "persona": "Собирает разрозненные идеи в единое целое."},
]

class InteractiveThinkingProcess:
    """Интерактивная система коллективного мышления с чат-интерфейсом."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.sync_r = 0.0
        self.conversation_history = []
        self.thinking_phases = []
        
    def initialize_system(self):
        """Инициализирует систему с агентами."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ КОЛЛЕКТИВНОГО РАЗУМА...")
        
        self.system = MolecularSystem(
            n_agents=10,
            dt=0.02,
            noise=0.03,
            sleep_every=400,
            k_sparse=6,
            exc_ratio=0.9
        )
        
        for layer in self.system.orbital.layers:
            layer.coupling *= 3.5
        
        for agent in self.system.agents:
            agent.omega = 1.0 + random.uniform(-0.06, 0.06)
        
        print("  ✅ 10 мыслящих агентов созданы")
        self._warm_up()
    
    def _warm_up(self):
        """Разогрев системы."""
        print("\n🔥 РАЗОГРЕВ СИСТЕМЫ (синхронизация мышления)...")
        
        set_regime(self.system, ConvergenceRegime.DIVERGENT)
        for i in range(300):
            self.system.step()
            if i % 100 == 99:
                print(f"  Хаос: r={self.system.order_parameter():.3f}")
        
        set_regime(self.system, ConvergenceRegime.CRITICAL)
        for i in range(300):
            self.system.step()
            if i % 100 == 99:
                print(f"  Баланс: r={self.system.order_parameter():.3f}")
        
        set_regime(self.system, ConvergenceRegime.LINEAR)
        for i in range(400):
            self.system.step()
            if i % 100 == 99:
                print(f"  Стабилизация: r={self.system.order_parameter():.3f}")
        
        self.sync_r = self.system.order_parameter()
        print(f"\n  ✅ СИНХРОНИЗАЦИЯ ДОСТИГНУТА: r={self.sync_r:.3f}")
    
    async def ask_question(self, question: str) -> Dict:
        """Задает вопрос и возвращает коллективный ответ."""
        print("\n" + "=" * 70)
        print(f"  ❓ ВОПРОС: {question}")
        print("=" * 70)
        
        # ФАЗА 1: Агенты думают
        print("\n🤔 ФАЗА 1: АГЕНТЫ ДУМАЮТ...")
        
        prompts = []
        for i, agent in enumerate(self.system.agents):
            role = THINKING_ROLES[i]
            state = agent.get_state()
            prompt = f"""
Ты — {role['name']}. Твоя роль: {role['persona']}

ВОПРОС: {question}

ОТВЕТЬ НА ВОПРОС С ТОЧКИ ЗРЕНИЯ ТВОЕЙ РОЛИ.
Будь конкретным, оригинальным и полезным.
Ответ должен быть 2-4 предложения.

Текущее состояние системы:
- Синхронизация: r={self.sync_r:.3f}
- Твой настрой: {state.get('mood', 0):+.2f}
- Твоя энергия: {state.get('energy', 0):.2f}

ОТВЕТ:
"""
            prompts.append(prompt)
        
        print("  ⚡ Агенты генерируют ответы...")
        t0 = time.time()
        
        try:
            results = await self._parallel_llm_calls(prompts)
            elapsed = time.time() - t0
            
            agent_answers = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ❌ Агент {i} [{THINKING_ROLES[i]['name']}]: ОШИБКА")
                    agent_answers.append({
                        "role": THINKING_ROLES[i]['name'],
                        "answer": "[Ошибка генерации]",
                        "error": True
                    })
                else:
                    content = result.choices[0].message.content
                    print(f"  ✅ Агент {i} [{THINKING_ROLES[i]['name']}]: {len(content)} символов")
                    agent_answers.append({
                        "role": THINKING_ROLES[i]['name'],
                        "answer": content.strip(),
                        "error": False
                    })
            
            print(f"\n  ⏱️ Агенты думали: {elapsed:.1f}с")
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации: {e}")
            return {"error": str(e)}
        
        # ФАЗА 2: Орбитальная синхронизация
        print("\n🔄 ФАЗА 2: ОРБИТАЛЬНАЯ СИНХРОНИЗАЦИЯ...")
        
        for i, answer in enumerate(agent_answers):
            if not answer['error']:
                self.system.agents[i].mood += 0.1
                self.system.agents[i].energy += 0.5
        
        for step in range(100):
            self.system.step()
            if step % 20 == 19:
                r = self.system.order_parameter()
                print(f"  Шаг {step+1}: r={r:.3f}")
        
        self.sync_r = self.system.order_parameter()
        print(f"\n  ✅ СИНХРОНИЗАЦИЯ: r={self.sync_r:.3f}")
        
        # ФАЗА 3: Коллективный ответ
        print("\n🎯 ФАЗА 3: ФОРМИРОВАНИЕ КОЛЛЕКТИВНОГО ОТВЕТА...")
        
        ranked = []
        for i, answer in enumerate(agent_answers):
            if not answer['error']:
                agent = self.system.agents[i]
                score = agent.mood * 0.3 + agent.energy * 0.3 + random.random() * 0.4
                ranked.append((score, i, answer))
        
        ranked.sort(reverse=True)
        
        top_answers = []
        for score, idx, answer in ranked[:3]:
            top_answers.append(answer)
            print(f"  #{len(top_answers)} [{answer['role']}] (score={score:.2f})")
            print(f"     {answer['answer'][:100]}...")
        
        # Синтез ответа
        print("\n🧠 СИНТЕЗ КОЛЛЕКТИВНОГО ОТВЕТА...")
        
        synthesis_prompt = f"""
ВОПРОС: {question}

ТОП-3 ОТВЕТА ОТ АГЕНТОВ:

1. [{top_answers[0]['role']}]: {top_answers[0]['answer']}

2. [{top_answers[1]['role']}]: {top_answers[1]['answer']}

3. [{top_answers[2]['role']}]: {top_answers[2]['answer']}

Синтезируй ЕДИНЫЙ, ЦЕЛЬНЫЙ и КРАСИВЫЙ ответ.
3-5 предложений, учитывающий все точки зрения.

ОТВЕТ:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты — мастер синтеза идей."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            final_answer = response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"  ❌ Ошибка синтеза: {e}")
            final_answer = top_answers[0]['answer']
        
        # Сохраняем результат
        result = {
            "question": question,
            "individual_answers": agent_answers,
            "top_answers": top_answers,
            "final_answer": final_answer,
            "sync_r": self.sync_r,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(result)
        
        print("\n" + "=" * 70)
        print("  💡 КОЛЛЕКТИВНЫЙ ОТВЕТ:")
        print("=" * 70)
        print(f"\n{final_answer}\n")
        print("=" * 70)
        
        return result
    
    async def _parallel_llm_calls(self, prompts: List[str]) -> List:
        """Выполняет параллельные вызовы LLM."""
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        tasks = []
        for prompt in prompts:
            tasks.append(client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты — эксперт в своей области. Отвечай кратко, конкретно и по делу."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8 + random.random() * 0.2,
                max_tokens=512
            ))
        
        return await asyncio.gather(*tasks, return_exceptions=True)

# ================================================================
# HTML-ИНТЕРФЕЙС ДЛЯ ЧАТА
# ================================================================
def generate_chat_html() -> str:
    """Генерирует HTML с интерфейсом чата."""
    return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Мыслящий Процесс — Чат</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0e2a 0%, #1a0a2a 50%, #0a0e2a 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: rgba(255,255,255,0.9);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }
        .header {
            padding: 20px 30px;
            background: rgba(10, 15, 30, 0.8);
            border-bottom: 1px solid rgba(95, 127, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        .header h1 {
            font-size: 1.5em;
            background: linear-gradient(135deg, #7f9fff, #b07fff, #ff7fbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header .status {
            font-size: 12px;
            opacity: 0.6;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .status .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #7fffd4;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .chat-container::-webkit-scrollbar {
            width: 4px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: rgba(95, 127, 255, 0.3);
            border-radius: 2px;
        }
        .message {
            max-width: 80%;
            padding: 15px 20px;
            border-radius: 16px;
            animation: slideIn 0.5s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, rgba(63, 104, 255, 0.3), rgba(100, 60, 200, 0.3));
            border: 1px solid rgba(95, 127, 255, 0.3);
        }
        .message.agent {
            align-self: flex-start;
            background: rgba(10, 15, 30, 0.6);
            border: 1px solid rgba(95, 127, 255, 0.15);
        }
        .message .role {
            font-size: 11px;
            opacity: 0.5;
            margin-bottom: 5px;
        }
        .message .text {
            line-height: 1.6;
        }
        .message .thinking {
            display: flex;
            gap: 5px;
            padding: 5px 0;
        }
        .message .thinking span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(95, 127, 255, 0.3);
            animation: bounce 1.4s infinite;
        }
        .message .thinking span:nth-child(2) { animation-delay: 0.2s; }
        .message .thinking span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        .input-container {
            padding: 20px 30px;
            background: rgba(10, 15, 30, 0.8);
            border-top: 1px solid rgba(95, 127, 255, 0.15);
            display: flex;
            gap: 10px;
            flex-shrink: 0;
        }
        .input-container input {
            flex: 1;
            padding: 12px 20px;
            border-radius: 30px;
            border: 1px solid rgba(95, 127, 255, 0.2);
            background: rgba(10, 15, 30, 0.6);
            color: rgba(255,255,255,0.9);
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        .input-container input:focus {
            border-color: rgba(95, 127, 255, 0.5);
            box-shadow: 0 0 30px rgba(80, 120, 255, 0.05);
        }
        .input-container input::placeholder {
            color: rgba(255,255,255,0.3);
        }
        .input-container button {
            padding: 12px 30px;
            border-radius: 30px;
            border: none;
            background: linear-gradient(135deg, #3f68ff, #7f3fff);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        .input-container button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 40px rgba(63, 104, 255, 0.3);
        }
        .input-container button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .suggestions {
            display: flex;
            gap: 8px;
            padding: 10px 30px;
            flex-wrap: wrap;
            flex-shrink: 0;
            background: rgba(10, 15, 30, 0.4);
        }
        .suggestions button {
            padding: 6px 16px;
            border-radius: 20px;
            border: 1px solid rgba(95, 127, 255, 0.15);
            background: rgba(10, 15, 30, 0.6);
            color: rgba(255,255,255,0.6);
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }
        .suggestions button:hover {
            background: rgba(63, 104, 255, 0.2);
            border-color: rgba(95, 127, 255, 0.3);
        }
        @media (max-width: 768px) {
            .header { padding: 15px; }
            .header h1 { font-size: 1.2em; }
            .chat-container { padding: 15px; }
            .message { max-width: 90%; }
            .input-container { padding: 15px; flex-direction: column; }
            .input-container button { width: 100%; }
            .suggestions { padding: 10px 15px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Мыслящий Процесс</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="agentStatus">10 агентов активны</span>
            <span id="syncStatus">синхронизация: 0.00</span>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="role">🧠 Система</div>
            <div class="text">Привет! Я — коллективный разум из 10 агентов.<br>Задай мне любой вопрос, и мы обсудим его вместе!</div>
        </div>
    </div>
    
    <div class="suggestions" id="suggestions">
        <button onclick="askQuestion('Как создать идеальный ИИ-помощник?')">🤖 ИИ-помощник</button>
        <button onclick="askQuestion('Что такое сознание?')">🧠 Сознание</button>
        <button onclick="askQuestion('Как совместить творчество и эффективность?')">🎨 Творчество</button>
        <button onclick="askQuestion('Что важнее: талант или труд?')">⭐ Талант vs Труд</button>
        <button onclick="askQuestion('Как создать гармоничное общество?')">🌍 Гармония</button>
    </div>
    
    <div class="input-container">
        <input id="questionInput" placeholder="Задайте вопрос..." onkeypress="if(event.key==='Enter') askQuestion()">
        <button id="sendButton" onclick="askQuestion()">💬 Спросить</button>
    </div>
    
    <script>
        let isProcessing = false;
        let questionCount = 0;
        
        function addMessage(role, content, isThinking = false) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            if (isThinking) {
                div.innerHTML = `
                    <div class="role">🧠 Агенты думают...</div>
                    <div class="thinking">
                        <span></span><span></span><span></span>
                    </div>
                `;
            } else {
                div.innerHTML = `
                    <div class="role">${role === 'user' ? '👤 Вы' : '🧠 Коллективный разум'}</div>
                    <div class="text">${content}</div>
                `;
            }
            
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function updateStatus(sync_r) {
            document.getElementById('syncStatus').textContent = `синхронизация: ${sync_r.toFixed(3)}`;
        }
        
        async function askQuestion(question = null) {
            if (isProcessing) return;
            
            const input = document.getElementById('questionInput');
            const button = document.getElementById('sendButton');
            
            if (!question) {
                question = input.value.trim();
                if (!question) return;
                input.value = '';
            }
            
            isProcessing = true;
            button.disabled = true;
            button.textContent = '⏳ Думаем...';
            
            // Показываем вопрос пользователя
            addMessage('user', question);
            
            // Показываем индикатор мышления
            addMessage('agent', '', true);
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                // Убираем индикатор мышления
                const messages = document.querySelectorAll('.message');
                if (messages.length > 0 && messages[messages.length - 1].querySelector('.thinking')) {
                    messages[messages.length - 1].remove();
                }
                
                if (data.error) {
                    addMessage('agent', '❌ Ошибка: ' + data.error);
                } else {
                    // Показываем ответы агентов (кратко)
                    if (data.individual_answers) {
                        const topAnswers = data.individual_answers
                            .filter(a => !a.error)
                            .slice(0, 3);
                        
                        for (let ans of topAnswers) {
                            addMessage('agent', `💭 ${ans.role}: ${ans.answer.substring(0, 100)}...`);
                        }
                    }
                    
                    // Показываем финальный ответ
                    addMessage('agent', '✨ ' + data.final_answer);
                    
                    // Обновляем статус
                    if (data.sync_r) {
                        updateStatus(data.sync_r);
                    }
                }
            } catch (error) {
                const messages = document.querySelectorAll('.message');
                if (messages.length > 0 && messages[messages.length - 1].querySelector('.thinking')) {
                    messages[messages.length - 1].remove();
                }
                addMessage('agent', '❌ Ошибка: ' + error.message);
            }
            
            isProcessing = false;
            button.disabled = false;
            button.textContent = '💬 Спросить';
        }
        
        // Получаем статус системы
        async function getStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                if (data.sync_r) {
                    updateStatus(data.sync_r);
                }
                if (data.question_count) {
                    document.getElementById('agentStatus').textContent = 
                        `${data.agents} агентов, ${data.question_count} вопросов`;
                }
            } catch (e) {
                // Игнорируем ошибки статуса
            }
        }
        
        // Обновляем статус каждые 5 секунд
        setInterval(getStatus, 5000);
        getStatus();
    </script>
</body>
</html>'''

# ================================================================
# HTTP-СЕРВЕР С API
# ================================================================
class ThinkingHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик HTTP-запросов с API для чата."""
    
    thinking_system = None
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(generate_chat_html().encode('utf-8'))
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                'sync_r': self.thinking_system.sync_r if self.thinking_system else 0,
                'agents': 10,
                'question_count': len(self.thinking_system.conversation_history) if self.thinking_system else 0
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            question = data.get('question', '')
            
            if not question:
                self.send_error(400, "No question provided")
                return
            
            # Запускаем обработку вопроса
            try:
                # Создаем новый event loop для этого запроса
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.thinking_system.ask_question(question)
                )
                loop.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_error(404)

# ================================================================
# ЗАПУСК
# ================================================================
def main():
    print("=" * 70)
    print("  🧠 MOLECULAR AI v7.0 — ИНТЕРАКТИВНЫЙ МЫСЛЯЩИЙ ПРОЦЕСС")
    print("  Чат-интерфейс для вопросов к коллективному разуму")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] Установите DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] API ключ: {api_key[:8]}...{api_key[-4:]}")

    # Инициализируем систему мышления
    thinker = InteractiveThinkingProcess(api_key)
    thinker.initialize_system()
    
    # Сохраняем ссылку для HTTP-обработчика
    ThinkingHandler.thinking_system = thinker
    
    # Запускаем сервер
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    port = 8000
    try:
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), ThinkingHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        webbrowser.open(f"http://localhost:{port}/")
        
        print(f"\n  🌐 Чат-интерфейс: http://localhost:{port}/")
        print(f"\n  🎯 Задавайте вопросы в чате!")
        print(f"  🧠 10 агентов готовы мыслить коллективно!")
        print(f"\n  Нажмите Ctrl+C для остановки")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
    except OSError:
        port = 8001
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), ThinkingHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/")
        print(f"\n  🌐 http://localhost:{port}/")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()