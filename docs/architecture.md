# Architecture

## Overview

ClawArm bridges natural language and physical robotic arm motion through three layers:

```
User (natural language)
    ↓
OpenClaw Agent (AI interpretation)
    ↓ Skill Mode: generates Python scripts
    ↓ Plugin Mode: calls bridge REST API
Python Bridge Server (FastAPI)
    ↓
Safety Layer (validates commands)
    ↓
pyAgxArm SDK (CAN communication)
    ↓
Robotic Arm (NERO / Piper)
```

## Components

### 1. OpenClaw Skill (`skills/agx-arm-codegen/`)

The skill teaches OpenClaw to generate complete, runnable Python scripts that use pyAgxArm. This is the approach described in the [original AgileX tutorial](https://mp.weixin.qq.com/s/V3EQ6E3ikN3srCzXrCOtiw).

**Flow**: User describes motion → OpenClaw reads SKILL.md → generates Python script → executes via Bash tool

**Best for**: Complex multi-step sequences, trajectories, demonstrations

### 2. OpenClaw Plugin (`plugin/`)

TypeScript plugin that registers four agent tools, each calling the bridge server over HTTP:

| Tool | Bridge Endpoint | Purpose |
|------|----------------|---------|
| `arm_connect` | `POST /connect` | Connect to arm, enable, set speed |
| `arm_status` | `GET /status` | Read joint angles, pose, motion state |
| `arm_move` | `POST /move` | Execute joint or Cartesian motion |
| `arm_stop` | `POST /stop` | Graceful disable or emergency stop |

**Best for**: Interactive, step-by-step control; status queries; quick adjustments

### 3. Python Bridge Server (`bridge/`)

FastAPI application (port 8420) that wraps pyAgxArm into REST endpoints.

**Key design decisions**:

- **Single arm instance**: The bridge manages one arm connection at a time. Multi-arm support would require running multiple bridge instances on different ports.
- **Synchronous motion**: Move endpoints block until motion completes (configurable via `wait` parameter). This simplifies the AI agent's workflow — it gets a response only when the arm has finished moving.
- **Driver abstraction**: The `ArmDriver` base class allows swapping between real hardware (`AgxArmDriver`) and a mock (`MockArmDriver`) without changing any other code.

### 4. Safety Layer (`bridge/safety.py`)

All motion commands pass through safety validation before reaching the driver:

- **Joint limits**: Per-robot-type angle ranges (e.g., NERO J1: ±150°)
- **Workspace bounds**: Configurable Cartesian bounding box
- **Speed cap**: Maximum speed percentage (default 80%)

Safety violations return HTTP 422 with a descriptive error. The AI agent sees this and can adjust parameters or inform the user.

### 5. Mock Driver (`bridge/drivers/mock_driver.py`)

Simulates arm behavior in memory:
- Tracks joint angles and flange pose
- Simulates motion completion with brief delays
- Supports all the same methods as the real driver

Used when `CLAWARM_MOCK=true` or when pyAgxArm is not installed.

## Data Flow: Plugin Mode

```
User: "Move the arm forward 10cm"
   ↓
OpenClaw Agent interprets intent
   ↓
Agent calls arm_status tool
   ↓ HTTP GET /status
Bridge returns current pose
   ↓
Agent calculates new pose (+0.1m on X)
   ↓
Agent calls arm_move tool (mode=L, target=[new_pose])
   ↓ HTTP POST /move
Bridge: safety check → set motion mode → move_l() → wait_motion_done()
   ↓
Bridge returns "Motion completed"
   ↓
Agent calls arm_status tool
   ↓
Agent reports new pose to user
```

## Data Flow: Skill Mode

```
User: "Write a script that makes the arm wave"
   ↓
OpenClaw Agent reads SKILL.md
   ↓
Agent generates Python script with move_j() sequence
   ↓
Agent executes script via Bash tool
   ↓
Script: connect → enable → move_j (wave pattern) → disable
   ↓
Agent reports script output to user
```

## Configuration

All configuration is done through environment variables and OpenClaw's `openclaw.json`:

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAWARM_MOCK` | `false` | Use mock driver |
| `CLAWARM_HOST` | `127.0.0.1` | Bridge bind address |
| `CLAWARM_PORT` | `8420` | Bridge port |
| `CLAWARM_SAFETY` | `true` | Enable safety layer |
| `CLAWARM_MAX_SPEED` | `80` | Max speed percentage |
