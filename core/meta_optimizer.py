#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaOptimizer v1 — L2 self-tuning for Molecular AI.
Platform adapts its own hyperparameters (dt, noise, coupling, topology)
to maximize orbital sync quality per task complexity.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import cos, sin
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class HyperConfig:
    """A candidate hyperparameter configuration."""
    dt: float = 0.05
    noise: float = 0.01
    k_sparse: int = 4
    exc_ratio: float = 0.90
    coupling_mult: float = 2.5
    n_agents: int = 5
    steps: int = 400

    def to_dict(self) -> Dict[str, float]:
        return {
            "dt": self.dt,
            "noise": self.noise,
            "k_sparse": self.k_sparse,
            "exc_ratio": self.exc_ratio,
            "coupling_mult": self.coupling_mult,
            "n_agents": self.n_agents,
            "steps": self.steps,
        }

    def copy(self) -> HyperConfig:
        return HyperConfig(**self.to_dict())


@dataclass
class MetaResult:
    """Outcome of evaluating a config."""
    config: HyperConfig
    sync_r: float
    steps_to_sync: int
    stability: float          # low variance = high stability
    score: float = 0.0


# ---------------------------------------------------------------------------
# Task Profiler
# ---------------------------------------------------------------------------

class TaskProfiler:
    """Infers task complexity from keywords / skill requirements."""

    COMPLEXITY_MAP = {
        "graphql": 7, "websocket": 6, "redis": 5, "cache": 5,
        "rate limit": 5, "jwt": 4, "oauth": 5, "docker": 6,
        "kubernetes": 8, "ci/cd": 5, "pytest": 3, "sql": 4,
        "postgres": 5, "mongo": 5, "react": 6, "vue": 5,
        "angular": 6, "fastapi": 5, "flask": 4, "django": 6,
        "async": 6, "tensorflow": 8, "pytorch": 8, "llm": 9,
        "embedding": 7, "vector": 6, "kafka": 7, "queue": 5,
    }

    def profile(self, task: str, keywords: List[str]) -> Dict[str, any]:
        """Returns task profile with inferred complexity and recommended regime."""
        scores = []
        for kw in keywords:
            scores.append(self.COMPLEXITY_MAP.get(kw.lower(), 5))
        complexity = max(scores) if scores else 5

        if complexity <= 4:
            regime = "LINEAR"
        elif complexity <= 7:
            regime = "CRITICAL"
        else:
            regime = "DIVERGENT"

        return {
            "task": task,
            "complexity": complexity,
            "regime": regime,
            "keywords": keywords,
        }


# ---------------------------------------------------------------------------
# Hyperparameter Space
# ---------------------------------------------------------------------------

