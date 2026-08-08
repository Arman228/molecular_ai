# -*- coding: utf-8 -*-
"""
Базовый адаптер для LLM с retry, timeout и prompt builder.
"""

import os
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Optional


class LLMAdapter(ABC):
    """
    Универсальный адаптер для любой LLM API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "default",
        max_retries: int = 3,
        timeout: float = 30.0,
        temperature: float = 0.7,
    ):
        self.api_key = api_key or os.getenv(self._env_key(), "")
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.temperature = temperature

    @abstractmethod
    def _env_key(self) -> str:
        """Имя переменной окружения для API ключа."""
        pass

    @abstractmethod
    def _call_api(self, prompt: str) -> str:
        """Прямой вызов API. Должен быть переопределён."""
        pass

    def call_llm(self, prompt: str) -> str:
        """
        Вызов LLM с retry и exponential backoff.
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return self._call_api(prompt)
            except Exception as e:
                last_error = e
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
        raise RuntimeError(
            f"LLM call failed after {self.max_retries} retries: {last_error}"
        )

    def build_prompt(self, agent, orbital, task: str) -> str:
        """
        Строит промпт с orbital context.
        """
        state = agent.get_state()
        sync_r = 0.0
        if hasattr(orbital, "get_mean_phase"):
            sync_r = orbital.get_mean_phase()

        return f"""=== ORBITAL CONTEXT ===
System sync: r ≈ {sync_r:.2f}
Agent {state['agent_id']} | Phase: {state['phase']:.2f} | Mood: {state.get('mood', 0):+.2f} | Spin: {state.get('spin', 0):.2f}

=== TASK ===
{task}

=== INSTRUCTION ===
Generate output maintaining compatibility with orbital state.
Respond concisely (1-3 sentences)."""