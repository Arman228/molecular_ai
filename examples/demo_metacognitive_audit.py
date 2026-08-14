#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — МЕТАКОГНИТИВНЫЙ АУДИТ С КОНЕЧНЫМ ЦИКЛОМ
Внешние якоря: операциональность (48 часов) + фальсифицируемость

КЛЮЧЕВЫЕ ИННОВАЦИИ:
1. Конечный цикл с точкой остановки (макс. 3 итерации)
2. Внешние якоря: реализуемость за 48 часов, возможность эксперимента
3. Сомнение в premises, а не в выводах
4. Намеренные сбои только к структурам
5. Проверка на измеримый результат

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_metacognitive_audit" "examples\demo_metacognitive_audit.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_metacognitive_audit.py
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
# РОЛИ АГЕНТОВ С МЕТА-УРОВНЕМ
# ================================================================
ROLES = [
    {"name": "Метакогнитивный_аудитор", "persona": "Проводит аудит мышления, проверяет premises, ищет логические основания."},
    {"name": "Критик_структур", "persona": "Анализирует структуры, применяет намеренные сбои, проверяет устойчивость."},
    {"name": "Синтезатор_решений", "persona": "Собирает улучшенные структуры, создает практичные решения."},
    {"name": "Экспериментатор", "persona": "Предлагает эксперименты для проверки, ищет фальсифицируемость."},
    {"name": "Прагматик_реализации", "persona": "Проверяет реализуемость за 48 часов, ищет практические шаги."},
    {"name": "Аналитик_предпосылок", "persona": "Находит скрытые premises, проверяет их на прочность."},
    {"name": "Инноватор_прорывов", "persona": "Генерирует новые premises, предлагает парадигмальные сдвиги."},
    {"name": "Философ_оснований", "persona": "Исследует фундаментальные основания, проверяет аксиомы."},
    {"name": "Рефлексиолог_процесса", "persona": "Наблюдает за процессом аудита, отмечает точки остановки."},
    {"name": "Мета-синтезатор", "persona": "Собирает все результаты аудита, формирует финальный вывод."},
]

