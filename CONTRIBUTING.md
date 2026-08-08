# Contributing to Molecular AI

Thank you for your interest! This project explores decentralized multi-agent intelligence via Kuramoto synchronization.

## Quick Start

```bash
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai
pip install -r requirements.txt
pytest tests/ -v
python main.py

Project Structure
molecular_ai/
├── core/           # Mathematical models (Kuramoto, orbital, plasticity)
├── adapters/       # LLM connectors (OpenAI, Anthropic, Gemini, etc.)
├── tests/          # pytest suite (10 tests)
├── examples/       # Demos: brainstorm, scaling, visualization
└── docs/           # (future) Architecture deep-dives

How to Contribute
1. Bug Reports
Open an Issue with:
Python version
Steps to reproduce
Expected vs actual behavior
2. Feature Requests
Check existing Issues first. If not listed, open a new one with:
Use case
Proposed approach
Acceptance criteria
3. Code Contributions
Fork the repository
Create a branch: git checkout -b feature/your-feature
Make changes
Run tests: pytest tests/ -v (must pass 10/10)
Commit with clear message
Open a Pull Request
Code Style
Pure Python 3.10+ compatible
No external deps for core (numpy optional)
Docstrings in English or Russian
Type hints where practical
Current Priorities
See Issues:
GPU acceleration (CUDA/Numba)
Distributed deployment (Redis/gRPC)
Live LLM integration (async API calls)
Questions?
Open a Discussion or email via GitHub profile.