# -*- coding: utf-8 -*-
"""
AutoTuner v5 — оптимизирован по результатам тестов.
"""

from typing import Dict


class AutoTuner:
    @staticmethod
    def tune(n_agents: int) -> Dict:
        if n_agents <= 5:
            return {
                "k_sparse": min(4, n_agents - 1),
                "exc_ratio": 0.85,
                "noise": 0.02,
                "coupling_boost": 1.0,
                "sleep_every": 300,
                "goal_interval": 250,
                "goal_threshold": 0.25,
                "omega_spread": 0.10,
            }

        if n_agents <= 12:
            # Оптимально для 6 агентов по тестам
            return {
                "k_sparse": 5,
                "exc_ratio": 0.90,
                "noise": 0.02,
                "coupling_boost": 2.0,
                "sleep_every": 300,
                "goal_interval": 200,
                "goal_threshold": 0.25,
                "omega_spread": 0.02,
            }

        if n_agents <= 30:
            return {
                "k_sparse": min(n_agents // 3, 10),
                "exc_ratio": 0.92,
                "noise": 0.015,
                "coupling_boost": 2.5,
                "sleep_every": 400,
                "goal_interval": 250,
                "goal_threshold": 0.25,
                "omega_spread": 0.05,
            }

        if n_agents <= 60:
            return {
                "k_sparse": min(n_agents // 4, 12),
                "exc_ratio": 0.93,
                "noise": 0.015,
                "coupling_boost": 3.0,
                "sleep_every": 500,
                "goal_interval": 300,
                "goal_threshold": 0.20,
                "omega_spread": 0.05,
            }

        return {
            "k_sparse": min(n_agents // 5, 15),
            "exc_ratio": 0.95,
            "noise": 0.01,
            "coupling_boost": 4.0,
            "sleep_every": 600,
            "goal_interval": 400,
            "goal_threshold": 0.15,
            "omega_spread": 0.02,
        }