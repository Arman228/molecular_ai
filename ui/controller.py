# ui/controller.py
"""
Molecular AI v7.0 — Ultimate System Controller
С ПОЛНОЙ ИНТЕГРАЦИЕЙ ВСЕХ МОДУЛЕЙ И УВЕЛИЧЕННЫМИ ТОКЕНАМИ
"""

import os
import sys
import random
import asyncio
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import shutil
from collections import deque
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.system import MolecularSystem
    from core.convergence_regime import ConvergenceRegime, set_regime
except ImportError as e:
    print("⚠️ Ошибка импорта core: " + str(e))

try:
    from core.auto_skills import AutoSkillEngine, attach_to_system
    HAS_AUTO_SKILLS = True
except ImportError as e:
    HAS_AUTO_SKILLS = False
    print("⚠️ AutoSkillEngine не найден: " + str(e))

try:
    from core.meta_optimizer import MetaOptimizer, attach_optimizer_to_engine
    HAS_META_OPTIMIZER = True
except ImportError as e:
    HAS_META_OPTIMIZER = False
    print("⚠️ MetaOptimizer не найден: " + str(e))

try:
    from core.sensor_fusion import SensorFusionLayer, PerAxisReputation
    HAS_SENSOR_FUSION = True
except ImportError as e:
    HAS_SENSOR_FUSION = False
    print("⚠️ SensorFusion не найден: " + str(e))

try:
    from core.tuning import AutoTuner
    HAS_TUNING = True
except ImportError as e:
    HAS_TUNING = False
    print("⚠️ AutoTuner не найден: " + str(e))

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️ OpenAI не установлен. Установите: pip install openai")

# ================================================================
# КЛАССЫ ДЛЯ САМООБУЧЕНИЯ
# ================================================================

