# -*- coding: utf-8 -*-
"""
Mock Adapter — имитирует LLM на основе состояния системы.
Полезен для тестирования без интернета и API ключей.
"""

import random
from adapters.base import LLMAdapter


class MockAdapter(LLMAdapter):
    """
    Умный mock: анализирует метрики и генерирует осмысленный ответ.
    """

    def __init__(self, model: str = "mock-llm-v1", **kwargs):
        # Не вызываем super().__init__ с api_key
        self.model = model
        self.max_retries = 1
        self.timeout = 1.0
        self.temperature = 0.7

    def _env_key(self) -> str:
        return ""

    def _call_api(self, prompt: str) -> str:
        # Извлекаем метрики из промпта (парсим простым способом)
        lines = prompt.split("\n")
        sync_r = 0.5
        mood = 0.0
        phase = 0.0
        spin = 1.0

        for line in lines:
            if "System sync:" in line:
                try:
                    sync_r = float(line.split("r ≈")[1].split()[0])
                except (IndexError, ValueError):
                    pass
            if "Mood:" in line:
                try:
                    mood = float(line.split("Mood:")[1].split()[0])
                except (IndexError, ValueError):
                    pass
            if "Phase:" in line:
                try:
                    phase = float(line.split("Phase:")[1].split()[0])
                except (IndexError, ValueError):
                    pass
            if "Spin:" in line:
                try:
                    spin = float(line.split("Spin:")[1].split()[0])
                except (IndexError, ValueError):
                    pass

        return self._generate_response(sync_r, mood, phase, spin)

    def _generate_response(self, sync_r: float, mood: float, phase: float, spin: float) -> str:
        """Генерация ответа на основе метрик."""
        responses = []

        # Анализ синхронизации
        if sync_r > 0.9:
            responses.append("Система демонстрирует высокую когерентность (r > 0.9). Коллективное сознание сформировано.")
        elif sync_r > 0.7:
            responses.append("Синхронизация стабильная, но есть резерв для усиления резонанса.")
        else:
            responses.append("Низкая синхронизация. Рекомендую увеличить coupling K для Gamma-слоя.")

        # Анализ настроения
        if mood > 0.5:
            responses.append("Позитивный эмоциональный фон способствует конструктивной динамике.")
        elif mood < -0.3:
            responses.append("Обнаружен тревожный паттерн. Активируйте механизм сна для консолидации.")
        else:
            responses.append("Эмоциональное состояние нейтральное.")

        # Анализ спина
        if spin > 0:
            responses.append("Экситаторный режим: система накапливает энергию.")
        else:
            responses.append("Ингибиторный режим: рекомендуется снизить нагрузку.")

        # Случайная рекомендация
        tips = [
            "Попробуйте увеличить k_sparse до 6 для лучшей связности.",
            "Добавьте шум σ=0.05 — это может стимулировать самоорганизацию.",
            "Период sleep consolidation можно сократить до 200 шагов.",
            "Используйте 85% экситаторов для оптимального баланса.",
        ]
        responses.append("💡 " + random.choice(tips))

        return "\n".join(responses)