#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSkillEngine — autonomous skill generation, validation, and evolution.
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
    """A newly generated skill awaiting validation and voting."""
    name: str
    category: str
    description: str
    complexity: int
    code: str               # Python implementation
    tests: str              # pytest code
    keywords: List[str]
    parent_task: str        # what task triggered creation
    birth_time: float = field(default_factory=time.time)
    validation_score: float = 0.0
    votes: List[Tuple[str, float]] = field(default_factory=list)  # (agent_role, score)

    @property
    def checksum(self) -> str:
        """Unique ID based on code content."""
        return hashlib.sha256(self.code.encode()).hexdigest()[:16]

    @property
    def is_safe(self) -> bool:
        """Static AST check for dangerous patterns."""
        dangerous = {"exec", "eval", "__import__", "os.system", "subprocess.call",
                     "subprocess.run", "open(os.devnull", "compile("}
        code_lower = self.code.lower()
        return not any(d in code_lower for d in dangerous)


@dataclass
class SkillEvolutionRecord:
    """Tracks how a skill performs over time (Hebbian memory)."""
    skill_name: str
    level: float = 0.1          # 0.0 – 1.0
    usage_count: int = 0
    success_history: List[bool] = field(default_factory=list)
    last_used: float = field(default_factory=time.time)
    pruned: bool = False

    def update(self, success: bool, alpha: float = 0.05):
        """Hebbian LTP/LTD update."""
        self.usage_count += 1
        self.last_used = time.time()
        self.success_history.append(success)
        if len(self.success_history) > 100:
            self.success_history.pop(0)

        if success:
            self.level = min(1.0, self.level + alpha)          # LTP
        else:
            self.level = max(0.0, self.level - alpha * 0.6)   # LTD

    @property
    def should_prune(self, age_threshold: float = 300.0, min_level: float = 0.05) -> bool:
        """Sleep-consolidation pruning: old and unused skills die."""
        age = time.time() - self.last_used
        return age > age_threshold and self.level < min_level


# ---------------------------------------------------------------------------
# Skill Gap Detector
# ---------------------------------------------------------------------------

class SkillGapDetector:
    """Analyses tasks and existing registry to find missing skills."""

    def __init__(self, registry_skills: Dict[str, Any], threshold: float = 0.25):
        self.registry = registry_skills
        self.threshold = threshold

    def detect(self, task: str, required_keywords: List[str]) -> Optional[Dict[str, Any]]:
        """
        Returns a 'gap ticket' if the task requires capabilities not covered
        by existing skills above threshold level.
        """
        task_lower = task.lower()
        uncovered = []

        for kw in required_keywords:
            # Do we have a skill that covers this keyword?
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
            "docker": "DevOps", "k8s": "DevOps", "ci": "DevOps",
            "pytest": "Testing", "test": "Testing", "coverage": "Testing",
            "pytorch": "AI/ML", "tensorflow": "AI/ML", "llm": "AI/ML",
            "redis": "Infrastructure", "kafka": "Infrastructure", "queue": "Infrastructure",
        }
        scores: Dict[str, int] = {}
        for kw in keywords:
            for mk, cat in mapping.items():
                if mk in kw.lower():
                    scores[cat] = scores.get(cat, 0) + 1
        if scores:
            return max(scores, key=scores.get)
        return "General"


# ---------------------------------------------------------------------------
# Skill Generator (LLM or Mock)
# ---------------------------------------------------------------------------

