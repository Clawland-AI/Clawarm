<p align="center">
  <img src="assets/clawarm-logo.png" alt="ClawArm Logo" width="480">
</p>

<p align="center">
  <strong>AI-Powered Robotic Arm Control via OpenClaw</strong><br>
  Say what you want the arm to do. ClawArm makes it happen.
</p>

<p align="center">
  <a href="https://clawarm.ai">clawarm.ai</a> &middot;
  <a href="https://github.com/Clawland-AI/clawarm">GitHub</a> &middot;
  <a href="docs/architecture.md">Architecture</a> &middot;
  <a href="docs/safety.md">Safety Guide</a>
</p>

<p align="center">
  <a href="https://clawarm.ai"><img src="https://img.shields.io/badge/website-clawarm.ai-blue" alt="Website"></a>
  <a href="https://github.com/Clawland-AI/clawarm/actions"><img src="https://github.com/Clawland-AI/clawarm/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Clawland-AI/clawarm/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Clawland-AI/clawarm" alt="License"></a>
  <a href="https://github.com/Clawland-AI/clawarm"><img src="https://img.shields.io/github/stars/Clawland-AI/clawarm?style=social" alt="Stars"></a>
</p>

---

<p align="center">
  <img src="assets/clawarm-banner.png" alt="ClawArm — Natural language to robotic arm motion" width="100%">
</p>

## What is ClawArm?

ClawArm bridges **natural language** and **physical robotic arm motion**. Built on top of [OpenClaw](https://openclaw.ai/), it lets you control NERO (7-DOF) and Piper (6-DOF) robotic arms by simply describing what you want — no manual joint calculations, no coordinate math.

### Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language Control** | "Pick up the red block" becomes actual robot motion |
| **Two Control Modes** | Skill mode (code generation) + Plugin mode (real-time tools) |
| **Safety Layer** | Joint limits, workspace bounds, velocity caps — every command is validated |
| **Mock Mode** | Develop and test without physical hardware |
| **Multi-Arm Support** | NERO 7-DOF and Piper 6-DOF out of the box |
| **OpenClaw Integration** | Works with OpenClaw's web UI, Feishu, Telegram, and more |

---

## How It Works

```
"Move the arm to pick up the red block"
         │
         ▼
   ┌─────────────┐
   │  OpenClaw    │  AI agent interprets intent
   │  Gateway     │
   └──────┬──────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
 Skill Mode   Plugin Mode
 (codegen)    (real-time)
    │            │
    ▼            ▼
 Python       Bridge API
 Script       :8420
    │            │
    └─────┬──────┘
          ▼
   ┌─────────────┐
   │  Safety      │  Joint limits, workspace bounds
   │  Layer       │
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │  Arm Driver  │  CAN bus communication
   └──────┬──────┘
          ▼
      Robot Arm
```

- **Skill Mode**: OpenClaw reads the `agx-arm-codegen` skill, generates a complete Python control script, and executes it. Best for complex, multi-step sequences.
- **Plugin Mode**: The ClawArm plugin provides `arm_move`, `arm_status`, and `arm_stop` tools that call the bridge server in real time. Best for interactive step-by-step control.

---

## Quick Start

### Prerequisites

- Linux with CAN interface (SocketCAN)
- Python 3.10+
- [OpenClaw](https://openclaw.ai/) installed
- Robotic arm connected via CAN bus

### 1. Clone and install

```bash
git clone https://github.com/Clawland-AI/clawarm.git
cd clawarm
pip install -e ".[dev,arm]"
```

### 2. Activate CAN

```bash
sudo bash setup/activate_can.sh
```

### 3. Start the bridge server

```bash
# With real hardware
clawarm-bridge

# Without hardware (mock mode for development)
CLAWARM_MOCK=true clawarm-bridge
```

### 4. Install the OpenClaw skill

```bash
# Copy skill to OpenClaw workspace
cp -r skills/agx-arm-codegen ~/.openclaw/skills/

# Or install the plugin for real-time tool access
cd plugin && npm install
openclaw plugins install ./plugin
```

### 5. Talk to the arm

Open the OpenClaw web UI or send a message via your configured channel:

```
> Move joint 1 to 0.5 radians, then return to zero position
> Pick up the object at position [0.3, 0.1, 0.2] and place it at [0.3, -0.1, 0.2]
> Draw a small circle in the XY plane at height 0.3m
```

---

## Project Structure

```
clawarm/
├── skills/                   OpenClaw Skills (Skill Mode)
│   └── agx-arm-codegen/      Natural-language → Python code generation
├── plugin/                   OpenClaw Plugin (Plugin Mode)
│   └── src/tools/            arm_connect, arm_status, arm_move, arm_stop
├── bridge/                   Python Bridge Server (FastAPI)
│   ├── drivers/              Real driver + mock driver for dev
│   └── safety.py             Joint limits, workspace bounds, velocity caps
├── examples/                 Demo scripts
├── workspace/                OpenClaw workspace templates (AGENTS.md, SOUL.md)
├── config/                   OpenClaw configuration templates
├── setup/                    Installation and CAN activation scripts
├── docs/                     Architecture, quickstart, safety docs
└── tests/                    Bridge server and safety tests
```

---

## Supported Arms

| Arm | DOF | Joint Control | Cartesian Control |
|-----|-----|---------------|-------------------|
| **NERO** | 7 | `move_j([j1..j7])` radians | `move_p/l([x,y,z,r,p,y])` meters/radians |
| **Piper** | 6 | `move_j([j1..j6])` radians | `move_p/l([x,y,z,r,p,y])` meters/radians |

---

## Configuration

```bash
cp config/openclaw.example.json ~/.openclaw/openclaw.json
```

Key settings:

```jsonc
{
  "plugins": {
    "entries": {
      "clawarm": {
        "enabled": true,
        "config": {
          "bridgeUrl": "http://localhost:8420",
          "defaultRobot": "nero",
          "safetyEnabled": true
        }
      }
    }
  }
}
```

---

## Safety

> **ClawArm controls real hardware.** Read [SECURITY.md](SECURITY.md) before use.

- Safety layer validates **all commands** before they reach the arm
- Per-robot-type joint angle limits enforced automatically
- Configurable Cartesian workspace boundary box
- Velocity capped at configurable percentage (default 80%)
- Emergency stop via API, OpenClaw tool, or physical button

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (uses mock driver, no hardware needed)
pytest

# Lint
ruff check .
```

## Docker

```bash
# Mock mode (no hardware)
docker compose up bridge-mock

# Real hardware (requires --privileged for CAN access)
docker compose up bridge
```

---

## License

MIT — see [LICENSE](LICENSE).

<p align="center">
  <a href="https://clawarm.ai">clawarm.ai</a> &middot;
  Built by <a href="https://github.com/Clawland-AI">Clawland AI</a> &middot;
  Powered by <a href="https://openclaw.ai/">OpenClaw</a>
</p>
