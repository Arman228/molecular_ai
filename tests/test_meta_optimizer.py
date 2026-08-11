#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core.meta_optimizer — L2 self-tuning.
"""

import pytest

from core.meta_optimizer import (
    HyperConfig,
    MetaResult,
    TaskProfiler,
    HyperparameterSpace,
    MetaObjective,
    MetaOptimizer,
)


class TestHyperConfig:
    def test_defaults(self):
        cfg = HyperConfig()
        assert cfg.dt == 0.05
        assert cfg.noise == 0.01
        assert cfg.k_sparse == 4

    def test_to_dict(self):
        cfg = HyperConfig(dt=0.1, noise=0.02)
        d = cfg.to_dict()
        assert d["dt"] == 0.1
        assert d["noise"] == 0.02

    def test_copy(self):
        cfg = HyperConfig(dt=0.1)
        cpy = cfg.copy()
        assert cpy.dt == 0.1
        cpy.dt = 0.2
        assert cfg.dt == 0.1


class TestTaskProfiler:
    def test_simple_task(self):
        p = TaskProfiler()
        profile = p.profile("JWT auth", ["jwt"])
        assert profile["complexity"] == 4
        assert profile["regime"] == "LINEAR"

    def test_complex_task(self):
        p = TaskProfiler()
        profile = p.profile("LLM pipeline", ["llm", "kubernetes"])
        assert profile["complexity"] == 9
        assert profile["regime"] == "DIVERGENT"

    def test_unknown_keyword(self):
        p = TaskProfiler()
        profile = p.profile("Foo bar", ["unknown"])
        assert profile["complexity"] == 5
        assert profile["regime"] == "CRITICAL"


class TestHyperparameterSpace:
    def test_sample_count(self):
        space = HyperparameterSpace({"complexity": 5})
        configs = space.sample(n=5)
        assert len(configs) == 5

    def test_sample_ranges(self):
        space = HyperparameterSpace({"complexity": 3})
        cfg = space.sample(n=1)[0]
        assert 0.03 <= cfg.dt <= 0.06
        assert 0.001 <= cfg.noise <= 0.01
        assert 3 <= cfg.n_agents <= 6

    def test_complex_sample_ranges(self):
        space = HyperparameterSpace({"complexity": 9})
        cfg = space.sample(n=1)[0]
        assert 0.01 <= cfg.dt <= 0.03
        assert 0.01 <= cfg.noise <= 0.05
        assert 8 <= cfg.n_agents <= 15

    def test_grid_size(self):
        space = HyperparameterSpace({"complexity": 5})
        grid = space.grid(resolution=3)
        assert len(grid) == 27


class TestMetaObjective:
    def test_evaluate_returns_result(self):
        obj = MetaObjective()
        cfg = HyperConfig(n_agents=5, steps=200)
        result = obj.evaluate(cfg)
        assert isinstance(result, MetaResult)
        assert 0.0 <= result.sync_r <= 1.0
        assert 0.0 <= result.stability <= 1.0
        assert result.steps_to_sync > 0
        assert 0.0 <= result.score <= 1.0

    def test_higher_coupling_better_sync(self):
        obj = MetaObjective()
        low = obj.evaluate(HyperConfig(coupling_mult=1.0, steps=300))
        high = obj.evaluate(HyperConfig(coupling_mult=4.0, steps=300))
        assert high.sync_r >= low.sync_r or high.score >= low.score

    def test_simulate_deterministic_with_seed(self):
        import random
        random.seed(42)
        obj1 = MetaObjective()
        r1, s1, st1 = obj1._simulate(HyperConfig(n_agents=5, steps=100))
        random.seed(42)
        obj2 = MetaObjective()
        r2, s2, st2 = obj2._simulate(HyperConfig(n_agents=5, steps=100))
        assert abs(r1 - r2) < 1e-9
        assert s1 == s2


class TestMetaOptimizer:
    def test_optimize_returns_config(self):
        opt = MetaOptimizer(n_samples=5)
        cfg = opt.optimize("GraphQL API", ["graphql"])
        assert isinstance(cfg, HyperConfig)
        assert cfg.dt > 0

    def test_optimize_improves_over_baseline(self):
        opt = MetaOptimizer(n_samples=10)
        baseline = HyperConfig()
        obj = MetaObjective()
        baseline_res = obj.evaluate(baseline)
        best_cfg = opt.optimize("LLM pipeline", ["llm", "kubernetes"])
        best_res = obj.evaluate(best_cfg)
        assert best_res.score >= baseline_res.score or best_res.sync_r >= baseline_res.sync_r

    def test_recommend_structure(self):
        opt = MetaOptimizer(n_samples=4)
        rec = opt.recommend("Redis cache", ["redis"])
        assert "profile" in rec
        assert "config" in rec
        assert rec["profile"]["complexity"] == 5

    def test_history_accumulates(self):
        opt = MetaOptimizer(n_samples=3)
        opt.optimize("Task A", ["jwt"])
        opt.optimize("Task B", ["graphql"])
        assert len(opt.history) == 6

    def test_grid_mode(self):
        opt = MetaOptimizer(n_samples=0, use_grid=True)
        cfg = opt.optimize("Test", ["test"])
        assert isinstance(cfg, HyperConfig)