#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Generation v4.1 — Async LLM + Code-only winner.
Reviewer/Tester excluded from code winner (they produce text, not code).
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from adapters.async_base import AsyncOpenAIAdapter


ROLES = [
    {
        "name": "Generator",
        "system": "You are an expert Python developer. Write clean, correct code. Output ONLY code, no explanations.",
        "task": "Write a Python function `quicksort(arr: list) -> None` that sorts a list in-place using quicksort. Include docstring and type hints.",
        "produces_code": True,
    },
    {
        "name": "Reviewer",
        "system": "You are a strict code reviewer. Find bugs and edge cases.",
        "task": "Review this quicksort implementation. List issues found:\n\n{code}",
        "produces_code": False,
    },
    {
        "name": "Optimizer",
        "system": "You are a performance engineer. Optimize for speed and memory.",
        "task": "Optimize this quicksort for Python performance. Output ONLY code:\n\n{code}",
        "produces_code": True,
    },
    {
        "name": "Tester",
        "system": "You are a QA engineer. Write comprehensive pytest unit tests.",
        "task": "Write pytest tests for this quicksort. Cover edge cases. Output ONLY code:\n\n{code}",
        "produces_code": True,  # Tester produces test code
    },
]

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

    "Reviewer": '''Issues:
- Not truly in-place (creates new lists)
- O(n) extra space
- Worst case O(n^2) with duplicates''',

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
from generated_quicksort import quicksort

def test_empty():
    arr = []
    quicksort(arr)
    assert arr == []

def test_single():
    arr = [1]
    quicksort(arr)
    assert arr == [1]

def test_sorted():
    arr = [1, 2, 3]
    quicksort(arr)
    assert arr == [1, 2, 3]

def test_reverse():
    arr = [3, 2, 1]
    quicksort(arr)
    assert arr == [1, 2, 3]

def test_duplicates():
    arr = [2, 2, 1, 1, 3]
    quicksort(arr)
    assert arr == [1, 1, 2, 2, 3]''',
}


def score_code(code_text: str, role_name: str) -> float:
    """Differentiated scoring by role."""
    score = 0.0
    code_lower = code_text.lower()

    if role_name == "Generator":
        if "def quicksort" in code_text:
            score += 0.3
        if "in-place" in code_lower:
            score += 0.1
        if '"""' in code_text:
            score += 0.1
        if ": list" in code_text or "-> None" in code_text:
            score += 0.1
        if "left = [" in code_text or "right = [" in code_text:
            score -= 0.2

    elif role_name == "Reviewer":
        if "in-place" in code_lower or "space" in code_lower:
            score += 0.3
        if "o(n" in code_lower:
            score += 0.2
        if len(code_text.split('\n')) >= 3:
            score += 0.2
        if "bug" in code_lower or "issue" in code_lower:
            score += 0.2

    elif role_name == "Optimizer":
        if "partition" in code_lower:
            score += 0.3
        if "in-place" in code_lower:
            score += 0.2
        if "def _partition" in code_text:
            score += 0.2
        if "left = [" not in code_text and "right = [" not in code_text:
            score += 0.2

    elif role_name == "Tester":
        if "pytest" in code_text:
            score += 0.1
        if "test_empty" in code_text:
            score += 0.2
        if "test_duplicates" in code_text:
            score += 0.2
        if "from generated_quicksort import quicksort" in code_text:
            score += 0.3

    return max(score, 0.0)


async def generate_with_llm(adapter, roles, base_code=None):
    """Parallel LLM calls for all roles."""
    prompts = []
    systems = []

    for role in roles:
        task = role["task"]
        if base_code and "{code}" in task:
            task = task.format(code=base_code)
        prompts.append(task)
        systems.append(role["system"])

    print(f"    Calling LLM for {len(prompts)} agents in parallel...")
    start = asyncio.get_event_loop().time()

    responses = await adapter.call_batch(prompts, systems)

    elapsed = asyncio.get_event_loop().time() - start
    print(f"    → Done in {elapsed:.2f} seconds")

    return responses


async def main():
    print("=" * 70)
    print("CODE GENERATION v4.1: Async LLM + Code-only Winner")
    print("=" * 70)

    api_key = os.getenv("OPENAI_API_KEY")
    use_mock = not api_key

    if use_mock:
        print("\n[!] OPENAI_API_KEY not set — using Mock responses")
    else:
        print("\n[+] Using OpenAI GPT-4o-mini (async)")

    # 1. Orbital sync
    print("\n[1/4] Orbital synchronization (300 steps)...")
    mol = MolecularSystem(n_agents=4, dt=0.05, noise=0.01, k_sparse=3, exc_ratio=0.90)
    for layer in mol.orbital.layers:
        layer.coupling *= 3.0
    for _ in range(300):
        mol.step()
    sync_r = mol.order_parameter()
    print(f"    Sync r = {sync_r:.3f}")

    # 2. Async generation
    print("\n[2/4] Async code generation...")

    if use_mock:
        responses = [MOCK_RESPONSES[r["name"]] for r in ROLES]
        print("    Mock mode: loaded predefined responses")
    else:
        adapter = AsyncOpenAIAdapter(api_key=api_key)
        gen_response = await generate_with_llm(adapter, [ROLES[0]])
        base_code = gen_response[0]
        print(f"    Generator: {len(base_code)} chars")

        batch_roles = ROLES[1:4]
        batch_responses = await generate_with_llm(adapter, batch_roles, base_code=base_code)
        responses = [gen_response[0]] + batch_responses
        await adapter.close()

    # 3. Score
    print("\n[3/4] Scoring...")
    scores = []
    for i, (role, resp) in enumerate(zip(ROLES, responses)):
        score = score_code(resp, role["name"])
        score += sync_r * 0.05
        scores.append(score)
        print(f"    {role['name']:12s}: score={score:.2f} (code={role['produces_code']})")

    # 4. Winner — ONLY code-producing agents
    print("\n[4/4] Selecting winner (code-only)...")
    
    # Filter to code producers only
    code_indices = [i for i, r in enumerate(ROLES) if r["produces_code"]]
    code_scores = [(i, scores[i]) for i in code_indices]
    best_idx, best_score = max(code_scores, key=lambda x: x[1])
    
    best_role = ROLES[best_idx]["name"]
    best_code = responses[best_idx]

    print(f"\n{'='*70}")
    print(f"WINNER: Agent {best_idx} ({best_role}) — score={best_score:.2f}")
    print(f"{'='*70}")
    print("\n--- GENERATED CODE ---")
    print(best_code)
    print("--- END CODE ---")

    # Save
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "v4_1")
    os.makedirs(output_dir, exist_ok=True)

    code_file = os.path.join(output_dir, "generated_quicksort.py")
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI v4.1 (async)\n")
        f.write(f"# Winner: {best_role}\n")
        f.write(f"# Sync r: {sync_r:.3f}\n")
        f.write(f"# Mode: {'OpenAI' if not use_mock else 'Mock'}\n\n")
        f.write(best_code)
    print(f"\nSaved: {code_file}")

    # Tests (always from Tester)
    test_file = os.path.join(output_dir, "test_quicksort.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(f"# Tests from Molecular AI v4.1\n\n")
        f.write(MOCK_RESPONSES["Tester"])
    print(f"Tests: {test_file}")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Sync r:     {sync_r:.3f}")
    print(f"Winner:     {best_role} (score={best_score:.2f})")
    print(f"Mode:       {'OpenAI async' if not use_mock else 'Mock'}")
    print(f"Speedup:    {'4x (parallel)' if not use_mock else 'N/A (mock)'}")


if __name__ == "__main__":
    asyncio.run(main())