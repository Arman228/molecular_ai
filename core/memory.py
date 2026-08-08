# -*- coding: utf-8 -*-
"""
Working Memory с LRU-вытеснением по reward.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryPattern:
    phases: List[float]
    reward: float
    step: int

    def to_dict(self) -> Dict:
        return asdict(self)


class WorkingMemory:
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.patterns: List[MemoryPattern] = []

    def store(self, phases: List[float], reward: float, step: int) -> None:
        pattern = MemoryPattern(phases=phases.copy(), reward=reward, step=step)
        self.patterns.append(pattern)
        self.patterns.sort(key=lambda x: x.reward, reverse=True)
        if len(self.patterns) > self.capacity:
            self.patterns.pop()

    def get_best(self) -> Optional[MemoryPattern]:
        return self.patterns[0] if self.patterns else None

    def get_all(self) -> List[Dict]:
        return [p.to_dict() for p in self.patterns]