@dataclass
class AuditIteration:
    """Запись одной итерации метакогнитивного аудита."""
    iteration: int
    premises_analyzed: List[str]
    weak_premises: List[Dict]
    structural_changes: List[str]
    improved_idea: str
    is_operational: bool
    is_falsifiable: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AuditResult:
    """Результат полного метакогнитивного аудита."""
    question: str
    initial_idea: str
    iterations: List[AuditIteration]
    final_answer: str
    audit_complete: bool
    total_iterations: int
    operational_score: float
    falsifiable_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class MetacognitiveAuditSystem:
    """Система метакогнитивного аудита с конечным циклом."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.sync_r = 0.0
        self.max_iterations = 3  # Конечный цикл
        self.audit_history = []
        self.current_audit = None
        self.iteration_counter = 0
        
    def initialize(self):
        """Инициализация системы."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ МЕТАКОГНИТИВНОГО АУДИТА...")
        
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
    
    async def audit(self, question: str) -> AuditResult:
        """Выполняет полный метакогнитивный аудит с конечным циклом."""
        self.iteration_counter += 1
        
        print("\n" + "=" * 70)
        print(f"  🧠 МЕТАКОГНИТИВНЫЙ АУДИТ #{self.iteration_counter}")
        print(f"  ❓ {question}")
        print("=" * 70)
        print(f"\n  📊 Параметры аудита:")
        print(f"    Макс. итераций: {self.max_iterations}")
        print(f"    Внешние якоря: операциональность (48ч) + фальсифицируемость")
        print("=" * 70)
        
        # ФАЗА 1: Первичная генерация идеи
        print("\n💡 ФАЗА 1: ПЕРВИЧНАЯ ГЕНЕРАЦИЯ")
        initial_idea = await self._generate_initial_idea(question)
        
        # ФАЗА 2: Метакогнитивный аудит (конечный цикл)
        print(f"\n🔍 ФАЗА 2: МЕТАКОГНИТИВНЫЙ АУДИТ (макс. {self.max_iterations} итераций)")
        
        iterations = []
        current_idea = initial_idea
        audit_complete = False
        
        for i in range(self.max_iterations):
            print(f"\n  📍 Итерация {i+1}/{self.max_iterations}")
            
            # 2a: Анализ premises
            print("    🔍 Анализ premises...")
            premises_analysis = await self._analyze_premises(current_idea)
            
            # 2b: Нахождение слабых premises
            print("    🎯 Поиск слабых premises...")
            weak_premises = await self._find_weak_premises(current_idea, premises_analysis)
            
            # 2c: Применение намеренных сбоев к структурам
            print("    ⚡ Применение намеренных сбоев...")
            structural_changes = await self._apply_structural_breaks(current_idea, weak_premises)
            
            # 2d: Пересборка с улучшениями
            print("    🔄 Пересборка улучшенной идеи...")
            improved_idea = await self._rebuild_with_anchors(
                current_idea, 
                weak_premises, 
                structural_changes
            )
            
            # 2e: Проверка операциональности
            print("    ⚓ Проверка операциональности (48ч)...")
            is_operational = await self._check_operational(improved_idea)
            
            # 2f: Проверка фальсифицируемости
            print("    🧪 Проверка фальсифицируемости...")
            is_falsifiable = await self._check_falsifiable(improved_idea)
            
            # Сохраняем итерацию
            iteration = AuditIteration(
                iteration=i+1,
                premises_analyzed=premises_analysis,
                weak_premises=weak_premises,
                structural_changes=structural_changes,
                improved_idea=improved_idea,
                is_operational=is_operational,
                is_falsifiable=is_falsifiable
            )
            iterations.append(iteration)
            
            # Показываем прогресс
            print(f"    ✅ Итерация {i+1} завершена")
            print(f"       Операционально: {'✅' if is_operational else '❌'}")
            print(f"       Фальсифицируемо: {'✅' if is_falsifiable else '❌'}")
            
            # Точка остановки: если достигнуты оба критерия
            if is_operational and is_falsifiable:
                print(f"\n  🛑 ДОСТИГНУТЫ ВНЕШНИЕ ЯКОРЯ! Остановка аудита.")
                audit_complete = True
                break
            
            # Обновляем текущую идею для следующей итерации
            current_idea = improved_idea
            
            # Синхронизируем систему после каждой итерации
            for _ in range(50):
                self.system.step()
            self.sync_r = self.system.order_parameter()
        
        # Если цикл завершился без достижения якорей
        if not audit_complete:
            print(f"\n  ⏹️ Достигнут лимит итераций ({self.max_iterations}). Завершение аудита.")
        
        # ФАЗА 3: Финальный синтез
        print("\n🎯 ФАЗА 3: ФИНАЛЬНЫЙ СИНТЕЗ")
        final_answer = await self._synthesize_final(question, iterations)
        
        # Вычисляем оценки
        operational_score = sum(1 for it in iterations if it.is_operational) / len(iterations)
        falsifiable_score = sum(1 for it in iterations if it.is_falsifiable) / len(iterations)
        
        # Создаем результат
        result = AuditResult(
            question=question,
            initial_idea=initial_idea,
            iterations=iterations,
            final_answer=final_answer,
            audit_complete=audit_complete,
            total_iterations=len(iterations),
            operational_score=operational_score,
            falsifiable_score=falsifiable_score
        )
        
        self.audit_history.append(result)
        self.current_audit = result
        
        # Выводим результат
        print("\n" + "=" * 70)
        print("  💡 РЕЗУЛЬТАТ МЕТАКОГНИТИВНОГО АУДИТА:")
        print("=" * 70)
        print(f"\n{final_answer}\n")
        print("=" * 70)
        print(f"\n  📊 СТАТИСТИКА АУДИТА:")
        print(f"    Итераций: {len(iterations)}")
        print(f"    Аудит завершен: {'✅' if audit_complete else '❌'}")
        print(f"    Операциональность: {operational_score:.1%}")
        print(f"    Фальсифицируемость: {falsifiable_score:.1%}")
        print("=" * 70)
        
        return result
    
    async def _generate_initial_idea(self, question: str) -> str:
        """Генерирует первичную идею."""
        prompt = f"""
ВОПРОС: {question}

Сгенерируй ИДЕЮ или ОТВЕТ на этот вопрос.
Будь конкретным, оригинальным, глубоким.
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
                temperature=0.85,
                max_tokens=512
            )
            
            idea = response.choices[0].message.content.strip()
            print(f"  ✅ Первичная идея: {idea[:100]}...")
            return idea
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return "Ошибка генерации первичной идеи"
    
    async def _analyze_premises(self, idea: str) -> List[str]:
        """Анализирует premises в идее."""
        prompt = f"""
