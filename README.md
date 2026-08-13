# Molecular AI v7.0

&gt; Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r &gt; 0.99 (3 agents), r &gt; 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)


---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py

DeepSeek Demos (Live LLM)
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py

Classic Demos
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py

DeepSeek Live Integration
5 Demo Scripts
| Script                          | Agents | Mode       | Features                        | Time | Cost     |
| ------------------------------- | ------ | ---------- | ------------------------------- | ---- | -------- |
| `demo_deepseek_full.py`         | 1      | Sync       | Basic orbital context           | 5s   | ~\$0.001 |
| `demo_deepseek_multi.py`        | 6      | Sequential | 6 roles, warm-up 800 steps      | 25s  | ~\$0.01  |
| `demo_deepseek_async_regime.py` | 6      | Async      | CRITICAL regime, parallel calls | 15s  | ~\$0.01  |
| `demo_deepseek_full_combo.py`   | 12     | Async      | DIVERGENT + SensorFusion voting | 35s  | ~\$0.02  |
| `demo_deepseek_30_agents.py`    | 30     | Async      | DIVERGENT, 30 roles, voting     | 75s  | ~\$0.05  |

Example Output (30 Agents)
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)

  30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer

Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
| Approach               | Calls | Input Tokens | Output Tokens | Cost       | Time |
| ---------------------- | ----- | ------------ | ------------- | ---------- | ---- |
| **Single LLM**         | 1     | 200          | 800           | \$0.002    | 3s   |
| **CrewAI / LangGraph** | ~35   | ~136,000     | ~18,000       | **\$0.27** | 115s |
| **Molecular AI v7.0**  | 60    | 94,500       | 39,000        | **\$0.05** | 75s  |

Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.

Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
| Version | Method                          | Outlier Load   | Best Improvement |
| ------- | ------------------------------- | -------------- | ---------------- |
| v2      | Median + MAD                    | 20% agents     | 0.06C error      |
| v6      | Two-Pass Median + Rep Filter    | 40% x 60% axes | 24.8% (Humidity) |
| v7      | SensorFusionLayer (core module) | 40% x 60% axes | 24.8% (Humidity) |

Architecture
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|

Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
 | File                                               | Description                       |
| -------------------------------------------------- | --------------------------------- |
| `core/sensor_fusion.py`                            | Reusable SensorFusionLayer module |
| `examples/sensor_fusion_multidim_reputation_v7.py` | 5D demo with 20 agents            |
| `tests/test_sensor_fusion.py`                      | Unit tests                        |
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py

Обновить README
Read
README.md
Добавить примеры
File created
README_v2.md
Think
Пользователь просит прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md, теперь нужно прочитать и вывести содержимое в чат.
Read
README_v2.md
Think
Всё готово. Пользователь просил прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md и прочитал содержимое. Теперь нужно вывести полный текст в чат. Но файл длинный (439 строк). Лучше прислать его целиком — пользователь сам скопирует.
Также напомню про rename .txt -> .py и про git push.
Вот полный обновлённый README.md — копируй и заменяй:
Markdown
Code
Preview
# Molecular AI v7.0

> Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)
plain

