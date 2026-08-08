# -*- coding: utf-8 -*-
"""
NVIDIA NIM Adapter — через NVIDIA API (build.nvidia.com).
"""

import json
import urllib.request
from typing import Optional
from adapters.base import LLMAdapter


class NvidiaAdapter(LLMAdapter):
    """
    Адаптер для NVIDIA NIM API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta/llama3-70b-instruct",
        base_url: str = "https://integrate.api.nvidia.com/v1",
        **kwargs,
    ):
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _env_key(self) -> str:
        return "NVIDIA_API_KEY"

    def _call_api(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": 512,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]