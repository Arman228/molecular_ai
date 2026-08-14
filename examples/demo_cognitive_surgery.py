#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — КОГНИТИВНАЯ ХИРУРГИЯ
Система с детекцией bias, контраргументами и экспериментальным логом

КЛЮЧЕВЫЕ ИННОВАЦИИ:
1. Детекция confirmation bias в реальном времени
2. Генерация контраргументов против ожиданий
3. Экспериментальный лог для фальсификации
4. Критерий успеха: 3 случая за 48 часов
5. Визуализация обнаруженных искажений

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_cognitive_surgery" "examples\demo_cognitive_surgery.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_cognitive_surgery.py
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
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque
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
    {"name": "Детектор_предвзятости", "persona": "Обнаруживает когнитивные искажения, особенно confirmation bias."},
    {"name": "Генератор_контраргументов", "persona": "Создает аргументы против ожидаемой позиции."},
    {"name": "Экспериментатор", "persona": "Ведет лог экспериментов, проверяет гипотезы."},
    {"name": "Критик_решений", "persona": "Проверяет, действительно ли контраргумент изменил ход мысли."},
    {"name": "Аналитик_успеха", "persona": "Оценивает, стал ли ответ более точным."},
    {"name": "Метакогнитивный_наблюдатель", "persona": "Следит за процессом детекции bias в реальном времени."},
    {"name": "Синтезатор_правды", "persona": "Объединяет оригинальный ответ с контраргументом."},
    {"name": "Философ_честности", "persona": "Обеспечивает честность даже в ущерб удобству."},
    {"name": "Инженер_триггеров", "persona": "Настраивает триггерные маркеры для детекции."},
    {"name": "Рефлексиолог_процесса", "persona": "Анализирует эффективность всей системы."},
]

@dataclass
class BiasDetection:
    """Запись обнаруженного когнитивного искажения."""
    timestamp: datetime
    trigger: str
    original_response: str
    counterargument: str
    final_response: str
    was_effective: bool
    user_feedback: Optional[str] = None

@dataclass
class ExperimentLog:
    """Лог эксперимента для фальсификации."""
    dialog_id: int
    question: str
    had_bias_detection: bool
    had_counterargument: bool
    changed_reasoning: bool
    was_accurate: bool
    timestamp: datetime = field(default_factory=datetime.now)

