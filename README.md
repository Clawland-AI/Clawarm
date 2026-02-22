# ClawArm — AI-Powered Robotic Arm Control via OpenClaw

[Clawland-AI](https://github.com/Clawland-AI) · [OpenClaw](https://openclaw.ai/) · [pyAgxArm](https://github.com/agilexrobotics/pyAgxArm)

Control NERO (7-DOF) and Piper (6-DOF) robotic arms with natural language through OpenClaw. Say what you want the arm to do — ClawArm generates and executes the motion.

> Inspired by [AgileX Robotics' OpenClaw + NERO tutorial](https://mp.weixin.qq.com/s/V3EQ6E3ikN3srCzXrCOtiw).

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
   │  pyAgxArm   │  CAN bus communication
   │  Driver      │
   └──────┬──────┘
          ▼
      Robot Arm
```

**Two control modes:**

- **Skill Mode**: OpenClaw reads the `agx-arm-codegen` skill, generates a complete Python script, and executes it. Best for complex, multi-step sequences.
- **Plugin Mode**: The ClawArm OpenClaw plugin provides `arm_move`, `arm_status`, and `arm_stop` tools that call the Python bridge in real time. Best for interactive control.

## Quick Start

### Prerequisites

- Linux with CAN interface (SocketCAN)
- Python 3.10+
- [OpenClaw](https://openclaw.ai/) installed
- [pyAgxArm](https://github.com/agilexrobotics/pyAgxArm) installed
- NERO or Piper arm connected via CAN bus

### 1. Clone and install

```bash
git clone https://github.com/Clawland-AI/clawarm.git
cd clawarm
pip install -e ".[dev]"
pip install pyAgxArm  # or: pip install -e ".[arm]"
```

### 2. Activate CAN

```bash
sudo bash setup/activate_can.sh
```

### 3. Start the bridge server

```bash
# Real hardware
clawarm-bridge

# Mock mode (no hardware needed)
CLAWARM_MOCK=true clawarm-bridge
```

### 4. Install the OpenClaw skill

```bash
# Copy skill to OpenClaw workspace
cp -r skills/agx-arm-codegen ~/.openclaw/skills/

# Or for the plugin approach, install the plugin
cd plugin && npm install
openclaw plugins install ./plugin
```

### 5. Talk to the arm

Open OpenClaw web UI or send a message via Feishu/Telegram:

```
> Move joint 1 to 0.5 radians, then return to zero position
> Pick up the object at position [0.3, 0.1, 0.2] and place it at [0.3, -0.1, 0.2]
> Draw a small circle in the XY plane at height 0.3m
```

## Project Structure

```
clawarm/
├── skills/                   OpenClaw Skills (Skill Mode)
│   └── agx-arm-codegen/      Natural-language → Python code generation
├── plugin/                   OpenClaw Plugin (Plugin Mode)
│   └── src/tools/            arm_connect, arm_status, arm_move, arm_stop
├── bridge/                   Python Bridge Server (FastAPI)
│   ├── drivers/              agx_driver (real) + mock_driver (dev)
│   └── safety.py             Joint limits, workspace bounds, velocity caps
├── examples/                 Demo scripts
├── workspace/                OpenClaw workspace templates (AGENTS.md, SOUL.md)
├── config/                   OpenClaw configuration templates
├── setup/                    Installation and CAN activation scripts
├── docs/                     Architecture, quickstart, safety docs
└── tests/                    Bridge server and safety tests
```

## Configuration

Copy the example config and adjust for your setup:

```bash
cp config/openclaw.example.json ~/.openclaw/openclaw.json
```

Key settings in `openclaw.json`:

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

## Supported Arms

| Arm | DOF | SDK | Joint Angles | Cartesian |
|-----|-----|-----|-------------|-----------|
| NERO | 7 | pyAgxArm | `move_j([j1..j7])` rad | `move_p/l([x,y,z,r,p,y])` m/rad |
| Piper | 6 | pyAgxArm | `move_j([j1..j6])` rad | `move_p/l([x,y,z,r,p,y])` m/rad |

## Safety

**ClawArm controls real hardware. Read [SECURITY.md](SECURITY.md) before use.**

- Safety layer validates all commands before they reach the arm
- Joint angle limits enforced per robot type
- Workspace boundary box prevents out-of-range motion
- Velocity capped at configurable percentage (default 80%)
- Emergency stop available via API, OpenClaw tool, and physical button

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
# Start bridge server in mock mode
docker compose up bridge-mock

# Start bridge server for real hardware (requires --privileged for CAN)
docker compose up bridge
```

## License

MIT — see [LICENSE](LICENSE).

Built by [Clawland-AI](https://github.com/Clawland-AI) · Powered by [OpenClaw](https://openclaw.ai/) and [pyAgxArm](https://github.com/agilexrobotics/pyAgxArm)
