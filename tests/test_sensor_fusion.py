#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for core.sensor_fusion.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import pytest
from core.sensor_fusion import (
    median,
    mad,
    two_pass_median_filter,
    robust_consensus_iqr,
    PerAxisReputation,
    SensorFusionLayer,
)


class TestMedian:
    def test_odd(self):
        assert median([1, 2, 3, 4, 5]) == 3

    def test_even(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_single(self):
        assert median([42]) == 42


class TestMAD:
    def test_basic(self):
        # Values: 1,2,3,4,5. Median=3. Deviations: 2,1,0,1,2. MAD=1.
        assert mad([1, 2, 3, 4, 5], 3) == 1

    def test_zero_fallback(self):
        assert mad([5, 5, 5], 5) == 0.001


class TestTwoPassMedianFilter:
    def test_no_outliers(self):
        values = [1, 2, 3, 4, 5]
        kept = two_pass_median_filter(values, threshold=2.0)
        assert len(kept) == 5

    def test_one_outlier(self):
        values = [1, 2, 3, 4, 100]
        kept = two_pass_median_filter(values, threshold=2.0)
        assert 4 not in kept  # 100 is outlier

    def test_40_percent_outliers(self):
        """Breakdown point test: 40% outliers should be filtered."""
        random.seed(42)
        true = 50.0
        values = [true + random.gauss(0, 1) for _ in range(12)]
        outliers = [true + 20 + random.gauss(0, 1) for _ in range(8)]
        all_vals = values + outliers
        kept = two_pass_median_filter(all_vals, threshold=3.0)
        # At least 7 good values should remain (filter is aggressive)
        assert len(kept) >= 7
        # Consensus should be close to true
        consensus = median([all_vals[i] for i in kept])
        assert abs(consensus - true) < 2.0

    def test_50_percent_outliers_breakdown(self):
        """At 50% outliers, filter may fail gracefully."""
        random.seed(123)
        true = 100.0
        values = [true + random.gauss(0, 1) for _ in range(10)]
        outliers = [true + 30 + random.gauss(0, 1) for _ in range(10)]
        all_vals = values + outliers
        kept = two_pass_median_filter(all_vals, threshold=2.0)
        # Should not crash, should return something
        assert len(kept) >= 3


class TestRobustConsensusIQR:
    def test_clean_data(self):
        values = [1, 2, 3, 4, 5]
        c, kept = robust_consensus_iqr(values, k=1.5)
        assert abs(c - 3.0) < 0.1
        assert len(kept) == 5

    def test_with_outlier(self):
        values = [1, 2, 3, 4, 100]
        c, kept = robust_consensus_iqr(values, k=1.5)
        assert abs(c - 2.5) < 0.5
        assert 4 not in kept


class TestPerAxisReputation:
    def test_init(self):
        rep = PerAxisReputation(5, 3)
        assert len(rep.reputation) == 5
        assert len(rep.reputation[0]) == 3
        assert all(r == 1.0 for r in rep.reputation[0])

    def test_update(self):
        rep = PerAxisReputation(3, 2)
        rep.update(0, [0, 2])
        assert rep.reputation[0][0] == 1.0
        assert rep.reputation[1][0] == 0.0
        assert rep.reputation[2][0] == 1.0

    def test_pre_filter(self):
        rep = PerAxisReputation(5, 1)
        for _ in range(10):
            rep.update(0, [0, 1, 2])
        trusted = rep.pre_filter(0, min_rep=0.5)
        assert 0 in trusted
        assert 1 in trusted
        assert 2 in trusted


class TestSensorFusionLayer:
    def test_process_dimension(self):
        dims = [{"name": "Temp", "unit": "C", "min": 0, "max": 100, "true": 50.0}]
        fusion = SensorFusionLayer(5, dims, threshold=2.0, min_rep=0.5)
        values = [48, 49, 50, 51, 100]
        consensus, trusted = fusion.process_dimension(values, 0)
        assert abs(consensus - 50) < 2
        assert 4 not in trusted  # 100 is outlier

    def test_process_round(self):
        dims = [
            {"name": "A", "unit": "x", "min": 0, "max": 10, "true": 5.0},
            {"name": "B", "unit": "y", "min": 0, "max": 10, "true": 5.0},
        ]
        fusion = SensorFusionLayer(4, dims)
        measurements = [
            [4.9, 5.1],
            [5.0, 5.0],
            [5.1, 4.9],
            [20.0, 20.0],  # outlier
        ]
        results = fusion.process_round(measurements)
        assert len(results) == 2
        assert abs(results[0] - 5.0) < 0.2
        assert abs(results[1] - 5.0) < 0.2

    def test_reputation_matrix_shape(self):
        dims = [{"name": "X", "unit": "x", "min": 0, "max": 10, "true": 5.0}]
        fusion = SensorFusionLayer(3, dims)
        m = fusion.get_reputation_matrix()
        assert len(m) == 3
        assert len(m[0]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])