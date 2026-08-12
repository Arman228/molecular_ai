#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeekAdapter v1 — safe LLM skill generation with circuit breaker,
rate limiting, cost tracking, and import whitelisting.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


# ---------------------------------------------------------------------------
# Safety configuration
# ---------------------------------------------------------------------------

ALLOWED_IMPORTS = {
    "typing", "collections", "collections.abc", "math", "itertools",
    "functools", "datetime", "json", "re", "hashlib", "random",
    "string", "pathlib", "dataclasses", "enum", "inspect", "uuid",
    "warnings", "contextlib", "io", "csv", "html", "xml.etree.ElementTree",
    "urllib.parse", "base64", "mimetypes", "tempfile", "shutil",
    "os.path", "time", "statistics", "decimal", "fractions", "numbers",
    "array", "bisect", "heapq", "copy", "pprint", "textwrap", "string",
    "enum", "typing", "abc", "types", "weakref", "pickle", "copyreg",
    "shelve", "dbm", "sqlite3", "asyncio", "concurrent.futures",
    "threading", "queue", "multiprocessing.dummy",
}

FORBIDDEN_IMPORTS = {
    "socket", "urllib.request", "http.client", "ftplib", "telnetlib",
    "subprocess", "os.system", "os.popen", "os.spawn", "os.exec",
    "sys", "platform", "pwd", "grp", "ctypes", "ctypes.util",
    "multiprocessing", "multiprocessing.pool", "multiprocessing.process",
}

SAFETY_PROMPT = """
CRITICAL SAFETY RULES:
1. Use ONLY Python standard library modules listed above.
2. NEVER import: socket, urllib.request, http.client, subprocess, os.system, sys, platform, ctypes, multiprocessing.
3. NEVER use exec(), eval(), compile(), __import__(), open() on user paths, os.remove(), shutil.rmtree().
4. Code must be deterministic and safe to run in a temporary pytest sandbox.
5. All file operations (if any) MUST use tempfile ONLY.
"""


# ---------------------------------------------------------------------------
# Circuit breaker & rate limiter
# ---------------------------------------------------------------------------

@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: float = 60.0
    _failures: int = 0
    _last_failure: float = 0.0
    _open: bool = False

    def call(self, fn, *args, **kwargs):
        if self._open:
            if time.time() - self._last_failure > self.recovery_timeout:
                self._open = False
                self._failures = 0
            else:
                raise RuntimeError("Circuit breaker OPEN — too many failures")
        try:
            result = fn(*args, **kwargs)
            self._failures = 0
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.time()
            if self._failures >= self.failure_threshold:
                self._open = True
            raise e


@dataclass
class RateLimiter:
    max_requests: int = 10
    window_sec: float = 60.0
    _timestamps: List[float] = field(default_factory=list)

    def acquire(self):
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < self.window_sec]
        if len(self._timestamps) >= self.max_requests:
            raise RuntimeError(f"Rate limit exceeded: {self.max_requests} requests per {self.window_sec}s")
        self._timestamps.append(now)


@dataclass
class CostTracker:
    max_cost_usd: float = 1.0
    _cost: float = 0.0
    _prices: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "deepseek-chat": (0.000001, 0.000002),
        "deepseek-coder": (0.000001, 0.000002),
    })

    def add(self, model: str, input_tokens: int, output_tokens: int):
        inp_p, out_p = self._prices.get(model, (0.0, 0.0))
        cost = input_tokens * inp_p + output_tokens * out_p
        self._cost += cost
        return cost

    @property
    def remaining(self) -> float:
        return max(0.0, self.max_cost_usd - self._cost)

    def check(self):
        if self._cost >= self.max_cost_usd:
            raise RuntimeError(f"Cost limit exceeded: ${self._cost:.4f} / ${self.max_cost_usd:.2f}")


# ---------------------------------------------------------------------------
# DeepSeek Adapter
# ---------------------------------------------------------------------------

