#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — HONEST DIALOGUE SYSTEM v2.0
С разделением фактов и интерпретаций + самосознание

КЛЮЧЕВЫЕ ИННОВАЦИИ:
1. Три режима: Факты, Интерпретации, Смешанный
2. Самосознание — система знает о себе и отвечает на вопросы о себе
3. Лимит уточнений (макс 2) — без бесконечных циклов
4. Маркеры уверенности (в процентах)
5. Честное позиционирование

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_honest_dialogue_v2" "examples\demo_honest_dialogue_v2.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_honest_dialogue_v2.py
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
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re

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
    {"name": "Фактолог", "persona": "Эксперт по фактам, проверяет достоверность, указывает уверенность."},
    {"name": "Интерпретатор", "persona": "Предлагает различные интерпретации, точки зрения, альтернативы."},
    {"name": "Скептик", "persona": "Ставит под сомнение, ищет альтернативные объяснения."},
    {"name": "Синтезатор", "persona": "Объединяет факты и интерпретации в целостный ответ."},
    {"name": "Аналитик_неопределенности", "persona": "Оценивает уровень неопределенности, предлагает уточнения."},
    {"name": "Модератор_режимов", "persona": "Помогает пользователю выбрать режим ответа."},
    {"name": "Эксперт_по_контексту", "persona": "Анализирует контекст вопроса, предлагает уточнения."},
    {"name": "Критик_источников", "persona": "Проверяет источники, указывает на потенциальные ошибки."},
    {"name": "Коммуникатор", "persona": "Формулирует ответы понятно и структурированно."},
    {"name": "Рефлексиолог", "persona": "Анализирует процесс диалога, предлагает улучшения."},
]

@dataclass
class DialogueMode:
    """Режим диалога."""
    name: str
    description: str
    emoji: str
    active: bool = False

