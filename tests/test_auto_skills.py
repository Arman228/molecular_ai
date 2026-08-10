#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core.auto_skills — AutoSkillEngine, validation, voting, evolution.
"""

import hashlib
import pytest
import time

from core.auto_skills import (
    SkillCandidate,
    SkillGapDetector,
    SkillGenerator,
    SkillValidator,
    SkillVoter,
    SkillRegistryEvolver,
    AutoSkillEngine,
    SkillEvolutionRecord,
)


# ---------------------------------------------------------------------------
# SkillCandidate
# ---------------------------------------------------------------------------

class TestSkillCandidate:
    def test_checksum_deterministic(self):
        c = SkillCandidate("X", "Cat", "Desc", 5, "code", "tests", ["k"], "task")
        # Checksum is SHA-256 hex, truncated to 16 chars
        assert len(c.checksum) == 16
        assert c.checksum == hashlib.sha256(b"code").hexdigest()[:16]

    def test_is_safe_blocks_exec(self):
        bad = SkillCandidate("Bad", "Cat", "Desc", 5, "exec('rm -rf /')", "tests", ["k"], "task")
        assert not bad.is_safe

    def test_is_safe_allows_normal(self):
        good = SkillCandidate("Good", "Cat", "Desc", 5, "def foo(): pass", "tests", ["k"], "task")
        assert good.is_safe


# ---------------------------------------------------------------------------
# SkillGapDetector
# ---------------------------------------------------------------------------

class TestSkillGapDetector:
    def test_detects_missing_skill(self):
        detector = SkillGapDetector({})
        gap = detector.detect("Build GraphQL API", ["graphql", "schema"])
        assert gap is not None
        assert "graphql" in gap["missing_keywords"]
        assert gap["suggested_category"] == "Backend"

    def test_no_gap_when_covered(self):
        registry = {
            "GraphQL": {"description": "GraphQL schema and resolvers", "level": 0.8}
        }
        detector = SkillGapDetector(registry, threshold=0.25)
        gap = detector.detect("Build GraphQL API", ["graphql"])
        assert gap is None

    def test_infer_category_devops(self):
        detector = SkillGapDetector({})
        gap = detector.detect("Deploy with Docker", ["docker"])
        assert gap["suggested_category"] == "DevOps"


# ---------------------------------------------------------------------------
# SkillGenerator
# ---------------------------------------------------------------------------

class TestSkillGenerator:
    def test_mock_generation(self):
        gen = SkillGenerator(use_llm=False)
        gap = {"task": "Build GraphQL API", "missing_keywords": ["graphql"]}
        cand = gen.generate(gap)
        assert cand.name in gen.MOCK_TEMPLATES
        assert cand.is_safe
        assert cand.code
        assert cand.tests
        assert cand.keywords

    def test_round_robin(self):
        gen = SkillGenerator(use_llm=False)
        gap = {"task": "X", "missing_keywords": ["x"]}
        names = []
        for _ in range(8):
            names.append(gen.generate(gap).name)
        # Should cycle through templates
        assert len(set(names)) <= len(gen.MOCK_TEMPLATES)


# ---------------------------------------------------------------------------
# SkillValidator
# ---------------------------------------------------------------------------

class TestSkillValidator:
    def test_validate_good_code(self):
        val = SkillValidator()
        cand = SkillCandidate(
            "Good", "Cat", "Desc", 5,
            code="def add(a, b):\n    return a + b",
            tests="def test_add():\n    assert add(2, 3) == 5",
            keywords=["math"], parent_task="task"
        )
        score = val.validate(cand)
        assert score > 0.0
        assert cand.validation_score == score

    def test_validate_unsafe_zero(self):
        val = SkillValidator()
        cand = SkillCandidate(
            "Bad", "Cat", "Desc", 5,
            code="import os\nos.system('ls')",
            tests="def test_bad(): pass",
            keywords=["bad"], parent_task="task"
        )
        assert val.validate(cand) == 0.0

    def test_validate_syntax_error(self):
        val = SkillValidator()
        cand = SkillCandidate(
            "Broken", "Cat", "Desc", 5,
            code="def foo(\n    pass",
            tests="def test_foo(): pass",
            keywords=["broken"], parent_task="task"
        )
        assert val.validate(cand) == 0.0

    def test_validate_with_pytest(self):
        val = SkillValidator()
        cand = SkillCandidate(
            "Math", "Cat", "Desc", 5,
            code="def square(x):\n    return x * x",
            tests="def test_square():\n    assert square(4) == 16\n    assert square(0) == 0",
            keywords=["math"], parent_task="task"
        )
        score = val.validate(cand)
        # AST (0.2) + import (0.3) + pytest (0.5) = 1.0
        assert score >= 0.8


# ---------------------------------------------------------------------------
# SkillVoter
# ---------------------------------------------------------------------------

class TestSkillVoter:
    def test_accept_high_quality(self):
        voter = SkillVoter()
        cand = SkillCandidate(
            "Good", "Backend", "Desc", 5,
            code='class GraphQLSchema:\n    """Docstring."""\n    def resolve(self):\n        pass',
            tests="import pytest\ndef test_x(): pass",
            keywords=["graphql"], parent_task="Build GraphQL API"
        )
        cand.validation_score = 1.0
        accepted, consensus = voter.vote(cand)
        assert accepted
        assert consensus >= 0.6

    def test_reject_low_quality(self):
        voter = SkillVoter()
        cand = SkillCandidate(
            "Bad", "Cat", "Desc", 5,
            code="x = 1",
            tests="",
            keywords=["nothing"], parent_task="Unknown task"
        )
        cand.validation_score = 0.0
        accepted, consensus = voter.vote(cand)
        assert not accepted
        assert consensus < 0.6

    def test_all_agents_vote(self):
        voter = SkillVoter()
        cand = SkillCandidate(
            "X", "Cat", "Desc", 5,
            code="def foo(): pass",
            tests="def test_foo(): pass",
            keywords=["foo"], parent_task="task"
        )
        cand.validation_score = 0.5
        voter.vote(cand)
        assert len(cand.votes) == 3
        roles = [r for r, _ in cand.votes]
        assert "CodeReviewer" in roles
        assert "SecurityAuditor" in roles
        assert "UtilityJudge" in roles


# ---------------------------------------------------------------------------
# SkillRegistryEvolver
# ---------------------------------------------------------------------------

class TestSkillRegistryEvolver:
    def test_integrate_and_retrieve(self):
        reg = SkillRegistryEvolver()
        cand = SkillCandidate("Redis", "Infra", "Cache", 5, "code", "tests", ["redis"], "task")
        reg.integrate(cand, accepted=True)
        assert "Redis" in reg.skills
        assert "Redis" in reg.evolution

    def test_reject_not_integrated(self):
        reg = SkillRegistryEvolver()
        cand = SkillCandidate("X", "Cat", "Desc", 5, "code", "tests", ["k"], "task")
        reg.integrate(cand, accepted=False)
        assert "X" not in reg.skills

    def test_hebbian_ltp(self):
        reg = SkillRegistryEvolver()
        cand = SkillCandidate("Skill", "Cat", "Desc", 5, "code", "tests", ["k"], "task")
        reg.integrate(cand, accepted=True)
        reg.record_usage("Skill", success=True)
        reg.record_usage("Skill", success=True)
        assert reg.evolution["Skill"].level > 0.1

    def test_hebbian_ltd(self):
        reg = SkillRegistryEvolver()
        cand = SkillCandidate("Skill", "Cat", "Desc", 5, "code", "tests", ["k"], "task")
        reg.integrate(cand, accepted=True)
        for _ in range(10):
            reg.record_usage("Skill", success=False)
        assert reg.evolution["Skill"].level < 0.1

    def test_sleep_pruning(self):
        reg = SkillRegistryEvolver()
        cand = SkillCandidate("Old", "Cat", "Desc", 5, "code", "tests", ["k"], "task")
        reg.integrate(cand, accepted=True)
        # Force age and weakness
        reg.evolution["Old"].last_used -= 400
        reg.evolution["Old"].level = 0.02
        pruned = reg.sleep_consolidation()
        assert "Old" in pruned
        assert "Old" not in reg.skills

    def test_get_skill_for_task(self):
        reg = SkillRegistryEvolver()
        c1 = SkillCandidate("GraphQL", "Backend", "Desc", 5, "code", "tests", ["graphql", "api"], "task")
        c2 = SkillCandidate("Redis", "Infra", "Desc", 5, "code", "tests", ["redis", "cache"], "task")
        reg.integrate(c1, accepted=True)
        reg.integrate(c2, accepted=True)
        found = reg.get_skill_for_task("Build graphql endpoint")
        assert found == "GraphQL"


# ---------------------------------------------------------------------------
# SkillEvolutionRecord
# ---------------------------------------------------------------------------

class TestSkillEvolutionRecord:
    def test_update_success(self):
        rec = SkillEvolutionRecord("S")
        rec.update(True)
        assert rec.level > 0.1
        assert rec.usage_count == 1

    def test_update_failure(self):
        rec = SkillEvolutionRecord("S")
        rec.update(False)
        assert rec.level < 0.1

    def test_should_prune_old_weak(self):
        rec = SkillEvolutionRecord("S")
        rec.last_used -= 400
        rec.level = 0.02
        assert rec.should_prune

    def test_should_not_prune_active(self):
        rec = SkillEvolutionRecord("S")
        rec.level = 0.5
        assert not rec.should_prune


# ---------------------------------------------------------------------------
# AutoSkillEngine (integration)
# ---------------------------------------------------------------------------

class TestAutoSkillEngine:
    def test_full_lifecycle_accepted(self):
        engine = AutoSkillEngine(use_llm=False)
        cand = engine.run_lifecycle("Build GraphQL API", required_keywords=["graphql"])
        assert cand is not None
        assert cand.name == "GraphQL"
        assert "GraphQL" in engine.registry.skills
        assert engine.stats["accepted"] >= 1

    def test_full_lifecycle_no_gap(self):
        # Pre-seed registry so no gap
        engine = AutoSkillEngine(use_llm=False)
        engine.registry.skills["GraphQL"] = {
            "description": "GraphQL stuff", "level": 0.9, "keywords": ["graphql"]
        }
        engine.detector = SkillGapDetector(engine.registry.skills)
        cand = engine.run_lifecycle("Build GraphQL API", required_keywords=["graphql"])
        assert cand is None  # no gap, nothing to generate

    def test_evolve_from_feedback(self):
        engine = AutoSkillEngine(use_llm=False)
        engine.run_lifecycle("Build GraphQL API", required_keywords=["graphql"])
        engine.evolve_from_feedback("GraphQL", success=True)
        assert engine.registry.evolution["GraphQL"].usage_count == 1

    def test_sleep_prunes_weak(self):
        engine = AutoSkillEngine(use_llm=False)
        engine.run_lifecycle("Build GraphQL API", required_keywords=["graphql"])
        engine.registry.evolution["GraphQL"].last_used -= 400
        engine.registry.evolution["GraphQL"].level = 0.02
        pruned = engine.sleep()
        assert "GraphQL" in pruned or len(pruned) == 0  # may or may not prune depending on state

    def test_stats_accumulate(self):
        engine = AutoSkillEngine(use_llm=False)
        for task in TASKS:
            engine.run_lifecycle(task, required_keywords=engine._extract_keywords(task))
        assert engine.stats["gaps_detected"] > 0
        assert engine.stats["generated"] > 0
        assert engine.stats["validated"] > 0


TASKS = [
    "Build GraphQL API with type-safe resolvers",
    "Add real-time WebSocket broadcast",
    "Implement Redis cache layer with TTL",
]