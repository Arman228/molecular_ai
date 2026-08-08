#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Dimensional Sensor Fusion v6.
Two-Pass Median + Reputation Pre-Filter. High outlier load.
"""

import os
import sys
import random
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem

DIMENSIONS = [
    {"name": "Temperature", "unit": "°C", "min": 15, "max": 35, "true": 23.5},
    {"name": "Humidity", "unit": "%", "min": 30, "max": 80, "true": 55.0},
    {"name": "Pressure", "unit": "hPa", "min": 980, "max": 1030, "true": 1013.0},
    {"name": "CO2", "unit": "ppm", "min": 300, "max": 700, "true": 450.0},
    {"name": "Noise", "unit": "dB", "min": 30, "max": 80, "true": 45.0},
]


def normalize(value, dim_min, dim_max):
    return 0.5 + (value - dim_min) / (dim_max - dim_min) * 1.0 if dim_max > dim_min else 1.0


def median(values):
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def mad(values, med):
    abs_dev = [abs(v - med) for v in values]
    s = sorted(abs_dev)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def two_pass_median_filter(values, threshold=2.0):
    """Two-pass: rough median -> filter -> refined median on kept."""
    if len(values) < 3:
        return list(range(len(values)))
    
    # Pass 1: rough median on all
    m1 = median(values)
    d1 = mad(values, m1)
    if d1 == 0:
        d1 = 0.001
    
    kept1 = [i for i, v in enumerate(values) if abs(v - m1) <= threshold * d1]
    if len(kept1) < 3:
        return kept1
    
    # Pass 2: refined median on kept1
    kept_vals = [values[i] for i in kept1]
    m2 = median(kept_vals)
    d2 = mad(kept_vals, m2)
    if d2 == 0:
        d2 = 0.001
    
    kept2 = [i for i in kept1 if abs(values[i] - m2) <= threshold * d2]
    return kept2 if len(kept2) >= 3 else kept1


def robust_consensus_iqr(values, k=1.5):
    remaining = list(range(len(values)))
    for _ in range(2):
        vals = [values[i] for i in remaining]
        s = sorted(vals)
        n = len(s)
        if n < 4:
            break
        q1 = s[n // 4]
        q3 = s[3 * n // 4]
        iqr = q3 - q1
        lower, upper = q1 - k * iqr, q3 + k * iqr
        new_remaining = [i for i in remaining if lower <= values[i] <= upper]
        if len(new_remaining) == len(remaining) or len(new_remaining) < 3:
            break
        remaining = new_remaining
    return sum(values[i] for i in remaining) / len(remaining), remaining


class PerAxisReputation:
    def __init__(self, n_agents, n_dims):
        self.reputation = [[1.0 for _ in range(n_dims)] for _ in range(n_agents)]
        self.history = [[[] for _ in range(n_dims)] for _ in range(n_agents)]
    
    def update(self, dim_idx, kept_indices, total_agents):
        for i in range(total_agents):
            kept = i in kept_indices
            self.history[i][dim_idx].append(kept)
            if len(self.history[i][dim_idx]) > 50:
                self.history[i][dim_idx].pop(0)
            recent = self.history[i][dim_idx][-15:] if len(self.history[i][dim_idx]) >= 15 else self.history[i][dim_idx]
            self.reputation[i][dim_idx] = sum(recent) / len(recent) if recent else 1.0
    
    def pre_filter(self, dim_idx, min_rep=0.5):
        return [i for i in range(len(self.reputation)) if self.reputation[i][dim_idx] >= min_rep]


def run_experiment(
    n_agents=20,
    steps_per_round=100,
    n_rounds=50,
    outlier_prob=0.40,
    outlier_axes_prob=0.60,
    outlier_bias_factor=0.30,
):
    print("=" * 70)
    print("EXPERIMENT v6: Two-Pass Median + Reputation Pre-Filter")
    print("High outlier load: 40% agents x 60% axes = ~4.8 outliers/dimension")
    print("=" * 70)
    print(f"Agents:         {n_agents}")
    print(f"Dimensions:     {len(DIMENSIONS)}")
    print(f"Rounds:         {n_rounds} x {steps_per_round} steps")
    print(f"Outlier prob:   {outlier_prob*100:.0f}% per agent per round")
    print(f"Outlier axes:   {outlier_axes_prob*100:.0f}% per axis")
    print(f"Bias factor:    {outlier_bias_factor*100:.0f}% of range")
    print("-" * 70)

    sys = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.01,
        k_sparse=min(4, n_agents - 1),
        exc_ratio=0.85,
    )
    for layer in sys.orbital.layers:
        layer.coupling *= 2.0

    agent_precision = [[random.uniform(0.5, 1.0) for _ in DIMENSIONS] for _ in range(n_agents)]
    rep = PerAxisReputation(n_agents, len(DIMENSIONS))
    round_errors = {d["name"]: [] for d in DIMENSIONS}

    for round_idx in range(n_rounds):
        measurements = []
        outlier_mask = []

        for i in range(n_agents):
            agent_meas = []
            agent_outlier = []
            is_outlier_agent = random.random() < outlier_prob

            for dim_idx, dim in enumerate(DIMENSIONS):
                if is_outlier_agent and random.random() < outlier_axes_prob:
                    bias = (dim["max"] - dim["min"]) * outlier_bias_factor
                    value = dim["true"] + random.choice([-1, 1]) * bias + random.gauss(0, 1.5)
                    agent_outlier.append(True)
                else:
                    noise = 1.0 / agent_precision[i][dim_idx]
                    value = dim["true"] + random.gauss(0, noise)
                    agent_outlier.append(False)
                agent_meas.append(value)

            measurements.append(agent_meas)
            outlier_mask.append(agent_outlier)

        for i, agent in enumerate(sys.agents):
            norms = [normalize(measurements[i][d], DIMENSIONS[d]["min"], DIMENSIONS[d]["max"]) 
                     for d in range(len(DIMENSIONS))]
            agent.omega = sum(norms) / len(norms)

        for _ in range(steps_per_round):
            sys.step()

        final_omegas = [a.omega for a in sys.agents]

        for dim_idx, dim in enumerate(DIMENSIONS):
            values = []
            for i in range(n_agents):
                drift = final_omegas[i] - 0.5
                val = measurements[i][dim_idx] + drift * (dim["max"] - dim["min"]) * 0.05
                values.append(val)

            # Baseline: Raw IQR k=1.5
            consensus_raw, _ = robust_consensus_iqr(values, k=1.5)
            err_raw = abs(consensus_raw - dim["true"])

            # v6: Two-pass median filter -> reputation pre-filter -> median consensus
            hard_kept = two_pass_median_filter(values, threshold=2.0)
            rep.update(dim_idx, hard_kept, n_agents)
            
            trusted = rep.pre_filter(dim_idx, min_rep=0.5)
            if len(trusted) >= 5:
                trusted_vals = [values[i] for i in trusted]
                consensus_v6 = median(trusted_vals)
            else:
                # Fallback: two-pass median on all (reputation not mature yet)
                consensus_v6 = median([values[i] for i in hard_kept]) if hard_kept else median(values)
            
            err_v6 = abs(consensus_v6 - dim["true"])
            round_errors[dim["name"]].append((err_raw, err_v6))

            if round_idx in (0, n_rounds // 2, n_rounds - 1):
                outlier_count = sum(1 for m in outlier_mask if m[dim_idx])
                print(f"  Round {round_idx+1:2d} | {dim['name']:12s} | "
                      f"Raw: {consensus_raw:8.2f} (err {err_raw:5.2f}) | "
                      f"v6: {consensus_v6:8.2f} (err {err_v6:5.2f}) | "
                      f"Out: {outlier_count:2d}/{n_agents} | Hard: {len(hard_kept):2d}")

    print("\n" + "=" * 70)
    print("FINAL STATISTICS (mean error)")
    print("=" * 70)
    print(f"{'Dimension':>12} | {'IQR k=1.5':>10} | {'2Pass+Rep':>12} | {'Improvement':>12}")
    print("-" * 70)

    for dim in DIMENSIONS:
        name = dim["name"]
        raw_errs = [e[0] for e in round_errors[name]]
        v6_errs = [e[1] for e in round_errors[name]]
        r_mean = sum(raw_errs) / len(raw_errs)
        v6_mean = sum(v6_errs) / len(v6_errs)
        improvement = ((r_mean - v6_mean) / r_mean * 100) if r_mean > 0 else 0
        print(f"{name:>12} | {r_mean:>10.3f} | {v6_mean:>12.3f} | {improvement:>11.1f}%")

    print("\n" + "=" * 70)
    print("REPUTATION MATRIX (agents x dimensions)")
    print("=" * 70)
    header = "Agent | " + " | ".join([d["name"][:4] for d in DIMENSIONS])
    print(header)
    print("-" * len(header))
    for i in range(n_agents):
        reps = " | ".join([f"{rep.reputation[i][d]:.2f}" for d in range(len(DIMENSIONS))])
        print(f"  {i:2d}  | {reps}")

    print("\n" + "=" * 70)
    print("SUMMARY v6")
    print("=" * 70)
    print("Two-pass median: rough -> filter -> refined. Resistant to 40% outliers.")
    print("Consensus = median (not weighted mean). Breakdown point ~50%.")
    print("Reputation pre-filter min_rep=0.5: only proven agents vote.")
    print("Fallback: if reputation immature, use two-pass median directly.")


def main():
    random.seed(42)
    run_experiment(
        n_agents=20,
        steps_per_round=100,
        n_rounds=50,
        outlier_prob=0.40,
        outlier_axes_prob=0.60,
        outlier_bias_factor=0.30,
    )


if __name__ == "__main__":
    main()