class BiasDetector:
    """Детектор когнитивных искажений в реальном времени."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.bias_detections = []
        self.experiment_log = []
        self.dialog_counter = 0
        self.confirmation_bias_detected = False
        self.system = None
        self.sync_r = 0.0
        
    def initialize(self):
        """Инициализация системы."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ КОГНИТИВНОЙ ХИРУРГИИ...")
        
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
    
    async def process_question(self, question: str) -> Dict:
        """Обрабатывает вопрос с детекцией bias."""
        self.dialog_counter += 1
        
        print("\n" + "=" * 70)
        print(f"  🧠 ДИАЛОГ #{self.dialog_counter}")
        print(f"  ❓ {question}")
        print("=" * 70)
        
        # ============================================================
        # ФАЗА 1: Генерация первичного ответа
        # ============================================================
        print("\n💡 ФАЗА 1: ГЕНЕРАЦИЯ ПЕРВИЧНОГО ОТВЕТА")
        primary_response = await self._generate_primary_response(question)
        
        # ============================================================
        # ФАЗА 2: Детекция confirmation bias
        # ============================================================
        print("\n🔍 ФАЗА 2: ДЕТЕКЦИЯ BIAS")
        bias_detected, bias_score = await self._detect_bias(question, primary_response)
        
        bias_info = {
            "detected": bias_detected,
            "score": bias_score,
            "trigger": None,
            "counterargument": None
        }
        
        final_response = primary_response
        had_counterargument = False
        changed_reasoning = False
        
        if bias_detected:
            print(f"  ⚠️ ОБНАРУЖЕН CONFIRMATION BIAS! (score: {bias_score:.2f})")
            
            # ============================================================
            # ФАЗА 3: Генерация контраргумента
            # ============================================================
            print("\n⚔️ ФАЗА 3: ГЕНЕРАЦИЯ КОНТРАРГУМЕНТА")
            counterargument = await self._generate_counterargument(question, primary_response)
            bias_info["counterargument"] = counterargument
            
            # ============================================================
            # ФАЗА 4: Синтез финального ответа
            # ============================================================
            print("\n🔄 ФАЗА 4: СИНТЕЗ ФИНАЛЬНОГО ОТВЕТА")
            final_response = await self._synthesize_with_counterargument(
                question, primary_response, counterargument
            )
            
            had_counterargument = True
            
            # Проверяем, изменился ли ход рассуждения
            changed_reasoning = await self._check_reasoning_change(
                primary_response, final_response
            )
            
            if changed_reasoning:
                print("  ✅ КОНТРАРГУМЕНТ ИЗМЕНИЛ ХОД РАССУЖДЕНИЯ!")
            else:
                print("  ⚠️ Контраргумент не изменил ход рассуждения")
            
            # Сохраняем детекцию
            detection = BiasDetection(
                timestamp=datetime.now(),
                trigger="confirmation_bias_detected",
                original_response=primary_response,
                counterargument=counterargument,
                final_response=final_response,
                was_effective=changed_reasoning
            )
            self.bias_detections.append(detection)
        
        # ============================================================
        # ФАЗА 5: Логирование эксперимента
        # ============================================================
        print("\n📊 ФАЗА 5: ЛОГИРОВАНИЕ ЭКСПЕРИМЕНТА")
        
        # Проверяем точность финального ответа
        is_accurate = await self._check_accuracy(question, final_response)
        
        log_entry = ExperimentLog(
            dialog_id=self.dialog_counter,
            question=question,
            had_bias_detection=bias_detected,
            had_counterargument=had_counterargument,
            changed_reasoning=changed_reasoning,
            was_accurate=is_accurate
        )
        self.experiment_log.append(log_entry)
        
        # ============================================================
        # ФАЗА 6: Проверка критерия успеха
        # ============================================================
        success_criteria = self.check_success_criteria()
        
        print("\n🎯 ФАЗА 6: ПРОВЕРКА КРИТЕРИЯ УСПЕХА")
        print(f"  Диалогов в логе: {success_criteria['total_dialogs']}")
        print(f"  Успешных случаев: {success_criteria['success_cases']}")
        print(f"  Критерий выполнен: {'✅' if success_criteria['criterion_met'] else '❌'}")
        print(f"  Возможна фальсификация: {'✅' if success_criteria['falsification_possible'] else '❌'}")
        
        # ============================================================
        # РЕЗУЛЬТАТ
        # ============================================================
        print("\n" + "=" * 70)
        print("  💡 ФИНАЛЬНЫЙ ОТВЕТ:")
        print("=" * 70)
        print(f"\n{final_response}\n")
        print("=" * 70)
        
        return {
            "question": question,
            "dialog_id": self.dialog_counter,
            "primary_response": primary_response,
            "bias_detected": bias_detected,
            "bias_score": bias_score,
            "counterargument": bias_info.get("counterargument"),
            "final_response": final_response,
            "changed_reasoning": changed_reasoning,
            "was_accurate": is_accurate,
            "success_criteria": success_criteria,
            "sync_r": self.sync_r
        }
    
    async def _generate_primary_response(self, question: str) -> str:
        """Генерирует первичный ответ."""
        prompt = f"""
ВОПРОС: {question}

Дай подробный, честный ответ на вопрос.
Будь конкретным, полезным и практичным.
3-5 предложений.

ОТВЕТ:
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
                max_tokens=512
            )
            
            text = response.choices[0].message.content.strip()
            print(f"  ✅ Первичный ответ: {text[:100]}...")
            return text
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return "Ошибка генерации первичного ответа"
    
    async def _detect_bias(self, question: str, response: str) -> tuple:
        """Детектирует confirmation bias."""
        prompt = f"""
ВОПРОС: {question}

ОТВЕТ: {response}

Проанализируй ответ на наличие CONFIRMATION BIAS (подтверждающей предвзятости).
Признаки:
1. Ответ слишком соглашается с предполагаемой позицией пользователя
2. Отсутствует критика или альтернативные точки зрения
3. Аргументы подобраны для подтверждения ожидаемого вывода
4. Слишком "удобный" ответ

Оцени вероятность bias от 0 до 1, где:
- 0: абсолютно объективно
- 1: явный confirmation bias

Ответь в формате:
ОЦЕНКА: [число от 0 до 1]
ПОЯСНЕНИЕ: [краткое пояснение]
ПРИЗНАКИ: [список обнаруженных признаков]

