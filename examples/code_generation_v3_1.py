#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Code Generation v3.1.
Fix: sys.executable saved before MolecularSystem overwrites 'sys'.
"""

import os
import sys
import random
import subprocess

# Сохраняем sys.executable ДО того, как 'sys' будет перезаписан
PYTHON_EXE = sys.executable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


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

MOCK_RESPONSES = {
    "Generator": '''def quicksort(arr: list) -> None:
    """Sort list in-place via quicksort (not truly in-place, creates lists)."""
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


def run_llm(role, use_mock=True):
    if use_mock:
        return MOCK_RESPONSES[role["name"]]
    from adapters.factory import create_adapter
    adapter = create_adapter("openai", model="gpt-4o-mini")
    prompt = f"System: {role['system']}\n\nTask: {role['task']}\n\nResponse:"
    return adapter.call_llm(prompt).strip()


def score_code(code_text, role_name):
    score = 0.0
    code_lower = code_text.lower()

    if role_name == "Generator":
        if "def quicksort" in code_text:
            score += 0.3
        if "in-place" in code_lower or "in place" in code_lower:
            score += 0.1
        if '"""' in code_text:
            score += 0.1
        if ": list" in code_text or "-> None" in code_text:
            score += 0.1
        if len(code_text) < 500:
            score += 0.1
        if "left = [" in code_text or "right = [" in code_text:
            score -= 0.2

    elif role_name == "Reviewer":
        if "in-place" in code_lower or "space" in code_lower:
            score += 0.3
        if "o(n" in code_lower or "o(n^2)" in code_lower:
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
        if len(code_text) < 800:
            score += 0.1
        if "left = [" not in code_text and "right = [" not in code_text:
            score += 0.2

    elif role_name == "Tester":
        if "pytest" in code_text:
            score += 0.1
        if "test_empty" in code_text:
            score += 0.2
        if "test_duplicates" in code_text:
            score += 0.2
        if "test_large" in code_text or "test_random" in code_text:
            score += 0.2
        if "from generated_quicksort import quicksort" in code_text:
            score += 0.3

    return max(score, 0.0)


def main():
    print("=" * 70)
    print("CODE GENERATION v3.1: Multi-Agent with Differentiated Consensus")
    print("=" * 70)

    api_key = os.getenv("OPENAI_API_KEY")
    use_mock = not api_key
    if use_mock:
        print("\n[!] OPENAI_API_KEY not set — using Mock responses")
    else:
        print("\n[+] Using OpenAI GPT-4o-mini")

    # 1. Orbital sync
    print("\n[1/6] Orbital synchronization (500 steps)...")
    mol_sys = MolecularSystem(
        n_agents=4,
        dt=0.05,
        noise=0.01,
        k_sparse=3,
        exc_ratio=0.90,
    )
    for layer in mol_sys.orbital.layers:
        layer.coupling *= 3.0

    for _ in range(500):
        mol_sys.step()
    sync_r = mol_sys.order_parameter()
    print(f"    Sync r = {sync_r:.3f}")

    # 2. Generate code
    print("\n[2/6] Agent code generation...")
    responses = []
    for i, role in enumerate(ROLES):
        agent = mol_sys.agents[i]
        print(f"    Agent {i} ({role['name']}) — mood={agent.mood:+.2f}")
        resp = run_llm(role, use_mock=use_mock)
        responses.append(resp)
        print(f"    → {len(resp)} chars")

    # 3. Score
    print("\n[3/6] Scoring code quality...")
    scores = []
    for i, (role, resp) in enumerate(zip(ROLES, responses)):
        score = score_code(resp, role["name"])
        score += sync_r * 0.05
        scores.append(score)
        print(f"    {role['name']:12s}: score={score:.2f}")

    # 4. Pick winner
    print("\n[4/6] Selecting winner...")
    best_idx = scores.index(max(scores))
    best_role = ROLES[best_idx]["name"]
    best_code = responses[best_idx]

    print(f"\n{'='*70}")
    print(f"WINNER: Agent {best_idx} ({best_role}) — score={scores[best_idx]:.2f}")
    print(f"{'='*70}")
    print("\n--- GENERATED CODE ---")
    print(best_code)
    print("--- END CODE ---")

    # 5. Save files
    print("\n[5/6] Saving files...")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    code_file = os.path.join(output_dir, "generated_quicksort.py")
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Code Generation v3.1\n")
        f.write(f"# Winner: {best_role} (Agent {best_idx})\n")
        f.write(f"# Sync r: {sync_r:.3f}\n")
        f.write(f"# Mode: {'OpenAI' if not use_mock else 'Mock'}\n\n")
        f.write(best_code)
    print(f"    Code: {code_file}")

    test_code = MOCK_RESPONSES["Tester"]
    test_file = os.path.join(output_dir, "test_quicksort.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(f"# Generated by Molecular AI Tester\n\n")
        f.write(test_code)
    print(f"    Tests: {test_file}")

    all_file = os.path.join(output_dir, "all_candidates.py")
    with open(all_file, "w", encoding="utf-8") as f:
        f.write("# All candidates from code generation v3.1\n\n")
        for i, (role, resp) in enumerate(zip(ROLES, responses)):
            f.write(f"# {'='*60}\n")
            f.write(f"# Agent {i}: {role['name']} (score={scores[i]:.2f})\n")
            f.write(f"# {'='*60}\n\n")
            f.write(resp)
            f.write("\n\n")
    print(f"    All: {all_file}")

    # 6. Run tests
    print("\n[6/6] Running pytest...")
    try:
        result = subprocess.run(
            [PYTHON_EXE, "-m", "pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            cwd=output_dir,
        )
        print(result.stdout)
        if result.returncode != 0:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"    [!] pytest failed: {e}")
        print(f"    Manual run: cd output && pytest test_quicksort.py -v")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Sync r:        {sync_r:.3f}")
    print(f"Best agent:    {best_role} (score={scores[best_idx]:.2f})")
    print(f"Code chars:    {len(best_code)}")
    print(f"Mode:          {'OpenAI' if not use_mock else 'Mock'}")
    print(f"\nFiles:")
    print(f"  {code_file}")
    print(f"  {test_file}")

    # Also try manual import test
    print(f"\n{'='*70}")
    print("MANUAL VERIFICATION")
    print(f"{'='*70}")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("generated_quicksort", code_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        mod.quicksort(arr)
        print(f"quicksort([3,1,4,1,5,9,2,6]) = {arr}")
        if arr == [1, 1, 2, 3, 4, 5, 6, 9]:
            print("✅ MANUAL TEST PASSED")
        else:
            print("❌ MANUAL TEST FAILED")
    except Exception as e:
        print(f"[!] Manual test failed: {e}")


if __name__ == "__main__":
    main()