class SkillGenerator:
    """Generates SkillCandidate from a gap ticket."""

    MOCK_TEMPLATES: Dict[str, Dict[str, str]] = {
        "GraphQL": {
            "category": "Backend",
            "description": "GraphQL schema definition and resolver implementation with type safety.",
            "complexity": "7",
            "code": '''from typing import List, Optional

class GraphQLSchema:
    """Minimal GraphQL schema builder."""
    def __init__(self):
        self.types: dict = {}
        self.resolvers: dict = {}

    def add_type(self, name: str, fields: dict):
        self.types[name] = fields

    def add_resolver(self, type_name: str, field: str, fn: callable):
        self.resolvers.setdefault(type_name, {})[field] = fn

    def resolve(self, type_name: str, field: str, root: dict) -> any:
        resolver = self.resolvers.get(type_name, {}).get(field)
        return resolver(root) if resolver else root.get(field)
''',
            "tests": '''import pytest
from auto_skill_graphql import GraphQLSchema

def test_add_type():
    s = GraphQLSchema()
    s.add_type("User", {"id": "ID", "name": "String"})
    assert "User" in s.types

def test_resolver():
    s = GraphQLSchema()
    s.add_type("Query", {"hello": "String"})
    s.add_resolver("Query", "hello", lambda _: "world")
    assert s.resolve("Query", "hello", {}) == "world"
''',
            "keywords": ["graphql", "schema", "resolver", "api"],
        },
        "WebSocket": {
            "category": "Backend",
            "description": "Async WebSocket handler with connection management and broadcast.",
            "complexity": "6",
            "code": '''import asyncio
from typing import Set

class WebSocketManager:
    """Manage active WebSocket connections."""
    def __init__(self):
        self.connections: Set[asyncio.Queue] = set()

    async def connect(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections.add(queue)
        return queue

    async def disconnect(self, queue: asyncio.Queue):
        self.connections.discard(queue)

    async def broadcast(self, message: str):
        dead = set()
        for q in self.connections:
            try:
                await q.put(message)
            except Exception:
                dead.add(q)
        self.connections -= dead
''',
            "tests": '''import pytest
import asyncio
from auto_skill_websocket import WebSocketManager

@pytest.mark.asyncio
async def test_connect():
    mgr = WebSocketManager()
    q = await mgr.connect()
    assert q in mgr.connections

@pytest.mark.asyncio
async def test_broadcast():
    mgr = WebSocketManager()
    q = await mgr.connect()
    await mgr.broadcast("hello")
    msg = await asyncio.wait_for(q.get(), timeout=1.0)
    assert msg == "hello"
''',
            "keywords": ["websocket", "async", "broadcast", "real-time"],
        },
        "RedisCache": {
            "category": "Infrastructure",
            "description": "In-memory caching layer with TTL and LRU eviction.",
            "complexity": "5",
            "code": '''import time
from collections import OrderedDict
from typing import Any, Optional

class RedisCache:
    """LRU cache with TTL support."""
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.store: OrderedDict[str, Any] = OrderedDict()
        self.ttl: dict = {}

    def set(self, key: str, value: Any, ttl_sec: Optional[int] = None):
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = value
        self.ttl[key] = time.time() + ttl_sec if ttl_sec else None
        while len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def get(self, key: str) -> Any:
        expire = self.ttl.get(key)
        if expire and time.time() > expire:
            del self.store[key]
            del self.ttl[key]
            return None
        if key in self.store:
            self.store.move_to_end(key)
            return self.store[key]
        return None

    def delete(self, key: str):
        self.store.pop(key, None)
        self.ttl.pop(key, None)
''',
            "tests": '''import pytest
import time
from auto_skill_redis import RedisCache

def test_set_get():
    c = RedisCache()
    c.set("a", 1)
    assert c.get("a") == 1

def test_ttl_expiry():
    c = RedisCache()
    c.set("b", 2, ttl_sec=0.1)
    time.sleep(0.2)
    assert c.get("b") is None

def test_lru_eviction():
    c = RedisCache(capacity=2)
    c.set("x", 1)
    c.set("y", 2)
    c.set("z", 3)
    assert c.get("x") is None
''',
            "keywords": ["redis", "cache", "ttl", "lru", "memory"],
        },
        "RateLimiter": {
            "category": "Security",
            "description": "Token-bucket rate limiter for API endpoints.",
            "complexity": "5",
            "code": '''import time
from typing import Dict

class TokenBucketLimiter:
    """Token bucket rate limiter per client ID."""
    def __init__(self, rate: float = 10.0, capacity: int = 20):
        self.rate = rate          # tokens per second
        self.capacity = capacity
        self.buckets: Dict[str, Dict] = {}

    def _refill(self, client: str):
        now = time.time()
        bucket = self.buckets.setdefault(client, {"tokens": self.capacity, "last": now})
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now

    def allow(self, client: str, tokens: int = 1) -> bool:
        self._refill(client)
        bucket = self.buckets[client]
        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return True
        return False

    def remaining(self, client: str) -> float:
        self._refill(client)
        return self.buckets[client]["tokens"]
''',
            "tests": '''import pytest
import time
from auto_skill_ratelimit import TokenBucketLimiter

def test_allow():
    lim = TokenBucketLimiter(rate=10, capacity=5)
    assert lim.allow("alice") is True
    assert lim.allow("alice", tokens=5) is False

def test_refill():
    lim = TokenBucketLimiter(rate=10, capacity=2)
    lim.allow("bob")
    lim.allow("bob")
    assert lim.allow("bob") is False
    time.sleep(0.25)
    assert lim.allow("bob") is True
''',
            "keywords": ["rate limit", "token bucket", "throttle", "api"],
        },
    }

    def __init__(self, use_llm: bool = False, adapter=None):
        self.use_llm = use_llm
        self.adapter = adapter
        self._mock_keys = list(self.MOCK_TEMPLATES.keys())
        self._mock_index = 0

    def generate(self, gap: Dict[str, Any]) -> SkillCandidate:
        """Generate a skill candidate from a gap ticket."""
        if self.use_llm and self.adapter:
            return self._generate_llm(gap)
        return self._generate_mock(gap)

    def _generate_mock(self, gap: Dict[str, Any]) -> SkillCandidate:
        """Round-robin mock generation for offline demo."""
        key = self._mock_keys[self._mock_index % len(self._mock_keys)]
        self._mock_index += 1
        tpl = self.MOCK_TEMPLATES[key]

        return SkillCandidate(
            name=key,
            category=tpl["category"],
            description=tpl["description"],
            complexity=int(tpl["complexity"]),
            code=tpl["code"],
            tests=tpl["tests"],
            keywords=tpl["keywords"],
            parent_task=gap["task"],
        )

    def _generate_llm(self, gap: Dict[str, Any]) -> SkillCandidate:
        """TODO: real LLM prompt engineering."""
        # Placeholder — will call adapter with structured prompt
        return self._generate_mock(gap)