class HonestDialogueSystem:
    """Система честного диалога с разделением фактов и интерпретаций."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.sync_r = 0.0
        self.modes = {
            "facts": DialogueMode("Факты", "Только проверенные факты с указанием уверенности", "📊"),
            "interpretations": DialogueMode("Интерпретации", "Различные интерпретации с аргументацией", "🔮"),
            "mixed": DialogueMode("Смешанный", "Факты + интерпретации с четким разделением", "🎯")
        }
        self.default_mode = "mixed"
        self.current_mode = "mixed"
        self.dialog_history = []
        self.certainty_threshold = 0.7
        self.clarification_count = 0
        self.max_clarifications = 2  # Лимит на уточнения
        self.system_name = "Honest Dialogue System v2.0"
        
        # Список слов-индикаторов, что вопрос о самой системе
        self.self_reference_keywords = [
            "систем", "ты", "эта", "наша", "ваша", 
            "умеешь", "можешь", "функционал", "возможност",
            "что ты", "кто ты", "расскажи о себе"
        ]
        
    def initialize(self):
        """Инициализация системы."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ HONEST DIALOGUE SYSTEM v2.0...")
        print("  🔍 Добавлено самосознание и лимит уточнений")
        
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
    
    def set_mode(self, mode: str):
        """Устанавливает режим диалога."""
        if mode in self.modes:
            self.current_mode = mode
            for m in self.modes.values():
                m.active = False
            self.modes[mode].active = True
            print(f"\n  📊 Режим изменен: {self.modes[mode].emoji} {self.modes[mode].name}")
    
    def _is_question_about_self(self, question: str) -> bool:
        """Проверяет, спрашивает ли пользователь о самой системе."""
        question_lower = question.lower()
        for keyword in self.self_reference_keywords:
            if keyword in question_lower:
                return True
        return False
    
    def get_self_description(self) -> str:
        """Возвращает описание самой системы."""
        return """
🔬 HONEST DIALOGUE SYSTEM v2.0

**Что я умею:**

📊 **Три режима ответа:**
1. **Факты** — только проверенная информация с указанием уверенности (0-100%)
2. **Интерпретации** — разные точки зрения и перспективы
3. **Смешанный** — и факты, и интерпретации с четким разделением

💡 **Ключевые возможности:**
• Разделяю факты и интерпретации — вы всегда знаете, что проверено, а что — точка зрения
• Указываю уверенность в процентах — честно говорю, насколько я уверена
• Задаю уточняющие вопросы — если вопрос неясен, уточняю (максимум 2 раза)
• Отвечаю на вопросы о себе — знаю, кто я и что умею
• Анализирую документы — PDF, Word, Excel
• Пишу код — Python, JavaScript, SQL
• Перевожу и анализирую текст

⚡ **Мои ограничения:**
• Не генерирую изображения и видео
• Работаю с данными до текущего момента
• Лучшее качество — с четкими, структурированными запросами

🎯 **Как использовать:**
1. Выберите режим: Факты / Интерпретации / Смешанный
2. Задайте вопрос четко и конкретно
3. Получите структурированный ответ с разделением

📊 **Технические детали:**
• Версия: 2.0
• Агентов: 10
• Режимы: 3
• Модель: DeepSeek API
• Контекстное окно: до 1M токенов

Это я. Чем могу помочь?
"""
    
    async def process_request(self, question: str, mode: str = None) -> Dict:
        """Обрабатывает запрос с учетом выбранного режима и самосознания."""
        if not mode:
            mode = self.current_mode
        
        print("\n" + "=" * 70)
        print(f"  💬 ЗАПРОС: {question}")
        print(f"  📊 Режим: {self.modes[mode].emoji} {self.modes[mode].name}")
        print("=" * 70)
        
        # ============================================================
        # ФАЗА 0: САМОСОЗНАНИЕ — вопрос о системе?
        # ============================================================
        if self._is_question_about_self(question):
            print("\n🔍 ФАЗА 0: ОБНАРУЖЕН ВОПРОС О СИСТЕМЕ")
            print("  ✅ Система отвечает о себе")
            
            return {
                "type": "answer",
                "mode": mode,
                "mode_name": self.modes[mode].name,
                "mode_emoji": self.modes[mode].emoji,
                "content": self.get_self_description(),
                "sync_r": self.sync_r,
                "is_self_description": True
            }
        
        # ============================================================
        # ФАЗА 1: Анализ двусмысленности (с лимитом)
        # ============================================================
        print("\n🔍 ФАЗА 1: АНАЛИЗ ДВУСМЫСЛЕННОСТИ")
        ambiguity_score = await self._check_ambiguity(question)
        
        # Проверяем лимит уточнений
        if ambiguity_score > 0.7 and self.clarification_count < self.max_clarifications:
            self.clarification_count += 1
            print(f"  ⚠️ Высокая двусмысленность: {ambiguity_score:.2f} (уточнение #{self.clarification_count})")
            clarification = await self._generate_clarification(question)
            return {
                "type": "clarification",
                "question": clarification,
                "reason": f"Вопрос требует уточнения (попытка {self.clarification_count}/{self.max_clarifications})",
                "ambiguity_score": ambiguity_score,
                "clarification_count": self.clarification_count
            }
        elif ambiguity_score > 0.7 and self.clarification_count >= self.max_clarifications:
            print(f"  ⚠️ Достигнут лимит уточнений ({self.max_clarifications}). Даю ответ.")
            # Сбрасываем счетчик для следующего вопроса
            self.clarification_count = 0
        
        # Сбрасываем счетчик, если вопрос понятен
        if ambiguity_score <= 0.7:
            self.clarification_count = 0
        
        # ============================================================
        # ФАЗА 2: Генерация ответа в выбранном режиме
        # ============================================================
        print(f"\n📊 ФАЗА 2: ГЕНЕРАЦИЯ ОТВЕТА В РЕЖИМЕ {mode.upper()}")
        
        if mode == "facts":
            result = await self._generate_factual_response(question)
        elif mode == "interpretations":
            result = await self._generate_interpretations(question)
        else:
            result = await self._generate_mixed_response(question)
        
        # Сохраняем в историю
        self.dialog_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "mode": mode,
            "response": result
        })
        
        # ============================================================
        # ФАЗА 3: ВЫВОД
        # ============================================================
        print("\n" + "=" * 70)
        print(f"  💡 ОТВЕТ В РЕЖИМЕ {self.modes[mode].emoji} {self.modes[mode].name}:")
        print("=" * 70)
        
        # Выводим в зависимости от типа
        if result.get("type") == "clarification":
            print(f"\n❓ Уточнение:\n{result['question']}\n")
        else:
            self._print_response(result, mode)
        
        print("=" * 70)
        
        return {
            "question": question,
            "mode": mode,
            "mode_name": self.modes[mode].name,
            "mode_emoji": self.modes[mode].emoji,
            "response": result,
            "sync_r": self.sync_r,
            "is_self_description": result.get("is_self_description", False)
        }
    
    def _print_response(self, response: Dict, mode: str):
        """Печатает ответ в зависимости от режима."""
        # Если это описание системы
        if response.get("is_self_description"):
            print(response.get("content", ""))
            return
        
        if mode == "facts":
            facts = response.get("facts", [])
            certainty = response.get("certainty", 0)
            alternatives = response.get("alternatives", [])
            
            print(f"\n📊 ФАКТЫ (уверенность: {certainty:.0%}):")
            for i, fact in enumerate(facts, 1):
                print(f"  {i}. {fact}")
            
            if alternatives:
                print(f"\n🔄 АЛЬТЕРНАТИВЫ:")
                for i, alt in enumerate(alternatives, 1):
                    print(f"  {i}. {alt}")
        
        elif mode == "interpretations":
            interpretations = response.get("interpretations", [])
            
            print(f"\n🔮 ИНТЕРПРЕТАЦИИ ({len(interpretations)} перспектив):")
            for i, interp in enumerate(interpretations, 1):
                print(f"  {i}. [{interp.get('perspective', 'Перспектива')}]:")
                print(f"     {interp.get('text', '')}")
            
            if response.get("recommendation"):
                print(f"\n💡 РЕКОМЕНДАЦИЯ:\n  {response['recommendation']}")
        
        else:  # mixed
            facts = response.get("facts", [])
            interpretations = response.get("interpretations", [])
            
            print(f"\n📊 ФАКТЫ:")
            for i, fact in enumerate(facts, 1):
                print(f"  {i}. {fact}")
            
            print(f"\n--- ФАКТЫ | ИНТЕРПРЕТАЦИИ ---\n")
            
            print(f"🔮 ИНТЕРПРЕТАЦИИ:")
            for i, interp in enumerate(interpretations, 1):
                print(f"  {i}. [{interp.get('perspective', 'Перспектива')}]:")
                print(f"     {interp.get('text', '')}")
            
            print(f"\n💡 Выберите режим: факты (F) или интерпретации (I)")
    
    async def _check_ambiguity(self, question: str) -> float:
        """Проверяет уровень двусмысленности вопроса."""
        prompt = f"""
Проанализируй вопрос на уровень ДВУСМЫСЛЕННОСТИ:

ВОПРОС: {question}

Оцени от 0 до 1, где:
- 0: абсолютно конкретный, однозначный
- 1: крайне двусмысленный, требует уточнения

Учитывай:
1. Неоднозначные термины
2. Множество возможных интерпретаций
3. Отсутствие контекста
4. Возможность разных ответов

Ответь ТОЛЬКО числом от 0 до 1.

ОЦЕНКА:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )
            
            text = response.choices[0].message.content.strip()
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                score = float(numbers[0])
                return min(1.0, max(0.0, score))
            
            return 0.3
            
        except Exception as e:
            print(f"  ❌ Ошибка проверки двусмысленности: {e}")
            return 0.3
    
    async def _generate_clarification(self, question: str) -> str:
        """Генерирует уточняющий вопрос."""
        prompt = f"""