ИДЕЯ:
{idea}

Проанализируй эту идею и найди все СКРЫТЫЕ PREMISES (предпосылки, допущения).
Каждая premises — это то, что принимается как истина без доказательства.

Выведи список premises (3-5 пунктов).

PREMISES:
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
            
            premises_text = response.choices[0].message.content.strip()
            premises = [p.strip() for p in premises_text.split('\n') if p.strip()]
            print(f"    ✅ Найдено premises: {len(premises)}")
            return premises
            
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return ["Идея основана на неявных допущениях"]
    
    async def _find_weak_premises(self, idea: str, premises: List[str]) -> List[Dict]:
        """Находит слабые premises."""
        premises_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(premises)])
        
        prompt = f"""
ИДЕЯ:
{idea}

PREMISES:
{premises_text}

Проанализируй каждую premises и найди СЛАБЫЕ МЕСТА:
- Логические ошибки
- Необоснованные допущения
- Потенциальные противоречия
- Неучтенные альтернативы

Для каждой слабой premises укажи:
1. Саму premises
2. Почему она слабая
3. Как можно усилить

СЛАБЫЕ PREMISES:
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
            
            weak_text = response.choices[0].message.content.strip()
            
            # Парсим результат в структурированный вид
            weak_premises = []
            lines = weak_text.split('\n')
            current = {}
            for line in lines:
                if line.strip():
                    if '1.' in line or '2.' in line or '3.' in line or '4.' in line or '5.' in line:
                        if current:
                            weak_premises.append(current)
                        current = {"premise": line.strip(), "weakness": "", "strengthen": ""}
                    elif current:
                        if "почему" in line.lower() or "слабость" in line.lower():
                            current["weakness"] = line.strip()
                        elif "усилить" in line.lower() or "strengthen" in line.lower():
                            current["strengthen"] = line.strip()
            
            if current:
                weak_premises.append(current)
            
            print(f"    ✅ Найдено слабых premises: {len(weak_premises)}")
            return weak_premises
            
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return [{"premise": "Все premises слабы", "weakness": "Требуется проверка", "strengthen": "Усилить через эксперимент"}]
    
    async def _apply_structural_breaks(self, idea: str, weak_premises: List[Dict]) -> List[str]:
        """Применяет намеренные сбои к структурам."""
        if not weak_premises:
            return ["Структуры устойчивы"]
        
        weak_text = "\n".join([
            f"- {wp.get('premise', '')}: {wp.get('weakness', '')}"
            for wp in weak_premises
        ])
        
        prompt = f"""
ИДЕЯ:
{idea}

СЛАБЫЕ PREMISES:
{weak_text}

Примени НАМЕРЕННЫЕ СБОИ к структурам идеи:
1. Представь, что premises ложны
2. Какие структуры разрушатся?
3. Какие структуры останутся устойчивыми?
4. Какие новые структуры могут возникнуть?

Опиши результаты сбоев (2-3 пункта).

