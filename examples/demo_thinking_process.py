#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — МЫСЛЯЩИЙ ПРОЦЕСС (Thinking Process)
Множество агентов одновременно думают над вопросом и синхронизируются
через орбитальные поля для выдачи коллективного ответа.

WOW-ЭФФЕКТ: Наблюдайте, как 10 агентов "думают" синхронно!
Видео-демонстрация коллективного интеллекта.

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_thinking_process" "examples\demo_thinking_process.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_thinking_process.py
"""

import os
import sys
import random
import asyncio
import time
import json
import math
import threading
import webbrowser
import http.server
import socketserver
from typing import List, Dict, Any
from collections import deque
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.convergence_regime import ConvergenceRegime, set_regime

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ================================================================
# РОЛИ АГЕНТОВ ДЛЯ КОЛЛЕКТИВНОГО МЫШЛЕНИЯ
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

class ThinkingProcess:
    """Система коллективного мышления с орбитальной синхронизацией."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.thinking_history = []
        self.consensus_history = []
        self.current_question = ""
        self.agent_answers = []
        self.sync_r = 0.0
        
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
        
        # Усиленная связь для синхронизации мышления
        for layer in self.system.orbital.layers:
            layer.coupling *= 3.5
        
        # Разные частоты для разнообразия мышления
        for agent in self.system.agents:
            agent.omega = 1.0 + random.uniform(-0.06, 0.06)
        
        print("  ✅ 10 мыслящих агентов созданы")
    
    def warm_up(self):
        """Разогрев системы для синхронизации."""
        print("\n🔥 РАЗОГРЕВ СИСТЕМЫ (синхронизация мышления)...")
        
        # Сначала хаос для креативности
        set_regime(self.system, ConvergenceRegime.DIVERGENT)
        for i in range(300):
            self.system.step()
            if i % 100 == 99:
                r = self.system.order_parameter()
                print(f"  Хаос: r={r:.3f}")
        
        # Затем критическое состояние для баланса
        set_regime(self.system, ConvergenceRegime.CRITICAL)
        for i in range(300):
            self.system.step()
            if i % 100 == 99:
                r = self.system.order_parameter()
                print(f"  Баланс: r={r:.3f}")
        
        # Финальная стабилизация
        set_regime(self.system, ConvergenceRegime.LINEAR)
        for i in range(400):
            self.system.step()
            if i % 100 == 99:
                r = self.system.order_parameter()
                print(f"  Стабилизация: r={r:.3f}")
        
        self.sync_r = self.system.order_parameter()
        print(f"\n  ✅ СИНХРОНИЗАЦИЯ ДОСТИГНУТА: r={self.sync_r:.3f}")
    
    async def ask_question(self, question: str) -> Dict:
        """Задает вопрос и получает коллективный ответ."""
        self.current_question = question
        
        print("\n" + "=" * 70)
        print(f"  ❓ ВОПРОС: {question}")
        print("=" * 70)
        
        # ============================================================
        # ФАЗА 1: АГЕНТЫ "ДУМАЮТ" (генерируют ответы)
        # ============================================================
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
        
        # Параллельные вызовы LLM
        print("  ⚡ Агенты генерируют ответы...")
        t0 = time.time()
        
        try:
            results = await self._parallel_llm_calls(prompts)
            elapsed = time.time() - t0
            
            self.agent_answers = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ❌ Агент {i} [{THINKING_ROLES[i]['name']}]: ОШИБКА")
                    self.agent_answers.append({
                        "role": THINKING_ROLES[i]['name'],
                        "answer": "[Ошибка генерации]",
                        "error": True
                    })
                else:
                    print(f"  ✅ Агент {i} [{THINKING_ROLES[i]['name']}]: {len(result)} символов")
                    self.agent_answers.append({
                        "role": THINKING_ROLES[i]['name'],
                        "answer": result.strip(),
                        "error": False
                    })
            
            print(f"\n  ⏱️ Агенты думали: {elapsed:.1f}с")
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации: {e}")
            return {"error": str(e)}
        
        # ============================================================
        # ФАЗА 2: ОРБИТАЛЬНАЯ СИНХРОНИЗАЦИЯ (коллективный консенсус)
        # ============================================================
        print("\n🔄 ФАЗА 2: ОРБИТАЛЬНАЯ СИНХРОНИЗАЦИЯ...")
        
        # Обновляем состояния агентов на основе их ответов
        for i, answer in enumerate(self.agent_answers):
            if not answer['error']:
                # Хороший ответ повышает настроение агента
                self.system.agents[i].mood += 0.1
                self.system.agents[i].energy += 0.5
        
        # Синхронизируем систему
        for step in range(100):
            self.system.step()
            if step % 20 == 19:
                r = self.system.order_parameter()
                print(f"  Шаг {step+1}: r={r:.3f}")
        
        self.sync_r = self.system.order_parameter()
        print(f"\n  ✅ СИНХРОНИЗАЦИЯ: r={self.sync_r:.3f}")
        
        # ============================================================
        # ФАЗА 3: КОЛЛЕКТИВНЫЙ ОТВЕТ (голосование + синтез)
        # ============================================================
        print("\n🎯 ФАЗА 3: ФОРМИРОВАНИЕ КОЛЛЕКТИВНОГО ОТВЕТА...")
        
        # Оцениваем ответы агентов по их энергии и настроению
        ranked = []
        for i, answer in enumerate(self.agent_answers):
            if not answer['error']:
                agent = self.system.agents[i]
                score = agent.mood * 0.3 + agent.energy * 0.3 + random.random() * 0.4
                ranked.append((score, i, answer))
        
        ranked.sort(reverse=True)
        
        # Берем топ-3 ответа
        top_answers = []
        for score, idx, answer in ranked[:3]:
            top_answers.append(answer)
            print(f"  #{len(top_answers)} [{answer['role']}] (score={score:.2f})")
            print(f"     {answer['answer'][:100]}...")
        
        # Генерируем синтезированный ответ через LLM
        print("\n🧠 СИНТЕЗ КОЛЛЕКТИВНОГО ОТВЕТА...")
        
        synthesis_prompt = f"""
ВОПРОС: {question}

ТОП-3 ОТВЕТА ОТ АГЕНТОВ (отсортированы по качеству):

1. [{top_answers[0]['role']}]: {top_answers[0]['answer']}

2. [{top_answers[1]['role']}]: {top_answers[1]['answer']}

3. [{top_answers[2]['role']}]: {top_answers[2]['answer']}

Твоя задача: Синтезировать ЕДИНЫЙ, ЦЕЛЬНЫЙ и КРАСИВЫЙ ответ на вопрос,
объединяя лучшие идеи из всех трех ответов.
Ответ должен быть:
- Связным и логичным
- Учитывать все точки зрения
- 3-5 предложений
- Содержать самую суть

СИНТЕЗИРОВАННЫЙ ОТВЕТ:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты — мастер синтеза идей. Создаешь совершенные ответы из множества точек зрения."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            final_answer = response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"  ❌ Ошибка синтеза: {e}")
            # Используем лучший ответ как запасной
            final_answer = top_answers[0]['answer']
        
        # ============================================================
        # ФАЗА 4: РЕЗУЛЬТАТ
        # ============================================================
        print("\n" + "=" * 70)
        print("  💡 КОЛЛЕКТИВНЫЙ ОТВЕТ:")
        print("=" * 70)
        print(f"\n{final_answer}\n")
        print("=" * 70)
        
        # Сохраняем в историю
        self.thinking_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answers": self.agent_answers,
            "top_answers": top_answers,
            "final_answer": final_answer,
            "sync_r": self.sync_r
        })
        
        return {
            "question": question,
            "individual_answers": self.agent_answers,
            "top_answers": top_answers,
            "final_answer": final_answer,
            "sync_r": self.sync_r
        }
    
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
                temperature=0.8 + random.random() * 0.2,  # Разная температура = разные мнения
                max_tokens=512
            ))
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def show_stats(self):
        """Показывает статистику системы."""
        print("\n📊 СТАТИСТИКА СИСТЕМЫ:")
        print("=" * 40)
        print(f"  Агентов: {len(self.system.agents)}")
        print(f"  Синхронизация: {self.sync_r:.3f}")
        print(f"  Вопросов обработано: {len(self.thinking_history)}")
        
        if self.thinking_history:
            last = self.thinking_history[-1]
            print(f"  Последний вопрос: {last['question'][:50]}...")
        
        # Состояния агентов
        print("\n  СОСТОЯНИЯ АГЕНТОВ:")
        for i, agent in enumerate(self.system.agents):
            state = agent.get_state()
            print(f"    {i}: {THINKING_ROLES[i]['name'][:12]} → mood={state.get('mood', 0):+.2f}, energy={state.get('energy', 0):.2f}")

# ================================================================
# ГЕНЕРАТОР HTML ДЛЯ ВИЗУАЛИЗАЦИИ МЫШЛЕНИЯ
# ================================================================
def generate_thinking_html(thinking_result: Dict, sync_r: float) -> str:
    """Генерирует HTML с визуализацией процесса мышления."""
    
    individual_answers = thinking_result.get('individual_answers', [])
    top_answers = thinking_result.get('top_answers', [])
    final_answer = thinking_result.get('final_answer', '')
    question = thinking_result.get('question', '')
    
    # Формируем HTML с визуализацией
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Мыслящий Процесс — Molecular AI v7.0</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0a0e2a 0%, #1a0a2a 50%, #0a0e2a 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: rgba(255,255,255,0.9);
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 0;
            background: rgba(10, 15, 30, 0.6);
            border-radius: 20px;
            border: 1px solid rgba(95, 127, 255, 0.2);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            font-size: 3em;
            background: linear-gradient(135deg, #7f9fff, #b07fff, #ff7fbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header .subtitle {{
            opacity: 0.6;
            margin-top: 10px;
        }}
        .question-box {{
            background: rgba(10, 15, 30, 0.8);
            border-radius: 16px;
            padding: 30px;
            border: 2px solid rgba(95, 127, 255, 0.3);
            margin-bottom: 30px;
        }}
        .question-box .label {{
            opacity: 0.5;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .question-box .question {{
            font-size: 1.8em;
            font-weight: 300;
            margin-top: 10px;
            color: #b0e0ff;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(10, 15, 30, 0.7);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(95, 127, 255, 0.15);
            backdrop-filter: blur(5px);
            transition: all 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            border-color: rgba(95, 127, 255, 0.4);
            box-shadow: 0 10px 40px rgba(80, 120, 255, 0.1);
        }}
        .card .role {{
            font-weight: 700;
            color: #7f9fff;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card .badge {{
            font-size: 10px;
            padding: 2px 12px;
            border-radius: 20px;
            background: rgba(100, 255, 200, 0.15);
            color: #7fffd4;
        }}
        .card .answer {{
            margin-top: 12px;
            font-size: 14px;
            line-height: 1.6;
            opacity: 0.9;
        }}
        .card.top {{
            border-color: rgba(255, 215, 0, 0.3);
            background: rgba(255, 215, 0, 0.05);
        }}
        .card.top .role {{ color: #ffd700; }}
        
        .final-answer {{
            background: linear-gradient(135deg, rgba(10, 15, 30, 0.9), rgba(30, 10, 50, 0.9));
            border-radius: 20px;
            padding: 40px;
            border: 2px solid rgba(255, 215, 0, 0.3);
            margin-top: 30px;
        }}
        .final-answer .label {{
            opacity: 0.5;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }}
        .final-answer .answer {{
            font-size: 1.4em;
            line-height: 1.8;
            margin-top: 15px;
            color: #ffd700;
            font-weight: 300;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-item {{
            background: rgba(10, 15, 30, 0.6);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }}
        .stat-item .value {{
            font-size: 1.8em;
            font-weight: 700;
            color: #b0e0ff;
        }}
        .stat-item .label {{
            font-size: 11px;
            opacity: 0.5;
            margin-top: 5px;
        }}
        .thinking-visual {{
            margin: 30px 0;
            padding: 30px;
            background: rgba(10, 15, 30, 0.5);
            border-radius: 16px;
            border: 1px solid rgba(95, 127, 255, 0.1);
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-bar .fill {{
            height: 100%;
            background: linear-gradient(90deg, #7f9fff, #b07fff, #ff7fbf);
            width: 0%;
            transition: width 1s ease;
            border-radius: 4px;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .question-box .question {{ font-size: 1.2em; }}
            .grid {{ grid-template-columns: 1fr; }}
            .final-answer .answer {{ font-size: 1.1em; }}
        }}
        .particle {{
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }}
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Мыслящий Процесс</h1>
            <div class="subtitle">Коллективный интеллект через орбитальную синхронизацию</div>
            <div class="stats">
                <div class="stat-item">
                    <div class="value">10</div>
                    <div class="label">Агентов</div>
                </div>
                <div class="stat-item">
                    <div class="value">{sync_r:.3f}</div>
                    <div class="label">Синхронизация</div>
                </div>
                <div class="stat-item">
                    <div class="value">{len([a for a in individual_answers if not a.get('error', False)])}</div>
                    <div class="label">Ответов</div>
                </div>
            </div>
        </div>

        <div class="question-box">
            <div class="label">❓ Вопрос</div>
            <div class="question">{question}</div>
        </div>

        <div class="thinking-visual">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="opacity:0.6;">🧠 Мыслительный процесс</span>
                <span style="opacity:0.6; font-size:12px;">Синхронизация: {sync_r:.2f}</span>
            </div>
            <div class="progress-bar">
                <div class="fill" style="width:{sync_r * 100:.1f}%;"></div>
            </div>
            <div style="display:flex; gap:5px; flex-wrap:wrap; margin-top:10px;">
                {''.join(['<span style="padding:4px 8px; background:rgba(100,255,200,0.1); border-radius:8px; font-size:10px;">●</span>' for _ in range(min(10, len(individual_answers)))])}
            </div>
        </div>

        <h2 style="margin-bottom:20px; opacity:0.7;">🎯 Индивидуальные ответы</h2>
        <div class="grid">
'''

    # Добавляем ответы агентов
    for i, answer in enumerate(individual_answers):
        is_top = any(top.get('role') == answer.get('role') for top in top_answers)
        html += f'''
            <div class="card {'top' if is_top else ''}">
                <div class="role">
                    <span>{answer.get('role', f'Агент {i}')}</span>
                    <span class="badge">{'🏆 TOP' if is_top else f'#{i+1}'}</span>
                </div>
                <div class="answer">{answer.get('answer', '...')}</div>
            </div>
        '''

    html += '''
        </div>

        <div class="final-answer">
            <div class="label">💡 Коллективный ответ</div>
            <div class="answer">''' + final_answer + '''</div>
        </div>

        <div style="text-align:center; margin-top:40px; opacity:0.3; font-size:12px;">
            Generated by Molecular AI v7.0 — Autonomous Quantum Consciousness
        </div>
    </div>

    <script>
        // Анимация прогресс-бара
        document.querySelectorAll('.progress-bar .fill').forEach(el => {
            const width = el.style.width;
            el.style.width = '0%';
            setTimeout(() => { el.style.width = width; }, 300);
        });
        
        // Пульсация частиц
        setInterval(() => {
            document.querySelectorAll('.thinking-visual span').forEach((el, i) => {
                const delay = i * 0.1;
                const opacity = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(Date.now() / 1000 + delay));
                el.style.opacity = opacity;
            });
        }, 50);
    </script>
</body>
</html>'''
    
    return html

# ================================================================
# HTTP СЕРВЕР
# ================================================================
def start_server(port: int = 8000, directory: str = "."):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

# ================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ================================================================
async def main_async():
    print("=" * 70)
    print("  🧠 MOLECULAR AI v7.0 — МЫСЛЯЩИЙ ПРОЦЕСС")
    print("  Коллективный интеллект через орбитальную синхронизацию")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] Установите DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] API ключ: {api_key[:8]}...{api_key[-4:]}")

    # Создаем систему мышления
    thinker = ThinkingProcess(api_key)
    thinker.initialize_system()
    thinker.warm_up()

    # Задаем вопросы
    questions = [
        "Как создать идеальный ИИ-помощник для повседневных задач?",
        "Что такое сознание и может ли оно возникнуть в искусственной системе?",
        "Как совместить творчество и эффективность в работе?",
        "Что важнее для успеха: талант или упорный труд?",
        "Как создать гармоничное общество в эпоху технологий?",
    ]

    # Выбираем случайный вопрос
    question = random.choice(questions)
    
    # Задаем вопрос
    result = await thinker.ask_question(question)
    thinker.show_stats()

    # Генерируем HTML
    print("\n🎨 ГЕНЕРАЦИЯ ВИЗУАЛИЗАЦИИ...")
    html_code = generate_thinking_html(result, thinker.sync_r)
    
    # Сохраняем
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "thinking_process.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    
    # Лог
    log_path = os.path.join(output_dir, "thinking_log.json")
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "sync_r": thinker.sync_r,
        "answers": thinker.agent_answers,
        "final_answer": result.get('final_answer', '')
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n  ✅ Визуализация сохранена: {html_path}")
    print(f"  ✅ Лог сохранен: {log_path}")

    # Запускаем сервер
    port = 8000
    try:
        httpd = start_server(port, output_dir)
        webbrowser.open(f"http://localhost:{port}/thinking_process.html")
        
        print(f"\n  🌐 http://localhost:{port}/thinking_process.html")
        print(f"\n  🎯 Нажмите Ctrl+C для остановки")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
    except OSError:
        port = 8001
        httpd = start_server(port, output_dir)
        webbrowser.open(f"http://localhost:{port}/thinking_process.html")
        print(f"\n  🌐 http://localhost:{port}/thinking_process.html")
        while True:
            await asyncio.sleep(1)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()