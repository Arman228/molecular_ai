# Molecular AI v6.0

&gt; Decentralized multi-agent intelligence via Kuramoto synchronization and shared orbital resonance.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.3.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing.

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | 50–92% savings vs classical star topology |
| **Synchronization** | r &gt; 0.99 (3 agents), r &gt; 0.85 (6 agents) |
| **Scalability** | Tested up to 100 agents |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **Sensor Fusion** | 18.5–24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

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
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 → 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation (latest)
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py

Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)

Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06°C error
v6	Two-Pass Median + Rep Filter	40% × 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% × 60% axes	24.8% (Humidity)

Architecture

Raw Sensors → Two-Pass Median Filter → Per-Axis Reputation → Median Consensus
     ↑___________________________________________↓

   Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files

  File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py

Run
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py

Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
python examples/code_generation_v3_1.py

Results (Mock mode, no API key):
Winner: Optimizer (score=1.03 vs Generator 0.53)
Generated: in-place quicksort with Lomuto partition
Tests: 6/6 pytest passed + manual verification passed
Sync r: 0.500
Architecture:
Generator → Reviewer → Optimizer → Tester
     ↓         ↓          ↓          ↓
   [code]   [issues]   [optimized]  [tests]
     └────────┴──────────┴──────────┘
              ↓
      SensorFusion consensus
              ↓
      Best code → pytest

      Files:
examples/code_generation_v3_1.py — orchestrator
output/generated_quicksort.py — winning code
output/test_quicksort.py — auto-generated tests

## Dynamic Code Generation

Auto-scaling agents by task complexity. User inputs task → analyzer detects modules → N agents → consensus → assembly.

```bash
python examples/dynamic_code_generation_v1.py "Flask REST API with JWT auth and React frontend"
Results:
Task: Flask REST API with JWT auth and React frontend
Detected: 3 modules (backend, frontend, auth)
Agents: 3 (auto-scaled)
Sync r: 0.999
Output: output/project/ with README.md + requirements.txt

Scaling:
Task	Modules	Agents
quicksort	generic	1
Flask API with JWT	backend, auth	2
Flask + React + tests	backend, frontend, auth, tests	4
Fullstack with Docker	backend, frontend, auth, db, tests, docs, config	7

Architecture:
User Task → Analyzer → [module1, module2, ...] → N agents
                                              ↓
                                    Orbital sync (r > 0.99)
                                              ↓
                              [Agent 1: backend] [Agent 2: frontend] [Agent 3: auth]
                                              ↓
                                    Project Assembly → output/project/

   Files:
examples/dynamic_code_generation_v1.py — orchestrator
output/project/ — generated artifacts    

## Async LLM + ConvergenceRegime

### Async LLM Calls
Parallel API calls via `asyncio.gather()` — 4× speedup vs sequential.

```bash
python examples/code_generation_v4_1.py

Architecture:
Agent 0 ─→ API ─┐
Agent 1 ─→ API ─┼→ asyncio.gather() → all responses in 2 sec
Agent 2 ─→ API ─┤
Agent 3 ─→ API ─┘

Files:
adapters/async_base.py — AsyncLLMAdapter with semaphore-based rate limiting
examples/code_generation_v4_1.py — async code generation, code-only winner

ConvergenceRegime 
Three regimes for controlled exploration vs exploitation:
Table
Regime	noise/dt	Sync r	Use case
LINEAR	< 0.5	> 0.9	Stable consensus, code generation
CRITICAL	≈ 1.0	~ 0.7-0.9	Brainstorm, exploration
DIVERGENT	> 2.0	< 0.5	Emergency 
python examples/brainstorm_regime.py

Results:
CRITICAL: sync r = 0.786 (diverse ideas)
LINEAR: sync r = 0.769 (stable consensus)
Files:
core/convergence_regime.py — regime detection and switching
examples/brainstorm_regime.py — demo with regime switching

Supported LLM Adapters
Provider	Models	Status
OpenAI	GPT-4o, GPT-4o-mini	✅ Tested
Anthropic	Claude 3.5 Sonnet, Haiku	✅ Tested
Google	Gemini 1.5 Flash	⚠️ Adapter ready, keys not tested
DeepSeek	DeepSeek API	⚠️ Adapter ready, keys not tested
Ollama	Local LLM via HTTP	✅ Tested
Mock	Offline testing	✅ Generates meaningful choices

Scientific Foundation
Kuramoto model — synchronization of coupled oscillators
Hebbian plasticity — "neurons that fire together, wire together" (sparse k=4)
Buzsaki's rhythms — hierarchical brain oscillations (4 levels)
TD-learning — reward + value_weights + goal detection
Emotional dynamics — mood, arousal, spin (excitatory 85%)

Project Structure
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
├── output/                 # Generated code artifacts
└── .github/workflows/      # CI/CD (Python 3.10–3.13)

Status
🔬 Research / Proof-of-Concept
This is an experimental architecture exploring resonance-based multi-agent coordination. Production readiness requires GPU acceleration, distributed deployment, and further validation.

Roadmap
#	Topic	Priority	Status
1	GPU Acceleration (CUDA/Numba)	High	Open
2	Distributed Deployment (Redis/gRPC)	High	Open
3	Async LLM Integration	Medium	Open
4	Live LLM (Gemini/DeepSeek keys)	Medium	Open
5	Multi-Agent Code Generation	Medium	v3.1 done, 6/6 tests
6	Community Publication	Medium	Open

License
MIT — see LICENSE