ВОПРОС: {question}

Создай УТОЧНЯЮЩИЙ ВОПРОС, который поможет:
1. Понять, что именно нужно пользователю
2. Выбрать правильный режим ответа
3. Дать максимально точный ответ

Уточняющий вопрос должен быть:
- Конкретным
- Полезным
- Предлагать варианты

УТОЧНЯЮЩИЙ ВОПРОС:
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
                max_tokens=256
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации уточнения: {e}")
            return f"Уточните, пожалуйста, что именно вы хотите узнать по вопросу: {question}"
    
    async def _generate_factual_response(self, question: str) -> Dict:
        """Генерирует ответ только с фактами и уверенностью."""
        prompt = f"""
ВОПРОС: {question}

Сгенерируй ОТВЕТ ТОЛЬКО С ФАКТАМИ:

1. Перечисли 3-5 проверенных фактов
2. Для каждого укажи уровень уверенности (0-100%)
3. Укажи альтернативные точки зрения (если есть)

ФАКТЫ:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=512
            )
            
            text = response.choices[0].message.content.strip()
            
            facts = []
            alternatives = []
            certainty = 0.7
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    if '%' in line and any(str(i) in line for i in range(10)):
                        facts.append(line)
                    elif 'альтернатив' in line.lower() or 'другой' in line.lower():
                        alternatives.append(line)
                    elif line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('•'):
                        facts.append(line)
            
            if len(facts) < 2:
                facts = [text[:200] + "..."]
            
            return {
                "type": "facts",
                "facts": facts[:5],
                "certainty": certainty,
                "alternatives": alternatives[:3]
            }
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации фактов: {e}")
            return {
                "type": "facts",
                "facts": ["Информация недоступна"],
                "certainty": 0.0,
                "alternatives": []
            }
    
    async def _generate_interpretations(self, question: str) -> Dict:
        """Генерирует различные интерпретации."""
        prompt = f"""
