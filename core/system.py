# -*- coding: utf-8 -*-
"""
MolecularSystem — оркестратор симуляции v6.0.
"""

import json
import math
import random
from typing import List, Dict, Optional
from core.utils import order_parameter, clip
from core.orbital import HierarchicalOrbital
from core.emotional_agent import EmotionalAgent
from core.plasticity import SparseHebbianPlasticity, MetaPlasticity
from core.reward import RewardSystem
from core.memory import WorkingMemory
from core.attention import AttentionModulator
from core.goals import GoalGenerator


class MolecularSystem:
    def __init__(
        self,
        n_agents: int = 12,
        dt: float = 0.05,
        noise: float = 0.02,
        sleep_every: int = 300,
        k_sparse: int = 4,
        exc_ratio: float = 0.85,
        goal_phase: float = 0.0,
    ):
        self.n = n_agents
        self.dt = dt
        self.noise = noise
        self.sleep_every = sleep_every
        self.step_count = 0
        self.goal_phase = goal_phase
        self.goal_generator = GoalGenerator(threshold=0.15, min_steps_per_goal=50)

        self.agents: List[EmotionalAgent] = []
        n_exc = int(n_agents * exc_ratio)
        exc_indices = set(random.sample(range(n_agents), n_exc))
        for i in range(n_agents):
            omega = 1.0 + random.uniform(-0.05, 0.05)
            is_exc = i in exc_indices
            agent = EmotionalAgent(
                agent_id=i,
                omega=omega,
                noise=noise,
                base_spin=1.0 if is_exc else -1.0,
                excitatory=is_exc,
            )
            self.agents.append(agent)

        self.orbital = HierarchicalOrbital()
        self.plasticity = SparseHebbianPlasticity(n_agents, k_sparse)
        self.meta = MetaPlasticity()
        self.reward_system = RewardSystem(n_agents)
        self.memory = WorkingMemory(capacity=5)
        self.attention = AttentionModulator()

    def step(self, coupled: bool = True) -> None:
        phases = [a.phase for a in self.agents]
        vectors = [a.get_frequency_vector() for a in self.agents]

        self.orbital.update(vectors, phases)

        r = order_parameter(phases)

        energies = [a.energy for a in self.agents]
        self.attention.compute_salience(phases, energies)
        eta = self.meta.get_eta(r)

        for agent in self.agents:
            sync = 0.5 * (1.0 + math.cos(agent.phase - self.orbital.layers[0].orbital.get_mean_phase()))
            agent.emotional_step(sync, self.dt)

            influence = 0.0
            if coupled:
                influence = self.orbital.total_influence(agent.phase, agent.omega)
                for (i, j), w in self.plasticity.W.items():
                    if i == agent.agent_id:
                        influence += 0.1 * w * math.sin(phases[j] - agent.phase)

            agent.step(self.dt, influence)

        new_phases = [a.phase for a in self.agents]
        self.plasticity.update(new_phases, eta=eta)

        reward = self.reward_system.compute_reward(
            new_phases, self.goal_phase, r, energies
        )
        self.reward_system.td_update(reward, new_phases, self.goal_phase)

        self.memory.store(new_phases, reward, self.step_count)

        moods = [a.mood for a in self.agents]
        if self.goal_generator.check_achieved(new_phases):
            new_goal = self.goal_generator.generate_new_goal(
                r, sum(moods) / len(moods) if moods else 0.0
            )
            self.goal_phase = new_goal
            self.reward_system.goals_achieved += 1

        self.step_count += 1
        if self.step_count % self.sleep_every == 0:
            self.plasticity.sleep_consolidation()

    def run(self, n_steps: int) -> None:
        for _ in range(n_steps):
            self.step()

    def order_parameter(self) -> float:
        return order_parameter([a.phase for a in self.agents])

    def get_metrics(self) -> Dict:
        phases = [a.phase for a in self.agents]
        moods = [a.mood for a in self.agents]
        return {
            "step": self.step_count,
            "sync_r": self.order_parameter(),
            "mean_mood": sum(moods) / len(moods) if moods else 0.0,
            "mean_energy": sum(a.energy for a in self.agents) / self.n,
            "total_goals_generated": self.goal_generator.total_goals,
            **self.reward_system.get_metrics(),
            "attention": self.attention.get_state(),
            "memory_best": self.memory.get_best().to_dict() if self.memory.get_best() else None,
        }

    def export_state(self) -> str:
        state = {
            "step": self.step_count,
            "agents": [a.get_state() for a in self.agents],
            "orbital": self.orbital.get_state(),
            "plasticity": {str(k[0]) + "_" + str(k[1]): v for k, v in self.plasticity.W.items()},
            "metrics": self.get_metrics(),
        }
        return json.dumps(state, indent=2, ensure_ascii=False)