class HyperparameterSpace:
    """Defines searchable ranges for each hyperparameter."""

    def __init__(self, profile: Dict[str, any]):
        self.profile = profile
        self.complexity = profile["complexity"]

    def sample(self, n: int = 1) -> List[HyperConfig]:
        """Generate n random configs adapted to task complexity."""
        configs = []
        for _ in range(n):
            cfg = HyperConfig()
            if self.complexity <= 4:
                cfg.dt = random.uniform(0.03, 0.06)
                cfg.noise = random.uniform(0.001, 0.01)
                cfg.k_sparse = random.randint(3, 5)
                cfg.exc_ratio = random.uniform(0.85, 0.95)
                cfg.coupling_mult = random.uniform(2.0, 3.5)
                cfg.n_agents = random.randint(3, 6)
                cfg.steps = random.randint(200, 400)
            elif self.complexity <= 7:
                cfg.dt = random.uniform(0.02, 0.05)
                cfg.noise = random.uniform(0.005, 0.02)
                cfg.k_sparse = random.randint(4, 7)
                cfg.exc_ratio = random.uniform(0.80, 0.90)
                cfg.coupling_mult = random.uniform(1.5, 2.5)
                cfg.n_agents = random.randint(5, 10)
                cfg.steps = random.randint(300, 600)
            else:
                cfg.dt = random.uniform(0.01, 0.03)
                cfg.noise = random.uniform(0.01, 0.05)
                cfg.k_sparse = random.randint(5, 9)
                cfg.exc_ratio = random.uniform(0.70, 0.85)
                cfg.coupling_mult = random.uniform(1.0, 2.0)
                cfg.n_agents = random.randint(8, 15)
                cfg.steps = random.randint(400, 800)
            configs.append(cfg)
        return configs

    def grid(self, resolution: int = 3) -> List[HyperConfig]:
        """Exhaustive grid over key axes (dt × noise × coupling)."""
        configs = []
        dt_vals = [0.01, 0.03, 0.05] if resolution <= 3 else [0.01, 0.02, 0.03, 0.05, 0.07]
        noise_vals = [0.001, 0.01, 0.03] if resolution <= 3 else [0.001, 0.005, 0.01, 0.02, 0.04]
        coupling_vals = [1.5, 2.5, 3.5] if resolution <= 3 else [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

        for dt in dt_vals:
            for noise in noise_vals:
                for cm in coupling_vals:
                    cfg = HyperConfig(dt=dt, noise=noise, coupling_mult=cm)
                    if self.complexity <= 4:
                        cfg.k_sparse = 4
                        cfg.n_agents = 5
                    elif self.complexity <= 7:
                        cfg.k_sparse = 6
                        cfg.n_agents = 8
                    else:
                        cfg.k_sparse = 8
                        cfg.n_agents = 12
                    configs.append(cfg)
        return configs


# ---------------------------------------------------------------------------
# Meta Objective
# ---------------------------------------------------------------------------

class MetaObjective:
    """Evaluates a hyperparameter config by running a mini orbital simulation."""

    def __init__(self, target_sync_r: float = 0.80, max_steps: int = 1000):
        self.target_sync_r = target_sync_r
        self.max_steps = max_steps

    def evaluate(self, config: HyperConfig) -> MetaResult:
        sync_r, steps, stability = self._simulate(config)

        score = 0.0
        score += 0.5 * sync_r
        score += 0.3 * (1.0 - steps / self.max_steps)
        score += 0.2 * stability

        return MetaResult(
            config=config,
            sync_r=sync_r,
            steps_to_sync=steps,
            stability=stability,
            score=score,
        )

    def _simulate(self, cfg: HyperConfig) -> Tuple[float, int, float]:
        n = cfg.n_agents
        dt = cfg.dt
        noise = cfg.noise
        coupling = cfg.coupling_mult * 0.5 / n

        phases = [random.uniform(0, 2 * 3.1415926535) for _ in range(n)]

        adj = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = min(abs(i - j), n - abs(i - j))
                    if dist <= cfg.k_sparse // 2 or random.random() < 0.15:
                        adj[i][j] = 1.0

        sync_history = []
        steps_to_target = cfg.steps

        for step in range(cfg.steps):
            new_phases = phases[:]
            for i in range(n):
                d_omega = 0.0
                for j in range(n):
                    if adj[i][j]:
                        d_omega += coupling * (phases[j] - phases[i])
                d_omega += random.gauss(0, noise)
                new_phases[i] = (phases[i] + d_omega * dt) % (2 * 3.1415926535)
            phases = new_phases

            sx = sum(cos(p) for p in phases)
            sy = sum(sin(p) for p in phases)
            r = ((sx / n) ** 2 + (sy / n) ** 2) ** 0.5
            sync_history.append(r)

            if r >= self.target_sync_r and steps_to_target == cfg.steps:
                steps_to_target = step + 1

        final_r = sync_history[-1] if sync_history else 0.0
        stability = 1.0 - (sum((r - final_r) ** 2 for r in sync_history[-50:]) / max(len(sync_history[-50:]), 1)) ** 0.5
        stability = max(0.0, min(1.0, stability))

        return final_r, steps_to_target, stability


# ---------------------------------------------------------------------------
# Meta Optimizer
# ---------------------------------------------------------------------------

class MetaOptimizer:
    """Searches hyperparameter space to find best config for a given task."""

    def __init__(self, n_samples: int = 12, use_grid: bool = False):
        self.n_samples = n_samples
        self.use_grid = use_grid
        self.objective = MetaObjective()
        self.history: List[MetaResult] = []

    def optimize(self, task: str, keywords: List[str]) -> HyperConfig:
        profiler = TaskProfiler()
        profile = profiler.profile(task, keywords)

        space = HyperparameterSpace(profile)
        if self.use_grid:
            candidates = space.grid(resolution=3)
        else:
            candidates = space.sample(n=self.n_samples)

        best_result: Optional[MetaResult] = None

        print(f"    [Meta] Profiling task: complexity={profile['complexity']}, regime={profile['regime']}")
        print(f"    [Meta] Searching {len(candidates)} configs...")

        for cfg in candidates:
            result = self.objective.evaluate(cfg)
            self.history.append(result)
            if best_result is None or result.score > best_result.score:
                best_result = result

        assert best_result is not None
        print(f"    [Meta] Best score={best_result.score:.3f}  sync_r={best_result.sync_r:.3f}  steps={best_result.steps_to_sync}")
        print(f"    [Meta] Config: dt={best_result.config.dt}, noise={best_result.config.noise}, "
              f"k={best_result.config.k_sparse}, agents={best_result.config.n_agents}, "
              f"coupling={best_result.config.coupling_mult:.1f}")

        return best_result.config

    def recommend(self, task: str, keywords: List[str]) -> Dict[str, any]:
        profiler = TaskProfiler()
        profile = profiler.profile(task, keywords)
        best_cfg = self.optimize(task, keywords)
        return {
            "profile": profile,
            "config": best_cfg.to_dict(),
            "history_size": len(self.history),
        }


# ---------------------------------------------------------------------------
# Integration with AutoSkillEngine
# ---------------------------------------------------------------------------

def attach_optimizer_to_engine(engine) -> MetaOptimizer:
    """Attach MetaOptimizer to AutoSkillEngine."""
    opt = MetaOptimizer(n_samples=8, use_grid=False)
    engine.meta_optimizer = opt
    return opt