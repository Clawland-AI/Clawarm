#!/usr/bin/env python3
"""Pick-and-place demo: move to a pick position, then to a place position using Cartesian control.

This example uses point-to-point (P) mode for Cartesian motions.
Adjust the pick_pose and place_pose for your setup.

Usage:
    python3 examples/pick_and_place.py
"""

import time

from pyAgxArm import AgxArmFactory, create_agx_arm_config


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


# Cartesian poses: [x, y, z, roll, pitch, yaw] in meters/radians
APPROACH_HEIGHT = 0.35  # meters above table
GRASP_HEIGHT = 0.15

PICK_XY = (0.30, 0.10)
PLACE_XY = (0.30, -0.10)

ORIENTATION = (0.0, 3.14159, 0.0)  # pointing downward


def make_pose(x, y, z):
    return [x, y, z, *ORIENTATION]


def main():
    print("=== Pick and Place Demo ===")
    print("WARNING: Ensure workspace is clear before running!\n")

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
    robot.set_speed_percent(30)
    print("Enabled at 30% speed\n")

    steps = [
        ("Approach pick position", make_pose(*PICK_XY, APPROACH_HEIGHT)),
        ("Lower to pick", make_pose(*PICK_XY, GRASP_HEIGHT)),
        ("Lift from pick", make_pose(*PICK_XY, APPROACH_HEIGHT)),
        ("Approach place position", make_pose(*PLACE_XY, APPROACH_HEIGHT)),
        ("Lower to place", make_pose(*PLACE_XY, GRASP_HEIGHT)),
        ("Release and lift", make_pose(*PLACE_XY, APPROACH_HEIGHT)),
    ]

    robot.set_motion_mode(robot.MOTION_MODE.P)

    for label, pose in steps:
        print(f"  -> {label}: {[round(v, 4) for v in pose]}")
        robot.move_p(pose)
        time.sleep(0.01)
        done = wait_motion_done(robot, timeout=5.0)
        if not done:
            print("     WARNING: motion timed out")

    # Return to home (joint mode)
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
