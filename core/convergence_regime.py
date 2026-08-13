#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convergence Regimes for Molecular AI.
Inspired by EGGROLL three-regime analysis.
"""

from enum import Enum


class ConvergenceRegime(Enum):
    LINEAR = "linear"
    CRITICAL = "critical"
    DIVERGENT = "divergent"


def set_regime(system, regime: ConvergenceRegime):
    dt = system.dt
    n_agents = len(system.agents)
    
    if regime == ConvergenceRegime.LINEAR:
        system.noise = dt * 0.2
        system.k_sparse = min(4, n_agents - 1)
        for layer in system.orbital.layers:
            layer.coupling = layer.coupling * 0.8 + 0.2
        
    elif regime == ConvergenceRegime.CRITICAL:
        system.noise = dt * 1.0
        system.k_sparse = min(6, n_agents - 1)
        for layer in system.orbital.layers:
            layer.coupling *= 1.5
            
    elif regime == ConvergenceRegime.DIVERGENT:
        system.noise = dt * 3.0
        system.k_sparse = min(2, n_agents - 1)
        for layer in system.orbital.layers:
            layer.coupling *= 0.5
    
    # FIX: propagate noise to all agents so regime change actually affects them
    for agent in system.agents:
        agent.noise = system.noise
    
    return regime


def detect_regime(system) -> ConvergenceRegime:
    ratio = system.noise / system.dt
    if ratio < 0.5:
        return ConvergenceRegime.LINEAR
    elif ratio < 2.0:
        return ConvergenceRegime.CRITICAL
    else:
        return ConvergenceRegime.DIVERGENT


def get_regime_description(regime: ConvergenceRegime) -> str:
    descriptions = {
        ConvergenceRegime.LINEAR: "Stable exploitation (sync r > 0.9)",
        ConvergenceRegime.CRITICAL: "Exploration mode (sync r ~ 0.7-0.9)",
        ConvergenceRegime.DIVERGENT: "Chaos/reset (sync r < 0.5)",
    }
    return descriptions.get(regime, "Unknown")