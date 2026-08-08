# -*- coding: utf-8 -*-
"""
Фабрика адаптеров — создаёт нужный адаптер по имени.
"""

from typing import Optional
from adapters.base import LLMAdapter


def create_adapter(
    name: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs,
) -> LLMAdapter:
    """
    Создаёт адаптер по имени провайдера.

    Available: openai, anthropic, ollama, deepseek, gemini
    """
    name = name.lower().strip()

    if name == "openai":
        from adapters.openai_adapter import OpenAIAdapter
        return OpenAIAdapter(api_key=api_key, model=model or "gpt-4o-mini", **kwargs)

    if name == "anthropic":
        from adapters.anthropic_adapter import AnthropicAdapter
        return AnthropicAdapter(api_key=api_key, model=model or "claude-3-5-haiku-20241022", **kwargs)

    if name == "ollama":
        from adapters.ollama_adapter import OllamaAdapter
        return OllamaAdapter(model=model or "llama3", **kwargs)

    if name == "deepseek":
        from adapters.deepseek_adapter import DeepSeekAdapter
        return DeepSeekAdapter(api_key=api_key, model=model or "deepseek-chat", **kwargs)

    if name == "gemini":
        from adapters.gemini_adapter import GeminiAdapter
        return GeminiAdapter(api_key=api_key, model=model or "gemini-1.5-flash", **kwargs)

    if name == "mock":
        from adapters.mock_adapter import MockAdapter
        return MockAdapter(**kwargs)

    raise ValueError(f"Unknown adapter: {name}. Available: openai, anthropic, ollama, deepseek, gemini")