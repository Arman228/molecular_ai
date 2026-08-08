# -*- coding: utf-8 -*-
"""
Goal Generator — динамические цели для v6.0.
"""

import math
import random
from typing import List, Dict


class GoalGenerator:
    """
    Генератор целевых состояний (goal phases).
    """

    def __init__(
        self,
        threshold: float = 0.20,
        min_steps_per_goal: int = 50,
        adapt_difficulty: bool = True,
    ):
        self.threshold = threshold
        self.min_steps_per_goal = min_steps_per_goal
        self.adapt_difficulty = adapt_difficulty

        self.current_goal: float = 0.0
        self.steps_on_current: int = 0
        self.goals_history: List[Dict] = []
        self.difficulty: float = 1.0

    def check_achieved(self, phases: List[float]) -> bool:
        self.steps_on_current += 1
        if self.steps_on_current < self.min_steps_per_goal:
            return False

                # 80% агентов близки к цели
        aligned_count = sum(1 for p in phases if abs(math.sin(p - self.current_goal)) < self.threshold)
        aligned = (aligned_count / len(phases)) >= 0.80
        return aligned

    def generate_new_goal(self, sync_r: float, mean_mood: float) -> float:
        self.goals_history.append({
            "goal": self.current_goal,
            "steps": self.steps_on_current,
            "difficulty": self.difficulty,
        })

        if self.adapt_difficulty:
            if sync_r > 0.9 and mean_mood > 0.5:
                self.difficulty = min(3.0, self.difficulty + 0.2)
            elif sync_r < 0.5:
                self.difficulty = max(0.5, self.difficulty - 0.2)

        spread = math.pi / self.difficulty
        self.current_goal = random.uniform(-spread, spread)
        self.steps_on_current = 0

        return self.current_goal

    @property
    def total_goals(self) -> int:
        return len(self.goals_history)

    def get_state(self) -> Dict:
        return {
            "current_goal": self.current_goal,
            "difficulty": self.difficulty,
            "steps_on_current": self.steps_on_current,
            "total_goals": self.total_goals,
            "history": self.goals_history[-5:],
        }