---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py
DeepSeek Demos (Live LLM)
bash
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py
Classic Demos
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py
DeepSeek Live Integration
5 Demo Scripts
Table
Script	Agents	Mode	Features	Time	Cost
demo_deepseek_full.py	1	Sync	Basic orbital context	5s	~$0.001
demo_deepseek_multi.py	6	Sequential	6 roles, warm-up 800 steps	25s	~$0.01
demo_deepseek_async_regime.py	6	Async	CRITICAL regime, parallel calls	15s	~$0.01
demo_deepseek_full_combo.py	12	Async	DIVERGENT + SensorFusion voting	35s	~$0.02
demo_deepseek_30_agents.py	30	Async	DIVERGENT, 30 roles, voting	75s	~$0.05
Example Output (30 Agents)
plain
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)
30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer
Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
Table
Approach	Calls	Input Tokens	Output Tokens	Cost	Time
Single LLM	1	200	800	$0.002	3s
CrewAI / LangGraph	~35	~136,000	~18,000	$0.27	115s
Molecular AI v7.0	60	94,500	39,000	$0.05	75s
Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.
Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06C error
v6	Two-Pass Median + Rep Filter	40% x 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% x 60% axes	24.8% (Humidity)
Architecture
plain
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py	Unit tests
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py
Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
python examples/code_generation_v3_1.py
Обновить README
Read
README.md
Добавить примеры
File created
README_v2.md
Think
Пользователь просит прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md, теперь нужно прочитать и вывести содержимое в чат.
Read
README_v2.md
Think
Всё готово. Пользователь просил прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md и прочитал содержимое. Теперь нужно вывести полный текст в чат. Но файл длинный (439 строк). Лучше прислать его целиком — пользователь сам скопирует.
Также напомню про rename .txt -> .py и про git push.
Вот полный обновлённый README.md — копируй и заменяй:
Markdown
Code
Preview
# Molecular AI v7.0

> Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)
plain

---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py
DeepSeek Demos (Live LLM)
bash
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py
Classic Demos
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py
DeepSeek Live Integration
5 Demo Scripts
Table
Script	Agents	Mode	Features	Time	Cost
demo_deepseek_full.py	1	Sync	Basic orbital context	5s	~$0.001
demo_deepseek_multi.py	6	Sequential	6 roles, warm-up 800 steps	25s	~$0.01
demo_deepseek_async_regime.py	6	Async	CRITICAL regime, parallel calls	15s	~$0.01
demo_deepseek_full_combo.py	12	Async	DIVERGENT + SensorFusion voting	35s	~$0.02
demo_deepseek_30_agents.py	30	Async	DIVERGENT, 30 roles, voting	75s	~$0.05
Example Output (30 Agents)
plain
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)
30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer
Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
Table
Approach	Calls	Input Tokens	Output Tokens	Cost	Time
Single LLM	1	200	800	$0.002	3s
CrewAI / LangGraph	~35	~136,000	~18,000	$0.27	115s
Molecular AI v7.0	60	94,500	39,000	$0.05	75s
Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.
Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06C error
v6	Two-Pass Median + Rep Filter	40% x 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% x 60% axes	24.8% (Humidity)
Architecture
plain
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py	Unit tests
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py
Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
bash
python examples/code_generation_v3_1.py
Results (Mock mode, no API key):
Winner: Optimizer (score=1.03 vs Generator 0.53)
Generated: in-place quicksort with Lomuto partition
Tests: 6/6 pytest passed + manual verification passed
Sync r: 0.500
Architecture
Generator -> Reviewer -> Optimizer -> Tester
     |         |          |          |
   [code]   [issues]   [optimized]  [tests]
     |________|__________|__________|
                |
        SensorFusion consensus
                |
        Best code -> pytest

Обновить README
Read
README.md
Добавить примеры
File created
README_v2.md
Think
Пользователь просит прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md, теперь нужно прочитать и вывести содержимое в чат.
Read
README_v2.md
Think
Всё готово. Пользователь просил прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md и прочитал содержимое. Теперь нужно вывести полный текст в чат. Но файл длинный (439 строк). Лучше прислать его целиком — пользователь сам скопирует.
Также напомню про rename .txt -> .py и про git push.
Вот полный обновлённый README.md — копируй и заменяй:
Markdown
Code
Preview
# Molecular AI v7.0

> Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)
plain

