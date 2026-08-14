#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSkillEngine v2.0 — autonomous skill generation, validation, and evolution.
Molecular AI creates its own skills: detect gap → generate → validate → vote → evolve.
"""

from __future__ import annotations

import ast
import hashlib
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SkillCandidate:
    name: str
    category: str
    description: str
    complexity: int
    code: str
    tests: str
    keywords: List[str]
    parent_task: str
    birth_time: float = field(default_factory=time.time)
    validation_score: float = 0.0
    votes: List[Tuple[str, float]] = field(default_factory=list)

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.code.encode()).hexdigest()[:16]

    @property
    def is_safe(self) -> bool:
        dangerous = {"exec", "eval", "__import__", "os.system", "subprocess"}
        code_lower = self.code.lower()
        return not any(d in code_lower for d in dangerous)


@dataclass
class SkillEvolutionRecord:
    skill_name: str
    level: float = 0.1
    usage_count: int = 0
    success_history: List[bool] = field(default_factory=list)
    last_used: float = field(default_factory=time.time)
    pruned: bool = False

    def update(self, success: bool, alpha: float = 0.05):
        self.usage_count += 1
        self.last_used = time.time()
        self.success_history.append(success)
        if len(self.success_history) > 100:
            self.success_history.pop(0)
        if success:
            self.level = min(1.0, self.level + alpha)
        else:
            self.level = max(0.0, self.level - alpha * 0.6)

    @property
    def should_prune(self, age_threshold: float = 300.0, min_level: float = 0.05) -> bool:
        age = time.time() - self.last_used
        return age > age_threshold and self.level < min_level


# ---------------------------------------------------------------------------
# Skill Gap Detector
# ---------------------------------------------------------------------------

class SkillGapDetector:
    def __init__(self, registry_skills: Dict[str, Any], threshold: float = 0.25):
        self.registry = registry_skills
        self.threshold = threshold

    def detect(self, task: str, required_keywords: List[str]) -> Optional[Dict[str, Any]]:
        task_lower = task.lower()
        uncovered = []
        for kw in required_keywords:
            covered = False
            for skill_name, info in self.registry.items():
                skill_text = f"{skill_name} {info.get('description', '')}".lower()
                if kw.lower() in skill_text:
                    level = info.get("level", 0.5)
                    if level >= self.threshold:
                        covered = True
                        break
            if not covered:
                uncovered.append(kw)
        if not uncovered:
            return None
        return {
            "task": task,
            "missing_keywords": uncovered,
            "severity": len(uncovered),
            "suggested_category": self._infer_category(uncovered),
        }

    def _infer_category(self, keywords: List[str]) -> str:
        """Heuristic category inference from keywords."""
        mapping = {
            "api": "Backend", "rest": "Backend", "graphql": "Backend",
            "react": "Frontend", "vue": "Frontend", "css": "Frontend",
            "jwt": "Security", "oauth": "Security", "encrypt": "Security",
            "postgres": "Database", "mongo": "Database", "sql": "Database",
            "docker": "DevOps", "k8s": "DevOps", "ci": "DevOps", "deploy": "DevOps",
            "pytest": "Testing", "test": "Testing", "coverage": "Testing",
            "pytorch": "AI/ML", "tensorflow": "AI/ML", "llm": "AI/ML",
            "redis": "Infrastructure", "kafka": "Infrastructure", "queue": "Infrastructure",
            "json": "Data", "parse": "Data", "file": "Data", "csv": "Data",
            "websocket": "Real-time", "broadcast": "Real-time", "async": "Real-time",
            "design": "UI/UX", "animation": "UI/UX", "grid": "UI/UX",
            "auth": "Security", "logging": "DevOps", "monitoring": "DevOps",
        }
        scores: Dict[str, int] = {}
        for kw in keywords:
            kw_lower = kw.lower()
            for mk, cat in mapping.items():
                if mk in kw_lower:
                    scores[cat] = scores.get(cat, 0) + 1
        if scores:
            return max(scores, key=scores.get)
        return "General"


# ---------------------------------------------------------------------------
# Skill Generator
# ---------------------------------------------------------------------------

class SkillGenerator:
    MOCK_TEMPLATES: Dict[str, Dict[str, str]] = {
        "GraphQL": {
            "category": "Backend",
            "description": "GraphQL schema definition and resolver implementation.",
            "complexity": "7",
            "code": """
