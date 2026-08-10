#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async LLM Adapter Base.
Parallel API calls via asyncio + httpx.
"""

import asyncio
import httpx
from typing import List, Optional


class AsyncLLMAdapter:
    """
    Base for async LLM calls.
    All agents call API in parallel via asyncio.gather().
    """

    def __init__(self, api_key: str, base_url: str, model: str, semaphore_limit: int = 10):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.semaphore = asyncio.Semaphore(semaphore_limit)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def call_single(self, prompt: str, system: str = "") -> str:
        """One async API call with rate limiting."""
        async with self.semaphore:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                return f"[ERROR] {e}"

    async def call_batch(self, prompts: List[str], systems: Optional[List[str]] = None) -> List[str]:
        """Parallel calls for all agents."""
        if systems is None:
            systems = [""] * len(prompts)

        tasks = [
            self.call_single(prompt, system)
            for prompt, system in zip(prompts, systems)
        ]
        return await asyncio.gather(*tasks)

    async def close(self):
        await self.client.aclose()


class AsyncOpenAIAdapter(AsyncLLMAdapter):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            model=model,
            semaphore_limit=10,
        )


class AsyncAnthropicAdapter(AsyncLLMAdapter):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
            model=model,
            semaphore_limit=5,
        )