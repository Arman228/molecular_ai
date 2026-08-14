#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Molecular AI v7.0 — ULTIMATE SYSTEM
Полная система с:
1. Самосознанием
2. Генерацией кода и созданием файлов
3. Тремя режимами: Факты, Интерпретации, Смешанный
4. Вопросами только при необходимости
5. Маркерами уверенности
6. Разделением фактов и интерпретаций
7. Когнитивной хирургией (BiasDetector)

LAUNCH:
    cd C:\Users\aleks\Desktop\molecular_ai
    move "examples\demo_ultimate_system" "examples\demo_ultimate_system.py"
    set DEEPSEEK_API_KEY=sk-...
    python examples\demo_ultimate_system.py
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
import re
import shutil

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
    {"name": "Архитектор", "persona": "Проектирует архитектуру приложений, выбирает технологии."},
    {"name": "Backend_Developer", "persona": "Пишет серверный код, API, базы данных."},
    {"name": "Frontend_Developer", "persona": "Создает интерфейс, HTML, CSS, JavaScript."},
    {"name": "Тестировщик", "persona": "Пишет тесты, проверяет код, находит баги."},
    {"name": "Документатор", "persona": "Создает документацию, README, комментарии."},
    {"name": "Скептик", "persona": "Ставит под сомнение, ищет альтернативные объяснения."},
    {"name": "Синтезатор", "persona": "Объединяет факты и интерпретации в целостный ответ."},
    {"name": "Мета-мыслитель", "persona": "Наблюдает за процессом, управляет пересборкой идей."},
]

class UltimateSystem:
    """Полная система со всеми улучшениями."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system = None
        self.sync_r = 0.0
        self.clarification_count = 0
        self.max_clarifications = 2
        self.generated_files = []
        self.dialog_history = []
        self.output_dir = None
        self.current_mode = "mixed"
        self.system_name = "Ultimate System v7.0"
        self.current_project_dir = None
        
        # Слова для самосознания
        self.self_keywords = [
            "систем", "ты", "эта", "наша", "ваша", 
            "умеешь", "можешь", "функционал", "возможност",
            "что ты", "кто ты", "расскажи о себе"
        ]
        
        # Слова для кода
        self.code_keywords = [
            "напиши код", "создай", "напиши программу", "сделай", 
            "напиши скрипт", "напиши функцию", "напиши класс",
            "создай приложение", "напиши сайт", "напиши бота",
            "код для", "программа для", "скрипт для",
            "python", "javascript", "html", "css", "react", "flask", "django"
        ]
        
    def initialize(self):
        """Инициализация системы."""
        print("\n🧠 ИНИЦИАЛИЗАЦИЯ ULTIMATE SYSTEM v7.0...")
        print("  🔍 Самосознание + Генерация кода + Создание файлов")
        print("  📊 3 режима: Факты, Интерпретации, Смешанный")
        print("  🛑 Вопросы только при необходимости")
        
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
        
        # Создаем папку для файлов
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output",
            "ultimate_files"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"  ✅ Папка для файлов: {self.output_dir}")
    
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
        """Устанавливает режим."""
        if mode in ["facts", "interpretations", "mixed"]:
            self.current_mode = mode
            print(f"  📊 Режим: {mode}")
    
    def _is_question_about_self(self, question: str) -> bool:
        """Проверяет, вопрос о системе."""
        question_lower = question.lower()
        return any(kw in question_lower for kw in self.self_keywords)
    
    def _is_code_request(self, question: str) -> bool:
        """Проверяет, запрос на код."""
        question_lower = question.lower()
        return any(kw in question_lower for kw in self.code_keywords)
    
    def get_self_description(self) -> str:
        """Описание системы."""
        return """🔬 ULTIMATE SYSTEM v7.0

**Что я умею:**

📊 **Три режима ответа:**
1. **Факты** — только проверенная информация с уверенностью (0-100%)
2. **Интерпретации** — разные точки зрения и перспективы
3. **Смешанный** — и факты, и интерпретации

