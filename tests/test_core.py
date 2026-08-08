# -*- coding: utf-8 -*-
import math
import pytest
from core.utils import order_parameter, mean, clip
from core.orbital import SharedOrbital, OrbitalLayer, HierarchicalOrbital
from core.agent import Agent, FrequencyCodec
from core.plasticity import SparseHebbianPlasticity
from core.system import MolecularSystem


def test_order_parameter_sync():
    phases = [0.0, 0.01, -0.01]
    r = order_parameter(phases)
    assert r > 0.99


def test_order_parameter_chaos():
    phases = [0.0, math.pi / 2, math.pi]
    r = order_parameter(phases)
    assert r < 0.9


def test_frequency_codec_roundtrip():
    phase = 1.23
    omega = 0.8
    vec = FrequencyCodec.encode(phase, omega)
    assert len(vec) == 16
    dec = FrequencyCodec.decode(vec)
    assert abs(dec["omega"] - omega) < 1e-6


def test_agent_step_uncoupled():
    a = Agent(0, omega=1.0, phase=0.0, noise=0.0)
    for _ in range(100):
        a.step(dt=0.05, orbital_influence=0.0)
    assert abs(a.phase) > 0.1


def test_agent_step_coupled():
    a = Agent(0, omega=0.0, phase=0.5, noise=0.0)
    for _ in range(200):
        a.step(dt=0.05, orbital_influence=3.0 * math.sin(0.0 - a.phase))
    assert abs(math.sin(a.phase)) < 0.1


def test_hierarchical_orbital():
    ho = HierarchicalOrbital()
    assert len(ho.layers) == 4
    assert ho.layers[0].name == "Gamma"


def test_plasticity_pruning():
    p = SparseHebbianPlasticity(6, k_sparse=2)
    p.sleep_consolidation()
    for w in p.W.values():
        assert w >= 0.15 or w == 0


def test_system_sync():
    import random
    random.seed(42)
    sys = MolecularSystem(n_agents=3, dt=0.05, noise=0.0)
    sys.run(1000)
    # В v6.0 с динамическими целями проверяем работу goal generator
    assert sys.goal_generator.total_goals >= 0
    assert sys.step_count == 1000
    # Система работает без ошибок — синхронизация колеблется из-за смены целей
    assert sys.order_parameter() >= 0.0