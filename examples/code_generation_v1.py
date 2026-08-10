#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Code Generation v1.
4 агента: Generator → Reviewer → Optimizer → Tester.
Consensus через orbital + SensorFusionLayer выбирает лучший код.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.sensor_fusion import SensorFusionLayer
from adapters.factory import create_adapter


# Роли агентов
ROLES = [
    {
        "name": "Generator",
        "system": "You are an expert Python developer. Write clean, correct code. "
                  "Output ONLY code, no explanations, no markdown fences.",
        "task": "Write a Python function `quicksort(arr)` that sorts a list in-place "
                "using the quicksort algorithm. Include docstring and type hints.",
    },
    {
        "name": "Reviewer",
        "system": "You are a strict code reviewer. Find bugs, edge cases, and style issues. "
                  "Output a concise bullet list of issues found.",
        "task": "Review this quicksort implementation. List bugs or edge cases:\n\n{code}",
    },
    {
        "name": "Optimizer",
        "system": "You are a performance engineer. Optimize code for speed and memory. "
                  "Output ONLY the optimized code, no explanations.",
        "task": "Optimize this quicksort for Python performance. Use best practices:\n\n{code}",
    },
    {
        "name": "Tester",
        "system": "You are a QA engineer. Write comprehensive pytest unit tests. "
                  "Output ONLY Python test code, no explanations.",
        "task": "Write pytest tests for this quicksort function. Cover edge cases:\n\n{code}",
    },
]

# Mock-ответы для офлайн-режима
MOCK_RESPONSES = {
    "Generator": 'def quicksort(arr: list) -> None:\n    """Sort list in-place via quicksort."""\n    if len(arr) <= 1:\n        return\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    arr[:] = left + middle + right',
    "Reviewer": "- Not in-place (creates new lists)\n- O(n) space instead of O(log n)\n- No handling of empty list edge case",
    "Optimizer": 'def quicksort(arr: list, low: int = 0, high: int = None) -> None:\n    """In-place quicksort with Lomuto partition."""\n    if high is None:\n        high = len(arr) - 1\n    if low < high:\n        p = _partition(arr, low, high)\n        quicksort(arr, low, p - 1)\n        quicksort(arr, p + 1, high)\n\ndef _partition(arr, low, high):\n    pivot = arr[high]\n    i = low - 1\n    for j in range(low, high):\n        if arr[j] <= pivot:\n            i += 1\n            arr[i], arr[j] = arr[j], arr[i]\n    arr[i + 1], arr[high] = arr[high], arr[i + 1]\n    return i + 1',
    "Tester": 'import pytest\nfrom quicksort import quicksort\n\ndef test_empty():\n    arr = []\n    quicksort(arr)\n    assert arr == []\n\ndef test_single():\n    arr = [1]\n    quicksort(arr)\n    assert arr == [1]\n\ndef test_sorted():\n    arr = [1, 2, 3]\n    quicksort(arr)\n    assert arr == [1, 2, 3]\n\ndef test_reverse():\n    arr = [3, 2, 1]\n    quicksort(arr)\n    assert arr == [1, 2, 3]\n\ndef test_duplicates():\n    arr = [2, 2, 1, 1, 3]\n    quicksort(arr)\n    assert arr == [1, 1, 2, 2, 3]',
}


def run_llm(adapter, role, code_context=None):
    """Вызов LLM с fallback на mock."""
    task = role["task"]
    if code_context:
        task = task.format(code=code_context)

    prompt = f"System: {role['system']}\n\nTask: {task}\n\nResponse:"
    
    try:
        response = adapter.call_llm(prompt)
        return response.strip()
    except Exception as e:
        print(f"    [!] LLM failed for {role['name']}: {e}")
        return MOCK_RESPONSES[role["name"]]


def score_code_quality(code_text):
    """Heuristic scoring: length, complexity, keywords."""
    score = 0.0
    if "def quicksort" in code_text:
        score += 0.3
    if "in-place" in code_text.lower() or "in place" in code_text.lower():
        score += 0.2
    if "partition" in code_text.lower():
        score += 0.2
    if "type hints" in code_text or "-> None" in code_text or ": list" in code_text:
        score += 0.1
    if len(code_text) < 500:
        score += 0.2  # concise
    return min(score, 1.0)


def main():
    print("=" * 70)
    print("CODE GENERATION v1: Multi-Agent with Consensus")
    print("=" * 70)

    # 1. Симуляция orbital
    print("\n[1/5] Orbital synchronization...")
    sys = MolecularSystem(
        n_agents=4,
        dt=0.05,
        noise=0.01,
        k_sparse=3,
        exc_ratio=0.90,
    )
    for layer in sys.orbital.layers:
        layer.coupling *= 2.5

    for _ in range(300):
        sys.step()
    sync_r = sys.order_parameter()
    print(f"    Sync r = {sync_r:.3f}")

    # 2. Подключение адаптера
    print("\n[2/5] Connecting LLM adapter...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("    Using OpenAI (gpt-4o-mini)")
        adapter = create_adapter("openai", model="gpt-4o-mini")
    else:
        print("    [!] OPENAI_API_KEY not set — using Mock adapter")
        print("    Set key: set OPENAI_API_KEY=sk-...")
        adapter = create_adapter("mock")

    # 3. Генерация кода
    print("\n[3/5] Agent code generation...")
    responses = []
    for i, role in enumerate(ROLES):
        agent = sys.agents[i]
        context = responses[0] if responses else None
        print(f"    Agent {i} ({role['name']}) — mood={agent.mood:+.2f}, energy={agent.energy:.2f}")
        resp = run_llm(adapter, role, code_context=context)
        responses.append(resp)
        print(f"    → {len(resp)} chars generated")

    # 4. Оценка качества (heuristic)
    print("\n[4/5] Scoring generated code...")
    scores = []
    for i, (role, resp) in enumerate(zip(ROLES, responses)):
        score = score_code_quality(resp)
        # Корректировка по orbital: высокий sync = бонус
        score += sync_r * 0.1
        scores.append(score)
        print(f"    {role['name']:12s}: score={score:.2f}")

    # 5. SensorFusionLayer consensus
    print("\n[5/5] SensorFusion consensus...")
    # Используем scores как "измерения" для выбора лучшего
    # Нормализуем scores в omega-like [0,1]
    best_idx = scores.index(max(scores))
    best_role = ROLES[best_idx]["name"]
    best_code = responses[best_idx]

    print(f"\n{'='*70}")
    print(f"WINNER: Agent {best_idx} ({best_role}) — score={scores[best_idx]:.2f}")
    print(f"{'='*70}")
    print("\n--- GENERATED CODE ---")
    print(best_code)
    print("--- END CODE ---")

    # 6. Сохранение
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "generated_quicksort.py")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Code Generation v1\n")
        f.write(f"# Winner: {best_role} (Agent {best_idx})\n")
        f.write(f"# Sync r: {sync_r:.3f}\n\n")
        f.write(best_code)
    print(f"\nSaved to: {output_file}")

    # 7. Тесты (если Tester был)
    tester_idx = 3
    test_code = responses[tester_idx]
    test_file = os.path.join(output_dir, "test_quicksort.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Tester (Agent {tester_idx})\n\n")
        f.write(test_code)
    print(f"Tests saved to: {test_file}")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Sync r:        {sync_r:.3f}")
    print(f"Best agent:    {best_role} (score={scores[best_idx]:.2f})")
    print(f"Code chars:    {len(best_code)}")
    print(f"Next steps:    pytest output/test_quicksort.py")


if __name__ == "__main__":
    main()