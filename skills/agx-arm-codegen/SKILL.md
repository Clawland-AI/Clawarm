---
name: agx-arm-codegen
description: Generate executable Python scripts to control NERO/Piper robotic arms via pyAgxArm SDK based on natural language descriptions. When the user describes a robotic arm motion, this skill guides code generation with correct API usage, safety checks, and motion completion polling.
metadata:
  {
    "openclaw":
      {
        "emoji": "🦾",
        "requires": { "bins": ["python3", "pip3"] },
      },
  }
---

## Overview

This skill generates **runnable Python scripts** that control AgileX robotic arms (NERO 7-DOF, Piper 6-DOF) using the [pyAgxArm](https://github.com/agilexrobotics/pyAgxArm) SDK. It does NOT execute motion directly — it produces code that the user runs on a machine with CAN connectivity to the arm.

## When to Use

- User says "write code to control the arm", "generate a script to move the arm", "make the arm do X"
- User describes a motion sequence in natural language
- User asks for a "runnable script" or "Python code" for arm control
- User mentions NERO, Piper, or AgileX arm control

## Code Generation Rules

### 1. Connection & Configuration

```python
from pyAgxArm import create_agx_arm_config, AgxArmFactory

robot_cfg = create_agx_arm_config(
    robot="nero",       # "nero" (7-DOF) or "piper" (6-DOF)
    comm="can",
    channel="can0",
    interface="socketcan",
)
robot = AgxArmFactory.create_arm(robot_cfg)
robot.connect()
```

### 2. Enable Sequence

**CRITICAL: The robot MUST be enabled BEFORE switching modes. If disabled, mode switches will fail.**

```python
import time

time.sleep(1)                    # 1s delay before mode switch
robot.set_normal_mode()
time.sleep(1)                    # 1s delay after mode switch

while not robot.enable():
    time.sleep(0.01)

robot.set_speed_percent(80)      # 0–100, start low for testing
```

### 3. Motion Modes

Set the motion mode explicitly before every `move_*` call:

| Mode | Constant | Method | Use Case |
|------|----------|--------|----------|
| Joint position | `robot.MOTION_MODE.J` | `robot.move_j([j1..jN])` | Smooth joint-space motion |
| Joint fast | `robot.MOTION_MODE.JS` | `robot.move_js([j1..jN])` | No smoothing — **use with caution** |
| Point-to-point | `robot.MOTION_MODE.P` | `robot.move_p([x,y,z,r,p,y])` | Cartesian, non-linear path |
| Linear | `robot.MOTION_MODE.L` | `robot.move_l([x,y,z,r,p,y])` | Straight-line Cartesian path |
| Arc | `robot.MOTION_MODE.C` | `robot.move_c(start, mid, end)` | Circular arc through 3 poses |

- NERO: 7 joints → `move_j` takes a list of 7 floats (radians)
- Piper: 6 joints → `move_j` takes a list of 6 floats (radians)
- Cartesian pose: `[x, y, z, roll, pitch, yaw]` — position in **meters**, orientation in **radians**

**CRITICAL: All movement commands (move_j, move_js, move_p, move_l, move_c) require normal mode.**

### 4. Motion Completion

Always wait for motion to finish before issuing the next command:

```python
def wait_motion_done(robot, timeout: float = 3.0, poll_interval: float = 0.1) -> bool:
    time.sleep(0.5)
    start_t = time.monotonic()
    while True:
        status = robot.get_arm_status()
        if status is not None and getattr(status.msg, "motion_status", None) == 0:
            return True
        if time.monotonic() - start_t > timeout:
            return False
        time.sleep(poll_interval)
```

**CRITICAL: motion_status == 0 means DONE (not == 1).**

### 5. Mode Switching

Switching between master, slave, and normal modes requires delays:

```python
time.sleep(1)              # 1s delay BEFORE switch
robot.set_normal_mode()    # or set_master_mode() / set_slave_mode()
time.sleep(1)              # 1s delay AFTER switch
```

### 6. Post-Move Delay

After every movement command, add a small sleep:

```python
robot.move_j([0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
time.sleep(0.01)          # small delay after move command
wait_motion_done(robot, timeout=3.0)
```

### 7. Reading State

```python
# Joint angles (list of floats, radians)
ja = robot.get_joint_angles()
if ja is not None:
    print(ja.msg)

# Flange pose [x, y, z, roll, pitch, yaw]
pose = robot.get_flange_pose()

# Motion status (0 = idle/done)
status = robot.get_arm_status()
```

### 8. Safety

- **Always remind the user**: clear workspace of people/obstacles before running
- **Suggest low speed first**: `robot.set_speed_percent(30)` for initial tests
- **Emergency stop**: `robot.electronic_emergency_stop()` — recovery requires `robot.reset()`
- **Disable at end**: optionally call `robot.disable()` when done
- **High-risk modes** (`move_js`, `move_mit`): flag in comments that these bypass smoothing

### 9. Script Structure

Every generated script should follow this template:

```python
#!/usr/bin/env python3
"""<description of what this script does>"""
import time
from pyAgxArm import create_agx_arm_config, AgxArmFactory


def wait_motion_done(robot, timeout=3.0, poll_interval=0.1):
    time.sleep(0.5)
    start_t = time.monotonic()
    while True:
        status = robot.get_arm_status()
        if status is not None and getattr(status.msg, "motion_status", None) == 0:
            return True
        if time.monotonic() - start_t > timeout:
            return False
        time.sleep(poll_interval)


def main():
    robot_cfg = create_agx_arm_config(
        robot="nero", comm="can", channel="can0", interface="socketcan",
    )
    robot = AgxArmFactory.create_arm(robot_cfg)
    robot.connect()

    time.sleep(1)
    robot.set_normal_mode()
    time.sleep(1)

    while not robot.enable():
        time.sleep(0.01)
    robot.set_speed_percent(80)

    # --- Motion commands go here ---
    robot.set_motion_mode(robot.MOTION_MODE.J)
    robot.move_j([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    time.sleep(0.01)
    wait_motion_done(robot, timeout=3.0)

    # --- Cleanup ---
    while not robot.disable():
        time.sleep(0.01)


if __name__ == "__main__":
    main()
```

## Reference

See `references/pyagxarm-api.md` for the complete API reference, joint limits, and additional examples.
