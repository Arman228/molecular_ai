#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — МЕТА-КОГНИТИВНАЯ СИСТЕМА (Исправленная)
С протоколом реверсивного сомнения и когнитивным сбросом

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_metacognitive_fixed" "examples\demo_metacognitive_fixed.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_metacognitive_fixed.py
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
ROLES = [
    {"name": "Скептик", "persona": "Сомневается во всём, ищет слабые места."},
    {"name": "Критик", "persona": "Атакует идеи, находит логические ошибки."},
    {"name": "Синтезатор", "persona": "Собирает лучшее из разных идей."},
    {"name": "Инноватор", "persona": "Генерирует прорывные идеи."},
    {"name": "Рефлексиолог", "persona": "Анализирует процесс мышления."},
    {"name": "Философ", "persona": "Ищет глубинные смыслы."},
    {"name": "Прагматик", "persona": "Проверяет практичность."},
    {"name": "Эксперт", "persona": "Глубокие знания в области."},
    {"name": "Хаос-инженер", "persona": "Вносит конструктивный хаос."},
    {"name": "Мета-мыслитель", "persona": "Управляет пересборкой идей."},
]

class MetacognitiveSystem:
    """Мета-когнитивная система с реверсивным сомнением."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.sync_r = 0.0
        self.iteration = 0
        self.thoughts = []
        self.skepticism_level = 0.7
        self.cognitive_reset_counter = 0
        
    def initialize(self):
        """Инициализация системы."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ МЕТА-КОГНИТИВНОЙ СИСТЕМЫ...")
        
        self.system = MolecularSystem(
            n_agents=10,
            dt=0.02,
            noise=0.03,
            sleep_every=400,
            k_sparse=6,
            exc_ratio=0.9
        )
        
        for layer in self.system.orbital.layers:
            layer.coupling *= 4.0
        
        for agent in self.system.agents:
            agent.omega = 1.0 + random.uniform(-0.08, 0.08)
        
        print("  ✅ 10 агентов созданы")
        self._warm_up()
    
    def _warm_up(self):
        """Разогрев системы."""
        print("\n🔥 РАЗОГРЕВ СИСТЕМЫ...")
        
        set_regime(self.system, ConvergenceRegime.DIVERGENT)
        for i in range(200):
            self.system.step()
            if i % 100 == 99:
                print(f"  Хаос: r={self.system.order_parameter():.3f}")
        
        set_regime(self.system, ConvergenceRegime.CRITICAL)
        for i in range(200):
            self.system.step()
            if i % 100 == 99:
                print(f"  Баланс: r={self.system.order_parameter():.3f}")
        
        set_regime(self.system, ConvergenceRegime.LINEAR)
        for i in range(300):
            self.system.step()
            if i % 100 == 99:
                print(f"  Стабильность: r={self.system.order_parameter():.3f}")
        
        self.sync_r = self.system.order_parameter()
        print(f"\n  ✅ СИНХРОНИЗАЦИЯ: r={self.sync_r:.3f}")
    
    async def think(self, question: str) -> Dict:
        """Процесс мышления с реверсивным сомнением."""
        self.iteration += 1
        
        print("\n" + "=" * 70)
        print(f"  🧠 ЦИКЛ МЫШЛЕНИЯ #{self.iteration}")
        print(f"  ❓ {question}")
        print("=" * 70)
        
        # ФАЗА 1: ГЕНЕРАЦИЯ ИДЕЙ
        print("\n💡 ФАЗА 1: ГЕНЕРАЦИЯ ИДЕЙ")
        ideas = await self._generate_ideas(question)
        
        # ФАЗА 2: РЕВЕРСИВНОЕ СОМНЕНИЕ
        print("\n🔍 ФАЗА 2: РЕВЕРСИВНОЕ СОМНЕНИЕ")
        weaknesses = await self._find_weaknesses(ideas)
        
        # ФАЗА 3: ПЕРЕСБОРКА
        print("\n🔄 ФАЗА 3: ДИНАМИЧЕСКАЯ ПЕРЕСБОРКА")
        rebuilt = await self._rebuild_ideas(ideas, weaknesses)
        
        # ФАЗА 4: КОГНИТИВНЫЙ СБРОС
        reset_triggered = self._should_reset()
        if reset_triggered:
            print("\n🧹 ФАЗА 4: КОГНИТИВНЫЙ СБРОС")
            await self._cognitive_reset()
        
        # ФАЗА 5: ФИНАЛЬНЫЙ ОТВЕТ
        print("\n🎯 ФАЗА 5: ФИНАЛЬНЫЙ СИНТЕЗ")
        final_answer = await self._synthesize(question, rebuilt, weaknesses)
        
        result = {
            "question": question,
            "iteration": self.iteration,
            "ideas": [{"role": i["role"], "text": i["text"][:200]} for i in ideas[:5]],
            "weaknesses": weaknesses,
            "rebuilt": [{"role": r["role"], "text": r["text"][:200]} for r in rebuilt],
            "final_answer": final_answer,
            "sync_r": self.sync_r,
            "reset_triggered": reset_triggered
        }
        
        self.thoughts.append(result)
        
        print("\n" + "=" * 70)
        print("  💡 ФИНАЛЬНЫЙ ОТВЕТ:")
        print("=" * 70)
        print(f"\n{final_answer}\n")
        print("=" * 70)
        
        return result
    
    async def _generate_ideas(self, question: str) -> List[Dict]:
        """Генерация идей."""
        prompts = []
        for i, role in enumerate(ROLES):
            state = self.system.agents[i].get_state()
            prompt = f"""
Ты — {role['name']}. Твоя роль: {role['persona']}

ВОПРОС: {question}

Дай ответ с точки зрения твоей роли. 2-3 предложения.
Будь конкретным и оригинальным.

ОТВЕТ:
"""
            prompts.append(prompt)
        
        print(f"  ⚡ 10 агентов генерируют идеи...")
        t0 = time.time()
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            tasks = []
            for prompt in prompts:
                tasks.append(client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.85,
                    max_tokens=256
                ))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - t0
            
            ideas = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    ideas.append({"role": ROLES[i]["name"], "text": "[Ошибка]"})
                else:
                    text = result.choices[0].message.content.strip()
                    ideas.append({"role": ROLES[i]["name"], "text": text})
                    print(f"  ✅ {ROLES[i]['name']}: {text[:60]}...")
            
            print(f"\n  ⏱️ Генерация: {elapsed:.1f}с")
            return ideas
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return [{"role": "Система", "text": "Ошибка генерации"}]
    
    async def _find_weaknesses(self, ideas: List[Dict]) -> List[Dict]:
        """Нахождение слабых мест."""
        critic_roles = ['Скептик', 'Критик', 'Философ', 'Рефлексиолог']
        critic_indices = [i for i, r in enumerate(ROLES) if r["name"] in critic_roles]
        
        weaknesses = []
        
        for idx in critic_indices[:3]:
            role = ROLES[idx]
            ideas_text = "\n".join([
                f"{i+1}. [{idea['role']}]: {idea['text'][:150]}"
                for i, idea in enumerate(ideas[:5])
            ])
            
            prompt = f"""
Ты — {role['name']}. Твоя роль: {role['persona']}

Проанализируй эти идеи и найди СЛАБЫЕ МЕСТА:

{ideas_text}

Найди: логические ошибки, предвзятости, пробелы в аргументации.
2-3 предложения.

СЛАБЫЕ МЕСТА:
"""
            
            try:
                client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
                
                response = await client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=256
                )
                
                text = response.choices[0].message.content.strip()
                weaknesses.append({"critic": role["name"], "text": text})
                print(f"  🔍 {role['name']}: {text[:60]}...")
                
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
        
        return weaknesses
    
    async def _rebuild_ideas(self, ideas: List[Dict], weaknesses: List[Dict]) -> List[Dict]:
        """Пересборка идей."""
        builder_roles = ['Синтезатор', 'Инноватор', 'Мета-мыслитель', 'Прагматик']
        builder_indices = [i for i, r in enumerate(ROLES) if r["name"] in builder_roles]
        
        rebuilt = []
        
        for idx in builder_indices[:3]:
            role = ROLES[idx]
            
            ideas_text = "\n".join([
                f"{i+1}. [{idea['role']}]: {idea['text'][:150]}"
                for i, idea in enumerate(ideas[:5])
            ])
            
            weaknesses_text = "\n".join([
                f"- {w['critic']}: {w['text']}"
                for w in weaknesses
            ]) if weaknesses else "Нет слабых мест"
            
            prompt = f"""
Ты — {role['name']}. Твоя роль: {role['persona']}

ИСХОДНЫЕ ИДЕИ:
{ideas_text}

СЛАБЫЕ МЕСТА:
{weaknesses_text}

Создай УЛУЧШЕННУЮ версию идей с учетом слабых мест.
2-3 предложения.

УЛУЧШЕННАЯ ИДЕЯ:
"""
            
            try:
                client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
                
                response = await client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.85,
                    max_tokens=256
                )
                
                text = response.choices[0].message.content.strip()
                rebuilt.append({"role": role["name"], "text": text})
                print(f"  🔄 {role['name']}: {text[:60]}...")
                
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
        
        return rebuilt
    
    def _should_reset(self) -> bool:
        """Определяет, нужен ли когнитивный сброс."""
        self.cognitive_reset_counter += 1
        return self.cognitive_reset_counter % 3 == 0
    
    async def _cognitive_reset(self):
        """Выполняет когнитивный сброс."""
        print("  🧹 ВЫПОЛНЕНИЕ КОГНИТИВНОГО СБРОСА...")
        
        set_regime(self.system, ConvergenceRegime.DIVERGENT)
        for i in range(50):
            self.system.step()
        
        for agent in self.system.agents:
            agent.mood = random.uniform(-0.5, 0.5)
            agent.energy = random.uniform(0.3, 0.7)
            agent.omega = 1.0 + random.uniform(-0.05, 0.05)
        
        set_regime(self.system, ConvergenceRegime.CRITICAL)
        for i in range(100):
            self.system.step()
        
        set_regime(self.system, ConvergenceRegime.LINEAR)
        for i in range(100):
            self.system.step()
        
        self.sync_r = self.system.order_parameter()
        print(f"  ✅ КОГНИТИВНЫЙ СБРОС ВЫПОЛНЕН! r={self.sync_r:.3f}")
    
    async def _synthesize(self, question: str, rebuilt: List[Dict], weaknesses: List[Dict]) -> str:
        """Финальный синтез."""
        ideas_text = "\n".join([
            f"{i+1}. [{idea['role']}]: {idea['text']}"
            for i, idea in enumerate(rebuilt[:3])
        ]) if rebuilt else "Нет идей"
        
        prompt = f"""
ВОПРОС: {question}

ЛУЧШИЕ ПЕРЕСОБРАННЫЕ ИДЕИ:
{ideas_text}

Создай ФИНАЛЬНЫЙ, ЦЕЛЬНЫЙ, ГЛУБОКИЙ ответ.
3-5 предложений.

ФИНАЛЬНЫЙ ОТВЕТ:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return "Ошибка синтеза"

# ================================================================
# HTML ДЛЯ ВЕБ-ЧАТА
# ================================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Мета-Когнитивная Система</title>
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
            padding: 15px 25px;
            background: rgba(10, 15, 30, 0.9);
            border-bottom: 1px solid rgba(95, 127, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 {
            font-size: 1.3em;
            background: linear-gradient(135deg, #7f9fff, #b07fff, #ff7fbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header .status {
            font-size: 11px;
            opacity: 0.7;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
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
        .status .badge {
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge.sync { background: rgba(100, 255, 200, 0.15); color: #7fffd4; border: 1px solid rgba(100, 255, 200, 0.15); }
        .badge.skeptic { background: rgba(255, 100, 100, 0.2); color: #ff7f7f; border: 1px solid rgba(255, 100, 100, 0.2); }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 25px;
            display: flex;
            flex-direction: column;
            gap: 12px;
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
            max-width: 85%;
            padding: 14px 18px;
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
        .message.meta {
            align-self: flex-start;
            background: rgba(255, 215, 0, 0.05);
            border: 1px solid rgba(255, 215, 0, 0.15);
            border-left: 3px solid #ffd700;
        }
        .message .role {
            font-size: 10px;
            opacity: 0.5;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .message .text {
            line-height: 1.6;
            font-size: 14px;
        }
        .message .text .highlight { color: #ffd700; font-weight: 600; }
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
            padding: 15px 25px;
            background: rgba(10, 15, 30, 0.9);
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
            white-space: nowrap;
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
            padding: 8px 25px;
            flex-wrap: wrap;
            flex-shrink: 0;
            background: rgba(10, 15, 30, 0.3);
        }
        .suggestions button {
            padding: 5px 14px;
            border-radius: 20px;
            border: 1px solid rgba(95, 127, 255, 0.15);
            background: rgba(10, 15, 30, 0.6);
            color: rgba(255,255,255,0.6);
            cursor: pointer;
            font-size: 11px;
            transition: all 0.3s;
        }
        .suggestions button:hover {
            background: rgba(63, 104, 255, 0.2);
            border-color: rgba(95, 127, 255, 0.3);
        }
        
        @media (max-width: 768px) {
            .header { padding: 12px 15px; }
            .header h1 { font-size: 1em; }
            .chat-container { padding: 12px 15px; }
            .message { max-width: 95%; padding: 12px 14px; }
            .input-container { padding: 12px 15px; flex-direction: column; }
            .input-container button { width: 100%; }
            .suggestions { padding: 8px 15px; }
            .suggestions button { font-size: 10px; padding: 4px 10px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Мета-Когнитивная Система</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="agentStatus">10 агентов</span>
            <span id="syncStatus" class="badge sync">sync: 0.00</span>
            <span id="skepticStatus" class="badge skeptic">скепсис: 0.00</span>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="role">🧠 Система</div>
            <div class="text">
                Привет! Я — <span class="highlight">Мета-Когнитивная Система</span>.<br>
                Я <span class="highlight">сомневаюсь</span> в своих выводах, ищу <span class="highlight">слабые места</span> 
                и <span class="highlight">пересобираю</span> идеи.<br>
                Задай вопрос, и я пройду через <span class="highlight">5 фаз мышления</span>!
            </div>
        </div>
    </div>
    
    <div class="suggestions" id="suggestions">
        <button onclick="askQuestion('Что такое сознание и может ли оно возникнуть в ИИ?')">🧠 Сознание в ИИ</button>
        <button onclick="askQuestion('Как создать идеальный ИИ-помощник для творческих задач?')">🎨 Творческий ИИ</button>
        <button onclick="askQuestion('Что важнее для успеха: талант или упорный труд?')">⭐ Талант vs Труд</button>
        <button onclick="askQuestion('Как изменить свою жизнь за год?')">🚀 Изменение жизни</button>
        <button onclick="askQuestion('Какие качества делают человека лидером?')">👑 Лидерство</button>
    </div>
    
    <div class="input-container">
        <input id="questionInput" placeholder="Задайте вопрос для мета-когнитивного анализа..." 
               onkeypress="if(event.key==='Enter') askQuestion()">
        <button id="sendButton" onclick="askQuestion()">💬 Задать вопрос</button>
    </div>
    
    <script>
        let isProcessing = false;
        
        function addMessage(role, content, isThinking = false) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            if (isThinking) {
                div.innerHTML = `
                    <div class="role">🧠 Система думает...</div>
                    <div class="thinking">
                        <span></span><span></span><span></span>
                    </div>
                `;
            } else {
                const roleIcon = role === 'user' ? '👤' : role === 'meta' ? '🔍' : '🧠';
                const roleName = role === 'user' ? 'Вы' : role === 'meta' ? 'Мета-анализ' : 'Коллективный разум';
                div.innerHTML = `
                    <div class="role">${roleIcon} ${roleName}</div>
                    <div class="text">${content}</div>
                `;
            }
            
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function updateStatus(data) {
            if (data.sync_r) {
                document.getElementById('syncStatus').textContent = `sync: ${data.sync_r.toFixed(3)}`;
            }
            if (data.skepticism) {
                document.getElementById('skepticStatus').textContent = `скепсис: ${data.skepticism.toFixed(2)}`;
            }
            if (data.agents) {
                document.getElementById('agentStatus').textContent = `${data.agents} агентов`;
            }
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
            button.textContent = '🧠 Думаем...';
            
            addMessage('user', question);
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
                    // Показываем слабости
                    if (data.weaknesses && data.weaknesses.length > 0) {
                        let weakText = '🔍 Выявленные слабые места:<br>';
                        data.weaknesses.forEach(w => {
                            weakText += `<br>• ${w.critic}: ${w.text}`;
                        });
                        addMessage('meta', weakText);
                    }
                    
                    // Показываем финальный ответ
                    addMessage('agent', '✨ ' + data.final_answer);
                    
                    // Информация о когнитивном сбросе
                    if (data.reset_triggered) {
                        addMessage('meta', '🧹 КОГНИТИВНЫЙ СБРОС ВЫПОЛНЕН! Система сбросила инерцию мышления.');
                    }
                    
                    updateStatus(data);
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
            button.textContent = '💬 Задать вопрос';
        }
        
        async function getStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                updateStatus(data);
            } catch (e) {}
        }
        
        setInterval(getStatus, 3000);
        getStatus();
    </script>
</body>
</html>'''

# ================================================================
# HTTP-СЕРВЕР
# ================================================================
class MetacognitiveHandler(http.server.SimpleHTTPRequestHandler):
    system = None
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                'sync_r': self.system.sync_r if self.system else 0,
                'agents': 10,
                'skepticism': self.system.skepticism_level if self.system else 0
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/ask':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                question = data.get('question', '')
                
                if not question:
                    self.send_error(400, "No question provided")
                    return
                
                # Запускаем обработку вопроса
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.system.think(question))
                loop.close()
                
                # Формируем ответ
                response = {
                    'question': question,
                    'iteration': result['iteration'],
                    'weaknesses': result.get('weaknesses', []),
                    'final_answer': result.get('final_answer', ''),
                    'sync_r': result.get('sync_r', 0),
                    'reset_triggered': result.get('reset_triggered', False)
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
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
    print("  🧠 MOLECULAR AI v7.0 — МЕТА-КОГНИТИВНАЯ СИСТЕМА")
    print("  Протокол реверсивного сомнения + когнитивный сброс")
    print("=" * 70)

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("\n[!] Установите DEEPSEEK_API_KEY=sk-...")
        return
    if not HAS_OPENAI:
        print("\n[!] pip install openai")
        return

    print(f"\n[OK] API ключ: {api_key[:8]}...{api_key[-4:]}")

    # Инициализация системы
    system = MetacognitiveSystem(api_key)
    system.initialize()
    
    # Сохраняем ссылку для обработчика
    MetacognitiveHandler.system = system
    
    # Запускаем сервер
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    port = 8000
    try:
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), MetacognitiveHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        webbrowser.open(f"http://localhost:{port}/")
        
        print(f"\n  🌐 Чат-интерфейс: http://localhost:{port}/")
        print(f"\n  🧠 СИСТЕМА ГОТОВА!")
        print(f"  🔍 Активен протокол реверсивного сомнения")
        print(f"  🧹 Когнитивный сброс каждые 3 цикла")
        print(f"\n  Нажмите Ctrl+C для остановки")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
    except OSError:
        port = 8001
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), MetacognitiveHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/")
        print(f"\n  🌐 http://localhost:{port}/")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()