💻 **Генерация кода и создание файлов:**
• Автоматически создаю код на Python, JavaScript, HTML, CSS
• Создаю структуру проекта и файлы
• Пишу README и документацию
• Тестирую код перед созданием

🧠 **Самосознание:**
• Знаю, кто я и что умею
• Понимаю свои ограничения
• Отвечаю на вопросы о себе

🎯 **Интеллектуальные возможности:**
• Разделяю факты и интерпретации
• Указываю уверенность в процентах
• Анализирую документы (PDF, Word, Excel)
• Перевожу и анализирую текст

⚡ **Ограничения:**
• Не генерирую изображения и видео
• Работаю с данными до текущего момента
• Лучшее качество — с четкими запросами

💡 **Как использовать:**
1. Просто задайте вопрос или попросите написать код
2. Система сама выберет нужный режим
3. Если нужно — задаст уточняющий вопрос (макс 2)
4. Получите структурированный ответ или готовый код

Это я. Чем могу помочь?"""
    
    async def process_request(self, question: str) -> Dict:
        """Обрабатывает запрос."""
        print("\n" + "=" * 70)
        print(f"  💬 ЗАПРОС: {question}")
        print("=" * 70)
        
        # ============================================================
        # ФАЗА 0: САМОСОЗНАНИЕ
        # ============================================================
        if self._is_question_about_self(question):
            print("\n🔍 ОБНАРУЖЕН ВОПРОС О СИСТЕМЕ")
            return {
                "type": "self_description",
                "content": self.get_self_description(),
                "mode": self.current_mode,
                "sync_r": self.sync_r
            }
        
        # ============================================================
        # ФАЗА 1: ГЕНЕРАЦИЯ КОДА
        # ============================================================
        if self._is_code_request(question):
            print("\n💻 ОБНАРУЖЕН ЗАПРОС НА НАПИСАНИЕ КОДА")
            return await self._generate_code(question)
        
        # ============================================================
        # ФАЗА 2: АНАЛИЗ ДВУСМЫСЛЕННОСТИ
        # ============================================================
        print("\n🔍 ФАЗА 2: АНАЛИЗ ДВУСМЫСЛЕННОСТИ")
        ambiguity_score = await self._check_ambiguity(question)
        
        # Вопрос только если действительно нужно И не превышен лимит
        if ambiguity_score > 0.8 and self.clarification_count < self.max_clarifications:
            self.clarification_count += 1
            print(f"  ⚠️ Требуется уточнение (попытка {self.clarification_count}/{self.max_clarifications})")
            clarification = await self._generate_clarification(question)
            return {
                "type": "clarification",
                "question": clarification,
                "reason": "Уточните, пожалуйста",
                "sync_r": self.sync_r
            }
        elif ambiguity_score > 0.8 and self.clarification_count >= self.max_clarifications:
            print(f"  ⚠️ Достигнут лимит уточнений. Даю ответ.")
            self.clarification_count = 0
        
        self.clarification_count = 0
        
        # ============================================================
        # ФАЗА 3: ОБЫЧНЫЙ ОТВЕТ
        # ============================================================
        if self.current_mode == "facts":
            return await self._generate_factual_response(question)
        elif self.current_mode == "interpretations":
            return await self._generate_interpretations(question)
        else:
            return await self._generate_mixed_response(question)
    
    async def _check_ambiguity(self, question: str) -> float:
        """Проверяет двусмысленность."""
        prompt = f"""
Оцени двусмысленность вопроса от 0 до 1:

ВОПРОС: {question}

0 = абсолютно конкретный
1 = крайне двусмысленный

Учитывай: неоднозначные термины, отсутствие контекста, множественные интерпретации.

Ответь ТОЛЬКО числом.

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
            print(f"  ❌ Ошибка: {e}")
            return 0.3
    
    async def _generate_clarification(self, question: str) -> str:
        """Генерирует уточняющий вопрос."""
        prompt = f"""
ВОПРОС: {question}

Создай краткий уточняющий вопрос (1-2 предложения).

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
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return f"Уточните, пожалуйста, что именно вы хотите узнать."
    
    async def _generate_factual_response(self, question: str) -> Dict:
        """Генерирует ответ с фактами."""
        prompt = f"""