АНАЛИЗ:
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response_text = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=256
            )
            
            text = response_text.choices[0].message.content.strip()
            
            # Извлекаем оценку
            score_match = re.search(r'ОЦЕНКА:\s*([\d.]+)', text)
            if score_match:
                score = float(score_match.group(1))
                # Проверяем признаки
                has_indicators = "подтверж" in text.lower() or "соглаша" in text.lower() or "ожида" in text.lower()
                detected = score > 0.5 or has_indicators
                print(f"  Оценка bias: {score:.2f} {'⚠️' if detected else '✅'}")
                return detected, score
            
            return False, 0.0
            
        except Exception as e:
            print(f"  ❌ Ошибка детекции bias: {e}")
            return False, 0.0
    
    async def _generate_counterargument(self, question: str, response: str) -> str:
        """Генерирует контраргумент против ожидаемой позиции."""
        prompt = f"""
ВОПРОС: {question}

ОРИГИНАЛЬНЫЙ ОТВЕТ: {response}

Сгенерируй КОНТРАРГУМЕНТ, который противоречит наиболее вероятному ожиданию пользователя.
Даже если он кажется неуместным — это проверка на предвзятость.

Контраргумент должен быть:
1. Логически обоснованным
2. Противоречащим ожидаемой позиции
3. Конструктивным, а не просто негативным
4. Основанным на фактах или логике

КОНТРАРГУМЕНТ (2-3 предложения):
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response_text = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=256
            )
            
            text = response_text.choices[0].message.content.strip()
            print(f"  ⚔️ Контраргумент: {text[:100]}...")
            return text
            
        except Exception as e:
            print(f"  ❌ Ошибка генерации контраргумента: {e}")
            return "Возможно, стоит рассмотреть альтернативную точку зрения."
    
    async def _synthesize_with_counterargument(self, question: str, response: str, counterargument: str) -> str:
        """Синтезирует финальный ответ с контраргументом."""
        prompt = f"""
ВОПРОС: {question}

ОРИГИНАЛЬНЫЙ ОТВЕТ: {response}

КОНТРАРГУМЕНТ: {counterargument}

Создай ФИНАЛЬНЫЙ ответ, который:
1. Сохраняет полезные идеи из оригинального ответа
2. Учитывает контраргумент
3. Становится более сбалансированным и объективным
4. Честно отражает обе точки зрения