РЕЗУЛЬТАТЫ СБОЕВ:
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
            
            breaks_text = response.choices[0].message.content.strip()
            breaks = [b.strip() for b in breaks_text.split('\n') if b.strip()]
            print(f"    ✅ Применено сбоев: {len(breaks)}")
            return breaks
            
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return ["Структуры устойчивы к сбоям"]
    
    async def _rebuild_with_anchors(self, idea: str, weak_premises: List[Dict], breaks: List[str]) -> str:
        """Пересобирает идею с учетом внешних якорей."""
        weak_text = "\n".join([
            f"- {wp.get('premise', '')}: {wp.get('strengthen', '')}"
            for wp in weak_premises
        ]) if weak_premises else "Нет слабых premises"
        
        breaks_text = "\n".join(breaks)
        
        prompt = f"""
ИСХОДНАЯ ИДЕЯ:
{idea}

УЛУЧШЕННЫЕ PREMISES:
{weak_text}

РЕЗУЛЬТАТЫ НАМЕРЕННЫХ СБОЕВ:
{breaks_text}

ВНЕШНИЕ ЯКОРЯ:
1. Операциональность: идея должна быть реализуема за 48 часов
2. Фальсифицируемость: должна быть возможность провести эксперимент

Создай УЛУЧШЕННУЮ ВЕРСИЮ идеи, которая:
1. Учитывает слабые premises
2. Использует результаты сбоев
3. Соответствует внешним якорям
4. Становится более устойчивой

УЛУЧШЕННАЯ ИДЕЯ (3-5 предложений):
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
            
            improved = response.choices[0].message.content.strip()
            print(f"    ✅ Идея пересобрана: {improved[:80]}...")
            return improved
            
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return idea
    
    async def _check_operational(self, idea: str) -> bool:
        """Проверяет операциональность (реализуемость за 48 часов)."""
        prompt = f"""
ИДЕЯ:
{idea}

Можно ли реализовать эту идею за 48 часов?
Оцени по шкале от 0 до 10, где:
- 0-3: невозможно за 48 часов
- 4-6: возможно, но сложно
- 7-10: легко реализуемо

Ответь ТОЛЬКО числом (0-10) и кратким пояснением.

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
                temperature=0.5,
                max_tokens=100
            )
            
            text = response.choices[0].message.content.strip()
            # Извлекаем число
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                score = int(numbers[0]) / 10
                return score >= 0.6  # Порог 6/10
            
            return False
            
        except Exception as e:
            print(f"    ❌ Ошибка проверки операциональности: {e}")
            return False
    
    async def _check_falsifiable(self, idea: str) -> bool:
        """Проверяет фальсифицируемость (возможность эксперимента)."""
        prompt = f"""
ИДЕЯ:
{idea}

Можно ли провести ЭКСПЕРИМЕНТ, который мог бы опровергнуть эту идею?
Оцени по шкале от 0 до 10, где:
- 0-3: невозможно проверить
- 4-6: можно, но сложно
- 7-10: легко проверить экспериментом

Ответь ТОЛЬКО числом (0-10) и кратким пояснением.

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
                temperature=0.5,
                max_tokens=100
            )
            
            text = response.choices[0].message.content.strip()
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                score = int(numbers[0]) / 10
                return score >= 0.6  # Порог 6/10
            
            return False
            
        except Exception as e:
            print(f"    ❌ Ошибка проверки фальсифицируемости: {e}")
            return False
    
    async def _synthesize_final(self, question: str, iterations: List[AuditIteration]) -> str:
        """Синтезирует финальный ответ из всех итераций."""
        iterations_text = ""
        for i, it in enumerate(iterations, 1):
            iterations_text += f"""
Итерация {i}:
- Улучшенная идея: {it.improved_idea[:150]}...
- Операциональна: {'✅' if it.is_operational else '❌'}
- Фальсифицируема: {'✅' if it.is_falsifiable else '❌'}
"""
        
        prompt = f"""
ВОПРОС: {question}

РЕЗУЛЬТАТЫ ВСЕХ ИТЕРАЦИЙ МЕТАКОГНИТИВНОГО АУДИТА:
{iterations_text}