class DeepSeekAdapter:
    """
    Safe DeepSeek API adapter for autonomous skill generation.
    """

    API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEFAULT_MODEL = "deepseek-chat"
    TIMEOUT = 30.0
    MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_cost_usd: float = 1.0,
        max_requests_per_min: int = 10,
        circuit_threshold: int = 3,
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.model = model
        self.client = httpx.Client(timeout=self.TIMEOUT) if HAS_HTTPX else None
        self.circuit = CircuitBreaker(failure_threshold=circuit_threshold)
        self.rate_limiter = RateLimiter(max_requests=max_requests_per_min, window_sec=60.0)
        self.cost_tracker = CostTracker(max_cost_usd=max_cost_usd)

    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        """Raw API call with retry logic."""
        if not HAS_HTTPX:
            raise RuntimeError("httpx not installed. Run: pip install httpx")
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set. Get one at https://platform.deepseek.com")

        self.cost_tracker.check()
        self.rate_limiter.acquire()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 8192,
            "response_format": {"type": "json_object"},
        }

        # Explicit UTF-8 serialization to fix Windows encoding bug
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = self.client.post(self.API_URL, headers=headers, content=payload_bytes)
                resp.raise_for_status()
                data = resp.json()

                # Track cost
                usage = data.get("usage", {})
                inp_tok = usage.get("prompt_tokens", 0)
                out_tok = usage.get("completion_tokens", 0)
                cost = self.cost_tracker.add(self.model, inp_tok, out_tok)

                return data
            except Exception as e:
                last_error = e
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        raise RuntimeError(f"DeepSeek API failed after {self.MAX_RETRIES} retries: {last_error}")

    def generate_skill(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a skill candidate from a gap ticket.
        Returns dict with name, category, description, complexity, code, tests, keywords.
        """
        task = gap["task"]
        missing = gap.get("missing_keywords", [])
        category = gap.get("suggested_category", "General")

        allowed_list = ", ".join(sorted(ALLOWED_IMPORTS))
        forbidden_list = ", ".join(sorted(FORBIDDEN_IMPORTS))

        system_prompt = f"""You are an expert Python developer and test engineer.
Your task is to generate a complete, self-contained Python module for a specific capability.

ALLOWED standard library imports: {allowed_list}
FORBIDDEN imports (NEVER use): {forbidden_list}
{SAFETY_PROMPT}

Return ONLY a JSON object with these exact keys:
- name: PascalCase skill name (e.g., "TaskQueue")
- category: short category (e.g., "Backend", "Testing", "Data")
- description: one-sentence description
- complexity: integer 1-10
- code: complete Python implementation with docstrings, using ONLY allowed imports
- tests: complete pytest unit tests covering normal cases, edge cases, and errors
- keywords: list of 3-5 lowercase strings describing the skill

The code must be production-quality, type-hinted where appropriate, and safe to execute in a sandbox.
"""

        user_prompt = f"""Create a Python skill for: {task}

Missing keywords: {', '.join(missing)}
Suggested category: {category}

Generate the JSON now."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        def _do_call():
            return self._call_api(messages, temperature=0.2)

        data = self.circuit.call(_do_call)

        # Extract JSON from response
        content = data["choices"][0]["message"]["content"]
        try:
            skill_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
            if match:
                skill_data = json.loads(match.group(1))
            else:
                raise RuntimeError(f"Failed to parse JSON from LLM response: {content[:200]}")

        # Validate forbidden imports
        code = skill_data.get("code", "")
        for forbidden in FORBIDDEN_IMPORTS:
            if f"import {forbidden}" in code or f"from {forbidden}" in code:
                raise RuntimeError(f"Generated code contains forbidden import: {forbidden}")

        return skill_data

    def get_stats(self) -> Dict[str, Any]:
        """Return adapter statistics."""
        return {
            "model": self.model,
            "total_cost_usd": self.cost_tracker._cost,
            "remaining_budget_usd": self.cost_tracker.remaining,
            "circuit_failures": self.circuit._failures,
            "circuit_open": self.circuit._open,
            "requests_in_window": len(self.rate_limiter._timestamps),
        }

    def close(self):
        if self.client:
            self.client.close()


# ---------------------------------------------------------------------------
# Integration helper
# ---------------------------------------------------------------------------

def attach_deepseek_to_engine(engine, api_key: Optional[str] = None, **kwargs):
    """
    Attach DeepSeek adapter to AutoSkillEngine.
    Sets engine.generator to use LLM mode with DeepSeek.
    """
    from core.auto_skills import SkillGenerator, SkillCandidate

    adapter = DeepSeekAdapter(api_key=api_key, **kwargs)
    engine.generator = SkillGenerator(use_llm=True, adapter=adapter)
    engine.deepseek = adapter
    return adapter


# Monkey-patch SkillGenerator to support DeepSeek
from core.auto_skills import SkillGenerator, SkillCandidate


def _deepseek_generate(self, gap: Dict[str, Any]) -> SkillCandidate:
    """Replacement for SkillGenerator._generate_llm using DeepSeek."""
    if self.adapter is None:
        raise RuntimeError("No LLM adapter attached")
    skill_data = self.adapter.generate_skill(gap)
    return SkillCandidate(
        name=skill_data["name"],
        category=skill_data.get("category", "General"),
        description=skill_data.get("description", ""),
        complexity=skill_data.get("complexity", 5),
        code=skill_data.get("code", "pass"),
        tests=skill_data.get("tests", "def test_placeholder(): pass"),
        keywords=skill_data.get("keywords", []),
        parent_task=gap["task"],
    )


# Patch the method
SkillGenerator._generate_llm = _deepseek_generate