---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py
DeepSeek Demos (Live LLM)
bash
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py
Classic Demos
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py
DeepSeek Live Integration
5 Demo Scripts
Table
Script	Agents	Mode	Features	Time	Cost
demo_deepseek_full.py	1	Sync	Basic orbital context	5s	~$0.001
demo_deepseek_multi.py	6	Sequential	6 roles, warm-up 800 steps	25s	~$0.01
demo_deepseek_async_regime.py	6	Async	CRITICAL regime, parallel calls	15s	~$0.01
demo_deepseek_full_combo.py	12	Async	DIVERGENT + SensorFusion voting	35s	~$0.02
demo_deepseek_30_agents.py	30	Async	DIVERGENT, 30 roles, voting	75s	~$0.05
Example Output (30 Agents)
plain
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)
30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer
Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
Table
Approach	Calls	Input Tokens	Output Tokens	Cost	Time
Single LLM	1	200	800	$0.002	3s
CrewAI / LangGraph	~35	~136,000	~18,000	$0.27	115s
Molecular AI v7.0	60	94,500	39,000	$0.05	75s
Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.
Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06C error
v6	Two-Pass Median + Rep Filter	40% x 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% x 60% axes	24.8% (Humidity)
Architecture
plain
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py	Unit tests
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py
Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
bash
python examples/code_generation_v3_1.py
Results (Mock mode, no API key):
Winner: Optimizer (score=1.03 vs Generator 0.53)
Generated: in-place quicksort with Lomuto partition
Tests: 6/6 pytest passed + manual verification passed
Sync r: 0.500
Architecture
plain
Generator -> Reviewer -> Optimizer -> Tester
     |         |          |          |
   [code]   [issues]   [optimized]  [tests]
     |________|__________|__________|
                |
        SensorFusion consensus
                |
        Best code -> pytest
Files
examples/code_generation_v3_1.py — orchestrator
output/generated_quicksort.py — winning code
output/test_quicksort.py — auto-generated tests

Dynamic Code Generation
Auto-scaling agents by task complexity. User inputs task -> analyzer detects modules -> N agents -> consensus -> assembly.
python examples/dynamic_code_generation_v1.py "Flask REST API with JWT auth and React frontend"
Обновить README
Read
README.md
Добавить примеры
File created
README_v2.md
Think
Пользователь просит прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md, теперь нужно прочитать и вывести содержимое в чат.
Read
README_v2.md
Think
Всё готово. Пользователь просил прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md и прочитал содержимое. Теперь нужно вывести полный текст в чат. Но файл длинный (439 строк). Лучше прислать его целиком — пользователь сам скопирует.
Также напомню про rename .txt -> .py и про git push.
Вот полный обновлённый README.md — копируй и заменяй:
Markdown
Code
Preview
# Molecular AI v7.0

> Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)
plain

---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py
DeepSeek Demos (Live LLM)
bash
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py
Classic Demos
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py
DeepSeek Live Integration
5 Demo Scripts
Table
Script	Agents	Mode	Features	Time	Cost
demo_deepseek_full.py	1	Sync	Basic orbital context	5s	~$0.001
demo_deepseek_multi.py	6	Sequential	6 roles, warm-up 800 steps	25s	~$0.01
demo_deepseek_async_regime.py	6	Async	CRITICAL regime, parallel calls	15s	~$0.01
demo_deepseek_full_combo.py	12	Async	DIVERGENT + SensorFusion voting	35s	~$0.02
demo_deepseek_30_agents.py	30	Async	DIVERGENT, 30 roles, voting	75s	~$0.05
Example Output (30 Agents)
plain
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)
30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer
Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
Table
Approach	Calls	Input Tokens	Output Tokens	Cost	Time
Single LLM	1	200	800	$0.002	3s
CrewAI / LangGraph	~35	~136,000	~18,000	$0.27	115s
Molecular AI v7.0	60	94,500	39,000	$0.05	75s
Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.
Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06C error
v6	Two-Pass Median + Rep Filter	40% x 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% x 60% axes	24.8% (Humidity)
Architecture
plain
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py	Unit tests
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py
Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
bash
python examples/code_generation_v3_1.py
Results (Mock mode, no API key):
Winner: Optimizer (score=1.03 vs Generator 0.53)
Generated: in-place quicksort with Lomuto partition
Tests: 6/6 pytest passed + manual verification passed
Sync r: 0.500
Architecture
plain
Generator -> Reviewer -> Optimizer -> Tester
     |         |          |          |
   [code]   [issues]   [optimized]  [tests]
     |________|__________|__________|
                |
        SensorFusion consensus
                |
        Best code -> pytest
