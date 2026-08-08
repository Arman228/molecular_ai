# -*- coding: utf-8 -*-
"""
AttentionModulator — фокусировка processing.
"""

import math
from typing import List, Dict


class AttentionModulator:
    def __init__(self, n_nodes: int = 2):
        self.n_nodes = n_nodes
        self.salience: List[float] = [0.0] * n_nodes

    def compute_salience(self, phases: List[float], energies: List[float]) -> List[float]:
        if not phases:
            return self.salience
        mean_p = sum(phases) / len(phases)
        var = sum((p - mean_p) ** 2 for p in phases) / len(phases)
        mean_e = sum(energies) / len(energies) if energies else 0.0
        self.salience[0] = math.tanh(var * 2.0)
        self.salience[1] = math.tanh(mean_e)
        return self.salience.copy()

    def modulate_coupling(self, base_K: float) -> float:
        s = sum(self.salience) / len(self.salience) if self.salience else 0.0
        return base_K * (1.0 + 0.5 * s)

    def get_state(self) -> Dict:
        return {"salience": self.salience.copy()}
