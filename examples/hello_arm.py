#!/usr/bin/env python3
"""Basic arm control: connect, move joint 1, return to home, disconnect.

Usage:
    python3 examples/hello_arm.py
    python3 examples/hello_arm.py --robot piper --channel can1
"""

import argparse
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


def main():
    parser = argparse.ArgumentParser(description="ClawArm hello world")
    parser.add_argument("--robot", default="nero", choices=["nero", "piper"])
    parser.add_argument("--channel", default="can0")
    parser.add_argument("--speed", type=int, default=30)
    args = parser.parse_args()

    dof = 7 if args.robot == "nero" else 6

    print(f"Connecting to {args.robot} on {args.channel}...")
    cfg = create_agx_arm_config(
        robot=args.robot, comm="can", channel=args.channel, interface="socketcan"
    )
    robot = AgxArmFactory.create_arm(cfg)
    robot.connect()

    time.sleep(1)
    robot.set_normal_mode()
    time.sleep(1)

    while not robot.enable():
        time.sleep(0.01)
    robot.set_speed_percent(args.speed)
    print(f"Enabled at {args.speed}% speed")

    # Move joint 1 to 0.3 rad
    target = [0.0] * dof
    target[0] = 0.3
    print(f"Moving joint 1 to 0.3 rad...")
    robot.set_motion_mode(robot.MOTION_MODE.J)
    robot.move_j(target)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=3.0)

    ja = robot.get_joint_angles()
    if ja is not None:
        print(f"Joint angles: {[round(a, 4) for a in ja.msg]}")

    # Return to home
    print("Returning to home position...")
    robot.move_j([0.0] * dof)
    time.sleep(0.01)
    wait_motion_done(robot, timeout=3.0)
    print("Home position reached")

    # Disable
    while not robot.disable():
        time.sleep(0.01)
    print("Disabled. Done.")


if __name__ == "__main__":
    main()
