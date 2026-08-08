# -*- coding: utf-8 -*-
"""
Hebbian plasticity, meta-plasticity.
"""

import math
import random
from typing import List, Dict, Tuple
from core.utils import clip


class SparseHebbianPlasticity:
    def __init__(self, n_agents: int, k_sparse: int = 4):
        self.n = n_agents
        self.k = k_sparse
        self.W: Dict[Tuple[int, int], float] = {}
        self._init_connections()

    def _init_connections(self) -> None:
        for i in range(self.n):
            targets = random.sample(range(self.n), min(self.k, self.n))
            for j in targets:
                if i == j:
                    continue
                self.W[(i, j)] = random.uniform(0.1, 0.5)

    def update(self, phases: List[float], eta: float = 0.01, threshold: float = 0.5) -> None:
        for (i, j), w in list(self.W.items()):
            delta = eta * (math.cos(phases[j] - phases[i]) - threshold)
            w_new = clip(w + delta, 0.0, 2.0)
            self.W[(i, j)] = w_new
            if w_new < 0.15:
                self._rewire(i, j, phases)

    def _rewire(self, i: int, old_j: int, phases: List[float]) -> None:
        del self.W[(i, old_j)]
        candidates = [x for x in range(self.n) if x != i and (i, x) not in self.W]
        if candidates:
            new_j = random.choice(candidates)
            self.W[(i, new_j)] = 0.2

    def sleep_consolidation(self, factor: float = 1.2) -> None:
        for key in list(self.W.keys()):
            w = self.W[key]
            if w > 1.2:
                self.W[key] = min(2.0, w * factor)
            elif w < 0.3:
                self.W[key] = w * 0.6
            if self.W[key] < 0.15:
                del self.W[key]

    def get_weights(self) -> Dict[Tuple[int, int], float]:
        return self.W.copy()


class MetaPlasticity:
    def __init__(self, base_eta: float = 0.01):
        self.base_eta = base_eta
        self.sync_history: List[float] = []

    def get_eta(self, current_r: float) -> float:
        self.sync_history.append(current_r)
        if len(self.sync_history) > 50:
            self.sync_history.pop(0)
        mean_sync = sum(self.sync_history) / len(self.sync_history) if self.sync_history else 0.0
        if mean_sync > 0.9:
            return self.base_eta * 0.5
        elif mean_sync < 0.5:
            return self.base_eta * 2.0
        return self.base_eta