Files
examples/code_generation_v3_1.py — orchestrator
output/generated_quicksort.py — winning code
output/test_quicksort.py — auto-generated tests
Dynamic Code Generation
Auto-scaling agents by task complexity. User inputs task -> analyzer detects modules -> N agents -> consensus -> assembly.
bash
python examples/dynamic_code_generation_v1.py "Flask REST API with JWT auth and React frontend"
Results:
Task: Flask REST API with JWT auth and React frontend
Detected: 3 modules (backend, frontend, auth)
Agents: 3 (auto-scaled)
Sync r: 0.999
Output: output/project/ with README.md + requirements.txt

Обновить README
Read
README.md
Добавить примеры
File created
README_v2.md
Think
Пользователь просит прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md, теперь нужно прочитать и вывести содержимое в чат.
Read
README_v2.md
Think
Всё готово. Пользователь просил прислать код README в чат, чтобы он заменил файл. Я уже записал его в README_v2.md и прочитал содержимое. Теперь нужно вывести полный текст в чат. Но файл длинный (439 строк). Лучше прислать его целиком — пользователь сам скопирует.
Также напомню про rename .txt -> .py и про git push.
Вот полный обновлённый README.md — копируй и заменяй:
Markdown
Code
Preview
# Molecular AI v7.0

> Decentralized multi-agent intelligence via Kuramoto synchronization, shared orbital resonance, and live LLM consensus.

