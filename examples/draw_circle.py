#!/usr/bin/env python3
"""Draw a circle in the XY plane using arc (C) mode.

The circle is approximated by two semicircular arcs.
Adjust CENTER, RADIUS, and HEIGHT for your workspace.

Usage:
    python3 examples/draw_circle.py
"""

import math
import time

from pyAgxArm import AgxArmFactory, create_agx_arm_config


def wait_motion_done(robot, timeout=5.0, poll_interval=0.1):
    time.sleep(0.5)
    start_t = time.monotonic()
    while True:
        status = robot.get_arm_status()
        if status is not None and getattr(status.msg, "motion_status", None) == 0:
            return True
        if time.monotonic() - start_t > timeout:
            return False
        time.sleep(poll_interval)


CENTER_X = 0.30   # meters
CENTER_Y = 0.00
HEIGHT = 0.30
RADIUS = 0.05     # 5cm circle
ORIENTATION = [0.0, math.pi, 0.0]  # end-effector pointing down


def circle_point(angle_rad):
    """Get a Cartesian pose on the circle at the given angle."""
    x = CENTER_X + RADIUS * math.cos(angle_rad)
    y = CENTER_Y + RADIUS * math.sin(angle_rad)
    return [x, y, HEIGHT, *ORIENTATION]


def main():
    print("=== Draw Circle Demo ===")
    print(f"Center: ({CENTER_X}, {CENTER_Y}, {HEIGHT})m, Radius: {RADIUS}m")
    print("WARNING: Ensure workspace is clear!\n")

    cfg = create_agx_arm_config(
        robot="nero", comm="can", channel="can0", interface="socketcan"
    )
    robot = AgxArmFactory.create_arm(cfg)
    robot.connect()

    time.sleep(1)
    robot.set_normal_mode()
    time.sleep(1)

    while not robot.enable():
        time.sleep(0.01)
    robot.set_speed_percent(20)
    print("Enabled at 20% speed\n")

    # Move to start of circle (0°) using point-to-point
    start_pose = circle_point(0)
    print(f"Moving to circle start: {[round(v, 4) for v in start_pose]}")
    robot.set_motion_mode(robot.MOTION_MODE.P)
    robot.move_p(start_pose)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=5.0)

    # Draw two semicircular arcs to complete the circle
    robot.set_motion_mode(robot.MOTION_MODE.C)

    # First semicircle: 0° -> 90° -> 180°
    arc1_start = circle_point(0)
    arc1_mid = circle_point(math.pi / 2)
    arc1_end = circle_point(math.pi)
    print("Drawing first semicircle (0° -> 180°)...")
    robot.move_c(arc1_start, arc1_mid, arc1_end)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=5.0)

    # Second semicircle: 180° -> 270° -> 360°
    arc2_start = circle_point(math.pi)
    arc2_mid = circle_point(3 * math.pi / 2)
    arc2_end = circle_point(2 * math.pi)
    print("Drawing second semicircle (180° -> 360°)...")
    robot.move_c(arc2_start, arc2_mid, arc2_end)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=5.0)

    print("Circle complete!")

    # Return to home
    print("\nReturning to home...")
    robot.set_motion_mode(robot.MOTION_MODE.J)
    robot.move_j([0.0] * 7)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=3.0)

    while not robot.disable():
        time.sleep(0.01)
    print("Done.")


if __name__ == "__main__":
    main()