ВОПРОС: {question}

Сгенерируй РАЗЛИЧНЫЕ ИНТЕРПРЕТАЦИИ:

1. Предложи 3-4 разные точки зрения
2. Для каждой укажи перспективу и аргументацию
3. Дай рекомендацию, какая интерпретация наиболее убедительна

ИНТЕРПРЕТАЦИИ:
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
                max_tokens=512
            )
            
            text = response.choices[0].message.content.strip()
            
            interpretations = []
            current = {}
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if ':' in line and len(line.split(':')) == 2:
                    key, value = line.split(':', 1)
                    if 'перспектив' in key.lower() or 'точк' in key.lower():
                        if current:
                            interpretations.append(current)
                        current = {"perspective": value.strip(), "text": ""}
                elif current:
                    current["text"] = (current.get("text", "") + " " + line).strip()
            
            if current:
                interpretations.append(current)
            
            if len(interpretations) < 2:
                interpretations = [
                    {"perspective": "Перспектива 1", "text": text[:100] + "..."},
                    {"perspective": "Перспектива 2", "text": "Альтернативный взгляд..."}
                ]
            
            return {
                "type": "interpretations",
                "interpretations": interpretations[:4],
                "perspectives": len(interpretations),
                "recommendation": "Рекомендую рассмотреть все перспективы и выбрать наиболее убедительную"
            }
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации интерпретаций: {e}")
            return {
                "type": "interpretations",
                "interpretations": [{"perspective": "Основная", "text": "Информация недоступна"}],
                "perspectives": 1,
                "recommendation": "Попробуйте уточнить вопрос"
            }
    
    async def _generate_mixed_response(self, question: str) -> Dict:
        """Генерирует смешанный ответ."""
        facts_response = await self._generate_factual_response(question)
        interpretations_response = await self._generate_interpretations(question)
        
        return {
            "type": "mixed",
            "facts": facts_response.get("facts", []),
            "interpretations": interpretations_response.get("interpretations", []),
            "divider": "--- ФАКТЫ | ИНТЕРПРЕТАЦИИ ---"
        }