[![Tests](https://github.com/aknazev8941-web/molecular-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/aknazev8941-web/molecular-ai/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Release](https://img.shields.io/badge/release-v0.4.0-orange)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing. Agents synchronize via shared orbital fields (16-float frequency vectors) instead of exchanging text — delivering **81% token savings** vs classical star topology.

---

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | **81% savings vs CrewAI/LangGraph** (5.3x cheaper) |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents), r ~ 0.56 (30 agents, DIVERGENT) |
| **Scalability** | Tested up to **100 agents** (simulation), **30 agents** (live LLM) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in **75 sec** |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |
| **Code Generation** | 6/6 pytest passed, multi-agent consensus |

---

## What's New in v7.0

- **Live DeepSeek Integration** — 5 demo scripts from 1 to 30 agents
- **Async Multi-Agent LLM Calls** — `asyncio.gather()`, 4x speedup
- **ConvergenceRegime Switching** — LINEAR / CRITICAL / DIVERGENT on-the-fly
- **SensorFusion Voting Consensus** — 30 experts vote, median-filtered, reputation-weighted
- **Token Economy Benchmark** — $0.05 vs $0.27 CrewAI for same task

---

## Architecture
┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌──────┼──────┐
▼      ▼      ▼
Agent 0  Agent 1  Agent N
(omega,theta,mood,spin)         (omega,theta,mood,spin)
│      │      │
└──────┴──────┘
│
Shared Field
(16-float frequency vector)
plain

---

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py
DeepSeek Demos (Live LLM)
bash
# Set your API key
set DEEPSEEK_API_KEY=sk-...        # Windows
export DEEPSEEK_API_KEY=sk-...     # Linux/Mac

# 1 agent — basic demo
python examples/demo_deepseek_full.py

# 6 agents — sequential multi-role
python examples/demo_deepseek_multi.py

# 6 agents — async + ConvergenceRegime (CRITICAL/DIVERGENT)
python examples/demo_deepseek_async_regime.py

# 12 agents — full combo: async + regime + SensorFusion voting
python examples/demo_deepseek_full_combo.py

# 30 agents — mega demo: Mars colony blueprint with 30 experts
python examples/demo_deepseek_30_agents.py
Classic Demos
bash
# Brainstorm with 6 agents
python examples/brainstorm.py

# Scaling test (3 -> 100 agents)
python examples/scaling_auto.py

# Sensor fusion 1D (Median + MAD)
python examples/sensor_fusion_v8.py

# Sensor fusion 5D + reputation
python examples/sensor_fusion_multidim_reputation_v7.py

# Multi-agent code generation (quicksort, 6/6 tests passed)
python examples/code_generation_v3_1.py
DeepSeek Live Integration
5 Demo Scripts
Table
Script	Agents	Mode	Features	Time	Cost
demo_deepseek_full.py	1	Sync	Basic orbital context	5s	~$0.001
demo_deepseek_multi.py	6	Sequential	6 roles, warm-up 800 steps	25s	~$0.01
demo_deepseek_async_regime.py	6	Async	CRITICAL regime, parallel calls	15s	~$0.01
demo_deepseek_full_combo.py	12	Async	DIVERGENT + SensorFusion voting	35s	~$0.02
demo_deepseek_30_agents.py	30	Async	DIVERGENT, 30 roles, voting	75s	~$0.05
Example Output (30 Agents)
plain
[PHASE 4] Generation round — 30 parallel async calls
  Agent  0 [Biologist     ] | mood=+1.00 | spin=+1.00
  Agent  1 [Engineer      ] | mood=+1.00 | spin=+1.00
  ...
  Agent 29 [Game_Designer ] | mood=+1.00 | spin=+1.00
  [OK] Generation done in 39.2s

[PHASE 5] SensorFusion voting — 30 parallel async evaluations
  [OK] Voting done in 36.1s
  Voter  0 [Biologist     ]: parsed 30 ratings
  ...
  Voter 29 [Game_Designer ]: parsed 30 ratings

[PHASE 6] SensorFusion robust consensus
  Top 10 consensus scores (median-filtered):
    #1 Proposal 29 [Game_Designer ]: 8.00 <<< WINNER
    #2 Proposal  1 [Engineer      ]: 7.67
    #3 Proposal 15 [Journalist    ]: 7.67
    ...
  [WINNER] Proposal 29 — Game_Designer
  Most reliable voter: Chemist (avg rep: 0.87)
30 Agent Roles
Biologist, Engineer, Economist, Sociologist, Futurist, Critic, Physicist, Medic, Architect, Agronomist, Diplomat, Psychologist, Lawyer, Ethicist, Artist, Journalist, Chemist, Roboticist, Geologist, Climatologist, Historian, Philosopher, Educator, Security, Logistician, Nutritionist, AI_Researcher, Geneticist, Urban_Planner, Game_Designer
Token Economy: 81% Savings vs CrewAI
Cost Comparison (30 agents, Mars Colony task)
Table
Approach	Calls	Input Tokens	Output Tokens	Cost	Time
Single LLM	1	200	800	$0.002	3s
CrewAI / LangGraph	~35	~136,000	~18,000	$0.27	115s
Molecular AI v7.0	60	94,500	39,000	$0.05	75s
Why cheaper?
Agents do NOT exchange text — they sync via 16-float orbital vectors (~0 tokens)
Voting uses compressed summaries (100 chars vs 600 chars full text)
No orchestrator — consensus via SensorFusion (code, not LLM)
Async parallel — 60 calls in 75 sec vs sequential 115 sec
Savings: 81% ($0.22 absolute) — 5.3x cheaper than CrewAI for same quality.
Sensor Fusion
Multi-dimensional robust consensus with per-axis reputation and two-pass median filtering.
Results v7 (SensorFusionLayer)
Table
Version	Method	Outlier Load	Best Improvement
v2	Median + MAD	20% agents	0.06C error
v6	Two-Pass Median + Rep Filter	40% x 60% axes	24.8% (Humidity)
v7	SensorFusionLayer (core module)	40% x 60% axes	24.8% (Humidity)
Architecture
plain
Raw Sensors -> Two-Pass Median Filter -> Per-Axis Reputation -> Median Consensus
     |___________________________________________|
Two-pass median: breakdown point ~50% outliers
Per-axis reputation: min_rep=0.5, window=50 rounds
Consensus: median (not weighted mean), resistant to residual outliers
Files
Table
File	Description
core/sensor_fusion.py	Reusable SensorFusionLayer module
examples/sensor_fusion_multidim_reputation_v7.py	5D demo with 20 agents
tests/test_sensor_fusion.py	Unit tests
bash
pytest tests/test_sensor_fusion.py -v
python examples/sensor_fusion_multidim_reputation_v7.py
Multi-Agent Code Generation
4 agents (Generator, Reviewer, Optimizer, Tester) generate code via orbital consensus.
bash
python examples/code_generation_v3_1.py
Results (Mock mode, no API key):
Winner: Optimizer (score=1.03 vs Generator 0.53)
Generated: in-place quicksort with Lomuto partition
Tests: 6/6 pytest passed + manual verification passed
Sync r: 0.500
Architecture
plain
Generator -> Reviewer -> Optimizer -> Tester
     |         |          |          |
   [code]   [issues]   [optimized]  [tests]
     |________|__________|__________|
                |
        SensorFusion consensus
                |
        Best code -> pytest
Files
examples/code_generation_v3_1.py — orchestrator
output/generated_quicksort.py — winning code
output/test_quicksort.py — auto-generated tests
Dynamic Code Generation
Auto-scaling agents by task complexity. User inputs task -> analyzer detects modules -> N agents -> consensus -> assembly.
bash
python examples/dynamic_code_generation_v1.py "Flask REST API with JWT auth and React frontend"
Results:
plain
Task: Flask REST API with JWT auth and React frontend
Detected: 3 modules (backend, frontend, auth)
Agents: 3 (auto-scaled)
Sync r: 0.999
Output: output/project/ with README.md + requirements.txt
Scaling
| Task                  | Modules                                          | Agents |
| --------------------- | ------------------------------------------------ | ------ |
| quicksort             | generic                                          | 1      |
| Flask API with JWT    | backend, auth                                    | 2      |
| Flask + React + tests | backend, frontend, auth, tests                   | 4      |
| Fullstack with Docker | backend, frontend, auth, db, tests, docs, config | 7      |

Architecture
User Task -> Analyzer -> [module1, module2, ...] -> N agents
                                              |
                                    Orbital sync (r > 0.99)
                                              |
                              [Agent 1: backend] [Agent 2: frontend] [Agent 3: auth]
                                              |
                                    Project Assembly -> output/project/

  Files
examples/dynamic_code_generation_v1.py — orchestrator
output/project/ — generated artifacts

Async LLM + ConvergenceRegime
Async LLM Calls
Parallel API calls via asyncio.gather() — 4x speedup vs sequential.
python examples/code_generation_v4_1.py
Architecture:
Agent 0 --> API --|
Agent 1 --> API --|---> asyncio.gather() -> all responses in 2 sec
Agent 2 --> API --|
Agent 3 --> API --|
Files
adapters/async_base.py — AsyncLLMAdapter with semaphore-based rate limiting
examples/code_generation_v4_1.py — async code generation, code-only winner
ConvergenceRegime
Three regimes for controlled exploration vs exploitation:
| Regime    | noise/dt | Sync r    | Use Case                          |
| --------- | -------- | --------- | --------------------------------- |
| LINEAR    | < 0.5    | > 0.9     | Stable consensus, code generation |
| CRITICAL  | ~ 1.0    | ~ 0.7-0.9 | Brainstorm, exploration           |
| DIVERGENT | > 2.0    | < 0.5     | Maximum creativity, chaos         |
python examples/brainstorm_regime.py
Results:
CRITICAL: sync r = 0.786 (diverse ideas)
LINEAR: sync r = 0.769 (stable consensus)
DIVERGENT: sync r = 0.562 (maximum chaos, 30 agents)
Files
core/convergence_regime.py — regime detection and switching
examples/brainstorm_regime.py — demo with regime switching
examples/demo_deepseek_async_regime.py — live LLM + regime
examples/demo_deepseek_full_combo.py — 12 agents + regime + voting
examples/demo_deepseek_30_agents.py — 30 agents + DIVERGENT + voting
Supported LLM Adapters
| Provider     | Models                   | Status                         |
| ------------ | ------------------------ | ------------------------------ |
| OpenAI       | GPT-4o, GPT-4o-mini      | Tested                         |
| Anthropic    | Claude 3.5 Sonnet, Haiku | Tested                         |
| Google       | Gemini 1.5 Flash         | Adapter ready, keys not tested |
| **DeepSeek** | **DeepSeek API**         | **Tested — 5 demo scripts**    |
| Ollama       | Local LLM via HTTP       | Tested                         |
| Mock         | Offline testing          | Generates meaningful choices   |

Scientific Foundation
Kuramoto model — synchronization of coupled oscillators
Hebbian plasticity — "neurons that fire together, wire together" (sparse k=4)
Buzsaki's rhythms — hierarchical brain oscillations (4 levels)
TD-learning — reward + value_weights + goal detection
Emotional dynamics — mood, arousal, spin (excitatory 85%)
Project Structure
molecular_ai/
├── core/
│   ├── sensor_fusion.py       # SensorFusionLayer (v0.2.0)
│   ├── convergence_regime.py  # LINEAR/CRITICAL/DIVERGENT switching
│   ├── system.py              # MolecularSystem orchestrator
│   ├── orbital.py             # HierarchicalOrbital (4 levels)
│   ├── agent.py               # Agent + FrequencyCodec
│   ├── plasticity.py          # SparseHebbianPlasticity
│   ├── reward.py              # TD-learning reward system
│   ├── memory.py              # WorkingMemory (capacity=5)
│   ├── attention.py           # AttentionModulator
│   ├── emotional_agent.py     # Mood + arousal dynamics
│   └── ...
├── adapters/                   # LLM adapters (OpenAI, Anthropic, Gemini, DeepSeek, etc.)
│   ├── base.py
│   ├── openai_adapter.py
│   ├── anthropic_adapter.py
│   ├── deepseek_adapter.py
│   ├── async_base.py          # AsyncLLMAdapter
│   └── ...
├── examples/                   # Demos and experiments
│   ├── demo_deepseek_full.py
│   ├── demo_deepseek_multi.py
│   ├── demo_deepseek_async_regime.py
│   ├── demo_deepseek_full_combo.py
│   ├── demo_deepseek_30_agents.py
│   ├── brainstorm.py
│   ├── brainstorm_regime.py
│   ├── scaling_auto.py
│   ├── sensor_fusion_v8.py
│   ├── sensor_fusion_multidim_reputation_v7.py
│   ├── code_generation_v3_1.py
│   ├── code_generation_v4_1.py
│   └── dynamic_code_generation_v1.py
├── tests/                      # pytest suite (10+ tests)
├── output/                     # Generated artifacts
└── .github/workflows/          # CI/CD (Python 3.10-3.13)

Status
Research / Proof-of-Concept
This is an experimental architecture exploring resonance-based multi-agent coordination. Production readiness requires GPU acceleration, distributed deployment, and further validation.
Roadmap
| # | Topic                               | Priority | Status               |
| - | ----------------------------------- | -------- | -------------------- |
| 1 | GPU Acceleration (CUDA/Numba)       | High     | Open                 |
| 2 | Distributed Deployment (Redis/gRPC) | High     | Open                 |
| 3 | **Async LLM Integration**           | Medium   | **Done (v7.0)**      |
| 4 | **Live LLM (DeepSeek)**             | Medium   | **Done (v7.0)**      |
| 5 | **SensorFusion Voting Consensus**   | Medium   | **Done (v7.0)**      |
| 6 | Multi-Agent Code Generation         | Medium   | v3.1 done, 6/6 tests |
| 7 | Community Publication               | Medium   | Open                 |

License
MIT — see LICENSE
