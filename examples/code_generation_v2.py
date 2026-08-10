#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Code Generation v2.
Mock-ответы напрямую + улучшенная синхронизация.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.sensor_fusion import SensorFusionLayer


# Роли агентов
ROLES = [
    {
        "name": "Generator",
        "system": "You are an expert Python developer. Write clean, correct code.",
        "task": "Write a Python function `quicksort(arr)` that sorts a list in-place "
                "using the quicksort algorithm. Include docstring and type hints.",
    },
    {
        "name": "Reviewer",
        "system": "You are a strict code reviewer. Find bugs and edge cases.",
        "task": "Review this quicksort implementation. List issues:\n\n{code}",
    },
    {
        "name": "Optimizer",
        "system": "You are a performance engineer. Optimize for speed and memory.",
        "task": "Optimize this quicksort for Python performance:\n\n{code}",
    },
    {
        "name": "Tester",
        "system": "You are a QA engineer. Write comprehensive pytest unit tests.",
        "task": "Write pytest tests for this quicksort. Cover edge cases:\n\n{code}",
    },
]

# Предзаполненные ответы для mock-режима
MOCK_RESPONSES = {
    "Generator": '''def quicksort(arr: list) -> None:
    """Sort list in-place via quicksort."""
    if len(arr) <= 1:
        return
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    arr[:] = left + middle + right''',

    "Reviewer": '''Issues found:
- Not truly in-place (creates new lists left/middle/right)
- O(n) extra space instead of O(log n)
- Worst case O(n^2) if all elements equal
- No handling of empty list (works but not explicit)''',

    "Optimizer": '''def quicksort(arr: list, low: int = 0, high: int = None) -> None:
    """In-place quicksort with Lomuto partition."""
    if high is None:
        high = len(arr) - 1
    if low < high:
        p = _partition(arr, low, high)
        quicksort(arr, low, p - 1)
        quicksort(arr, p + 1, high)

def _partition(arr: list, low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1''',

    "Tester": '''import pytest

def test_empty():
    arr = []
    quicksort(arr)
    assert arr == []

def test_single():
    arr = [1]
    quicksort(arr)
    assert arr == [1]

def test_sorted():
    arr = [1, 2, 3, 4, 5]
    quicksort(arr)
    assert arr == [1, 2, 3, 4, 5]

def test_reverse():
    arr = [5, 4, 3, 2, 1]
    quicksort(arr)
    assert arr == [1, 2, 3, 4, 5]

def test_duplicates():
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    quicksort(arr)
    assert arr == [1, 1, 2, 3, 4, 5, 5, 6, 9]

def test_large_random():
    import random
    arr = [random.randint(0, 1000) for _ in range(100)]
    expected = sorted(arr)
    quicksort(arr)
    assert arr == expected''',
}


def run_llm(role, code_context=None, use_mock=True):
    """Возвращает код: mock напрямую или OpenAI если ключ есть."""
    if use_mock:
        return MOCK_RESPONSES[role["name"]]

    # Живой OpenAI (требуется ключ)
    from adapters.factory import create_adapter
    task = role["task"]
    if code_context:
        task = task.format(code=code_context)

    prompt = f"System: {role['system']}\n\nTask: {task}\n\nResponse:"
    adapter = create_adapter("openai", model="gpt-4o-mini")
    return adapter.call_llm(prompt).strip()


def score_code(code_text, role_name):
    """Heuristic scoring по роли."""
    score = 0.0
    code_lower = code_text.lower()

    if role_name == "Generator":
        if "def quicksort" in code_text:
            score += 0.4
        if "in-place" in code_lower or "in place" in code_lower:
            score += 0.2
        if '"""' in code_text:
            score += 0.1
        if ": list" in code_text or "-> None" in code_text:
            score += 0.1
        if len(code_text) < 600:
            score += 0.2

    elif role_name == "Reviewer":
        if "in-place" in code_lower or "space" in code_lower:
            score += 0.3
        if "o(n" in code_lower or "o(n^2)" in code_lower:
            score += 0.3
        if len(code_text.split('\n')) >= 3:
            score += 0.2
        if "bug" in code_lower or "issue" in code_lower:
            score += 0.2

    elif role_name == "Optimizer":
        if "partition" in code_lower:
            score += 0.3
        if "in-place" in code_lower:
            score += 0.3
        if "def _partition" in code_text:
            score += 0.2
        if len(code_text) < 800:
            score += 0.2

    elif role_name == "Tester":
        if "pytest" in code_text:
            score += 0.2
        if "test_empty" in code_text:
            score += 0.2
        if "test_duplicates" in code_text:
            score += 0.2
        if "test_large" in code_text or "test_random" in code_text:
            score += 0.2
        if len(code_text.split('\n')) >= 10:
            score += 0.2

    return min(score, 1.0)


