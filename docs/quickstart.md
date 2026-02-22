# Quick Start Guide

This guide walks you through setting up ClawArm from scratch.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Linux (Ubuntu 22.04+) | CAN interface requires SocketCAN |
| Python 3.10+ | For the bridge server |
| [OpenClaw](https://openclaw.ai/) | AI agent framework |
| NERO or Piper arm | Connected via CAN bus |
| CAN adapter | USB-to-CAN (e.g., CANable, Kvaser) |

## Step 1: Install ClawArm

```bash
git clone https://github.com/Clawland-AI/clawarm.git
cd clawarm
pip install -e ".[dev]"
```

## Step 2: Install pyAgxArm

```bash
# From GitHub (recommended)
git clone https://github.com/agilexrobotics/pyAgxArm.git
cd pyAgxArm && pip install . && cd ..

# Also need python-can
pip install python-can
```

## Step 3: Activate CAN Interface

Connect your CAN adapter, then:

```bash
sudo bash setup/activate_can.sh
# Default: can0 at 1Mbps

# Or specify interface and bitrate:
sudo bash setup/activate_can.sh can1 500000
```

Verify:
```bash
ifconfig can0
# Should show can0 as UP
```

## Step 4: Start the Bridge Server

```bash
# With real hardware:
clawarm-bridge

# Without hardware (mock mode):
CLAWARM_MOCK=true clawarm-bridge
```

The bridge server starts on `http://127.0.0.1:8420`. Verify:

```bash
curl http://127.0.0.1:8420/
# {"ok":true,"message":"ClawArm Bridge v0.1.0"}
```

## Step 5: Install OpenClaw Skill

```bash
# Copy skill to OpenClaw's skill directory
cp -r skills/agx-arm-codegen ~/.openclaw/skills/

# Copy workspace templates
mkdir -p ~/.openclaw/workspace-clawarm/memory
cp workspace/AGENTS.md ~/.openclaw/workspace-clawarm/
cp workspace/SOUL.md ~/.openclaw/workspace-clawarm/
```

## Step 6: Configure OpenClaw

```bash
# If starting fresh:
cp config/openclaw.example.json ~/.openclaw/openclaw.json

# Edit to set your model API key and preferences
```

Key settings to configure:
- `env.QWEN_API_KEY` — your model provider API key
- `agents.list[0].workspace` — point to `~/.openclaw/workspace-clawarm`
- `plugins.entries.clawarm.config.bridgeUrl` — should match your bridge server URL

## Step 7: Restart OpenClaw

```bash
pkill -9 -f openclaw
# Daemon will restart automatically with new config
```

## Step 8: Talk to the Arm

Open the OpenClaw web UI (`http://localhost:18789`) or send a message through your configured channel:

```
Connect to the arm
```

```
Move joint 1 to 30 degrees
```

```
Show me the current arm status
```

```
Return to home position and disable
```

## Verify Everything Works

```bash
python3 setup/check_env.py
```

This checks all dependencies, CAN status, bridge connectivity, and OpenClaw installation.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `CAN interface not found` | Check USB adapter connection, run `sudo bash setup/activate_can.sh` |
| `pyAgxArm not installed` | `pip install pyAgxArm` or use mock mode |
| `Bridge server not running` | Start with `clawarm-bridge` |
| `OpenClaw not responding` | Check `openclaw doctor`, verify config |
| `Safety violation error` | Check joint limits or workspace bounds in bridge/safety.py |
