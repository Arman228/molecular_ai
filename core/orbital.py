# -*- coding: utf-8 -*-
"""
Orbital — общее поле и иерархические уровни.
"""

import math
from typing import List, Dict
from core.utils import mean, normalize_angle, HAS_NUMPY

if HAS_NUMPY:
    import numpy as np


class SharedOrbital:
    def __init__(self, dim: int = 16):
        self.dim = dim
        self.field: List[float] = [0.0] * dim
        self.history: List[List[float]] = []
        self.mean_phase: float = 0.0

    def update(self, vectors: List[List[float]], phases: List[float]) -> None:
        if not vectors:
            return
        n = len(vectors)
        self.field = [sum(v[i] for v in vectors) / n for i in range(self.dim)]
        self.mean_phase = self._compute_mean_phase(phases)
        self.history.append(self.field.copy())
        if len(self.history) > 1000:
            self.history.pop(0)

    def _compute_mean_phase(self, phases: List[float]) -> float:
        if not phases:
            return 0.0
        x = sum(math.cos(p) for p in phases) / len(phases)
        y = sum(math.sin(p) for p in phases) / len(phases)
        return math.atan2(y, x)

    def get_field(self) -> List[float]:
        return self.field.copy()

    def get_mean_phase(self) -> float:
        return self.mean_phase


class OrbitalLayer:
    def __init__(self, name: str, coupling: float, decay: float, dim: int = 16):
        self.name = name
        self.coupling = coupling
        self.decay = decay
        self.orbital = SharedOrbital(dim=dim)

    def update(self, vectors: List[List[float]], phases: List[float]) -> None:
        self.orbital.update(vectors, phases)

    def influence(self, agent_phase: float, agent_omega: float) -> float:
        phi = self.orbital.get_mean_phase()
        return self.coupling * math.sin(phi - agent_phase)

    def get_state(self) -> Dict:
        return {
            "name": self.name,
            "coupling": self.coupling,
            "decay": self.decay,
            "mean_phase": self.orbital.get_mean_phase(),
        }


class HierarchicalOrbital:
    LAYERS_CONFIG = [
        ("Gamma", 3.5, 0.30),
        ("Beta", 2.0, 0.60),
        ("Alpha", 1.0, 0.85),
        ("Delta", 0.5, 0.97),
    ]

    def __init__(self, dim: int = 16):
        self.layers: List[OrbitalLayer] = [
            OrbitalLayer(name, c, d, dim) for name, c, d in self.LAYERS_CONFIG
        ]

    def update(self, vectors: List[List[float]], phases: List[float]) -> None:
        for layer in self.layers:
            layer.update(vectors, phases)

    def total_influence(self, agent_phase: float, agent_omega: float) -> float:
        total = 0.0
        for layer in self.layers:
            total += layer.decay * layer.influence(agent_phase, agent_omega)
        return total

    def get_state(self) -> List[Dict]:
        return [layer.get_state() for layer in self.layers]