class GraphQLSchema:
    def __init__(self):
        self.types = {}
        self.resolvers = {}

    def add_type(self, name, fields):
        self.types[name] = fields

    def add_resolver(self, type_name, field, resolver):
        self.resolvers.setdefault(type_name, {})[field] = resolver

    def resolve(self, type_name, field, root):
        resolver = self.resolvers.get(type_name, {}).get(field)
        return resolver(root) if resolver else root.get(field)
""",
            "tests": """
def test_add_type():
    s = GraphQLSchema()
    s.add_type("User", {"id": "ID"})
    assert "User" in s.types

def test_resolver():
    s = GraphQLSchema()
    s.add_type("Query", {"hello": "String"})
    s.add_resolver("Query", "hello", lambda _: "world")
    assert s.resolve("Query", "hello", {}) == "world"
""",
            "keywords": ["graphql", "schema", "resolver"],
        },
        "JSONParser": {
            "category": "Data",
            "description": "JSON parsing and validation.",
            "complexity": "4",
            "code": """
import json

class JSONParser:
    @staticmethod
    def parse(data):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
""",
            "tests": """
def test_parse_valid():
    data = '{"name": "test"}'
    result = JSONParser.parse(data)
    assert result["name"] == "test"
""",
            "keywords": ["json", "parse", "validation"],
        },
        "FileProcessor": {
            "category": "Data",
            "description": "File operations.",
            "complexity": "4",
            "code": """
class FileProcessor:
    @staticmethod
    def read_file(path):
        with open(path, 'r') as f:
            return f.read()

    @staticmethod
    def write_file(path, content):
        with open(path, 'w') as f:
            f.write(content)
""",
            "tests": """
import tempfile
import os

def test_write_and_read():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    FileProcessor.write_file(path, "hello")
    result = FileProcessor.read_file(path)
    assert result == "hello"
    os.unlink(path)