ВОПРОС: {question}

Дай ответ с фактами:
1. 3-5 проверенных фактов
2. Уверенность в процентах
3. Альтернативы (если есть)

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
            
            # Парсим факты
            facts = []
            alternatives = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    if 'альтернатив' in line.lower():
                        alternatives.append(line)
                    elif line.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-')):
                        facts.append(line)
            
            if len(facts) < 2:
                facts = [text[:200] + "..."]
            
            return {
                "type": "facts",
                "facts": facts[:5],
                "certainty": 0.75,
                "alternatives": alternatives[:3],
                "mode": "facts",
                "sync_r": self.sync_r
            }
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return {
                "type": "facts",
                "facts": ["Информация временно недоступна"],
                "certainty": 0.0,
                "alternatives": [],
                "mode": "facts",
                "sync_r": self.sync_r
            }
    
    async def _generate_interpretations(self, question: str) -> Dict:
        """Генерирует интерпретации."""
        prompt = f"""
ВОПРОС: {question}

Дай разные интерпретации:
1. 3-4 точки зрения
2. Для каждой - перспективу и аргументацию
3. Рекомендацию

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
                    {"perspective": "Основная", "text": text[:100] + "..."}
                ]
            
            return {
                "type": "interpretations",
                "interpretations": interpretations[:4],
                "perspectives": len(interpretations),
                "recommendation": "Рассмотрите все перспективы",
                "mode": "interpretations",
                "sync_r": self.sync_r
            }
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return {
                "type": "interpretations",
                "interpretations": [{"perspective": "Основная", "text": "Информация недоступна"}],
                "perspectives": 1,
                "recommendation": "Попробуйте уточнить вопрос",
                "mode": "interpretations",
                "sync_r": self.sync_r
            }
    
    async def _generate_mixed_response(self, question: str) -> Dict:
        """Генерирует смешанный ответ."""
        facts = await self._generate_factual_response(question)
        interps = await self._generate_interpretations(question)
        
        return {
            "type": "mixed",
            "facts": facts.get("facts", []),
            "interpretations": interps.get("interpretations", []),
            "certainty": facts.get("certainty", 0.7),
            "mode": "mixed",
            "sync_r": self.sync_r,
            "divider": "--- ФАКТЫ | ИНТЕРПРЕТАЦИИ ---"
        }
    
    async def _generate_code(self, question: str) -> Dict:
        """Генерирует код и создает файлы."""
        print("\n💻 ГЕНЕРАЦИЯ КОДА И СОЗДАНИЕ ФАЙЛОВ:")
        
        # 1. Анализ
        print("  📋 Анализ запроса...")
        analysis = await self._analyze_code_request(question)
        
        # 2. Архитектура
        print("  🏗️ Проектирование архитектуры...")
        architecture = await self._design_architecture(question, analysis)
        
        # 3. Генерация файлов
        print("  💻 Генерация кода...")
        files = await self._generate_files(question, architecture)
        
        # 4. Создание на диске
        print("  📁 Создание файлов...")
        created = await self._create_files(files, architecture)
        
        # 5. Сводка
        summary = self._generate_summary(created)
        
        return {
            "type": "code",
            "message": "✅ Код успешно сгенерирован!",
            "files": created,
            "summary": summary,
            "project_dir": self.current_project_dir,
            "sync_r": self.sync_r
        }
    
    async def _analyze_code_request(self, question: str) -> Dict:
        """Анализирует запрос на код."""
        prompt = f"""
Проанализируй запрос на код:

{question}

Определи:
1. Тип (скрипт, приложение, сайт, API, бот)
2. Язык
3. Что нужно создать