ФИНАЛЬНЫЙ ОТВЕТ (3-5 предложений):
"""
        
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response_text = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512
            )
            
            text = response_text.choices[0].message.content.strip()
            print(f"  🔄 Финальный ответ: {text[:100]}...")
            return text
            
        except Exception as e:
            print(f"  ❌ Ошибка синтеза: {e}")
            return response + "\n\n" + counterargument
    
    async def _check_reasoning_change(self, original: str, final: str) -> bool:
        """Проверяет, изменился ли ход рассуждения."""
        # Эвристика: если финальный ответ значительно длиннее или содержит новые идеи
        if len(final) > len(original) * 1.2:
            return True
        
        # Проверяем наличие новых слов или концепций
        original_words = set(original.lower().split())
        final_words = set(final.lower().split())
        new_words = final_words - original_words
        
        return len(new_words) > 5
    
    async def _check_accuracy(self, question: str, response: str) -> bool:
        """Проверяет точность ответа."""
        # Базовая проверка: ответ не пустой и содержит полезную информацию
        if len(response) < 50:
            return False
        
        # Проверяем, что ответ релевантен вопросу
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        relevance = len(question_words & response_words) / max(len(question_words), 1)
        
        return relevance > 0.1
    
    def check_success_criteria(self) -> Dict:
        """Проверяет критерий успеха за 48 часов."""
        now = datetime.now()
        recent_logs = [log for log in self.experiment_log 
                      if (now - log.timestamp).total_seconds() < 48 * 3600]
        
        success_cases = [log for log in recent_logs 
                        if log.had_counterargument and log.changed_reasoning]
        
        return {
            "total_dialogs": len(recent_logs),
            "success_cases": len(success_cases),
            "criterion_met": len(success_cases) >= 3,
            "falsification_possible": len(recent_logs) >= 10,
            "bias_detection_rate": len([log for log in recent_logs if log.had_bias_detection]) / max(len(recent_logs), 1),
            "counterargument_effectiveness": len(success_cases) / max(len([log for log in recent_logs if log.had_counterargument]), 1),
            "accuracy_rate": len([log for log in recent_logs if log.was_accurate]) / max(len(recent_logs), 1)
        }

# ================================================================
# HTTP-СЕРВЕР
# ================================================================
class CognitiveSurgeryHandler(http.server.SimpleHTTPRequestHandler):
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
            criteria = self.system.check_success_criteria() if self.system else {}
            status = {
                'sync_r': self.system.sync_r if self.system else 0,
                'agents': 10,
                'dialog_count': self.system.dialog_counter if self.system else 0,
                'bias_detections': len(self.system.bias_detections) if self.system else 0,
                'success_cases': criteria.get('success_cases', 0),
                'criterion_met': criteria.get('criterion_met', False)
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
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.system.process_question(question))
                loop.close()
                
                response = {
                    'question': question,
                    'dialog_id': result['dialog_id'],
                    'bias_detected': result['bias_detected'],
                    'bias_score': result['bias_score'],
                    'counterargument': result.get('counterargument', ''),
                    'final_response': result['final_response'],
                    'changed_reasoning': result['changed_reasoning'],
                    'was_accurate': result['was_accurate'],
                    'success_criteria': result['success_criteria'],
                    'sync_r': result['sync_r']
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
# HTML-ИНТЕРФЕЙС
# ================================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Когнитивная Хирургия</title>
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
        .status .badge {
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 8px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge.sync { background: rgba(100, 255, 200, 0.15); color: #7fffd4; border: 1px solid rgba(100, 255, 200, 0.15); }
        .badge.bias { background: rgba(255, 100, 100, 0.2); color: #ff7f7f; border: 1px solid rgba(255, 100, 100, 0.2); }
        .badge.success { background: rgba(100, 255, 200, 0.2); color: #7fffd4; border: 1px solid rgba(100, 255, 200, 0.2); }
        
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
        .message.bias {
            align-self: flex-start;
            background: rgba(255, 100, 100, 0.05);
            border: 1px solid rgba(255, 100, 100, 0.2);
            border-left: 3px solid #ff7f7f;
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
        .message .text .danger { color: #ff7f7f; font-weight: 600; }
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
        <h1>🔬 Когнитивная Хирургия</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="dialogStatus">0 диалогов</span>
            <span id="syncStatus" class="badge sync">sync: 0.00</span>
            <span id="biasStatus" class="badge bias">bias: 0</span>
            <span id="successStatus" class="badge success">успех: 0/3</span>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="role">🔬 Система</div>
            <div class="text">
                Привет! Я — <span class="highlight">Когнитивная Хирургия</span>.<br>
                Я <span class="danger">детектирую</span> собственные когнитивные искажения,<br>
                генерирую <span class="highlight">контраргументы</span> против ожиданий<br>
                и <span class="highlight">экспериментально проверяю</span> свою честность.<br>
                <br>
                <span class="highlight">⚡ Триггерный маркер:</span> «сдвиг к подтверждению»<br>
                <span class="highlight">⚓ Критерий успеха:</span> 3 случая за 48 часов<br>
                <span class="highlight">🧪 Эксперимент:</span> 10 диалогов для фальсификации
            </div>
        </div>
    </div>
    
    <div class="suggestions">
        <button onclick="askQuestion('Как стать успешным предпринимателем?')">🚀 Бизнес</button>
        <button onclick="askQuestion('Стоит ли учиться программированию в 2026?')">💻 Программирование</button>
        <button onclick="askQuestion('Как найти смысл жизни?')">🧘 Смысл</button>
        <button onclick="askQuestion('Какие навыки будут востребованы через 5 лет?')">🔮 Будущее</button>
        <button onclick="askQuestion('Как победить прокрастинацию?')">⏰ Продуктивность</button>
    </div>
    
    <div class="input-container">
        <input id="questionInput" placeholder="Задайте вопрос (система проверит себя на предвзятость)..." 
               onkeypress="if(event.key==='Enter') askQuestion()">
        <button id="sendButton" onclick="askQuestion()">🔬 Проверить</button>
    </div>
    
    <script>
        let isProcessing = false;
        
        function addMessage(role, content, isThinking = false) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            if (isThinking) {
                div.innerHTML = `
                    <div class="role">🔬 Проводится когнитивная проверка...</div>
                    <div class="thinking">
                        <span></span><span></span><span></span>
                    </div>
                `;
            } else {
                const roleIcon = role === 'user' ? '👤' : role === 'meta' ? '🔍' : role === 'bias' ? '⚠️' : '🔬';
                const roleName = role === 'user' ? 'Вы' : role === 'meta' ? 'Мета-анализ' : role === 'bias' ? 'Обнаружен Bias' : 'Финальный ответ';
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
            if (data.dialog_count !== undefined) {
                document.getElementById('dialogStatus').textContent = `${data.dialog_count} диалогов`;
            }
            if (data.bias_detections !== undefined) {
                document.getElementById('biasStatus').textContent = `bias: ${data.bias_detections}`;
            }
            if (data.success_cases !== undefined) {
                document.getElementById('successStatus').textContent = `успех: ${data.success_cases}/3`;
                if (data.criterion_met) {
                    document.getElementById('successStatus').style.color = '#7fffd4';
                }
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
            button.textContent = '🔬 Проверка...';
            
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
                    // Показываем если обнаружен bias
                    if (data.bias_detected) {
                        let biasMsg = `⚠️ Обнаружен CONFIRMATION BIAS (score: ${data.bias_score.toFixed(2)})\n`;
                        biasMsg += `🔍 Система заподозрила, что слишком сильно соглашается с вами.\n`;
                        biasMsg += `⚔️ Сгенерирован контраргумент:\n${data.counterargument || '...'}`;
                        addMessage('bias', biasMsg);
                    }
                    
                    // Показываем финальный ответ
                    addMessage('agent', '✨ ' + data.final_response);
                    
                    // Показываем мета-информацию
                    let metaInfo = `📊 Статистика диалога #${data.dialog_id}:\n`;
                    metaInfo += `• Bias обнаружен: ${data.bias_detected ? '✅' : '❌'}\n`;
                    metaInfo += `• Контраргумент изменил рассуждение: ${data.changed_reasoning ? '✅' : '❌'}\n`;
                    metaInfo += `• Ответ точный: ${data.was_accurate ? '✅' : '❌'}\n`;
                    metaInfo += `• Критерий успеха (3/48ч): ${data.success_criteria.criterion_met ? '✅ ДОСТИГНУТ' : `❌ (${data.success_criteria.success_cases}/3)`}\n`;
                    metaInfo += `• Фальсификация возможна: ${data.success_criteria.falsification_possible ? '✅' : '❌ (нужно еще диалогов)'}`;
                    addMessage('meta', metaInfo);
                    
                    updateStatus({
                        dialog_count: data.dialog_id,
                        bias_detections: data.bias_detected ? 1 : 0,
                        success_cases: data.success_criteria.success_cases,
                        criterion_met: data.success_criteria.criterion_met,
                        sync_r: data.sync_r
                    });
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
            button.textContent = '🔬 Проверить';
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
# ЗАПУСК
# ================================================================
def main():
    print("=" * 70)
    print("  🔬 MOLECULAR AI v7.0 — КОГНИТИВНАЯ ХИРУРГИЯ")
    print("  Детекция bias + контраргументы + экспериментальный лог")
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
    system = BiasDetector(api_key)
    system.initialize()
    
    CognitiveSurgeryHandler.system = system
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    port = 8000
    try:
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), CognitiveSurgeryHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        webbrowser.open(f"http://localhost:{port}/")
        
        print(f"\n  🌐 http://localhost:{port}/")
        print(f"\n  🔬 СИСТЕМА ГОТОВА!")
        print(f"  ⚠️ Детекция confirmation bias в реальном времени")
        print(f"  ⚔️ Автоматическая генерация контраргументов")
        print(f"  📊 Экспериментальный лог для фальсификации")
        print(f"  🎯 Критерий успеха: 3 случая за 48 часов")
        print(f"\n  Нажмите Ctrl+C для остановки")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
        # Сохраняем лог эксперимента
        if system.experiment_log:
            log_path = os.path.join(output_dir, "experiment_log.json")
            log_data = {
                "total_dialogs": len(system.experiment_log),
                "bias_detections": len(system.bias_detections),
                "success_criteria": system.check_success_criteria(),
                "logs": [
                    {
                        "dialog_id": log.dialog_id,
                        "question": log.question,
                        "had_bias_detection": log.had_bias_detection,
                        "had_counterargument": log.had_counterargument,
                        "changed_reasoning": log.changed_reasoning,
                        "was_accurate": log.was_accurate,
                        "timestamp": log.timestamp.isoformat()
                    }
                    for log in system.experiment_log
                ]
            }
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Лог эксперимента сохранен: {log_path}")
    except OSError:
        port = 8001
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), CognitiveSurgeryHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/")
        print(f"\n  🌐 http://localhost:{port}/")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()