""",
            "keywords": ["file", "read", "write"],
        },
    }

    def __init__(self, use_llm: bool = False, adapter=None):
        self.use_llm = use_llm
        self.adapter = adapter
        self._mock_keys = list(self.MOCK_TEMPLATES.keys())
        self._mock_index = 0

    def generate(self, gap: Dict[str, Any]) -> SkillCandidate:
        for kw in gap.get("missing_keywords", []):
            kw_lower = kw.lower()
            for key, tpl in self.MOCK_TEMPLATES.items():
                if kw_lower in key.lower():
                    return self._generate_from_template(key, gap)
                if any(kw_lower in k for k in tpl.get("keywords", [])):
                    return self._generate_from_template(key, gap)
        key = self._mock_keys[self._mock_index % len(self._mock_keys)]
        self._mock_index += 1
        return self._generate_from_template(key, gap)

    def _generate_from_template(self, template_key: str, gap: Dict[str, Any]) -> SkillCandidate:
        tpl = self.MOCK_TEMPLATES.get(template_key)
        if not tpl:
            return SkillCandidate(
                name="GenericSkill",
                category="General",
                description="Generic skill",
                complexity=3,
                code="# Code here",
                tests="# Tests here",
                keywords=[],
                parent_task=gap["task"],
            )
        return SkillCandidate(
            name=template_key,
            category=tpl["category"],
            description=tpl["description"],
            complexity=int(tpl["complexity"]),
            code=tpl["code"],
            tests=tpl["tests"],
            keywords=tpl.get("keywords", []),
            parent_task=gap["task"],
        )


# ---------------------------------------------------------------------------
# Skill Validator
# ---------------------------------------------------------------------------

class SkillValidator:
    def __init__(self, timeout_sec: float = 5.0):
        self.timeout = timeout_sec

    def validate(self, candidate: SkillCandidate) -> float:
        if not candidate.is_safe:
            return 0.0
        score = 0.0
        try:
            ast.parse(candidate.code)
            score += 0.2
        except SyntaxError:
            return 0.0
        import_ok = self._test_import(candidate)
        if import_ok:
            score += 0.3
        else:
            return score
        pytest_ok = self._test_pytest(candidate)
        if pytest_ok:
            score += 0.5
        candidate.validation_score = score
        return score

    def _test_import(self, candidate: SkillCandidate) -> bool:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(candidate.code)
                tmp_path = f.name
            tmp_dir = os.path.dirname(tmp_path)
            sys.path.insert(0, tmp_dir)
            try:
                import importlib
                module_name = os.path.basename(tmp_path)[:-3]
                mod = importlib.import_module(module_name)
                members = [name for name in dir(mod) if not name.startswith("_")]
                return len(members) > 0
            finally:
                sys.path.remove(tmp_dir)
                os.unlink(tmp_path)
        except Exception:
            return False

    def _test_pytest(self, candidate: SkillCandidate) -> bool:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(candidate.code)
                f.write("\n\n")
                f.write(candidate.tests)
                tmp_path = f.name
            result = subprocess.run(
                [sys.executable, "-m", "pytest", tmp_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            os.unlink(tmp_path)
            return result.returncode == 0
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Skill Voter
# ---------------------------------------------------------------------------

class SkillVoter:
    def __init__(self, n_agents: int = 3):
        self.n_agents = n_agents

    def vote(self, candidate: SkillCandidate) -> Tuple[bool, float]:
        votes = []
        code_score = self._score_code(candidate.code)
        votes.append(("CodeReviewer", code_score))
        sec_score = 0.3 if candidate.is_safe else 0.0
        sec_score += 0.4 * candidate.validation_score
        votes.append(("SecurityAuditor", min(sec_score, 1.0)))
        util_score = self._score_utility(candidate)
        votes.append(("UtilityJudge", util_score))
        candidate.votes = votes
        scores = [s for _, s in votes]
        consensus = sum(scores) / len(scores)
        accepted = consensus >= 0.6 and all(s >= 0.3 for s in scores)
        return accepted, consensus

    def _score_code(self, code: str) -> float:
        score = 0.0
        if 'class ' in code or 'def ' in code:
            score += 0.5
        if '"""' in code:
            score += 0.3
        if len(code) < 2000:
            score += 0.2
        return min(score, 1.0)

    def _score_utility(self, candidate: SkillCandidate) -> float:
        score = 0.0
        task_lower = candidate.parent_task.lower()
        for kw in candidate.keywords:
            if kw.lower() in task_lower:
                score += 0.3
        score += 0.2 if candidate.validation_score >= 0.8 else 0.0
        return min(score, 1.0)


# ---------------------------------------------------------------------------
# Skill Registry Evolver
# ---------------------------------------------------------------------------

class SkillRegistryEvolver:
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.evolution: Dict[str, SkillEvolutionRecord] = {}
        self.candidates_history: List[SkillCandidate] = []

    def integrate(self, candidate: SkillCandidate, accepted: bool):
        if not accepted:
            return
        self.skills[candidate.name] = {
            "name": candidate.name,
            "category": candidate.category,
            "description": candidate.description,
            "complexity": candidate.complexity,
            "code": candidate.code,
            "tests": candidate.tests,
            "keywords": candidate.keywords,
            "checksum": candidate.checksum,
            "level": 0.1,
        }
        self.evolution[candidate.name] = SkillEvolutionRecord(skill_name=candidate.name)
        self.candidates_history.append(candidate)

    def record_usage(self, skill_name: str, success: bool):
        if skill_name in self.evolution:
            self.evolution[skill_name].update(success)
            self.skills[skill_name]["level"] = self.evolution[skill_name].level

    def sleep_consolidation(self) -> List[str]:
        pruned = []
        for name, record in list(self.evolution.items()):
            if record.should_prune:
                record.pruned = True
                self.skills.pop(name, None)
                pruned.append(name)
        return pruned

    def get_skill_for_task(self, task: str, min_level: float = 0.05) -> Optional[str]:
        task_lower = task.lower()
        best_name = None
        best_score = 0.0
        for name, info in self.skills.items():
            if info.get("level", 0.0) < min_level:
                continue
            score = 0.0
            for kw in info.get("keywords", []):
                if kw.lower() in task_lower:
                    score += 1.0
            if score > best_score:
                best_score = score
                best_name = name
        return best_name


