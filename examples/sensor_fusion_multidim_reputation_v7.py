#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Dimensional Sensor Fusion v7.
Refactored: uses core.sensor_fusion.SensorFusionLayer.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem
from core.sensor_fusion import SensorFusionLayer, robust_consensus_iqr

DIMENSIONS = [
    {"name": "Temperature", "unit": "°C", "min": 15, "max": 35, "true": 23.5},
    {"name": "Humidity", "unit": "%", "min": 30, "max": 80, "true": 55.0},
    {"name": "Pressure", "unit": "hPa", "min": 980, "max": 1030, "true": 1013.0},
    {"name": "CO2", "unit": "ppm", "min": 300, "max": 700, "true": 450.0},
    {"name": "Noise", "unit": "dB", "min": 30, "max": 80, "true": 45.0},
]


def normalize(value, dim_min, dim_max):
    return 0.5 + (value - dim_min) / (dim_max - dim_min) * 1.0 if dim_max > dim_min else 1.0


def run_experiment(
    n_agents=20,
    steps_per_round=100,
    n_rounds=50,
    outlier_prob=0.40,
    outlier_axes_prob=0.60,
    outlier_bias_factor=0.30,
):
    print("=" * 70)
    print("EXPERIMENT v7: SensorFusionLayer (Two-Pass Median + Per-Axis Rep)")
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

    fusion = SensorFusionLayer(
        n_agents=n_agents,
        dimensions=DIMENSIONS,
        threshold=2.0,
        min_rep=0.5,
    )

    agent_precision = [[random.uniform(0.5, 1.0) for _ in DIMENSIONS] for _ in range(n_agents)]
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

        # Apply drift and run fusion
        for dim_idx, dim in enumerate(DIMENSIONS):
            values = []
            for i in range(n_agents):
                drift = final_omegas[i] - 0.5
                val = measurements[i][dim_idx] + drift * (dim["max"] - dim["min"]) * 0.05
                values.append(val)

            # Baseline: Raw IQR k=1.5
            consensus_raw, _ = robust_consensus_iqr(values, k=1.5)
            err_raw = abs(consensus_raw - dim["true"])

            # v7: SensorFusionLayer
            consensus_v7, _ = fusion.process_dimension(values, dim_idx)
            err_v7 = abs(consensus_v7 - dim["true"])

            round_errors[dim["name"]].append((err_raw, err_v7))

            if round_idx in (0, n_rounds // 2, n_rounds - 1):
                outlier_count = sum(1 for m in outlier_mask if m[dim_idx])
                print(f"  Round {round_idx+1:2d} | {dim['name']:12s} | "
                      f"Raw: {consensus_raw:8.2f} (err {err_raw:5.2f}) | "
                      f"v7: {consensus_v7:8.2f} (err {err_v7:5.2f}) | "
                      f"Out: {outlier_count:2d}/{n_agents}")

    print("\n" + "=" * 70)
    print("FINAL STATISTICS (mean error)")
    print("=" * 70)
    print(f"{'Dimension':>12} | {'IQR k=1.5':>10} | {'SensorFusion':>12} | {'Improvement':>12}")
    print("-" * 70)

    for dim in DIMENSIONS:
        name = dim["name"]
        raw_errs = [e[0] for e in round_errors[name]]
        v7_errs = [e[1] for e in round_errors[name]]
        r_mean = sum(raw_errs) / len(raw_errs)
        v7_mean = sum(v7_errs) / len(v7_errs)
        improvement = ((r_mean - v7_mean) / r_mean * 100) if r_mean > 0 else 0
        print(f"{name:>12} | {r_mean:>10.3f} | {v7_mean:>12.3f} | {improvement:>11.1f}%")

    print("\n" + "=" * 70)
    print("REPUTATION MATRIX (agents x dimensions)")
    print("=" * 70)
    header = "Agent | " + " | ".join([d["name"][:4] for d in DIMENSIONS])
    print(header)
    print("-" * len(header))
    matrix = fusion.get_reputation_matrix()
    for i in range(n_agents):
        reps = " | ".join([f"{matrix[i][d]:.2f}" for d in range(len(DIMENSIONS))])
        print(f"  {i:2d}  | {reps}")

    print("\n" + "=" * 70)
    print("SUMMARY v7")
    print("=" * 70)
    print("SensorFusionLayer: reusable core module.")
    print("Two-pass median: breakdown point ~50%.")
    print("Per-axis reputation: min_rep=0.5, window=50.")


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