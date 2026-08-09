# Molecular AI v6.0

&gt; Decentralized multi-agent intelligence via Kuramoto synchronization and shared orbital resonance.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.2.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing.

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | 50–92% savings vs classical star topology |
| **Synchronization** | r &gt; 0.99 (3 agents), r &gt; 0.85 (6 agents) |
| **Scalability** | Tested up to 100 agents |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **Sensor Fusion** | 18.5–24.8% improvement vs IQR at 40% outlier load |

## Architecture

┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(ω,θ,mood)         (ω,θ,mood)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)


## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py

Examples
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 → 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation (latest)
python examples/sensor_fusion_multidim_reputation_v7.py

Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.

Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06°C error
v6	Two-Pass Median + Rep Filter	40% × 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% × 60% axes	24.8% (Humidity)

Architecture
plain
Raw Sensors → Two-Pass Median Filter → Per-Axis Reputation → Median Consensus
     ↑___________________________________________↓
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers 

Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py

Run
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py

Supported LLM Adapters
Table
Provider	Models	Status
OpenAI	GPT-4o, GPT-4o-mini	✅ Tested
Anthropic	Claude 3.5 Sonnet, Haiku	✅ Tested
Google	Gemini 1.5 Flash	⚠️ Adapter ready, keys not tested
DeepSeek	DeepSeek API	⚠️ Adapter ready, keys not tested
Ollama	Local LLM via HTTP	✅ Tested
Mock	Offline testing	✅ Generates  meaningful choices 

Scientific Foundation
Kuramoto model — synchronization of coupled oscillators
Hebbian plasticity — "neurons that fire together, wire together" (sparse k=4)
Buzsaki's rhythms — hierarchical brain oscillations (4 levels)
TD-learning — reward + value_weights + goal detection
Emotional dynamics — mood, arousal, spin (excitatory 85%) 

Project Structure
plain
molecular_ai/
├── core/
│   ├── sensor_fusion.py    # SensorFusionLayer (v0.2.0)
│   ├── system.py           # MolecularSystem orchestrator
│   ├── orbital.py          # HierarchicalOrbital (4 levels)
│   ├── agent.py            # Agent + FrequencyCodec
│   ├── plasticity.py       # SparseHebbianPlasticity
│   ├── reward.py           # TD-learning reward system
│   ├── memory.py           # WorkingMemory (capacity=5)
│   ├── attention.py        # AttentionModulator
│   ├── emotional_agent.py  # Mood + arousal dynamics
│   └── ...
├── adapters/               # LLM adapters (OpenAI, Anthropic, Gemini, etc.)
├── examples/               # Demos and experiments
├── tests/                  # pytest suite (10+ tests)
└── .github/workflows/      # CI/CD (Python 3.10–3.13)

Status
🔬 Research / Proof-of-Concept
This is an experimental architecture exploring resonance-based multi-agent coordination. Production readiness requires GPU acceleration, distributed deployment, and further validation.

Roadmap
Table
#	Topic	Priority
1	GPU Acceleration (CUDA/Numba)	High
2	Distributed Deployment (Redis/gRPC)	High
3	Async LLM Integration	Medium
4	Live LLM (Gemini/DeepSeek keys)	Medium
5	Multi-Agent Code Generation	Medium
6	Community Publication	Medium

License
MIT — see LICENSE

