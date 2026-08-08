# -*- coding: utf-8 -*-
"""
Вспомогательные функции / Utility helpers.
Чистый Python с опциональным numpy fallback.
"""

import math
import random
from typing import List, Union

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False


def mean(values):
    if not values:
        return 0.0
    values = list(values)
    return sum(values) / len(values)


def sin(x: float) -> float:
    return math.sin(x)


def cos(x: float) -> float:
    return math.cos(x)


def clip(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def order_parameter(phases: List[float]) -> float:
    if HAS_NUMPY:
        arr = np.array(phases, dtype=float)
        return float(abs(np.mean(np.exp(1j * arr))))
    n = len(phases)
    if n == 0:
        return 0.0
    sx = sum(math.cos(p) for p in phases) / n
    sy = sum(math.sin(p) for p in phases) / n
    return math.hypot(sx, sy)


def gauss_noise(sigma: float = 0.02) -> float:
    u1 = random.random()
    u2 = random.random()
    while u1 == 0:
        u1 = random.random()
    mag = sigma * math.sqrt(-2.0 * math.log(u1))
    return mag * math.cos(2.0 * math.pi * u2)


def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle
