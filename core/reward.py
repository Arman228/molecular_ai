# -*- coding: utf-8 -*-
"""
Reward System на основе TD-learning.
"""

import math
from typing import List, Dict
from core.utils import mean, clip


class RewardSystem:
    def __init__(
        self,
        n_agents: int,
        gamma: float = 0.95,
        alpha: float = 0.01,
    ):
        self.n = n_agents
        self.gamma = gamma
        self.alpha = alpha
        self.value_weights = [0.0] * n_agents
        self.prev_value = 0.0
        self.total_reward = 0.0
        self.goals_achieved = 0

    def compute_reward(
        self,
        phases: List[float],
        goal_phase: float,
        sync_r: float,
        energies: List[float],
        goal_threshold: float = 0.2,
    ) -> float:
        mean_energy = mean(energies) if energies else 0.0
        alignment = 1.0 - mean(abs(math.sin(p - goal_phase)) for p in phases)
        sync_bonus = 0.5 * sync_r
        energy_cost = 0.3 * mean_energy
                # 80% агентов должны быть близки к цели (реалистично для больших систем)
        aligned_ratio = sum(1 for p in phases if abs(math.sin(p - goal_phase)) < goal_threshold) / len(phases)
        goal_achieved = aligned_ratio >= 0.80
        goal_bonus = 2.0 if goal_achieved else 0.0
        if goal_achieved:
            self.goals_achieved += 1
        reward = alignment + sync_bonus - energy_cost + goal_bonus
        self.total_reward += reward
        return reward

    def td_update(self, reward: float, phases: List[float], goal_phase: float) -> float:
        V_s = mean(math.cos(p - goal_phase) for p in phases)
        td_error = reward + self.gamma * V_s - self.prev_value
        self.prev_value = V_s
        for i in range(self.n):
            self.value_weights[i] += self.alpha * td_error * math.cos(phases[i] - goal_phase)
            self.value_weights[i] = clip(self.value_weights[i], -5.0, 5.0)
        return td_error

    def get_metrics(self) -> Dict:
        return {
            "total_reward": self.total_reward,
            "goals_achieved": self.goals_achieved,
            "mean_value_weight": mean(self.value_weights),
        }