# ================================================================
# AUTO SKILL ENGINE
# ================================================================

class AutoSkillEngine:
    def __init__(self, use_llm: bool = False, adapter=None):
        self.detector = SkillGapDetector({})
        self.generator = SkillGenerator(use_llm=use_llm, adapter=adapter)
        self.validator = SkillValidator()
        self.voter = SkillVoter()
        self.registry = SkillRegistryEvolver()
        self.stats = {
            "gaps_detected": 0,
            "generated": 0,
            "validated": 0,
            "accepted": 0,
            "pruned": 0,
        }

    def _skill_exists(self, keywords: List[str]) -> bool:
        if not keywords:
            return False
        for kw in keywords:
            kw_lower = kw.lower()
            for skill_name, info in self.registry.skills.items():
                if kw_lower in skill_name.lower():
                    return True
                for k in info.get("keywords", []):
                    if kw_lower in k.lower():
                        return True
        return False

    def run_lifecycle(self, task: str, required_keywords: Optional[List[str]] = None) -> Optional[SkillCandidate]:
        if required_keywords is None:
            required_keywords = self._extract_keywords(task)

        if self._skill_exists(required_keywords):
            return None

        if required_keywords:
            for kw in required_keywords:
                for key in self.generator.MOCK_TEMPLATES.keys():
                    if kw.lower() in key.lower():
                        gap = {
                            "task": task,
                            "missing_keywords": required_keywords,
                            "suggested_category": "General"
                        }
                        candidate = self.generator._generate_from_template(key, gap)
                        if candidate:
                            self.registry.integrate(candidate, accepted=True)
                            self.stats["accepted"] += 1
                            return candidate

        gap = self.detector.detect(task, required_keywords or [])
        if gap is None:
            return None

        self.stats["gaps_detected"] += 1
        candidate = self.generator.generate(gap)
        self.stats["generated"] += 1
        val_score = self.validator.validate(candidate)
        self.stats["validated"] += 1
        accepted, consensus = self.voter.vote(candidate)
        self.registry.integrate(candidate, accepted)
        if accepted:
            self.stats["accepted"] += 1
        return candidate if accepted else None

    def evolve_from_feedback(self, skill_name: str, success: bool):
        self.registry.record_usage(skill_name, success)

    def sleep(self) -> List[str]:
        pruned = self.registry.sleep_consolidation()
        self.stats["pruned"] += len(pruned)
        return pruned

    def _extract_keywords(self, task: str) -> List[str]:
        tech_keywords = [
            "graphql", "json", "file", "parse", "docker", "deploy",
            "api", "rest", "react", "vue", "css", "html",
            "jwt", "oauth", "postgres", "mongo", "sql",
            "redis", "cache", "websocket", "async", "design"
        ]
        found = [kw for kw in tech_keywords if kw.lower() in task.lower()]
        if not found:
            words = re.findall(r"[A-Za-z]+", task.lower())
            stop_words = {"this", "that", "with", "from"}
            found = [w for w in words if len(w) > 3 and w not in stop_words]
        return found[:10]


# ================================================================
# HELPERS
# ================================================================

def attach_to_system(system, use_llm: bool = False, adapter=None) -> AutoSkillEngine:
    """
    Attach AutoSkillEngine to a MolecularSystem instance.
    Adds `system.auto_skill` attribute.
    """
    engine = AutoSkillEngine(use_llm=use_llm, adapter=adapter)
    system.auto_skill = engine
    return engine