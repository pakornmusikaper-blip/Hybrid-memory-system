# Hybrid Memory System v2 — The Substrate Agent

> *v2.2 now with Consciousness Bridge — bidirectional communication between conscious and subconscious*

> *v2.1 with Growth System: automatic belief validation, pattern recognition, contradiction detection*

> *"A memory system that doesn't just store — it thinks, learns, and grows."*

## What's New in v2

v2 introduces the **Substrate Agent** — a background intelligence layer that runs continuously and autonomously learns from context.

### The Core Innovation: Subconscious for AI

Every human has two thinking systems:
1. **Conscious** — deliberate, focused, aware of its own reasoning
2. **Subconscious** — background, continuous, develops understanding without awareness

The Substrate Agent is the AI equivalent of the subconscious. It runs all the time. It learns. It grows. It prepares context. But it never interrupts — it only serves when called upon.

## Architecture

```
┌─────────────────────────────────────────────┐
│                 SUBSTRATE AGENT               │
│  ┌───────────────────────────────────────┐  │
│  │  Local Model (Qwen 1.8B/0.5B)        │  │
│  │  • Always running                      │  │
│  │  • Absorbs context continuously       │  │
│  │  • Develops own understanding          │  │
│  │  • Prepares anticipatory context        │  │
│  │  • Grows through experience            │  │
│  └───────────────────────────────────────┘  │
│                    ↑                          │
│         own_memory/ (its own beliefs)       │
│                    ↓                          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│         MEMORY LAYERS (Passive)              │
│  Sources → Structured → Wiki → Search      │
└─────────────────────────────────────────────┘
```

## Features

### Six Core Operations

| Operation | Description |
|-----------|-------------|
| **Context Weaving** | Combines context from multiple memory layers |
| **Connection Forging** | Finds implicit connections between knowledge |
| **Anticipatory Preparation** | Pre-prepares context for likely scenarios |
| **Belief Formation** | Develops understanding that persists over time |
| **Pattern Recognition** | Identifies recurring themes and behaviors |
| **Reality Validation** | Validates beliefs against known facts |

### v2.1 Growth System

| Feature | Description |
|---------|-------------|
| **Automatic Validation** | Validates beliefs against facts automatically |
| **Confidence Decay** | Old beliefs decay over time unless validated |
| **Contradiction Detection** | Finds beliefs that contradict each other |
| **Pattern Recognition** | Identifies recurring subject patterns |
| **Growth Tracking** | Tracks learning progress over time |

### v2.2 Consciousness Bridge

| Feature | Description |
|---------|-------------|
| **Bidirectional Communication** | Conscious and substrate exchange messages |
| **Intuition Surfacing** | Substrate surfaces unexpected insights proactively |
| **Belief Synchronization** | Beliefs flow between layers with tracking |
| **Correction Protocol** | Conscious can correct substrate beliefs |
| **Priority Messaging** | High-priority intuitions surface immediately |

### Own Memory

The Substrate Agent has its own private memory layer (`substrate/own_memory/`) where it stores:
- `beliefs/` — Things the agent believes about the domain
- `patterns/` — Recognized patterns and trends
- `anticipation_cache/` — Pre-prepared context bundles
- `growth_log/` — History of learning and growth

### Model Support

v2 supports multiple local models:
- **Qwen 0.5B** — Fast, works on CPU (with 4-bit quantization)
- **Qwen 1.5B** — Better quality, needs more memory
- **Qwen 1.8B** — Best local quality
- **Phi-3-mini** — Excellent reasoning capabilities
- **Mistral 7B** — Best balance (needs GPU)

## Requirements

### Hardware

| Mode | Requirements |
|------|-------------|
| **CPU (4-bit)** | 8GB+ RAM, Qwen 0.5B only |
| **CPU (full)** | 16GB+ RAM, slow inference |
| **GPU** | NVIDIA GPU with 6GB+ VRAM recommended |

### Software

```
Python >= 3.10
torch >= 2.0.0
transformers >= 4.35.0
accelerate >= 0.25.0
bitsandbytes >= 0.41.0 (for 4-bit quantization)
pyyaml >= 6.0
```

## Installation

```bash
# Clone the repository
git clone https://github.com/pakornmusikaper-blip/Hybrid-memory-system.git
cd Hybrid-memory-system/v2

# Install dependencies
pip install torch transformers accelerate bitsandbytes pyyaml

# Download a model (example: Qwen 0.5B)
huggingface-cli download Qwen/Qwen2-0.5B
```

## Quick Start

```bash
# Initialize the agent
cd v2
export PYTHONPATH=/path/to/v2

# Run the agent
python -m substrate run

# Query the agent
python -m substrate serve "What do you know about my projects?"

# Check status
python -m substrate status

# View beliefs
python -m substrate beliefs
```

## Configuration

Edit `substrate/config/default.yaml` to customize:

```yaml
model:
  name: Qwen/Qwen2-0.5B  # or Qwen/Qwen2-1.5B, etc.
  quantization: 4-bit     # none, 8-bit, or 4-bit

runtime:
  device: cpu  # or cuda if you have GPU
  max_memory_gb: 8

operation:
  cycle_seconds: 60
  fallback_mode: false  # true for development without model
```

## API Usage

```python
from pathlib import Path
from substrate.agent.core import SubstrateAgent

# Initialize
memory_root = Path("/path/to/knowledge-system")
agent = SubstrateAgent(memory_root)

# Start background processing
agent.start()

# Serve a query (from conscious layer)
result = agent.serve("What is the current state of Project X?")
print(result)

# Absorb new context
agent.absorb({
    "source": "email",
    "content": "User decided to pivot Project X direction",
    "scenario": "project_x_pivot"
})

# Stop when done
agent.stop()
```

## Directory Structure

```
v2/
├── substrate/
│   ├── __main__.py           # CLI entry point
│   ├── config/
│   │   └── default.yaml      # Model & operation config
│   ├── agent/
│   │   ├── __init__.py
│   │   └── core.py           # SubstrateAgent class
│   └── own_memory/
│       ├── beliefs/          # Belief storage
│       ├── patterns/          # Pattern storage
│       ├── anticipation_cache/ # Pre-prepared context
│       └── growth_log/       # Growth tracking
├── SUBSTRATE-DESIGN.md       # Full design document
├── IMPLEMENTATION.md         # Technical implementation
└── README.md                 # This file
```

## Development Status

v2.1 is in active development. The core architecture and growth system are complete and tested.

### Version History

- **v2.0** — Core Substrate Agent with Qwen model support
- **v2.1** — Growth System: belief validation, pattern recognition, contradiction detection
- **v2.2** — Consciousness Bridge: bidirectional communication, intuition surfacing

### Known Limitations

- **CPU inference is slow** — For interactive use, a GPU is recommended
- **4-bit quantization** helps significantly but may reduce quality slightly
- **Model download** requires HuggingFace account for higher rate limits

### Roadmap

- [x] v2.0 Core architecture
- [x] v2.0 Model loading (Qwen 0.5B, 1.5B)
- [x] v2.0 Belief formation
- [x] v2.0 Anticipation caching
- [x] v2.1 Growth System
- [x] v2.1 Belief validation
- [x] v2.1 Pattern recognition
- [x] v2.2 Consciousness Bridge
- [x] v2.2 Intuition surfacing
- [ ] GPU acceleration
- [ ] Model fine-tuning integration
- [ ] Web UI for monitoring

## Contributing

Contributions welcome! Please read the design document first and open an issue to discuss major changes.

## License

MIT — same as v1

---

*Built with the belief that memory systems should be alive, not just stored.*
