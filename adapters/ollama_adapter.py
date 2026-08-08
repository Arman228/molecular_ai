# -*- coding: utf-8 -*-
"""
Ollama Adapter — локальный LLM через HTTP API.
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from adapters.base import LLMAdapter


class OllamaAdapter(LLMAdapter):
    """
    Адаптер для локального Ollama (llama3, mistral, phi3 и др.).
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3",
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.host = host.rstrip("/")

    def _env_key(self) -> str:
        return ""  # Ollama не требует API ключа

    def _call_api(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        data = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama not reachable at {self.host}: {e}")