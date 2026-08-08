# -*- coding: utf-8 -*-
from core.system import MolecularSystem


def test_system_goals():
    sys = MolecularSystem(n_agents=6, dt=0.05, noise=0.02)
    sys.run(1000)
    m = sys.get_metrics()
    assert m["goals_achieved"] >= 0
    assert -1.0 <= m["mean_mood"] <= 1.0

def test_system_export():
    sys = MolecularSystem(n_agents=3)
    sys.run(10)
    s = sys.export_state()
    assert "step" in s
    assert "agents" in s