class KnowledgeBase:
    """База знаний с поиском."""
    
    def __init__(self, storage_path: str = "data/learning/knowledge_base.json"):
        self.storage_path = storage_path
        self.entries = []
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.load()
    
    def add_entry(self, question: str, answer: str, rating: float = 0.5, user_id: str = None, context: Dict = None):
        entry = {
            "id": hashlib.md5((question + str(time.time())).encode()).hexdigest(),
            "question": question,
            "answer": answer,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "context": context or {},
            "keywords": self._extract_keywords(question),
            "use_count": 0,
            "success_count": 0
        }
        self.entries.append(entry)
        self.save()
        return entry
    
    def search(self, question: str, top_k: int = 3, user_id: str = None) -> List[Dict]:
        keywords = self._extract_keywords(question)
        scored = []
        
        for entry in self.entries:
            score = 0.0
            entry_keywords = entry.get("keywords", [])
            if isinstance(entry_keywords, list):
                common = set(keywords) & set(entry_keywords)
                score += len(common) * 2.0
            
            rating = entry.get("rating", 0)
            if isinstance(rating, (int, float)):
                score += rating * 3.0
            
            if user_id and entry.get("user_id") == user_id:
                score += 10.0
            
            use_count = entry.get("use_count", 0)
            if isinstance(use_count, (int, float)):
                score += min(use_count / 10.0, 5.0)
            
            scored.append((score, entry))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]
    
    def update_usage(self, entry_id: str, success: bool = True):
        for entry in self.entries:
            if entry.get("id") == entry_id:
                entry["use_count"] = entry.get("use_count", 0) + 1
                if success:
                    entry["success_count"] = entry.get("success_count", 0) + 1
                self.save()
                break
    
    def get_stats(self) -> Dict:
        if not self.entries:
            return {"total_entries": 0, "avg_rating": 0.0}
        
        total_rating = sum(e.get("rating", 0) for e in self.entries if isinstance(e.get("rating"), (int, float)))
        return {
            "total_entries": len(self.entries),
            "avg_rating": total_rating / len(self.entries) if self.entries else 0.0
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\w+', text.lower())
        stop_words = {'это', 'все', 'как', 'что', 'для', 'на', 'с', 'по', 'из', 'у', 'же', 'бы', 'да', 'нет', 'или', 'когда', 'где', 'почему', 'зачем', 'кто', 'который', 'такой'}
        return [w for w in words if len(w) > 2 and w not in stop_words][:10]
    
    def save(self):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({"entries": self.entries}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения базы знаний: {e}")
    
    def load(self):
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
                print(f"✅ Загружено {len(self.entries)} записей из базы знаний")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки базы знаний: {e}")


class LearningSystem:
    """Система самообучения."""
    
    def __init__(self, storage_dir: str = "data/learning"):
        os.makedirs(storage_dir, exist_ok=True)
        self.knowledge_base = KnowledgeBase(os.path.join(storage_dir, "knowledge_base.json"))
        self.metrics = {
            "total_interactions": 0,
            "successful_answers": 0,
            "failed_answers": 0
        }
        self._load_metrics()
    
    def _load_metrics(self):
        try:
            path = os.path.join(os.path.dirname(self.knowledge_base.storage_path), "metrics.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.metrics.update(json.load(f))
        except:
            pass
    
    def _save_metrics(self):
        try:
            path = os.path.join(os.path.dirname(self.knowledge_base.storage_path), "metrics.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения метрик: {e}")
    
    def get_personalized_context(self, question: str, user_id: str = None) -> Dict:
        try:
            similar = self.knowledge_base.search(question, top_k=3, user_id=user_id)
            return {"similar_questions": similar}
        except Exception as e:
            print(f"⚠️ Ошибка поиска: {e}")
            return {"similar_questions": []}
    
    def get_learning_stats(self) -> Dict:
        return {
            "knowledge_base": self.knowledge_base.get_stats(),
            "metrics": self.metrics,
            "success_rate": self.metrics["successful_answers"] / max(1, self.metrics["total_interactions"])
        }


# ================================================================
# ОСНОВНОЙ КОНТРОЛЛЕР
# ================================================================

class UltimateController:
    def __init__(self):
        self.system = None
        self.is_running = False
        self.thread = None
        self.stats_history = []
        self.generated_projects = []
        self.current_mode = "mixed"
        self.output_dir = None
        self.sync_r = 0.0
        
        self.dialog_history = deque(maxlen=50)
        self.context_memory = {}
        
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.client = None
        if self.api_key and HAS_OPENAI:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            print("✅ DeepSeek API инициализирован")
        else:
            print("⚠️ DeepSeek API не инициализирован")
        
        self.current_project_dir = None
        
        # Самообучение
        self.learning_system = LearningSystem("data/learning")
        print("✅ Система самообучения инициализирована")
        
        # AutoSkillEngine
        self.auto_skill = None
        if HAS_AUTO_SKILLS:
            self.auto_skill = AutoSkillEngine(use_llm=bool(self.client), adapter=self.client)
            print("✅ AutoSkillEngine инициализирован")
        else:
            print("⚠️ AutoSkillEngine не доступен")
        
        # MetaOptimizer
        self.meta_optimizer = None
        if HAS_META_OPTIMIZER:
            self.meta_optimizer = MetaOptimizer(n_samples=8, use_grid=False)
            if self.auto_skill:
                attach_optimizer_to_engine(self.auto_skill)
            print("✅ MetaOptimizer инициализирован")
        else:
            print("⚠️ MetaOptimizer не доступен")
        
        # Sensor Fusion
        self.sensor_fusion = None
        if HAS_SENSOR_FUSION:
            dimensions = [
                {"name": "accuracy", "weight": 1.0},
                {"name": "creativity", "weight": 0.8},
                {"name": "relevance", "weight": 1.0},
                {"name": "clarity", "weight": 0.9},
                {"name": "novelty", "weight": 0.7}
            ]
            self.sensor_fusion = SensorFusionLayer(
                n_agents=10,
                dimensions=dimensions,
                threshold=2.0,
                min_rep=0.5,
                reputation_window=50
            )
            print("✅ Sensor Fusion инициализирован")
        else:
            print("⚠️ Sensor Fusion не доступен")
        
        # AutoTuner
        self.tuner = None
        if HAS_TUNING:
            self.tuner = AutoTuner()
            print("✅ AutoTuner инициализирован")
        else:
            print("⚠️ AutoTuner не доступен")
    
    # ================================================================
    # УМНОЕ РАСПОЗНАВАНИЕ
    # ================================================================
    
    def _detect_intent(self, question: str) -> str:
        question_lower = question.lower()
        
        if question.startswith('/'):
            return 'command'
        
        if any(kw in question_lower for kw in ['создай навык', 'сгенерируй навык', 'новый навык']):
            return 'skill_generation'
        
        if any(kw in question_lower for kw in ['оптимизируй', 'настрой параметры', 'подбери конфиг']):
            return 'optimization'
        
        if self._is_question(question):
            if any(kw in question_lower for kw in ['напиши код', 'создай код', 'сгенерируй код']):
                return 'code_request'
            return 'question'
        
        if self._is_code_request_advanced(question):
            return 'code_request'
        
        if self._is_question_about_self(question):
            return 'self_question'
        
        return 'question'
    
    def _is_question(self, question: str) -> bool:
        question_lower = question.lower()
        
        question_words = [
            'что', 'как', 'почему', 'зачем', 'где', 'когда', 'кто', 'какой',
            'сколько', 'куда', 'откуда', 'чей', 'чья', 'чьё', 'чьи'
        ]
        if any(q in question_lower for q in question_words):
            if any(kw in question_lower for kw in ['напиши', 'создай', 'сделай', 'сгенерируй']):
                return False
            return True
        
        if '?' in question:
            return True
        
        question_verbs = ['объясни', 'расскажи', 'покажи', 'опиши', 'подскажи', 'помоги']
        if any(v in question_lower for v in question_verbs):
            if any(kw in question_lower for kw in ['код', 'программу', 'скрипт', 'файл']):
                return False
            return True
        
        return False
    
    def _is_code_request_advanced(self, question: str) -> bool:
        question_lower = question.lower()
        
        code_requests = [
            'напиши код', 'создай код', 'сгенерируй код',
            'напиши программу', 'создай программу',
            'напиши скрипт', 'создай скрипт',
            'сделай сайт', 'создай сайт',
            'сделай игру', 'создай игру'
        ]
        if any(req in question_lower for req in code_requests):
            return True
        
        if any(kw in question_lower for kw in ['создай', 'сделай', 'сгенерируй']):
            if not self._is_question(question):
                create_objects = ['игру', 'сайт', 'программу', 'скрипт', 'приложение', 'проект', 'код', 'страницу', 'лендинг']
                if any(obj in question_lower for obj in create_objects):
                    return True
        
        code_keywords = ['python', 'javascript', 'html', 'css', 'react', 'flask', 'django', 'node']
        if any(kw in question_lower for kw in code_keywords):
            if any(q in question_lower for q in ['что такое', 'как работает', 'зачем']):
                return False
            return True
        
        return False
    
    def _is_question_about_self(self, question: str) -> bool:
        self_phrases = ["расскажи о себе", "что ты умеешь", "кто ты", "ты кто", "опиши себя"]
        return any(p in question.lower() for p in self_phrases)
    
    def get_self_description(self) -> str:
        text = """🧠 Molecular AI v7.0 — Ultimate System

**Что я умею:**
• Отвечаю на вопросы с учетом контекста
• Пишу код на Python, JavaScript, HTML, CSS
• Генерирую полноценные проекты
• Загружаю и анализирую файлы и картинки
• Самообучаюсь на ваших оценках
• 🔥 СОЗДАЮ НОВЫЕ НАВЫКИ! (AutoSkillEngine)
• ⚡ ОПТИМИЗИРУЮ ПАРАМЕТРЫ! (MetaOptimizer)
• 🧠 КОНСЕНСУС АГЕНТОВ! (SensorFusion)
• 🔧 АВТОНАСТРОЙКА! (AutoTuner)

**🤖 Агенты:**
• 10 агентов с разными ролями
• Курамото синхронизация (r=0.65-0.95)
• 3 режима: Факты, Интерпретации, Смешанный

**🧠 Самообучение:**
• Запоминает успешные ответы
• Персонализируется под вас
• Команды: /learning, /rate 0.8

**🔥 Auto Skills:**
• /skill [задача] — создать навык
• /skills — список навыков
• /skill_stats — статистика навыков
• /sleep — очистка слабых навыков

**⚡ MetaOptimizer:**
• /optimize [задача] — найти лучшие параметры
• /optimize_info — информация об оптимизаторе

**🧠 Sensor Fusion:**
• /fusion — матрица репутации агентов
• /fusion_stats — статистика сенсорного слияния

**🔧 AutoTuner:**
• /tune — автонастройка параметров

**📁 Файлы:**
• Загружайте картинки, документы, код
• Drag & Drop поддержка"""
        return text
    
    # ================================================================
    # ОСНОВНЫЕ МЕТОДЫ
    # ================================================================
    
    def init_system(self, n_agents: int = 10, dt: float = 0.02, noise: float = 0.03):
        try:
            self.system = MolecularSystem(
                n_agents=n_agents,
                dt=dt,
                noise=noise,
                sleep_every=400,
                k_sparse=6,
                exc_ratio=0.9
            )
            
            for layer in self.system.orbital.layers:
                layer.coupling *= 4.0
            
            for agent in self.system.agents:
                agent.omega = 1.0 + random.uniform(-0.08, 0.08)
            
            self._warm_up()
            
            self.output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "output",
                "ultimate_files"
            )
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.is_running = True
            return {
                "status": "ok", 
                "agents": n_agents, 
                "sync_r": float(self.system.order_parameter())
            }
        except Exception as e:
            return {"error": "Ошибка: " + str(e)}
    
    def _warm_up(self):
        try:
            set_regime(self.system, ConvergenceRegime.DIVERGENT)
            for _ in range(200):
                self.system.step()
            set_regime(self.system, ConvergenceRegime.CRITICAL)
            for _ in range(200):
                self.system.step()
            set_regime(self.system, ConvergenceRegime.LINEAR)
            for _ in range(300):
                self.system.step()
            self.sync_r = float(self.system.order_parameter())
        except Exception as e:
            print("⚠️ Ошибка разогрева: " + str(e))
    
    def step(self, n_steps: int = 1) -> Dict:
        if not self.system:
            return {}
        try:
            for _ in range(n_steps):
                self.system.step()
            metrics = {
                "sync_r": float(self.system.order_parameter()),
                "step": self.system.step_count,
                "mean_mood": float(sum(a.mood for a in self.system.agents) / len(self.system.agents))
            }
            self.stats_history.append(metrics)
            return metrics
        except Exception as e:
            return {"error": str(e)}
    
    def run_async(self, n_steps: int = 100, callback=None):
        if self.is_running:
            return
        self.is_running = True
        def run():
            for i in range(n_steps):
                if not self.is_running:
                    break
                metrics = self.step(1)
                if callback:
                    callback(metrics, i)
                time.sleep(0.01)
            self.is_running = False
        self.thread = threading.Thread(target=run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def set_mode(self, mode: str):
        if mode in ["facts", "interpretations", "mixed"]:
            self.current_mode = mode
            return {"mode": mode}
        return {"error": "Invalid mode"}
    
    # ================================================================
    # ГЛАВНЫЙ МЕТОД ОБРАБОТКИ ЗАПРОСОВ
    # ================================================================
    
    async def ask_question(self, question: str, mode: str = None, files: List[Dict] = None, user_id: str = None) -> Dict:
        if not self.system:
            return {"error": "System not initialized"}
        
        intent = self._detect_intent(question)
        
        if intent == 'command':
            return await self._handle_command(question)
        
        if intent == 'skill_generation' and HAS_AUTO_SKILLS:
            return await self._generate_skill(question)
        
        if intent == 'optimization' and HAS_META_OPTIMIZER:
            return await self._optimize_parameters(question)
        
        if intent == 'self_question':
            return {
                "type": "self_description",
                "content": self.get_self_description()
            }
        
        if intent == 'code_request':
            return await self._generate_code(question)
        
        return await self._generate_answer_with_fusion(question)
    
    # ================================================================
    # ГЕНЕРАЦИЯ ОТВЕТОВ
    # ================================================================
    
    async def _generate_answer_with_fusion(self, question: str) -> Dict:
        context = self.learning_system.get_personalized_context(question)
        similar = context.get("similar_questions", [])
        
        if similar and similar[0].get("rating", 0) > 0.8:
            best = similar[0]
            self.learning_system.knowledge_base.update_usage(best["id"], success=True)
            return {
                "type": "answer",
                "content": "💡 Из базы знаний:\n\n" + best["answer"],
                "using_cache": True,
                "confidence": best.get("rating", 0.8)
            }
        
        if HAS_SENSOR_FUSION and self.sensor_fusion and self.system:
            try:
                measurements = []
                n_agents = min(len(self.system.agents), 10)
                
                for i in range(n_agents):
                    agent = self.system.agents[i]
                    mood_factor = (agent.mood + 1) / 2
                    energy_factor = min(agent.energy / 10, 1.0)
                    sync_factor = self.sync_r
                    
                    measurements.append([
                        mood_factor * 0.7 + 0.3,
                        (1 - abs(agent.mood)) * 0.5 + 0.5,
                        sync_factor * 0.6 + 0.4,
                        energy_factor * 0.5 + 0.5,
                        (1 - sync_factor) * 0.5 + 0.3
                    ])
                
                consensus = self.sensor_fusion.process_round(measurements)
                trusted_agents = self.sensor_fusion.reputation.pre_filter(0, min_rep=0.5)
                
                if self.client:
                    fusion_prompt = f"Вопрос: {question}\n\nКонсенсус агентов:\n"
                    fusion_prompt += f"Точность: {consensus[0]:.2f}\n"
                    fusion_prompt += f"Креативность: {consensus[1]:.2f}\n"
                    fusion_prompt += f"Релевантность: {consensus[2]:.2f}\n"
                    fusion_prompt += f"Ясность: {consensus[3]:.2f}\n"
                    fusion_prompt += f"Новизна: {consensus[4]:.2f}\n\n"
                    fusion_prompt += "Дай ответ на вопрос с учетом этих параметров."
                    
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": fusion_prompt}],
                        temperature=0.7,
                        max_tokens=4096
                    )
                    content = response.choices[0].message.content
                    entry = self.learning_system.knowledge_base.add_entry(question, content, rating=0.7)
                    
                    return {
                        "type": "answer",
                        "content": content,
                        "entry_id": entry["id"],
                        "consensus": consensus,
                        "trusted_agents": len(trusted_agents)
                    }
            except Exception as e:
                print(f"⚠️ Ошибка сенсорного слияния: {e}")
        
        return await self._generate_answer(question)
    
    async def _generate_answer(self, question: str) -> Dict:
        if self.client:
            try:
                prompt = f"Вопрос: {question}\n\nДай полезный, развернутый ответ."
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=4096
                )
                content = response.choices[0].message.content
                entry = self.learning_system.knowledge_base.add_entry(question, content, rating=0.7)
                return {
                    "type": "answer",
                    "content": content,
                    "entry_id": entry["id"]
                }
            except Exception as e:
                return {"type": "answer", "content": f"❌ Ошибка DeepSeek: {str(e)}"}
        
        return {"type": "answer", "content": "⚠️ DeepSeek API не настроен. Установите DEEPSEEK_API_KEY"}
    
    # ================================================================
    # ГЕНЕРАЦИЯ НАВЫКОВ
    # ================================================================
    
    async def _generate_skill(self, question: str) -> Dict:
        if not HAS_AUTO_SKILLS or not self.auto_skill:
            return {"type": "answer", "content": "❌ AutoSkillEngine не доступен"}
        
        task = re.sub(r'(создай навык|сгенерируй навык|новый навык)\s*', '', question, flags=re.IGNORECASE).strip()
        if not task:
            return {"type": "answer", "content": "❌ Укажите задачу для создания навыка.\nПример: 'Создай навык для работы с GraphQL API'"}
        
        try:
            candidate = self.auto_skill.run_lifecycle(task)
            
            if candidate and candidate.validation_score >= 0.6:
                text = f"🔥 НАВЫК СОЗДАН!\n\n"
                text += f"📌 Название: {candidate.name}\n"
                text += f"📂 Категория: {candidate.category}\n"
                text += f"📊 Сложность: {candidate.complexity}/10\n"
                text += f"⭐ Оценка: {candidate.validation_score:.2f}\n"
                text += f"📝 Описание: {candidate.description}\n"
                text += f"🔑 Ключевые слова: {', '.join(candidate.keywords)}\n\n"
                text += f"💻 Код ({len(candidate.code)} символов):\n```python\n{candidate.code[:500]}{'...' if len(candidate.code) > 500 else ''}\n```\n"
                
                if candidate.tests:
                    text += f"\n🧪 Тесты:\n```python\n{candidate.tests[:300]}{'...' if len(candidate.tests) > 300 else ''}\n```\n"
                
                text += f"\n💡 Используйте этот навык для решения задач с ключевыми словами: {', '.join(candidate.keywords)}"
                
                return {"type": "answer", "content": text}
            else:
                score = candidate.validation_score if candidate else 0
                return {"type": "answer", "content": f"❌ Навык не принят (оценка: {score:.2f})\nПопробуйте уточнить задачу."}
                
        except Exception as e:
            return {"type": "answer", "content": f"❌ Ошибка создания навыка: {str(e)}"}
    
    # ================================================================
    # ОПТИМИЗАЦИЯ
    # ================================================================
    
    async def _optimize_parameters(self, question: str) -> Dict:
        if not HAS_META_OPTIMIZER or not self.meta_optimizer:
            return {"type": "answer", "content": "❌ MetaOptimizer не доступен"}
        
        task = re.sub(r'(оптимизируй|настрой параметры|подбери конфиг)\s*', '', question, flags=re.IGNORECASE).strip()
        if not task:
            return {"type": "answer", "content": "❌ Укажите задачу для оптимизации.\nПример: 'Оптимизируй параметры для GraphQL API'"}
        
        try:
            keywords = self.auto_skill._extract_keywords(task) if self.auto_skill else []
            result = self.meta_optimizer.recommend(task, keywords)
            
            text = "⚡ ОПТИМИЗАЦИЯ ГИПЕРПАРАМЕТРОВ:\n\n"
            text += f"📌 Задача: {task}\n"
            text += f"📊 Сложность: {result['profile']['complexity']}/10\n"
            text += f"🎯 Рекомендуемый режим: {result['profile']['regime']}\n"
            text += f"🔑 Ключевые слова: {', '.join(result['profile']['keywords'][:5])}\n\n"
            
            text += "⚡ ЛУЧШАЯ КОНФИГУРАЦИЯ:\n"
            text += "─" * 30 + "\n"
            for key, value in result['config'].items():
                if isinstance(value, float):
                    if value < 1:
                        text += f"   {key:14s}: {value:.4f}\n"
                    else:
                        text += f"   {key:14s}: {value:.1f}\n"
                else:
                    text += f"   {key:14s}: {value}\n"
            
            text += "\n📊 Рекомендации для настройки системы:\n"
            
            config = result['config']
            if config.get('dt', 0) < 0.03:
                text += "   • Используйте маленький dt (0.01-0.03) для точности\n"
            elif config.get('dt', 0) > 0.04:
                text += "   • Используйте большой dt (0.04-0.06) для скорости\n"
            
            if config.get('noise', 0) < 0.01:
                text += "   • Низкий шум → стабильные, предсказуемые ответы\n"
            elif config.get('noise', 0) > 0.02:
                text += "   • Высокий шум → креативные, разнообразные ответы\n"
            
            if config.get('n_agents', 0) > 8:
                text += "   • Много агентов → лучшее качество, медленнее\n"
            else:
                text += "   • Мало агентов → быстрее, но меньше креативности\n"
            
            text += f"\n💡 Используйте эти параметры при инициализации системы:\n"
            text += f"   /init {config.get('n_agents', 10)} {config.get('dt', 0.02):.3f} {config.get('noise', 0.02):.3f}"
            
            self.context_memory["last_optimization"] = {
                "task": task,
                "config": config,
                "regime": result['profile']['regime']
            }
            
            return {"type": "answer", "content": text}
            
        except Exception as e:
            return {"type": "answer", "content": f"❌ Ошибка оптимизации: {str(e)}"}
    
    # ================================================================
    # ГЕНЕРАЦИЯ КОДА (С УВЕЛИЧЕННЫМИ ТОКЕНАМИ)
    # ================================================================
    
    async def _generate_code(self, question: str) -> Dict:
        try:
            project_name = "project_" + datetime.now().strftime('%Y%m%d_%H%M%S')
            project_dir = os.path.join(self.output_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            self.current_project_dir = project_dir
            
            if "html" in question.lower() or "сайт" in question.lower() or "страницу" in question.lower():
                main_file = "index.html"
                lang = "html"
            elif "game" in question.lower() or "игра" in question.lower():
                main_file = "game.html"
                lang = "html"
            else:
                main_file = "main.py"
                lang = "python"
            
            main_path = os.path.join(project_dir, main_file)
            
            if self.client:
                try:
                    code_prompt = f"Создай ПОЛНЫЙ код для задачи: {question}\n"
                    code_prompt += "ВАЖНО: Не обрезай код! Создай полностью рабочий файл.\n"
                    code_prompt += "Только код, без объяснений. "
                    if lang == "html":
                        code_prompt += "Это HTML страница с CSS и JavaScript в одном файле.\n"
                        code_prompt += "Включи все стили, скрипты и контент. НЕ ОБРЕЗАЙ!\n"
                    else:
                        code_prompt += "Это Python скрипт.\n"
                    
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": code_prompt}],
                        temperature=0.8,
                        max_tokens=16384
                    )
                    code_content = response.choices[0].message.content
                    code_content = re.sub(r'```\w*\n?', '', code_content)
                    code_content = re.sub(r'```', '', code_content)
                except Exception as e:
                    code_content = f"# Ошибка генерации: {str(e)}\n# Запрос: {question}"
            else:
                code_content = f"# DeepSeek API не настроен\n# Запрос: {question}"
            
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            readme_path = os.path.join(project_dir, "README.md")
            readme_content = f"# {project_name}\n\n## Описание\n{question}\n\n## Запуск\n"
            if lang == "html":
                readme_content += "Откройте в браузере"
            else:
                readme_content += f"python {main_file}"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            files = [
                {"name": main_file, "size": round(os.path.getsize(main_path) / 1024, 1)},
                {"name": "README.md", "size": round(os.path.getsize(readme_path) / 1024, 1)}
            ]
            
            project_info = {
                "name": project_name,
                "dir": project_dir,
                "files": files,
                "timestamp": datetime.now().isoformat()
            }
            self.generated_projects.append(project_info)
            
            return {
                "type": "code",
                "message": f"💻 Код сгенерирован в папке: {project_dir}",
                "files": files,
                "project_dir": project_dir,
                "edit_hint": "Используйте /preview для просмотра HTML"
            }
            
        except Exception as e:
            return {"type": "code", "message": f"❌ Ошибка: {str(e)}"}
    
    # ================================================================
    # КОМАНДЫ
    # ================================================================
    
    async def _handle_command(self, command: str) -> Dict:
        # ============================================================
        # САМООБУЧЕНИЕ
        # ============================================================
        
        if command == '/learning':
            stats = self.learning_system.get_learning_stats()
            text = f"📊 СТАТИСТИКА ОБУЧЕНИЯ:\n\n"
            text += f"🧠 Записей: {stats['knowledge_base']['total_entries']}\n"
            text += f"⭐ Средний рейтинг: {stats['knowledge_base']['avg_rating']:.2f}\n"
            text += f"📈 Успешных ответов: {stats['metrics']['successful_answers']}\n"
            text += f"📉 Неудачных: {stats['metrics']['failed_answers']}\n"
            text += f"🎯 Успешность: {stats['success_rate']:.1%}"
            return {"type": "command", "content": text}
        
        elif command.startswith('/rate'):
            try:
                parts = command.split()
                if len(parts) < 2:
                    return {"type": "command", "content": "❌ Используйте: /rate 0.8"}
                rating = float(parts[1])
                if rating < 0 or rating > 1:
                    return {"type": "command", "content": "❌ Оценка должна быть от 0 до 1"}
                
                entries = self.learning_system.knowledge_base.entries
                if entries:
                    last = entries[-1]
                    old_rating = last.get("rating", 0)
                    if isinstance(old_rating, (int, float)):
                        last["rating"] = (old_rating + rating) / 2
                    else:
                        last["rating"] = rating
                    self.learning_system.knowledge_base.save()
                    return {"type": "command", "content": f"✅ Оценка {rating:.2f} сохранена!"}
                else:
                    return {"type": "command", "content": "❌ Нет записей для оценки"}
            except ValueError:
                return {"type": "command", "content": "❌ Используйте: /rate 0.8"}
        
        # ============================================================
        # AUTO SKILLS
        # ============================================================
        
        elif command.startswith('/skill'):
            task = command.replace('/skill', '').strip()
            if not task:
                return {"type": "command", "content": "❌ Укажите задачу для создания навыка.\nПример: /skill JSONParser"}
            
            if not HAS_AUTO_SKILLS or not self.auto_skill:
                return {"type": "command", "content": "❌ AutoSkillEngine не доступен"}
            
            try:
                result = await self._generate_skill(f"создай навык {task}")
                return result
            except Exception as e:
                return {"type": "command", "content": f"❌ Ошибка создания навыка: {str(e)}"}
        
        elif command == '/skills':
            if not HAS_AUTO_SKILLS or not self.auto_skill:
                return {"type": "command", "content": "❌ AutoSkillEngine не доступен"}
            
            skills = self.auto_skill.registry.skills
            if not skills:
                return {"type": "command", "content": "📭 Нет созданных навыков"}
            
            text = "📚 СПИСОК НАВЫКОВ:\n\n"
            for name, info in skills.items():
                level = info.get("level", 0)
                status = "🟢" if level > 0.3 else "🟡" if level > 0.1 else "🔴"
                text += f"{status} {name} (уровень: {level:.2f})\n"
                text += f"   📂 {info.get('category', 'General')} | Сложность: {info.get('complexity', 0)}/10\n"
                text += f"   📝 {info.get('description', '')[:60]}...\n\n"
            text += f"\n📊 Всего: {len(skills)} навыков"
            return {"type": "command", "content": text}
        
        elif command == '/skill_stats':
            if not HAS_AUTO_SKILLS or not self.auto_skill:
                return {"type": "command", "content": "❌ AutoSkillEngine не доступен"}
            
            stats = self.auto_skill.stats
            text = "📊 СТАТИСТИКА НАВЫКОВ:\n\n"
            text += f"🔍 Обнаружено пробелов: {stats['gaps_detected']}\n"
            text += f"💡 Сгенерировано навыков: {stats['generated']}\n"
            text += f"✅ Принято навыков: {stats['accepted']}\n"
            text += f"🧪 Проверено: {stats['validated']}\n"
            text += f"🗑️ Удалено (сон): {stats['pruned']}\n"
            return {"type": "command", "content": text}
        
        elif command == '/sleep':
            if not HAS_AUTO_SKILLS or not self.auto_skill:
                return {"type": "command", "content": "❌ AutoSkillEngine не доступен"}
            
            pruned = self.auto_skill.sleep()
            if pruned:
                return {"type": "command", "content": f"💤 Удалены слабые навыки: {', '.join(pruned)}"}
            else:
                return {"type": "command", "content": "💤 Нет навыков для удаления"}
        
        # ============================================================
        # META OPTIMIZER
        # ============================================================
        
        elif command.startswith('/optimize'):
            if command == '/optimize_info':
                if not HAS_META_OPTIMIZER or not self.meta_optimizer:
                    return {"type": "command", "content": "❌ MetaOptimizer не доступен"}
                
                text = "⚡ ИНФОРМАЦИЯ О META OPTIMIZER:\n\n"
                text += f"📊 Всего оптимизаций: {len(self.meta_optimizer.history)}\n"
                text += f"📈 Лучший результат: {max([r.score for r in self.meta_optimizer.history]) if self.meta_optimizer.history else 'N/A'}\n"
                text += f"🎯 Целевая синхронизация: {self.meta_optimizer.objective.target_sync_r}\n"
                text += f"🔢 Количество образцов: {self.meta_optimizer.n_samples}\n"
                text += f"📋 Режим: {'Сетка' if self.meta_optimizer.use_grid else 'Случайный поиск'}\n\n"
                
                text += "📊 ПОСЛЕДНИЕ РЕЗУЛЬТАТЫ:\n"
                for result in self.meta_optimizer.history[-3:]:
                    text += f"   • sync_r={result.sync_r:.3f}, steps={result.steps_to_sync}, score={result.score:.3f}\n"
                
                return {"type": "command", "content": text}
            
            elif command == '/apply_optimized':
                last_opt = self.context_memory.get("last_optimization")
                if not last_opt:
                    return {"type": "command", "content": "❌ Нет сохраненных оптимизаций. Сначала выполните /optimize"}
                
                config = last_opt.get("config", {})
                n_agents = config.get('n_agents', 10)
                dt = config.get('dt', 0.02)
                noise = config.get('noise', 0.02)
                regime = last_opt.get('regime', 'CRITICAL')
                
                result = self.init_system(n_agents=n_agents, dt=dt, noise=noise)
                
                if regime == "LINEAR":
                    set_regime(self.system, ConvergenceRegime.LINEAR)
                elif regime == "CRITICAL":
                    set_regime(self.system, ConvergenceRegime.CRITICAL)
                elif regime == "DIVERGENT":
                    set_regime(self.system, ConvergenceRegime.DIVERGENT)
                
                text = f"✅ ПРИМЕНЕНЫ ОПТИМИЗИРОВАННЫЕ ПАРАМЕТРЫ:\n\n"
                text += f"👥 Агентов: {n_agents}\n"
                text += f"⏱️ dt: {dt:.4f}\n"
                text += f"📊 Шум: {noise:.4f}\n"
                text += f"🎯 Режим: {regime}\n"
                text += f"🌀 Синхронизация: {result.get('sync_r', 0):.3f}\n"
                text += f"📌 Задача: {last_opt.get('task', 'не указана')}"
                
                return {"type": "command", "content": text}
            
            else:
                task = command.replace('/optimize', '').strip()
                if not task:
                    return {"type": "command", "content": "❌ Укажите задачу для оптимизации.\nПример: /optimize Создай GraphQL API"}
                
                if not HAS_META_OPTIMIZER or not self.meta_optimizer:
                    return {"type": "command", "content": "❌ MetaOptimizer не доступен"}
                
                try:
                    result = await self._optimize_parameters(f"оптимизируй {task}")
                    return result
                except Exception as e:
                    return {"type": "command", "content": f"❌ Ошибка оптимизации: {str(e)}"}
        
        # ============================================================
        # SENSOR FUSION
        # ============================================================
        
        elif command == '/fusion':
            if not HAS_SENSOR_FUSION or not self.sensor_fusion:
                return {"type": "command", "content": "❌ Sensor Fusion не доступен"}
            
            matrix = self.sensor_fusion.get_reputation_matrix()
            text = "📊 МАТРИЦА РЕПУТАЦИИ АГЕНТОВ:\n\n"
            text += "      " + " ".join([f"  D{i}  " for i in range(len(matrix[0]))]) + "\n"
            text += "      " + "-" * (len(matrix[0]) * 6) + "\n"
            for i, row in enumerate(matrix):
                text += f"A{i:2d}   " + " ".join([f"{v:.2f}" for v in row]) + "\n"
            
            trusted = self.sensor_fusion.reputation.pre_filter(0, min_rep=0.5)
            text += f"\n📈 Доверенных агентов: {len(trusted)} из {len(matrix)}"
            text += f"\n🎯 Порог доверия: {self.sensor_fusion.min_rep}"
            
            return {"type": "command", "content": text}
        
        elif command == '/fusion_stats':
            if not HAS_SENSOR_FUSION or not self.sensor_fusion:
                return {"type": "command", "content": "❌ Sensor Fusion не доступен"}
            
            text = "📊 СТАТИСТИКА SENSOR FUSION:\n\n"
            text += f"👥 Агентов: {self.sensor_fusion.n_agents}\n"
            text += f"📐 Измерений: {self.sensor_fusion.n_dims}\n"
            text += f"📏 Порог: {self.sensor_fusion.threshold}\n"
            text += f"🎯 Мин. репутация: {self.sensor_fusion.min_rep}\n"
            text += f"📋 Окно репутации: {self.sensor_fusion.reputation.window}\n\n"
            
            text += "📋 ИЗМЕРЕНИЯ:\n"
            for dim in self.sensor_fusion.dimensions:
                text += f"   • {dim['name']} (вес: {dim.get('weight', 1.0)})\n"
            
            return {"type": "command", "content": text}
        
        # ============================================================
        # AUTO TUNER
        # ============================================================
        
        elif command == '/tune':
            if not HAS_TUNING or not self.tuner:
                return {"type": "command", "content": "❌ AutoTuner не доступен"}
            
            n_agents = len(self.system.agents) if self.system else 10
            params = self.tuner.tune(n_agents)
            
            text = f"🔧 АВТОНАСТРОЙКА ПАРАМЕТРОВ:\n\n"
            text += f"👥 Для {n_agents} агентов:\n"
            text += f"   • k_sparse: {params.get('k_sparse', 'N/A')}\n"
            text += f"   • exc_ratio: {params.get('exc_ratio', 'N/A')}\n"
            text += f"   • noise: {params.get('noise', 'N/A')}\n"
            text += f"   • coupling_boost: {params.get('coupling_boost', 'N/A')}\n"
            text += f"   • sleep_every: {params.get('sleep_every', 'N/A')}\n"
            text += f"   • goal_interval: {params.get('goal_interval', 'N/A')}\n"
            text += f"   • omega_spread: {params.get('omega_spread', 'N/A')}\n\n"
            
            text += "💡 Рекомендации:\n"
            if params.get('k_sparse', 0) > 5:
                text += "   • Используйте разреженную связь (k_sparse высокий)\n"
            if params.get('exc_ratio', 0) > 0.9:
                text += "   • Высокое возбуждение → более креативные агенты\n"
            if params.get('noise', 0) < 0.02:
                text += "   • Низкий шум → стабильные ответы\n"
            
            return {"type": "command", "content": text}
        
        # ============================================================
        # СТАНДАРТНЫЕ КОМАНДЫ
        # ============================================================
        
        elif command == '/clear':
            return {"type": "command", "content": "🧹 Чат очищен", "clear": True}
        
        elif command == '/help':
            help_text = "📚 ДОСТУПНЫЕ КОМАНДЫ:\n\n"
            help_text += "📊 /learning — статистика обучения\n"
            help_text += "⭐ /rate 0.8 — оценить последний ответ\n"
            help_text += "🔥 /skill [задача] — создать навык\n"
            help_text += "📚 /skills — список навыков\n"
            help_text += "📊 /skill_stats — статистика навыков\n"
            help_text += "💤 /sleep — очистка слабых навыков\n"
            help_text += "⚡ /optimize [задача] — оптимизация параметров\n"
            help_text += "⚡ /optimize_info — информация об оптимизаторе\n"
            help_text += "⚡ /apply_optimized — применить оптимизированные параметры\n"
            help_text += "🧠 /fusion — матрица репутации агентов\n"
            help_text += "🧠 /fusion_stats — статистика сенсорного слияния\n"
            help_text += "🔧 /tune — автонастройка параметров\n"
            help_text += "🧹 /clear — очистить чат\n"
            help_text += "🤖 /agents — информация об агентах\n"
            help_text += "📁 /projects — список проектов\n"
            help_text += "👁️ /preview — открыть HTML в браузере\n"
            help_text += "ℹ️ /info — информация о проекте"
            return {"type": "command", "content": help_text}
        
        elif command == '/agents':
            return await self._get_agents_info()
        
        elif command == '/projects':
            return self._get_projects_list()
        
        elif command == '/preview':
            return self._preview_project()
        
        elif command == '/info':
            return self._get_project_info()
        
        return {"type": "command", "content": f"❌ Неизвестная команда: {command}\nИспользуйте /help для списка команд"}
    
    # ================================================================
    # КОМАНДЫ-ПОМОЩНИКИ
    # ================================================================
    
    async def _get_agents_info(self) -> Dict:
        if not self.system:
            return {"type": "command", "content": "❌ Система не инициализирована"}
        
        info = "🤖 ИНФОРМАЦИЯ ОБ АГЕНТАХ:\n\n"
        info += f"👥 Количество: {len(self.system.agents)}\n"
        info += f"🌀 Синхронизация: {self.sync_r:.3f}\n"
        info += f"📊 Среднее настроение: {sum(a.mood for a in self.system.agents) / len(self.system.agents):.2f}\n"
        info += f"📈 Шагов: {self.system.step_count}\n"
        return {"type": "command", "content": info}
    
    def _get_projects_list(self) -> Dict:
        if not self.generated_projects:
            return {"type": "command", "content": "📁 Нет созданных проектов"}
        
        text = "📁 СПИСОК ПРОЕКТОВ:\n\n"
        for i, project in enumerate(self.generated_projects, 1):
            text += f"{i}. {project['name']}\n"
            text += f"   📂 {project['dir']}\n"
            text += f"   📄 Файлов: {len(project.get('files', []))}\n\n"
        return {"type": "command", "content": text}
    
    def _preview_project(self) -> Dict:
        if not self.current_project_dir:
            return {"type": "command", "content": "❌ Нет открытого проекта"}
        
        main_file = self.find_main_file(self.current_project_dir)
        if not main_file:
            return {"type": "command", "content": "❌ Не найден основной файл"}
        
        if main_file.endswith('.html'):
            import webbrowser
            webbrowser.open(f"file://{main_file}")
            return {"type": "command", "content": f"✅ HTML открыт в браузере\n📄 {os.path.basename(main_file)}"}
        else:
            return {"type": "command", "content": f"❌ Не HTML файл: {os.path.basename(main_file)}"}
    
    def _get_project_info(self) -> Dict:
        if not self.current_project_dir:
            return {"type": "command", "content": "❌ Нет открытого проекта"}
        
        files = self.get_project_files(self.current_project_dir)
        text = "📊 ИНФОРМАЦИЯ О ПРОЕКТЕ:\n\n"
        text += f"📂 {os.path.basename(self.current_project_dir)}\n"
        text += f"📍 {self.current_project_dir}\n\n"
        text += f"📄 Файлов: {len(files)}\n"
        for f in files:
            text += f"   - {f['name']} ({f['size']} KB)\n"
        return {"type": "command", "content": text}
    
    # ================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ================================================================
    
    def get_state(self) -> Dict:
        if not self.system:
            return {"error": "System not initialized"}
        try:
            state = {
                "sync_r": self.sync_r,
                "step": self.system.step_count,
                "mean_mood": float(sum(a.mood for a in self.system.agents) / len(self.system.agents)),
                "agents": len(self.system.agents),
                "mode": self.current_mode,
                "projects": len(self.generated_projects),
                "is_running": self.is_running,
                "deepseek_available": bool(self.client),
                "current_project": self.current_project_dir,
                "learning": self.learning_system.get_learning_stats()
            }
            if HAS_AUTO_SKILLS and self.auto_skill:
                state["skills"] = {
                    "total": len(self.auto_skill.registry.skills),
                    "accepted": self.auto_skill.stats.get("accepted", 0),
                    "pruned": self.auto_skill.stats.get("pruned", 0)
                }
            if HAS_META_OPTIMIZER and self.meta_optimizer:
                state["meta"] = {
                    "history_size": len(self.meta_optimizer.history),
                    "best_score": max([r.score for r in self.meta_optimizer.history]) if self.meta_optimizer.history else 0
                }
            if HAS_SENSOR_FUSION and self.sensor_fusion:
                state["fusion"] = {
                    "n_agents": self.sensor_fusion.n_agents,
                    "n_dims": self.sensor_fusion.n_dims,
                    "trusted_agents": len(self.sensor_fusion.reputation.pre_filter(0))
                }
            return state
        except Exception as e:
            return {"error": str(e)}
    
    def get_projects(self) -> List[Dict]:
        return self.generated_projects
    
    def set_current_project(self, project_dir: str):
        self.current_project_dir = project_dir
        return {"status": "ok", "project_dir": project_dir}
    
    def find_main_file(self, project_dir: str) -> Optional[str]:
        if not project_dir or not os.path.exists(project_dir):
            return None
        priority = ['index.html', 'main.html', 'game.html', 'main.py', 'app.py']
        for name in priority:
            path = os.path.join(project_dir, name)
            if os.path.exists(path):
                return path
        for f in os.listdir(project_dir):
            if f.endswith(('.html', '.py')) and f not in ['README.md']:
                return os.path.join(project_dir, f)
        return None
    
    def get_project_files(self, project_dir: str) -> List[Dict]:
        if not project_dir or not os.path.exists(project_dir):
            return []
        files = []
        for f in os.listdir(project_dir):
            path = os.path.join(project_dir, f)
            if os.path.isfile(path):
                files.append({
                    "name": f,
                    "path": path,
                    "size": round(os.path.getsize(path) / 1024, 2)
                })
        return files
    
    def update_project_info(self, project_dir: str):
        if not project_dir:
            return
        files = self.get_project_files(project_dir)
        for project in self.generated_projects:
            if project.get("dir") == project_dir:
                project["files"] = files
                break