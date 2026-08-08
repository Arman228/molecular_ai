# -*- coding: utf-8 -*-
"""
OpenAI Adapter — GPT-4o, GPT-4o-mini.
"""

import os
from typing import Optional
from adapters.base import LLMAdapter

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OpenAIAdapter(LLMAdapter):
    """
    Адаптер для OpenAI API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        **kwargs,
    ):
        if not HAS_OPENAI:
            raise ImportError("Install openai: pip install openai")
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.client = OpenAI(api_key=self.api_key)

    def _env_key(self) -> str:
        return "OPENAI_API_KEY"

    def _call_api(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=512,
            timeout=int(self.timeout),
        )
        return response.choices[0].message.content