Создай ФИНАЛЬНЫЙ, ЦЕЛЬНЫЙ, ГЛУБОКИЙ ответ на вопрос.
Он должен:
1. Учитывать все улучшения из итераций
2. Быть операциональным (реализуемым за 48 часов)
3. Быть фальсифицируемым (проверяемым экспериментом)
4. Содержать практические шаги

Ответ должен быть 4-6 предложений.

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
            print(f"  ❌ Ошибка синтеза: {e}")
            return iterations[-1].improved_idea if iterations else "Ошибка синтеза"

# ================================================================
# HTML ДЛЯ ВЕБ-ЧАТА
# ================================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Метакогнитивный Аудит</title>
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
        .badge.audit { background: rgba(255, 215, 0, 0.2); color: #ffd700; border: 1px solid rgba(255, 215, 0, 0.2); }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 25px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .chat-container::-webkit-scrollbar { width: 4px; }
        .chat-container::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        .chat-container::-webkit-scrollbar-thumb { background: rgba(95, 127, 255, 0.3); border-radius: 2px; }
        
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
        .input-container input::placeholder { color: rgba(255,255,255,0.3); }
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
        <h1>🧠 Метакогнитивный Аудит</h1>
        <div class="status">
            <span class="dot"></span>
            <span id="agentStatus">10 агентов</span>
            <span id="syncStatus" class="badge sync">sync: 0.00</span>
            <span id="auditStatus" class="badge audit">аудит: 0</span>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="role">🧠 Система</div>
            <div class="text">
                Привет! Я — <span class="highlight">Система Метакогнитивного Аудита</span>.<br>
                Я проверяю <span class="highlight">premises</span>, применяю <span class="highlight">намеренные сбои</span> 
                и использую <span class="highlight">внешние якоря</span>.<br>
                <br>
                <span class="highlight">⚓ Внешние якоря:</span><br>
                • Операциональность (реализуемость за 48 часов)<br>
                • Фальсифицируемость (возможность эксперимента)<br>
                <br>
                Задай вопрос, и я проведу <span class="highlight">3-итерационный аудит</span>!
            </div>
        </div>
    </div>
    
    <div class="suggestions">
        <button onclick="askQuestion('Как создать идеальный ИИ-помощник для творческих задач?')">🎨 Творческий ИИ</button>
        <button onclick="askQuestion('Что важнее для успеха: талант или упорный труд?')">⭐ Талант vs Труд</button>
        <button onclick="askQuestion('Как изменить свою жизнь за год?')">🚀 Изменение жизни</button>
        <button onclick="askQuestion('Какие качества делают человека лидером?')">👑 Лидерство</button>
        <button onclick="askQuestion('Как создать гармоничное общество в эпоху технологий?')">🌍 Гармония</button>
    </div>
    
    <div class="input-container">
        <input id="questionInput" placeholder="Задайте вопрос для метакогнитивного аудита..." 
               onkeypress="if(event.key==='Enter') askQuestion()">
        <button id="sendButton" onclick="askQuestion()">🔍 Запустить аудит</button>
    </div>
    
    <script>
        let isProcessing = false;
        let auditCount = 0;
        
        function addMessage(role, content, isThinking = false) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            if (isThinking) {
                div.innerHTML = `
                    <div class="role">🧠 Проводится аудит...</div>
                    <div class="thinking">
                        <span></span><span></span><span></span>
                    </div>
                `;
            } else {
                const roleIcon = role === 'user' ? '👤' : role === 'meta' ? '🔍' : '🧠';
                const roleName = role === 'user' ? 'Вы' : role === 'meta' ? 'Мета-анализ' : 'Результат аудита';
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
            if (data.audit_count !== undefined) {
                document.getElementById('auditStatus').textContent = `аудит: ${data.audit_count}`;
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
            button.textContent = '🔍 Аудит...';
            
            addMessage('user', question);
            addMessage('agent', '', true);
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                const messages = document.querySelectorAll('.message');
                if (messages.length > 0 && messages[messages.length - 1].querySelector('.thinking')) {
                    messages[messages.length - 1].remove();
                }
                
                if (data.error) {
                    addMessage('agent', '❌ Ошибка: ' + data.error);
                } else {
                    // Показываем итерации аудита
                    if (data.iterations) {
                        for (let it of data.iterations) {
                            let details = `📋 Итерация ${it.iteration}/${data.total_iterations}\n`;
                            details += `🔍 Анализ premises: ${it.premises_analyzed.length} найдено\n`;
                            details += `⚡ Слабых premises: ${it.weak_premises.length}\n`;
                            details += `🔄 Структурных изменений: ${it.structural_changes.length}\n`;
                            details += `⚓ Операционально: ${it.is_operational ? '✅' : '❌'}\n`;
                            details += `🧪 Фальсифицируемо: ${it.is_falsifiable ? '✅' : '❌'}`;
                            addMessage('meta', details);
                        }
                    }
                    
                    // Показываем финальный ответ
                    addMessage('agent', '✨ ' + data.final_answer);
                    
                    // Статистика аудита
                    let stats = `📊 Статистика аудита:\n`;
                    stats += `• Итераций: ${data.total_iterations}\n`;
                    stats += `• Аудит завершен: ${data.audit_complete ? '✅' : '❌'}\n`;
                    stats += `• Операциональность: ${(data.operational_score * 100).toFixed(0)}%\n`;
                    stats += `• Фальсифицируемость: ${(data.falsifiable_score * 100).toFixed(0)}%`;
                    addMessage('meta', stats);
                    
                    auditCount++;
                    updateStatus({ audit_count: auditCount, sync_r: data.sync_r });
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
            button.textContent = '🔍 Запустить аудит';
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
class AuditHandler(http.server.SimpleHTTPRequestHandler):
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
                'audit_count': len(self.system.audit_history) if self.system else 0
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
                result = loop.run_until_complete(self.system.audit(question))
                loop.close()
                
                response = {
                    'question': question,
                    'iterations': [
                        {
                            'iteration': it.iteration,
                            'premises_analyzed': it.premises_analyzed,
                            'weak_premises': it.weak_premises,
                            'structural_changes': it.structural_changes,
                            'improved_idea': it.improved_idea[:200] + '...' if len(it.improved_idea) > 200 else it.improved_idea,
                            'is_operational': it.is_operational,
                            'is_falsifiable': it.is_falsifiable
                        }
                        for it in result.iterations
                    ],
                    'final_answer': result.final_answer,
                    'audit_complete': result.audit_complete,
                    'total_iterations': result.total_iterations,
                    'operational_score': result.operational_score,
                    'falsifiable_score': result.falsifiable_score,
                    'sync_r': self.system.sync_r
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
    print("  🧠 MOLECULAR AI v7.0 — МЕТАКОГНИТИВНЫЙ АУДИТ")
    print("  Конечный цикл + внешние якоря (48ч + эксперимент)")
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
    system = MetacognitiveAuditSystem(api_key)
    system.initialize()
    
    AuditHandler.system = system
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    port = 8000
    try:
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), AuditHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        webbrowser.open(f"http://localhost:{port}/")
        
        print(f"\n  🌐 http://localhost:{port}/")
        print(f"\n  🧠 СИСТЕМА ГОТОВА!")
        print(f"  🔍 Метакогнитивный аудит с конечным циклом")
        print(f"  ⚓ Внешние якоря: операциональность + фальсифицируемость")
        print(f"  🛑 Макс. итераций: {system.max_iterations}")
        print(f"\n  Нажмите Ctrl+C для остановки")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n  🛑 Остановка сервера...")
    except OSError:
        port = 8001
        os.chdir(output_dir)
        httpd = socketserver.TCPServer(("", port), AuditHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/")
        print(f"\n  🌐 http://localhost:{port}/")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()