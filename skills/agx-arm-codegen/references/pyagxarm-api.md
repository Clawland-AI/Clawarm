# pyAgxArm API Reference

SDK source: [github.com/agilexrobotics/pyAgxArm](https://github.com/agilexrobotics/pyAgxArm)
Reference demo: `pyAgxArm/demos/nero/test1.py`

## 1. Connection

```python
from pyAgxArm import create_agx_arm_config, AgxArmFactory

robot_cfg = create_agx_arm_config(
    robot="nero",           # "nero" | "piper" | "piper_h" | "piper_l" | "piper_x"
    comm="can",
    channel="can0",         # CAN interface name (check with `ifconfig`)
    interface="socketcan",
)
robot = AgxArmFactory.create_arm(robot_cfg)
robot.connect()
```

- `create_agx_arm_config(robot, comm, channel, interface, **kwargs)` — creates a config dict
- `AgxArmFactory.create_arm(config)` — returns the arm driver instance
- `robot.connect()` — opens CAN connection and starts the read thread

## 2. Enable / Disable

```python
import time

# Enable (normal mode must be set first)
robot.set_normal_mode()
while not robot.enable():
    time.sleep(0.01)

robot.set_speed_percent(100)    # 0–100

# Disable
while not robot.disable():
    time.sleep(0.01)
```

### Mode Methods

| Method | Description |
|--------|-------------|
| `robot.set_normal_mode()` | Standard single-arm control |
| `robot.set_master_mode()` | Zero-force drag mode |
| `robot.set_slave_mode()` | Follow master arm |

**Rule**: 1-second sleep before AND after every mode switch.

## 3. Motion Modes

Set before calling any `move_*` method:

```python
robot.set_motion_mode(robot.MOTION_MODE.J)   # Joint position (smooth)
robot.set_motion_mode(robot.MOTION_MODE.JS)  # Joint fast (no smoothing)
robot.set_motion_mode(robot.MOTION_MODE.P)   # Point-to-point (Cartesian)
robot.set_motion_mode(robot.MOTION_MODE.L)   # Linear (Cartesian)
robot.set_motion_mode(robot.MOTION_MODE.C)   # Circular arc
```

## 4. Movement Commands

| Method | Parameters | Units |
|--------|-----------|-------|
| `robot.move_j(joints)` | `[j1, j2, ..., jN]` | radians |
| `robot.move_js(joints)` | `[j1, j2, ..., jN]` | radians (fast, no smoothing) |
| `robot.move_p(pose)` | `[x, y, z, roll, pitch, yaw]` | meters / radians |
| `robot.move_l(pose)` | `[x, y, z, roll, pitch, yaw]` | meters / radians |
| `robot.move_c(start, mid, end)` | 3 poses, each `[x, y, z, r, p, y]` | meters / radians |

- NERO: 7 joints → `move_j`/`move_js` take 7 floats
- Piper: 6 joints → `move_j`/`move_js` take 6 floats

## 5. Motion Completion

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

**`motion_status == 0` = motion complete** (not `== 1`).

## 6. Reading State

| Method | Returns |
|--------|---------|
| `robot.get_arm_status()` | Status object; `.msg.motion_status` (0 = idle) |
| `robot.get_flange_pose()` | `[x, y, z, roll, pitch, yaw]` in meters/radians |
| `robot.get_joint_angles()` | Object with `.msg` (list of joint angles in radians), `.hz`, `.timestamp` |

## 7. Emergency & Advanced

| Method | Description |
|--------|-------------|
| `robot.electronic_emergency_stop()` | Software E-stop; requires `robot.reset()` to recover |
| `robot.reset()` | Reset after E-stop |
| `robot.move_mit(joint_idx, p_des, v_des, kp, kd, t_ff)` | MIT impedance control — advanced, use with extreme caution |

## 8. Home Position

```python
# NERO (7 joints)
robot.move_j([0, 0, 0, 0, 0, 0, 0])

# Piper (6 joints)
robot.move_j([0, 0, 0, 0, 0, 0])
```

## 9. Minimal Runnable Template

```python
#!/usr/bin/env python3
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

    robot.set_motion_mode(robot.MOTION_MODE.J)
    robot.move_j([0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    time.sleep(0.01)
    wait_motion_done(robot, timeout=3.0)

    while not robot.disable():
        time.sleep(0.01)


if __name__ == "__main__":
    main()
```

## 10. Dependencies

```bash
pip3 install python-can
git clone https://github.com/agilexrobotics/pyAgxArm.git
cd pyAgxArm && pip3 install .
```

CAN activation (Linux):

```bash
sudo ip link set can0 up type can bitrate 1000000
```
