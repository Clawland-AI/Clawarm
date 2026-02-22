# Safety Guide

ClawArm controls real robotic hardware. This document covers the safety mechanisms and procedures you need to know.

## Safety Hierarchy

1. **Physical E-stop** (highest priority) — hardware button on the arm controller
2. **Software emergency stop** — `arm_stop` tool or `POST /stop` with `emergency_stop`
3. **Software disable** — graceful shutdown via `arm_stop` or `POST /disable`
4. **Safety layer** — pre-move validation of joint limits, workspace bounds, speed
5. **Agent rules** — AGENTS.md instructions for confirmation and slow start

## Physical Safety Checklist

Before every session:

- [ ] Workspace is clear of people within the arm's reach envelope
- [ ] No objects that could be damaged by unexpected motion
- [ ] Physical E-stop button is within reach
- [ ] Someone is present who knows how to use the E-stop
- [ ] First test of new motions uses `speed_percent=30` or lower

## Safety Layer Details

### Joint Limits

Each robot type has per-joint angle limits (in radians):

**NERO (7-DOF)**

| Joint | Min (rad) | Max (rad) | Degrees |
|-------|-----------|-----------|---------|
| J1 | -2.618 | +2.618 | ±150° |
| J2 | -2.094 | +2.094 | ±120° |
| J3 | -2.618 | +2.618 | ±150° |
| J4 | -2.094 | +2.094 | ±120° |
| J5 | -2.618 | +2.618 | ±150° |
| J6 | -2.094 | +2.094 | ±120° |
| J7 | -2.618 | +2.618 | ±150° |

**Piper (6-DOF)**

| Joint | Min (rad) | Max (rad) | Degrees |
|-------|-----------|-----------|---------|
| J1 | -2.618 | +2.618 | ±150° |
| J2 | -2.094 | +2.094 | ±120° |
| J3 | -2.618 | +2.618 | ±150° |
| J4 | -2.094 | +2.094 | ±120° |
| J5 | -2.618 | +2.618 | ±150° |
| J6 | -1.571 | +1.571 | ±90° |

### Workspace Bounds (Default)

| Axis | Min | Max |
|------|-----|-----|
| X | -1.0 m | +1.0 m |
| Y | -1.0 m | +1.0 m |
| Z | -0.1 m | +1.2 m |

Customize by modifying `SafetyConfig` in the bridge server or setting environment variables.

### Speed Cap

Default maximum: **80%**. Override with `CLAWARM_MAX_SPEED` environment variable.

The AI agent is instructed to start at 30% for new motions. Even if the agent requests 100%, the safety layer caps it.

## Emergency Procedures

### Software Emergency Stop

Via OpenClaw:
```
Emergency stop!
```
The agent will immediately call `arm_stop` with `action=emergency_stop`.

Via API:
```bash
curl -X POST http://127.0.0.1:8420/stop -H "Content-Type: application/json" -d '{"action":"emergency_stop"}'
```

### Recovery After Emergency Stop

The arm requires a reset after an electronic emergency stop:

```bash
# Via API (after restarting bridge or reconnecting)
curl -X POST http://127.0.0.1:8420/connect -H "Content-Type: application/json" -d '{"robot":"nero"}'
```

Or via OpenClaw:
```
Reset the arm and reconnect
```

### Kill the Bridge Server

If all else fails, terminate the bridge server to cut all communication:

```bash
# Find and kill the process
pkill -f clawarm-bridge

# Or if running in Docker
docker compose down
```

## High-Risk Operations

| Operation | Risk | Mitigation |
|-----------|------|------------|
| `move_js` (fast joint) | No smoothing, sudden motion | Agent warns user, requires explicit confirmation |
| `move_mit` (impedance) | Direct torque control | Not exposed via plugin; only available in skill-generated code with explicit warnings |
| High speed (>80%) | Reduced reaction time | Safety layer caps speed; agent requires explicit approval |
| Arc motion (`move_c`) | Complex trajectory | Validate all three poses before execution |

## Disabling Safety

**Not recommended.** If you must disable safety for testing:

```bash
CLAWARM_SAFETY=false clawarm-bridge
```

This disables joint limit checks, workspace bounds, and speed caps. Use only in controlled lab environments with physical E-stop readily available.
