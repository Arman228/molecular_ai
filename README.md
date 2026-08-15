# 🧬 Molecular AI v7.0

**Decentralized multi-agent intelligence via Kuramoto synchronization**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-7.0-orange)]()

> Agents synchronize through orbital fields instead of text messages, achieving **81% token savings** compared to classical architectures (CrewAI, LangGraph).

---

## 📋 About

Molecular AI is a self-organizing multi-agent system inspired by neural oscillations in the brain. Instead of exchanging text messages, agents synchronize through **orbital fields** (16-dimensional frequency vectors).

### Key Results

| Metric | Value |
|--------|-------|
| **Token savings** | **81%** vs CrewAI/LangGraph |
| **Synchronization** | r > 0.99 (3 agents), r > 0.85 (6 agents) |
| **Scalability** | Up to 100 agents (simulation) |
| **Speed** | 2500+ steps/sec (3 agents, CPU) |
| **LLM consensus** | 30 agents async + SensorFusion voting in 75 sec |
| **Sensor Fusion** | 18.5-24.8% improvement vs IQR at 40% outlier load |

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **🌀 Kuramoto synchronization** | Agents sync through shared orbital fields |
| **🧠 Self-learning** | System remembers successful answers |
| **💻 Code generation** | Automatic project creation through agents |
| **📁 File upload** | Support for images, PDF, documents |
| **🌐 Bilingual UI** | Russian and English interface |
| **🔥 AutoSkills** | Self-created skills system |
| **⚡ MetaOptimizer** | Automatic hyperparameter optimization |
| **🧠 Sensor Fusion** | Agent consensus through sensor fusion |
| **🔧 AutoTuner** | Automatic parameter tuning based on agent count |

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────┐
│ Molecular AI v7.0 │
├─────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────┐ │
│ │ Web Interface (Flask) │ │
│ │ Russian / English · 3 modes │ │
│ └───────────────────────────────────────────┘ │
│ │ │
│ ┌───────────────────────────────────────────┐ │
│ │ Ultimate Controller │ │
│ │ (UI ↔ Core Bridge) │ │
│ └───────────────────────────────────────────┘ │
│ │ │
│ ┌───────────────────────────────────────────┐ │
│ │ MolecularSystem (Core) │ │
│ │ ┌──────────────────────────────────┐ │ │
│ │ │ 10+ agents with orbital fields │ │ │
│ │ └──────────────────────────────────┘ │ │
│ │ ┌──────────────────────────────────┐ │ │
│ │ │ Hierarchical Orbital (4 layers)│ │ │
│ │ │ Gamma → Beta → Alpha → Delta │ │ │
│ │ └──────────────────────────────────┘ │ │
│ └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘


### Orbital Layers

| Layer | Coupling | Decay | Role |
|-------|----------|-------|------|
| **Gamma** | 3.5 | 0.30 | Fast synchronization (reflexes) |
| **Beta** | 2.0 | 0.60 | Conscious thinking |
| **Alpha** | 1.0 | 0.85 | Calm state, memory |
| **Delta** | 0.5 | 0.97 | Deep integration |

---

## 🧠 Skills System (AutoSkills)

The system can **create its own skills** on demand!

| Skill | Category | Description |
|-------|-----------|-------------|
| **JSONParser** | Data | JSON parsing and validation |
| **FileProcessor** | Data | File operations (read, write, copy) |
| **CSVProcessor** | Data | CSV read/write |
| **RedisCache** | Infrastructure | LRU cache with TTL |
| **RateLimiter** | Security | Token-bucket rate limiter |
| **WebSocket** | Real-time | Connection manager |
| **DesignSystem** | UI/UX | Design system with tokens |
| **AnimationEngine** | UI/UX | Animation engine with easing |
| **ResponsiveGrid** | UI/UX | Responsive grid system |
| **ReactComponent** | Frontend | React-like component |

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/aknazev8941-web/molecular-ai.git
cd molecular-ai

# Install dependencies
pip install -r requirements.txt

# Set API key
export DEEPSEEK_API_KEY=sk-...
# or (Windows)
set DEEPSEEK_API_KEY=sk-...

Run
python main.py
Open in browser: http://localhost:5000

5000

📚 Commands
Command	Description
/help	Show all commands
/learning	Learning statistics
/rate 0.8	Rate last answer
/skill [task]	Create skill
/skills	List skills
/skill_stats	Skill statistics
/sleep	Clean weak skills
/optimize [task]	Optimize parameters
/optimize_info	Optimizer information
/apply_optimized	Apply optimized parameters
/fusion	Agent reputation matrix
/fusion_stats	Sensor fusion statistics
/tune	Auto-tune parameters
/clear	Clear chat
/agents	Agent information
/projects	Project list
/preview	Preview HTML
/info	Project information

📊 Technology Stack
Component	Technology
Core	Python 3.10+
Web Interface	Flask + HTML/CSS/JS
AI API	DeepSeek (OpenAI-compatible)
Synchronization	Kuramoto model
Knowledge Base	JSON (local)
Frontend	Vanilla JavaScript

📂 Project Structure
molecular-ai/
├── core/              # Core system
│   ├── system.py      # MolecularSystem
│   ├── agent.py       # Agent
│   ├── orbital.py     # HierarchicalOrbital
│   ├── auto_skills.py # AutoSkillEngine
│   ├── meta_optimizer.py # MetaOptimizer
│   └── sensor_fusion.py # SensorFusion
├── ui/                # Web interface
│   ├── app.py         # Flask application
│   ├── controller.py  # UltimateController
│   └── templates/
│       └── index.html # Bilingual UI
├── data/              # Data storage
├── output/            # Output files
├── main.py            # Entry point
├── requirements.txt   # Dependencies
└── README.md          # Documentation

🧪 Testing
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auto_skills.py -v

# Run with coverage
pytest tests/ --cov=core --cov=ui
Test Results
✅ 105 passed, 0 failed
🎯 100% success rate

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing)

Make your changes

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing)

Open a Pull Request

📄 License
MIT License — see LICENSE file for details.

💬 Contact
GitHub: aknazev8941-web

Project: Molecular AI

⭐ Star the Project
If you find this project useful, please give it a star on GitHub!

Made with 🧬 and ❤️

🎯 What's New in v7.0
Live DeepSeek Integration — 5 demo scripts from 1 to 30 agents

Async Multi-Agent LLM Calls — asyncio.gather(), 4x speedup

ConvergenceRegime Switching — LINEAR / CRITICAL / DIVERGENT on-the-fly

SensorFusion Voting Consensus — 30 experts vote, median-filtered

Token Economy Benchmark — $0.05 vs $0.27 CrewAI for same task

Bilingual UI — Russian and English interface

AutoSkillEngine — Self-created skills system

MetaOptimizer — Automatic hyperparameter optimization"# molecular_ai" 
