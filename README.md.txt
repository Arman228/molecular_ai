# Molecular AI v6.0

&gt; Decentralized multi-agent intelligence via Kuramoto synchronization and shared orbital resonance.

[![Tests](https://img.shields.io/badge/tests-10%2F10%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

Inspired by neural oscillations in the brain (gamma, beta, alpha, delta rhythms), Molecular AI coordinates agents through **resonance**, not message passing.

## Key Results

| Metric | Value |
|--------|-------|
| **Token economy** | 50–92% savings vs classical star topology |
| **Synchronization** | r &gt; 0.99 (3 agents), r &gt; 0.75 (6 agents) |
| **Scalability** | Tested up to 100 agents |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |

## Architecture

┌─────────────────────────────────────────┐
│         Hierarchical Orbital            │
│  Gamma(3.5) → Beta(2.0) → Alpha(1.0) → Delta(0.5) │
└─────────────────────────────────────────┘
│
┌───────────────┼───────────────┐
▼               ▼               ▼
Agent 0         Agent 1         Agent N
(ω, θ, mood)   (ω, θ, mood)   (ω, θ, mood)
│               │               │
└───────────────┴───────────────┘
Shared Field
(16-float frequency vector)


## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/molecular-ai.git
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

# Token economy comparison
python examples/token_economy_v2.py
Supported LLM Adapters
OpenAI (GPT-4o, GPT-4o-mini)
Anthropic (Claude 3.5 Sonnet, Haiku)
Google Gemini (1.5 Flash)
DeepSeek
Ollama (local)
Mock (offline testing)
Scientific Foundation
Kuramoto model — synchronization of coupled oscillators
Hebbian plasticity — "neurons that fire together, wire together"
Buzsaki's rhythms — hierarchical brain oscillations
Tononi's IIT — integrated information theory
Status
🔬 Research / Proof-of-Concept
This is an experimental architecture exploring resonance-based multi-agent coordination.
Production readiness requires GPU acceleration, distributed deployment, and further validation.