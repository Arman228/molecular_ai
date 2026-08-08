# -*- coding: utf-8 -*-
"""
Anthropic Adapter — Claude 3.5 Sonnet, Haiku.
"""

import os
from typing import Optional
from adapters.base import LLMAdapter

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class AnthropicAdapter(LLMAdapter):
    """
    Адаптер для Anthropic Claude API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022",
        **kwargs,
    ):
        if not HAS_ANTHROPIC:
            raise ImportError("Install anthropic: pip install anthropic")
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.client = Anthropic(api_key=self.api_key)

    def _env_key(self) -> str:
        return "ANTHROPIC_API_KEY"

    def _call_api(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
            timeout=int(self.timeout),
        )
        return response.content[0].text