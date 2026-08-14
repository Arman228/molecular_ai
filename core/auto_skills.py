#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSkillEngine — autonomous skill generation
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
from typing import Any, Dict, List, Optional, Tuple


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
            "suggested_category": "General",
        }


# ---------------------------------------------------------------------------
# Skill Generator
# ---------------------------------------------------------------------------

class SkillGenerator:
    MOCK_TEMPLATES: Dict[str, Dict[str, str]] = {
        "JSONParser": {
            "category": "Data",
            "description": "JSON parsing and validation",
            "complexity": "4",
            "code": """
import json
from typing import Dict

class JSONParser:
    @staticmethod
    def parse(data: str) -> Dict:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
""",
            "tests": """
import pytest
from auto_skill_json import JSONParser

def test_parse_valid():
    data = '{"name": "test"}'
    result = JSONParser.parse(data)
    assert result["name"] == "test"
""",
            "keywords": ["json", "parse", "validation"],
        },
        
        "FileProcessor": {
            "category": "Data",
            "description": "File operations",
            "complexity": "4",
            "code": """
import os

class FileProcessor:
    @staticmethod
    def read_file(path: str, encoding: str = "utf-8") -> str:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(path: str, content: str, encoding: str = "utf-8") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
""",
            "tests": """
import pytest
import tempfile
import os
from auto_skill_file import FileProcessor

def test_write_and_read():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
    FileProcessor.write_file(path, "hello")
    result = FileProcessor.read_file(path)
    assert result == "hello"
    os.unlink(path)
""",
            "keywords": ["file", "read", "write"],
        },

        "CSVProcessor": {
            "category": "Data",
            "description": "CSV reading and writing",
            "complexity": "4",
            "code": """
import csv
from typing import List, Dict

class CSVProcessor:
    @staticmethod
    def read_csv(path: str) -> List[Dict[str, str]]:
        with open(path, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    @staticmethod
    def write_csv(path: str, data: List[Dict[str, str]]) -> None:
        if not data:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
""",
            "tests": """
import pytest
import tempfile
import os
from auto_skill_csv import CSVProcessor

def test_write_and_read():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
    data = [{"name": "Alice"}]
    CSVProcessor.write_csv(path, data)
    result = CSVProcessor.read_csv(path)
    assert len(result) == 1
    os.unlink(path)
""",
            "keywords": ["csv", "read", "write"],
        },

        "RedisCache": {
            "category": "Infrastructure",
            "description": "In-memory LRU cache",
            "complexity": "5",
            "code": """
from collections import OrderedDict
from typing import Any, Optional

class RedisCache:
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.store: OrderedDict[str, Any] = OrderedDict()

    def set(self, key: str, value: Any) -> None:
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = value
        while len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def get(self, key: str) -> Any:
        if key in self.store:
            self.store.move_to_end(key)
            return self.store[key]
        return None
""",
            "tests": """
import pytest
from auto_skill_redis import RedisCache

def test_set_get():
    c = RedisCache()
    c.set("a", 1)
    assert c.get("a") == 1
""",
            "keywords": ["cache", "lru", "memory"],
        },

        "RateLimiter": {
            "category": "Security",
            "description": "Token-bucket rate limiter",
            "complexity": "5",
            "code": """
import time
from typing import Dict

class RateLimiter:
    def __init__(self, rate: float = 10.0, capacity: int = 20):
        self.rate = rate
        self.capacity = capacity
        self.buckets: Dict[str, Dict] = {}

    def _refill(self, client: str) -> None:
        now = time.time()
        bucket = self.buckets.setdefault(client, {"tokens": self.capacity, "last": now})
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now

    def allow(self, client: str) -> bool:
        self._refill(client)
        bucket = self.buckets[client]
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False
""",
            "tests": """
import pytest
import time
from auto_skill_ratelimit import RateLimiter

def test_allow():
    lim = RateLimiter(rate=10, capacity=5)
    for _ in range(5):
        assert lim.allow("alice") is True
    assert lim.allow("alice") is False
""",
            "keywords": ["rate limit", "throttle"],
        },

        "WebSocket": {
            "category": "Real-time",
            "description": "WebSocket connection manager",
            "complexity": "6",
            "code": """
import asyncio
from typing import Set

class WebSocketManager:
    def __init__(self):
        self.connections: Set[asyncio.Queue] = set()

    async def connect(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections.add(queue)
        return queue

    async def broadcast(self, message: str) -> None:
        for q in self.connections:
            try:
                await q.put(message)
            except Exception:
                pass
""",
            "tests": """
import pytest
import asyncio
from auto_skill_websocket import WebSocketManager

@pytest.mark.asyncio
async def test_connect():
    mgr = WebSocketManager()
    q = await mgr.connect()
    assert q in mgr.connections
""",
            "keywords": ["websocket", "async", "broadcast"],
        },

        "DesignSystem": {
            "category": "UI/UX",
            "description": "Design system with tokens",
            "complexity": "6",
            "code": """
from typing import Dict, Any

class DesignSystem:
    def __init__(self):
        self.tokens = {
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#8b5cf6",
            }
        }
    
    def get_token(self, category: str, name: str) -> Any:
        return self.tokens.get(category, {}).get(name)
""",
            "tests": """
import pytest
from auto_skill_design import DesignSystem

def test_tokens():
    ds = DesignSystem()
    assert ds.get_token("colors", "primary") == "#3b82f6"
""",
            "keywords": ["design", "ui", "tokens"],
        },

        "ReactComponent": {
            "category": "Frontend",
            "description": "React-like component",
            "complexity": "6",
            "code": """
from typing import Dict, Any

class ReactComponent:
    def __init__(self, props: Dict[str, Any] = None):
        self.props = props or {}
        self.state: Dict[str, Any] = {}
    
    def set_state(self, new_state: Dict[str, Any]) -> None:
        self.state.update(new_state)
    
    def render(self) -> str:
        return f"<div>{self.__class__.__name__}</div>"
""",
            "tests": """
import pytest
from auto_skill_react import ReactComponent

def test_state():
    comp = ReactComponent()
    comp.set_state({"count": 1})
    assert comp.state["count"] == 1
""",
            "keywords": ["react", "component", "state"],
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


# ---------------------------------------------------------------------------
# AutoSkillEngine
# ---------------------------------------------------------------------------

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

    def run_lifecycle(self, task: str, required_keywords: Optional[List[str]] = None) -> Optional[SkillCandidate]:
        if required_keywords is None:
            required_keywords = self._extract_keywords(task)
        gap = self.detector.detect(task, required_keywords)
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

    def sleep(self) -> List[str]:
        pruned = self.registry.sleep_consolidation()
        self.stats["pruned"] += len(pruned)
        return pruned

    def _extract_keywords(self, task: str) -> List[str]:
        tech_keywords = ["json", "file", "csv", "cache", "rate", "websocket", "design", "react"]
        found = [kw for kw in tech_keywords if kw.lower() in task.lower()]
        if not found:
            words = re.findall(r"[A-Za-z]+", task.lower())
            stop_words = {"this", "that", "with", "from"}
            found = [w for w in words if len(w) > 3 and w not in stop_words]
        return found[:10]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def attach_to_system(system, use_llm: bool = False, adapter=None) -> AutoSkillEngine:
    engine = AutoSkillEngine(use_llm=use_llm, adapter=adapter)
    system.auto_skill = engine
    return engine