# ---------------------------------------------------------------------------
# Skill Validator (Sandbox)
# ---------------------------------------------------------------------------

class SkillValidator:
    """Validates candidate skill via AST + import + pytest in temp sandbox."""

    def __init__(self, timeout_sec: float = 5.0):
        self.timeout = timeout_sec

    def validate(self, candidate: SkillCandidate) -> float:
        """
        Returns score 0.0–1.0.
        Checks: AST safety → syntax → import → pytest.
        """
        if not candidate.is_safe:
            return 0.0

        score = 0.0

        # 1. AST parse (20%)
        try:
            ast.parse(candidate.code)
            score += 0.2
        except SyntaxError:
            return 0.0

        # 2. Import test in temp module (30%)
        import_ok = self._test_import(candidate)
        if import_ok:
            score += 0.3
        else:
            return score  # dead at 0.2

        # 3. Pytest run (50%)
        pytest_ok = self._test_pytest(candidate)
        if pytest_ok:
            score += 0.5

        candidate.validation_score = score
        return score

    def _test_import(self, candidate: SkillCandidate) -> bool:
        """Try importing generated code as a temporary module."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(candidate.code)
                tmp_path = f.name

            # Add temp dir to path briefly
            tmp_dir = os.path.dirname(tmp_path)
            sys.path.insert(0, tmp_dir)
            try:
                module_name = os.path.basename(tmp_path)[:-3]
                importlib = __import__("importlib")
                mod = importlib.import_module(module_name)
                # Check that module has callable classes/functions
                members = [name for name in dir(mod) if not name.startswith("_")]
                return len(members) > 0
            finally:
                sys.path.remove(tmp_dir)
                os.unlink(tmp_path)
        except Exception:
            return False

    def _test_pytest(self, candidate: SkillCandidate) -> bool:
        """Run candidate tests in isolated temp file."""
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
# Skill Voter (Orbital Consensus)
# ---------------------------------------------------------------------------

class SkillVoter:
    """
    3-agent orbital panel votes on skill acceptance.
    Roles: CodeReviewer, SecurityAuditor, UtilityJudge.
    """

    def __init__(self, n_agents: int = 3):
        self.n_agents = n_agents

    def vote(self, candidate: SkillCandidate) -> Tuple[bool, float]:
        """
        Returns (accepted, consensus_score).
        Accepted if consensus_score >= 0.6 and all agents > 0.3.
        """
        votes = []

        # Agent 0: CodeReviewer — cares about code quality
        code_score = self._score_code(candidate.code)
        votes.append(("CodeReviewer", code_score))

        # Agent 1: SecurityAuditor — cares about safety + tests
        sec_score = 0.3 if candidate.is_safe else 0.0
        sec_score += 0.4 * candidate.validation_score
        sec_score += 0.3 if "pytest" in candidate.tests.lower() else 0.0
        votes.append(("SecurityAuditor", min(sec_score, 1.0)))

        # Agent 2: UtilityJudge — cares about relevance to task
        util_score = self._score_utility(candidate)
        votes.append(("UtilityJudge", util_score))

        candidate.votes = votes

        scores = [s for _, s in votes]
        consensus = sum(scores) / len(scores)
        accepted = consensus >= 0.6 and all(s >= 0.3 for s in scores)

        return accepted, consensus

    def _score_code(self, code: str) -> float:
        score = 0.0
        lines = code.strip().splitlines()
        if len(lines) >= 5:
            score += 0.2
        if 'class ' in code or 'def ' in code:
            score += 0.3
        if '"""' in code or "'''" in code:
            score += 0.2
        if 'typing' in code or '->' in code:
            score += 0.2
        if len(code) < 2000:
            score += 0.1
        return min(score, 1.0)

    def _score_utility(self, candidate: SkillCandidate) -> float:
        score = 0.0
        task_lower = candidate.parent_task.lower()
        for kw in candidate.keywords:
            if kw.lower() in task_lower:
                score += 0.25
        score += 0.2 if candidate.validation_score >= 0.8 else 0.0
        score += 0.1 if candidate.complexity <= 8 else 0.0
        return min(score, 1.0)


