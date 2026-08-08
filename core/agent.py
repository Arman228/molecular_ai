# -*- coding: utf-8 -*-
"""
Agent и FrequencyCodec.
"""

import math
import random
from typing import List, Dict
from core.utils import sin, cos, clip, normalize_angle, gauss_noise


class FrequencyCodec:
    DIM = 16

    @staticmethod
    def encode(phase: float, omega: float) -> List[float]:
        vec = [0.0] * FrequencyCodec.DIM
        for k in range(4):
            vec[k] = sin((k + 1) * phase)
            vec[k + 4] = cos((k + 1) * phase)
        for k in range(4):
            vec[k + 8] = omega
            vec[k + 12] = abs(sin(phase))
        return vec

    @staticmethod
    def decode(vec: List[float]) -> Dict[str, float]:
        if len(vec) < 8:
            return {"phase": 0.0, "omega": 0.0}
        s1 = vec[0]
        c1 = vec[4]
        phase = math.atan2(s1, c1)
        omega = vec[8] if len(vec) > 8 else 0.0
        return {"phase": phase, "omega": omega}


class Agent:
    def __init__(
        self,
        agent_id: int,
        omega: float = 1.0,
        phase: float = None,
        noise: float = 0.02,
        spin: float = 1.0,
    ):
        self.agent_id = agent_id
        self.omega = omega
        self.phase = phase if phase is not None else random.uniform(-math.pi, math.pi)
        self.noise = noise
        self.spin = clip(spin, -1.5, 1.5)
        self.energy = 0.0
        self.history: List[float] = []

    def step(self, dt: float, orbital_influence: float = 0.0) -> None:
        dtheta = self.omega + orbital_influence + gauss_noise(self.noise)
        self.phase += dt * dtheta
        self.phase = normalize_angle(self.phase)
        self.energy = abs(dtheta)
        self.history.append(self.phase)
        if len(self.history) > 2000:
            self.history.pop(0)

    def get_frequency_vector(self) -> List[float]:
        return FrequencyCodec.encode(self.phase, self.omega)

    def get_state(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "phase": self.phase,
            "omega": self.omega,
            "spin": self.spin,
            "energy": self.energy,
        }
