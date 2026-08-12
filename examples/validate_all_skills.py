#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate All Skills v3 — proper module naming so imports work.
"""

import json
import os
import re
import subprocess
import sys
import tempfile


def to_snake(name: str) -> str:
    """PatternResonance -> pattern_resonance"""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def validate_skill(name: str, code: str, tests: str) -> dict:
    """Run pytest with proper module naming."""
    result = {
        "name": name,
        "ast_ok": False,
        "import_ok": False,
        "total_tests": 0,
        "passed_tests": 0,
        "score": 0.0,
        "error": None,
    }

    # 1. AST
    try:
        import ast
        ast.parse(code)
        result["ast_ok"] = True
        result["score"] += 0.2
    except SyntaxError as e:
        result["error"] = f"AST: {e}"
        return result

    # 2. Import
    module_name = to_snake(name)
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, f"{module_name}.py")

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code)

        sys.path.insert(0, tmp_dir)
        import importlib
        mod = importlib.import_module(module_name)
        members = [n for n in dir(mod) if not n.startswith("_")]
        if len(members) > 0:
            result["import_ok"] = True
            result["score"] += 0.3
        sys.path.remove(tmp_dir)
    except Exception as e:
        result["error"] = f"Import: {str(e)[:100]}"
        return result

    # 3. Pytest — add tests to same file, run from tmp_dir
    try:
        with open(tmp_path, "a", encoding="utf-8") as f:
            f.write("\n\n")
            f.write(tests)

        # Create conftest.py to add tmp_dir to path
        with open(os.path.join(tmp_dir, "conftest.py"), "w", encoding="utf-8") as f:
            f.write("import sys\n")
            f.write(f"sys.path.insert(0, {repr(tmp_dir)})\n")

        r = subprocess.run(
            [sys.executable, "-m", "pytest", tmp_path, "-v", "--tb=no", "--no-header"],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
            cwd=tmp_dir,
        )

        stdout = r.stdout + r.stderr
        passed_match = re.search(r"(\d+)\s+passed", stdout)
        failed_match = re.search(r"(\d+)\s+failed", stdout)
        error_match = re.search(r"(\d+)\s+error", stdout)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0

        result["passed_tests"] = passed
        result["total_tests"] = passed + failed + errors

        if result["total_tests"] > 0:
            pass_rate = passed / result["total_tests"]
            result["score"] += 0.5 * pass_rate

    except Exception as e:
        result["error"] = f"Pytest: {e}"

    # Cleanup
    try:
        import shutil
        shutil.rmtree(tmp_dir)
    except:
        pass

    return result


def main():
    print("=" * 75)
    print("VALIDATE ALL SKILLS v3")
    print("Proper module naming: PatternResonance -> pattern_resonance.py")
    print("=" * 75)

    registry_path = "data/skills_registry.json"
    seed_path = "data/seed_skills.json"

    skills = []
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = list(data.get("registry", {}).values())
    elif os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.get("skills", [])
    else:
        print("\n[!] No skills found.")
        return

    print(f"\nLoaded {len(skills)} skills")

    print("\n" + "-" * 75)
    print(f"{'Skill':<28} {'AST':>4} {'Imp':>4} {'Tests':>7} {'Pass%':>6} {'Score':>6} {'Status':>8}")
    print("-" * 75)

    passed = 0
    total_tests_all = 0
    total_passed_all = 0

    for skill in skills:
        name = skill.get("name", "Unknown")[:28]
        code = skill.get("code", "")
        tests = skill.get("tests", "")

        if not code:
            print(f"{name:<28} {'-':>4} {'-':>4} {'-':>7} {'-':>6} {'0.00':>6} {'NO CODE':>8}")
            continue

        res = validate_skill(name, code, tests)
        total_tests_all += res["total_tests"]
        total_passed_all += res["passed_tests"]

        status = "PASS" if res["score"] >= 0.65 else "FAIL"
        if res["score"] >= 0.65:
            passed += 1

        ast_mark = "✅" if res["ast_ok"] else "❌"
        imp_mark = "✅" if res["import_ok"] else "❌"
        tests_str = f"{res['passed_tests']}/{res['total_tests']}" if res["total_tests"] > 0 else "-/-"
        pass_pct = f"{100*res['passed_tests']/res['total_tests']:.0f}%" if res["total_tests"] > 0 else "-"

        print(f"{name:<28} {ast_mark:>4} {imp_mark:>4} {tests_str:>7} {pass_pct:>6} {res['score']:>6.2f} {status:>8}")

        if res["error"] and res["score"] < 0.65:
            print(f"    → {res['error'][:80]}")

    print("-" * 75)
    print(f"\n{'SUMMARY':<28} {passed}/{len(skills)} skills PASS (score >= 0.65)")
    print(f"{'Total tests run':<28} {total_passed_all}/{total_tests_all} passed ({100*total_passed_all/max(total_tests_all,1):.1f}%)")

    if passed == len(skills):
        print(f"\n🎉 ALL {len(skills)} SKILLS VALIDATED!")
    else:
        print(f"\n✅ {passed} skills production-ready")
        print(f"⚠️  {len(skills)-passed} skills need attention")

    print("\n" + "=" * 75)


if __name__ == "__main__":
    main()