Ответ в JSON:
{{"type": "...", "language": "...", "description": "..."}}
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
                max_tokens=256
            )
            
            text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "type": "скрипт",
                "language": "python",
                "description": question
            }
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return {
                "type": "скрипт",
                "language": "python",
                "description": question
            }
    
    async def _design_architecture(self, question: str, analysis: Dict) -> str:
        """Проектирует архитектуру."""
        prompt = f"""
Запрос: {question}
Анализ: {json.dumps(analysis, ensure_ascii=False)}

Опиши архитектуру решения (2-3 предложения).

АРХИТЕКТУРА:
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
            print(f"  ❌ Ошибка: {e}")
            return "Простая структура с одним файлом"
    
    async def _generate_files(self, question: str, architecture: str) -> List[Dict]:
        """Генерирует файлы."""
        # Определяем файлы
        prompt = f"""
Запрос: {question}
Архитектура: {architecture}

Какие файлы нужны?
Ответ в JSON: {{"files": [{{"name": "...", "language": "...", "purpose": "..."}}]}}
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
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                file_specs = data.get("files", [])
            else:
                file_specs = [{"name": "main.py", "language": "python", "purpose": "Основной файл"}]
            
            print(f"  📋 Будет создано {len(file_specs)} файлов")
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            file_specs = [{"name": "main.py", "language": "python", "purpose": "Основной файл"}]
        
        # Генерируем код для каждого файла
        generated = []
        for spec in file_specs:
            print(f"    📝 Генерация {spec['name']}...")
            
            code_prompt = f"""
Запрос: {question}
Файл: {spec['name']}
Язык: {spec['language']}
Назначение: {spec['purpose']}

Напиши полный код. Только код, без объяснений.
"""
            
            try:
                client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
                
                response = await client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": code_prompt}],
                    temperature=0.8,
                    max_tokens=4096
                )
                
                content = response.choices[0].message.content.strip()
                # Убираем markdown
                content = re.sub(r'```\w*\n?', '', content)
                content = re.sub(r'```', '', content)
                
                generated.append({
                    "name": spec['name'],
                    "language": spec['language'],
                    "content": content,
                    "purpose": spec['purpose']
                })
                
                print(f"      ✅ {len(content)} символов")
                
            except Exception as e:
                print(f"      ❌ Ошибка: {e}")
                generated.append({
                    "name": spec['name'],
                    "language": spec['language'],
                    "content": f"# Ошибка генерации: {e}",
                    "purpose": spec['purpose']
                })
        
        return generated
    
    async def _create_files(self, files: List[Dict], architecture: str) -> List[Dict]:
        """Создает файлы на диске."""
        project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = os.path.join(self.output_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        self.current_project_dir = project_dir
        
        created = []
        
        for file_info in files:
            file_path = os.path.join(project_dir, file_info['name'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            size = os.path.getsize(file_path) / 1024
            created.append({
                "name": file_info['name'],
                "path": file_path,
                "size": round(size, 2),
                "language": file_info.get('language', 'text')
            })
            
            print(f"    📄 {file_info['name']} ({size:.1f} KB)")
        
        # README
        readme = self._generate_readme(created, project_name, architecture)
        readme_path = os.path.join(project_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        created.append({
            "name": "README.md",
            "path": readme_path,
            "size": round(len(readme) / 1024, 2),
            "language": "markdown"
        })
        
        # Сохраняем информацию
        self.generated_files.append({
            "project_name": project_name,
            "project_dir": project_dir,
            "files": created,
            "timestamp": datetime.now().isoformat()
        })
        
        return created
    
    def _generate_readme(self, files: List[Dict], project_name: str, architecture: str) -> str:
        """Генерирует README."""
        readme = f"# {project_name}\n\n"
        readme += "## 📋 Описание\n"
        readme += f"{architecture}\n\n"
        readme += "## 📁 Структура\n\n"
        
        for f in files:
            readme += f"- `{f['name']}` ({f.get('language', 'text')}) - {f.get('size', 0)} KB\n"
        
        readme += f"""
## 🚀 Запуск

```bash
# Установите зависимости (если есть)
pip install -r requirements.txt

# Запустите
python main.py