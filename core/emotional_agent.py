# -*- coding: utf-8 -*-
"""
EmotionalAgent с mood, arousal, spin.
"""

import math
import random
from typing import Dict
from core.agent import Agent, FrequencyCodec
from core.utils import clip, sin, cos


class EmotionalAgent(Agent):
    def __init__(
        self,
        agent_id: int,
        omega: float = 1.0,
        phase: float = None,
        noise: float = 0.02,
        base_spin: float = 1.0,
        excitatory: bool = True,
    ):
        super().__init__(agent_id, omega, phase, noise, spin=base_spin)
        self.base_spin = base_spin
        self.excitatory = excitatory
        self.mood = 0.0
        self.arousal = 0.5
        self.sensory_input = 0.0

    def emotional_step(self, sync_with_orbital: float, dt: float = 0.05) -> None:
        target_mood = 2.0 * sync_with_orbital - 1.0
        self.mood += 0.1 * (target_mood - self.mood)
        self.mood = clip(self.mood, -1.0, 1.0)

        self.arousal += 0.05 * (self.energy - self.arousal)
        self.arousal = clip(self.arousal, 0.1, 1.0)

        sign_mood = 1.0 if (self.mood + 0.1) >= 0 else -1.0
        self.spin = self.base_spin * (0.5 + 0.5 * self.arousal) * sign_mood
        self.spin = clip(self.spin, -1.5, 1.5)

    def effective_coupling(self, base_K: float) -> float:
        if self.spin < 0:
            return base_K * -0.5
        return base_K * (1.0 + 0.2 * self.spin)

    def step(self, dt: float, orbital_influence: float = 0.0) -> None:
        K_eff = self.effective_coupling(1.0)
        modulated_influence = K_eff * orbital_influence
        super().step(dt, modulated_influence)

    def get_state(self) -> Dict:
        s = super().get_state()
        s.update({
            "mood": self.mood,
            "arousal": self.arousal,
            "base_spin": self.base_spin,
            "excitatory": self.excitatory,
        })
        return s