# ---------------------------------------------------------------------------
# Skill Registry Evolver (Hebbian + Pruning)
# ---------------------------------------------------------------------------

class SkillRegistryEvolver:
    """Maintains auto-generated skills with Hebbian LTP/LTD and sleep pruning."""

    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}          # name -> metadata
        self.evolution: Dict[str, SkillEvolutionRecord] = {}  # name -> record
        self.candidates_history: List[SkillCandidate] = []

    def integrate(self, candidate: SkillCandidate, accepted: bool):
        """Add accepted skill to registry."""
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
            "birth_time": candidate.birth_time,
        }
        self.evolution[candidate.name] = SkillEvolutionRecord(skill_name=candidate.name)
        self.candidates_history.append(candidate)

    def record_usage(self, skill_name: str, success: bool):
        """Call this after an agent uses the skill."""
        if skill_name in self.evolution:
            self.evolution[skill_name].update(success)
            self.skills[skill_name]["level"] = self.evolution[skill_name].level

    def sleep_consolidation(self) -> List[str]:
        """
        Prune weak/unused skills. Returns list of pruned names.
        Analogous to LTP/LTD pruning in biological sleep.
        """
        pruned = []
        for name, record in list(self.evolution.items()):
            if record.should_prune:
                record.pruned = True
                self.skills.pop(name, None)
                pruned.append(name)
        return pruned

    def get_skill_for_task(self, task: str, min_level: float = 0.05) -> Optional[str]:
        """Find best matching skill for a task."""
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
# AutoSkillEngine — Orchestrator
# ---------------------------------------------------------------------------

class AutoSkillEngine:
    """
    Main entry point.  Usage:
        engine = AutoSkillEngine()
        engine.run_lifecycle(task="Build GraphQL API with caching")
    """

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
        """
        Full cycle: detect → generate → validate → vote → integrate.
        Returns accepted candidate or None.
        """
        if required_keywords is None:
            required_keywords = self._extract_keywords(task)

        # 1. Detect gap
        gap = self.detector.detect(task, required_keywords)
        if gap is None:
            return None
        self.stats["gaps_detected"] += 1
        print(f"    [Gap] {gap['missing_keywords']} in task: {task[:50]}...")

        # 2. Generate
        candidate = self.generator.generate(gap)
        self.stats["generated"] += 1
        print(f"    [Gen] Skill '{candidate.name}' ({candidate.category}, complexity={candidate.complexity})")

        # 3. Validate
        val_score = self.validator.validate(candidate)
        self.stats["validated"] += 1
        print(f"    [Val] Score={val_score:.2f} (safe={candidate.is_safe})")

        # 4. Vote
        accepted, consensus = self.voter.vote(candidate)
        print(f"    [Vote] Consensus={consensus:.2f} → {'ACCEPTED' if accepted else 'REJECTED'}")
        for role, sc in candidate.votes:
            print(f"        {role:20s}: {sc:.2f}")

        # 5. Integrate
        self.registry.integrate(candidate, accepted)
        if accepted:
            self.stats["accepted"] += 1

        return candidate if accepted else None

    def evolve_from_feedback(self, skill_name: str, success: bool):
        """External feedback loop: task succeeded/failed using this skill."""
        self.registry.record_usage(skill_name, success)

    def sleep(self) -> List[str]:
        """Periodic maintenance: prune dead skills."""
        pruned = self.registry.sleep_consolidation()
        self.stats["pruned"] += len(pruned)
        return pruned

    def _extract_keywords(self, task: str) -> List[str]:
        """Naïve keyword extraction from task text."""
        tech_keywords = [
            "graphql", "websocket", "redis", "cache", "rate limit", "jwt", "oauth",
            "docker", "kubernetes", "ci/cd", "pytest", "sql", "postgres", "mongo",
            "react", "vue", "angular", "fastapi", "flask", "django", "async",
            "tensorflow", "pytorch", "llm", "embedding", "vector", "kafka", "queue",
        ]
        found = [kw for kw in tech_keywords if kw.lower() in task.lower()]
        # If nothing found, treat every word as potential keyword
        if not found:
            found = [w for w in re.findall(r"[A-Za-z]+", task) if len(w) > 3]
        return found


# ---------------------------------------------------------------------------
# Helpers for MolecularSystem integration
# ---------------------------------------------------------------------------

def attach_to_system(system, use_llm: bool = False, adapter=None) -> AutoSkillEngine:
    """
    Attach AutoSkillEngine to a MolecularSystem instance.
    Adds `system.auto_skill` attribute.
    """
    engine = AutoSkillEngine(use_llm=use_llm, adapter=adapter)
    system.auto_skill = engine
    return engine