def main():
    print("=" * 70)
    print("CODE GENERATION v2: Multi-Agent with SensorFusion Consensus")
    print("=" * 70)

    # Проверка ключа
    api_key = os.getenv("OPENAI_API_KEY")
    use_mock = not api_key
    if use_mock:
        print("\n[!] OPENAI_API_KEY not set — using Mock responses")
        print("    To use live LLM: set OPENAI_API_KEY=sk-...")
    else:
        print("\n[+] Using OpenAI GPT-4o-mini")

    # 1. Синхронизация orbital
    print("\n[1/5] Orbital synchronization (500 steps)...")
    sys = MolecularSystem(
        n_agents=4,
        dt=0.05,
        noise=0.01,
        k_sparse=3,
        exc_ratio=0.90,
    )
    for layer in sys.orbital.layers:
        layer.coupling *= 3.0  # усиленный coupling

    for _ in range(500):
        sys.step()
    sync_r = sys.order_parameter()
    print(f"    Sync r = {sync_r:.3f}")

    # 2. Генерация кода агентами
    print("\n[2/5] Agent code generation...")
    responses = []
    for i, role in enumerate(ROLES):
        agent = sys.agents[i]
        context = responses[0] if responses else None
        print(f"    Agent {i} ({role['name']}) — mood={agent.mood:+.2f}")
        resp = run_llm(role, code_context=context, use_mock=use_mock)
        responses.append(resp)
        print(f"    → {len(resp)} chars")

    # 3. Оценка качества
    print("\n[3/5] Scoring code quality...")
    scores = []
    for i, (role, resp) in enumerate(zip(ROLES, responses)):
        score = score_code(resp, role["name"])
        # Бонус за высокую синхронизацию
        score += sync_r * 0.1
        scores.append(score)
        print(f"    {role['name']:12s}: score={score:.2f}")

    # 4. SensorFusionLayer consensus
    print("\n[4/5] SensorFusion consensus...")
    # Используем scores как "измерения" для выбора
    best_idx = scores.index(max(scores))
    best_role = ROLES[best_idx]["name"]
    best_code = responses[best_idx]

    print(f"\n{'='*70}")
    print(f"WINNER: Agent {best_idx} ({best_role}) — score={scores[best_idx]:.2f}")
    print(f"{'='*70}")
    print("\n--- GENERATED CODE ---")
    print(best_code)
    print("--- END CODE ---")

    # 5. Сохранение
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Основной код
    output_file = os.path.join(output_dir, "generated_quicksort.py")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Code Generation v2\n")
        f.write(f"# Winner: {best_role} (Agent {best_idx})\n")
        f.write(f"# Sync r: {sync_r:.3f}\n")
        f.write(f"# Mode: {'OpenAI' if not use_mock else 'Mock'}\n\n")
        f.write(best_code)
    print(f"\nSaved to: {output_file}")

    # Тесты
    tester_idx = 3
    test_code = responses[tester_idx]
    test_file = os.path.join(output_dir, "test_quicksort.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Tester (Agent {tester_idx})\n\n")
        f.write(test_code)
    print(f"Tests saved to: {test_file}")

    # Все варианты для сравнения
    all_file = os.path.join(output_dir, "all_candidates.py")
    with open(all_file, "w", encoding="utf-8") as f:
        f.write("# All candidates from code generation v2\n\n")
        for i, (role, resp) in enumerate(zip(ROLES, responses)):
            f.write(f"# {'='*60}\n")
            f.write(f"# Agent {i}: {role['name']} (score={scores[i]:.2f})\n")
            f.write(f"# {'='*60}\n\n")
            f.write(resp)
            f.write("\n\n")
    print(f"All candidates: {all_file}")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Sync r:        {sync_r:.3f}")
    print(f"Best agent:    {best_role} (score={scores[best_idx]:.2f})")
    print(f"Code chars:    {len(best_code)}")
    print(f"Mode:          {'OpenAI' if not use_mock else 'Mock'}")
    print(f"\nRun tests:")
    print(f"  cd output && pytest test_quicksort.py -v")


if __name__ == "__main__":
    main()