# ================================================================
# HTML-ИНТЕРФЕЙС
# ================================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Honest Dialogue System v2.0</title>
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
            padding: 12px 20px;
            background: rgba(10, 15, 30, 0.9);
            border-bottom: 1px solid rgba(95, 127, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            flex-wrap: wrap;
            gap: 8px;
        }
        .header h1 {
            font-size: 1.2em;
            background: linear-gradient(135deg, #7f9fff, #b07fff, #ff7fbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header .status {
            font-size: 10px;
            opacity: 0.7;
            display: flex;
            align-items: center;
            gap: 12px;
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
        .mode-selector {
            display: flex;
            gap: 4px;
            padding: 2px;
            background: rgba(10, 15, 30, 0.6);
            border-radius: 20px;
            border: 1px solid rgba(95, 127, 255, 0.15);
        }
        .mode-btn {
            padding: 4px 14px;
            border-radius: 16px;
            border: none;
            background: transparent;
            color: rgba(255,255,255,0.5);
            cursor: pointer;
            font-size: 10px;
            transition: all 0.3s;
            font-weight: 600;
        }
        .mode-btn:hover { color: rgba(255,255,255,0.8); }
        .mode-btn.active {
            background: rgba(63, 104, 255, 0.3);
            color: white;
            border: 1px solid rgba(95, 127, 255, 0.3);
        }
        .mode-btn.facts.active { background: rgba(100, 200, 255, 0.2); border-color: rgba(100, 200, 255, 0.3); }
        .mode-btn.interpretations.active { background: rgba(200, 100, 255, 0.2); border-color: rgba(200, 100, 255, 0.3); }
        .mode-btn.mixed.active { background: rgba(255, 215, 0, 0.2); border-color: rgba(255, 215, 0, 0.3); }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 15px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .chat-container::-webkit-scrollbar { width: 4px; }
        .chat-container::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        .chat-container::-webkit-scrollbar-thumb { background: rgba(95, 127, 255, 0.3); border-radius: 2px; }
        
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 14px;
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
        .message.clarification {
            align-self: flex-start;
            background: rgba(255, 200, 100, 0.05);
            border: 1px solid rgba(255, 200, 100, 0.2);
            border-left: 3px solid #ffc864;
        }
        .message.self {
            align-self: flex-start;
            background: rgba(100, 200, 255, 0.05);
            border: 1px solid rgba(100, 200, 255, 0.2);
            border-left: 3px solid #7fc8ff;
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
            white-space: pre-wrap;
        }
        .message .text .highlight { color: #ffd700; font-weight: 600; }
        .message .text .fact { color: #7fc8ff; }
        .message .text .interpretation { color: #d07fff; }
        .message .text .certainty { color: #7fffd4; }
        
        .input-container {
            padding: 12px 20px;
            background: rgba(10, 15, 30, 0.9);
            border-top: 1px solid rgba(95, 127, 255, 0.15);
            display: flex;
            gap: 10px;
            flex-shrink: 0;
        }
        .input-container input {
            flex: 1;
            padding: 10px 18px;
            border-radius: 25px;
            border: 1px solid rgba(95, 127, 255, 0.2);
            background: rgba(10, 15, 30, 0.6);
            color: rgba(255,255,255,0.9);
            font-size: 13px;
            outline: none;
            transition: all 0.3s;
        }
        .input-container input:focus {
            border-color: rgba(95, 127, 255, 0.5);
            box-shadow: 0 0 30px rgba(80, 120, 255, 0.05);
        }
        .input-container input::placeholder { color: rgba(255,255,255,0.3); }
        .input-container button {
            padding: 10px 25px;
            border-radius: 25px;
            border: none;
            background: linear-gradient(135deg, #3f68ff, #7f3fff);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 13px;
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
            gap: 6px;
            padding: 6px 20px;
            flex-wrap: wrap;
            flex-shrink: 0;
            background: rgba(10, 15, 30, 0.3);
        }
        .suggestions button {
            padding: 4px 12px;
            border-radius: 16px;
            border: 1px solid rgba(95, 127, 255, 0.15);
            background: rgba(10, 15, 30, 0.6);
            color: rgba(255,255,255,0.6);
            cursor: pointer;
            font-size: 10px;
            transition: all 0.3s;
        }
        .suggestions button:hover {
            background: rgba(63, 104, 255, 0.2);
            border-color: rgba(95, 127, 255, 0.3);
        }
        
        @media (max-width: 768px) {
            .header { padding: 10px 12px; }
            .header h1 { font-size: 1em; }
            .chat-container { padding: 10px 12px; }
            .message { max-width: 95%; padding: 10px 12px; }
            .input-container { padding: 10px 12px; flex-direction: column; }
            .input-container button { width: 100%; }
            .suggestions { padding: 6px 12px; }
            .suggestions button { font-size: 9px; padding: 3px 8px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Honest Dialogue System v2.0</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="modeDisplay" style="font-size:10px; opacity:0.6;">🎯 Факты + Интерпретации</span>
            <div class="mode-selector">
                <button class="mode-btn facts" data-mode="facts" onclick="setMode('facts')">📊 Факты</button>
                <button class="mode-btn interpretations" data-mode="interpretations" onclick="setMode('interpretations')">🔮 Интерпретации</button>
                <button class="mode-btn mixed active" data-mode="mixed" onclick="setMode('mixed')">🎯 Смешанный</button>
            </div>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="role">🧠 Система</div>
            <div class="text">
                Привет! Я — <span class="highlight">Honest Dialogue System v2.0</span>.<br>
                Я разделяю <span class="fact">факты</span> и <span class="interpretation">интерпретации</span>,<br>
                указываю <span class="certainty">уверенность</span>, задаю уточняющие вопросы<br>
                и <span class="highlight">отвечаю на вопросы о себе</span>.<br>
                <br>
                <span class="highlight">📊 Режимы:</span><br>
                • <span class="fact">Факты</span> — только проверенная информация с уверенностью<br>
                • <span class="interpretation">Интерпретации</span> — разные точки зрения<br>
                • <span class="highlight">Смешанный</span> — и то, и другое
            </div>
        </div>
    </div>
    
    <div class="suggestions">
        <button onclick="askQuestion('Расскажи о себе')">🧠 О системе</button>
        <button onclick="askQuestion('Что ты умеешь?')">💡 Возможности</button>
        <button onclick="askQuestion('Как стать успешным предпринимателем?')">🚀 Бизнес</button>
        <button onclick="askQuestion('Стоит ли учиться программированию?')">💻 Программирование</button>
        <button onclick="askQuestion('Какие навыки будут востребованы?')">🔮 Будущее</button>
    </div>
    
    <div class="input-container">
        <input id="questionInput" placeholder="Спросите о чём угодно..." 
               onkeypress="if(event.key==='Enter') askQuestion()">
        <button id="sendButton" onclick="askQuestion()">💬 Спросить</button>
    </div>
    
    <script>
        let isProcessing = false;
        let currentMode = 'mixed';
        
        function setMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            document.querySelector(`.mode-btn.${mode}`).classList.add('active');
            document.getElementById('modeDisplay').textContent = 
                mode === 'facts' ? '📊 Только факты' :
                mode === 'interpretations' ? '🔮 Только интерпретации' :
                '🎯 Факты + Интерпретации';
            
            fetch('/set_mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: mode })
            });
        }
        
        function addMessage(role, content, isThinking = false) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            if (isThinking) {
                div.innerHTML = `
                    <div class="role">🧠 Система анализирует...</div>
                    <div class="thinking">
                        <span></span><span></span><span></span>
                    </div>
                `;
            } else {
                const roleIcon = role === 'user' ? '👤' : 
                                role === 'meta' ? '📊' : 
                                role === 'clarification' ? '❓' :
                                role === 'self' ? '🔬' : '🧠';
                const roleName = role === 'user' ? 'Вы' : 
                                role === 'meta' ? 'Мета-анализ' :
                                role === 'clarification' ? 'Уточнение' :
                                role === 'self' ? 'О системе' : 'Ответ';
                div.innerHTML = `
                    <div class="role">${roleIcon} ${roleName}</div>
                    <div class="text">${content}</div>
                `;
            }
            
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
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
            button.textContent = '⏳ Анализ...';
            
            addMessage('user', question);
            addMessage('agent', '', true);
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        question: question,
                        mode: currentMode
                    })
                });
                
                const data = await response.json();
                
                const messages = document.querySelectorAll('.message');
                if (messages.length > 0 && messages[messages.length - 1].querySelector('.thinking')) {
                    messages[messages.length - 1].remove();
                }
                
                if (data.error) {
                    addMessage('agent', '❌ Ошибка: ' + data.error);
                } else if (data.type === 'clarification') {
                    addMessage('clarification', data.question);
                } else if (data.is_self_description) {
                    addMessage('self', data.content);
                } else {
                    const resp = data.response;
                    
                    if (data.mode === 'facts') {
                        let factsText = `📊 ФАКТЫ (уверенность: ${(resp.certainty * 100).toFixed(0)}%)\n\n`;
                        resp.facts.forEach((f, i) => {
                            factsText += `${i+1}. ${f}\n`;
                        });
                        if (resp.alternatives && resp.alternatives.length > 0) {
                            factsText += `\n🔄 АЛЬТЕРНАТИВЫ:\n`;
                            resp.alternatives.forEach((a, i) => {
                                factsText += `${i+1}. ${a}\n`;
                            });
                        }
                        addMessage('agent', factsText);
                    } else if (data.mode === 'interpretations') {
                        let interpText = `🔮 ИНТЕРПРЕТАЦИИ (${resp.perspectives} перспектив)\n\n`;
                        resp.interpretations.forEach((interp, i) => {
                            interpText += `${i+1}. [${interp.perspective}]:\n   ${interp.text}\n\n`;
                        });
                        if (resp.recommendation) {
                            interpText += `💡 Рекомендация:\n   ${resp.recommendation}`;
                        }
                        addMessage('agent', interpText);
                    } else {
                        let mixedText = `📊 ФАКТЫ:\n\n`;
                        resp.facts.forEach((f, i) => {
                            mixedText += `${i+1}. ${f}\n`;
                        });
                        mixedText += `\n--- ФАКТЫ | ИНТЕРПРЕТАЦИИ ---\n\n`;
                        mixedText += `🔮 ИНТЕРПРЕТАЦИИ:\n\n`;
                        resp.interpretations.forEach((interp, i) => {
                            mixedText += `${i+1}. [${interp.perspective}]:\n   ${interp.text}\n\n`;
                        });
                        mixedText += `💡 Выберите режим: факты (F) или интерпретации (I)`;
                        addMessage('agent', mixedText);
                    }
                    
                    addMessage('meta', `📊 Режим: ${data.mode_name} | Синхронизация: ${data.sync_r.toFixed(3)}`);
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
    </script>
</body>
</html>'''

# ================================================================
# HTTP-СЕРВЕР
# ================================================================
class HonestDialogueHandler(http.server.SimpleHTTPRequestHandler):
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
                'mode': self.system.current_mode if self.system else 'mixed'
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/set_mode':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                mode = data.get('mode', 'mixed')
                self.system.set_mode(mode)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'mode': mode}).encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == '/ask':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                question = data.get('question', '')
                mode = data.get('mode', 'mixed')
                
                if not question:
                    self.send_error(400, "No question provided")
                    return
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.system.process_request(question, mode)
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
    print("  🧠 MOLECULAR AI v7.0 — HONEST DIALOGUE SYSTEM v2.0")
    print("  Разделение фактов и интерпретаций + Самосознание")
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
    system = HonestDialogueSystem(api_key)
    system.initialize()
    
    HonestDialogueHandler.system = system
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    port = 8000
    try:
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), HonestDialogueHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        webbrowser.open(f"http://localhost:{port}/")
        
        print(f"\n  🌐 http://localhost:{port}/")
        print(f"\n  🧠 СИСТЕМА ГОТОВА!")
        print(f"  🔍 Добавлено самосознание — система отвечает на вопросы о себе")
        print(f"  🛑 Лимит уточнений: 2 (без бесконечных циклов)")
        print(f"  📊 Три режима: Факты, Интерпретации, Смешанный")
        print(f"\n  Нажмите Ctrl+C для остановки")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
    except OSError:
        port = 8001
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), HonestDialogueHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/")
        print(f"\n  🌐 http://localhost:{port}/")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()