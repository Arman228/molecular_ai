#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensor Fusion Layer for Molecular AI.
Two-pass median + per-axis reputation for robust multi-dimensional consensus.
"""

import random
from typing import List, Tuple, Dict


def median(values: List[float]) -> float:
    """Compute median of a list."""
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def mad(values: List[float], med: float = None) -> float:
    """Compute Median Absolute Deviation."""
    if med is None:
        med = median(values)
    abs_dev = [abs(v - med) for v in values]
    s = sorted(abs_dev)
    n = len(s)
    result = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    return result if result > 0 else 0.001


def two_pass_median_filter(values: List[float], threshold: float = 2.0) -> List[int]:
    """
    Two-pass median filter.
    Returns indices of values that pass both passes.
    Breakdown point ~50% outliers.
    """
    n = len(values)
    if n < 3:
        return list(range(n))

    # Pass 1: rough median on all
    m1 = median(values)
    d1 = mad(values, m1)
    kept1 = [i for i, v in enumerate(values) if abs(v - m1) <= threshold * d1]
    if len(kept1) < 3:
        return kept1

    # Pass 2: refined median on kept1
    kept_vals = [values[i] for i in kept1]
    m2 = median(kept_vals)
    d2 = mad(kept_vals, m2)
    kept2 = [i for i in kept1 if abs(values[i] - m2) <= threshold * d2]
    return kept2 if len(kept2) >= 3 else kept1


def iqr_bounds(values: List[float], k: float = 1.5) -> Tuple[float, float]:
    """Return (lower, upper) bounds via IQR rule."""
    s = sorted(values)
    n = len(s)
    if n < 4:
        return min(values) - 0.1, max(values) + 0.1
    q1 = s[n // 4]
    q3 = s[3 * n // 4]
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def robust_consensus_iqr(values: List[float], k: float = 1.5) -> Tuple[float, List[int]]:
    """IQR-based outlier rejection with iterative refinement."""
    remaining = list(range(len(values)))
    for _ in range(2):
        vals = [values[i] for i in remaining]
        lower, upper = iqr_bounds(vals, k)
        new_remaining = [i for i in remaining if lower <= values[i] <= upper]
        if len(new_remaining) == len(remaining) or len(new_remaining) < 3:
            break
        remaining = new_remaining
    consensus = sum(values[i] for i in remaining) / len(remaining)
    return consensus, remaining


class PerAxisReputation:
    """
    Per-axis reputation tracker.
    Each agent has separate reputation per dimension.
    """

    def __init__(self, n_agents: int, n_dims: int, window: int = 50, recent: int = 15):
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.window = window
        self.recent = recent
        self.reputation = [[1.0 for _ in range(n_dims)] for _ in range(n_agents)]
        self.history = [[[] for _ in range(n_dims)] for _ in range(n_agents)]

    def update(self, dim_idx: int, kept_indices: List[int]):
        """Update reputation for one dimension based on which agents were kept."""
        kept_set = set(kept_indices)
        for i in range(self.n_agents):
            self.history[i][dim_idx].append(i in kept_set)
            if len(self.history[i][dim_idx]) > self.window:
                self.history[i][dim_idx].pop(0)
            hist = self.history[i][dim_idx]
            recent = hist[-self.recent:] if len(hist) >= self.recent else hist
            self.reputation[i][dim_idx] = sum(recent) / len(recent) if recent else 1.0

    def pre_filter(self, dim_idx: int, min_rep: float = 0.5) -> List[int]:
        """Return indices of agents with reputation >= min_rep for this dimension."""
        return [i for i in range(self.n_agents) if self.reputation[i][dim_idx] >= min_rep]

    def get_weights(self, dim_idx: int) -> List[float]:
        """Return normalized weights for all agents on this dimension."""
        reps = [max(self.reputation[i][dim_idx], 0.1) for i in range(self.n_agents)]
        total = sum(reps)
        return [r / total for r in reps]

    def get_matrix(self) -> List[List[float]]:
        """Return full reputation matrix [agents x dimensions]."""
        return [row[:] for row in self.reputation]


class SensorFusionLayer:
    """
    Multi-dimensional sensor fusion with two-pass median + per-axis reputation.
    """

    def __init__(
        self,
        n_agents: int,
        dimensions: List[Dict],
        threshold: float = 2.0,
        min_rep: float = 0.5,
        reputation_window: int = 50,
    ):
        self.n_agents = n_agents
        self.dimensions = dimensions
        self.n_dims = len(dimensions)
        self.threshold = threshold
        self.min_rep = min_rep
        self.reputation = PerAxisReputation(n_agents, self.n_dims, window=reputation_window)

    def process_dimension(self, values: List[float], dim_idx: int) -> Tuple[float, List[int]]:
        """
        Process one dimension: filter -> update reputation -> consensus.
        Returns (consensus, trusted_indices).
        """
        # Step 1: Two-pass median filter
        hard_kept = two_pass_median_filter(values, threshold=self.threshold)

        # Step 2: Update reputation
        self.reputation.update(dim_idx, hard_kept)

        # Step 3: Pre-filter by reputation
        trusted = self.reputation.pre_filter(dim_idx, min_rep=self.min_rep)

        # Step 4: Consensus
        if len(trusted) >= 5:
            trusted_vals = [values[i] for i in trusted]
            consensus = median(trusted_vals)
        else:
            # Fallback: two-pass median on all
            consensus = median([values[i] for i in hard_kept]) if hard_kept else median(values)

        return consensus, trusted

    def process_round(self, measurements: List[List[float]]) -> List[float]:
        """
        Process full round: measurements[agent][dim] -> consensus[dim].
        """
        results = []
        for dim_idx in range(self.n_dims):
            values = [measurements[i][dim_idx] for i in range(self.n_agents)]
            consensus, _ = self.process_dimension(values, dim_idx)
            results.append(consensus)
        return results

    def get_reputation_matrix(self) -> List[List[float]]:
        return self.reputation.get_matrix()