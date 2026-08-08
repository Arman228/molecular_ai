# -*- coding: utf-8 -*-
"""
DeepSeek Adapter.
"""

import os
import json
import urllib.request
from typing import Optional
from adapters.base import LLMAdapter


class DeepSeekAdapter(LLMAdapter):
    """
    Адаптер для DeepSeek API (OpenAI-compatible).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        **kwargs,
    ):
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _env_key(self) -> str:
        return "DEEPSEEK_API_KEY"

    def _call_api(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        data = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": 512,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]