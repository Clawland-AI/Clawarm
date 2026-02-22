"""Arm connection lifecycle manager — handles connect, enable, and driver selection."""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

from .drivers.base import ArmDriver
from .drivers.mock_driver import MockArmDriver
from .models import DOF_MAP, MotionMode, RobotType
from .safety import SafetyConfig, SafetyValidator

logger = logging.getLogger(__name__)

MODE_SWITCH_DELAY = 1.0
POST_MOVE_DELAY = 0.01
MOTION_POLL_INTERVAL = 0.1
DEFAULT_TIMEOUT = 3.0


def _use_mock() -> bool:
    return os.environ.get("CLAWARM_MOCK", "").lower() in ("1", "true", "yes")


def _create_driver() -> ArmDriver:
    if _use_mock():
        logger.info("Using MockArmDriver (CLAWARM_MOCK is set)")
        return MockArmDriver()
    try:
        from .drivers.agx_driver import AgxArmDriver
        return AgxArmDriver()
    except Exception:
        logger.warning("pyAgxArm not available, falling back to MockArmDriver")
        return MockArmDriver()


class ArmManager:
    """Manages a single arm driver instance with safety validation."""

    def __init__(self, safety_config: SafetyConfig | None = None) -> None:
        self._driver: Optional[ArmDriver] = None
        self._robot_type: Optional[RobotType] = None
        self._safety = SafetyValidator(safety_config)

    @property
    def connected(self) -> bool:
        return self._driver is not None and self._driver.is_connected

    @property
    def enabled(self) -> bool:
        return self.connected and getattr(self._driver, "is_enabled", False)

    @property
    def robot_type(self) -> Optional[RobotType]:
        return self._robot_type

    @property
    def dof(self) -> Optional[int]:
        return DOF_MAP.get(self._robot_type) if self._robot_type else None

    def connect(self, robot: RobotType, channel: str = "can0", interface: str = "socketcan") -> str:
        if self.connected:
            self.disconnect()

        self._driver = _create_driver()
        self._driver.connect(robot.value, channel, interface)
        self._robot_type = robot

        time.sleep(MODE_SWITCH_DELAY)
        self._driver.set_normal_mode()
        time.sleep(MODE_SWITCH_DELAY)

        retries = 0
        while not self._driver.enable():
            time.sleep(0.01)
            retries += 1
            if retries > 500:
                raise RuntimeError("Failed to enable arm after 500 retries")

        default_speed = self._safety.validate_speed(80)
        self._driver.set_speed_percent(default_speed)

        return f"Connected to {robot.value} on {channel} (dof={DOF_MAP.get(robot, '?')})"

    def disconnect(self) -> str:
        if not self._driver:
            return "Not connected"
        if self.enabled:
            retries = 0
            while not self._driver.disable():
                time.sleep(0.01)
                retries += 1
                if retries > 100:
                    break
        self._driver.disconnect()
        self._driver = None
        self._robot_type = None
        return "Disconnected"

    def get_status(self) -> dict:
        if not self._driver or not self._driver.is_connected:
            return {"connected": False, "enabled": False}

        return {
            "connected": True,
            "enabled": getattr(self._driver, "is_enabled", False),
            "robot_type": self._robot_type.value if self._robot_type else None,
            "dof": self.dof,
            "joint_angles": self._driver.get_joint_angles(),
            "flange_pose": self._driver.get_flange_pose(),
            "motion_status": self._driver.get_motion_status(),
        }

    def move(
        self,
        mode: MotionMode,
        target: list[float],
        mid_point: list[float] | None = None,
        end_point: list[float] | None = None,
        speed_percent: int | None = None,
        wait: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> str:
        if not self.connected or not self.enabled:
            raise RuntimeError("Arm not connected or not enabled. Call /connect first.")
        if self._robot_type is None:
            raise RuntimeError("Robot type unknown")

        self._safety.validate_move(self._robot_type, mode, target, mid_point, end_point)

        if speed_percent is not None:
            clamped = self._safety.validate_speed(speed_percent)
            self._driver.set_speed_percent(clamped)

        self._driver.set_motion_mode(mode.value)

        if mode in (MotionMode.J, MotionMode.JS):
            self._driver.move_j(target)
        elif mode == MotionMode.P:
            self._driver.move_p(target)
        elif mode == MotionMode.L:
            self._driver.move_l(target)
        elif mode == MotionMode.C:
            if mid_point is None or end_point is None:
                raise ValueError("Arc motion (C) requires mid_point and end_point")
            self._driver.move_c(target, mid_point, end_point)

        time.sleep(POST_MOVE_DELAY)

        if wait:
            done = self._wait_motion_done(timeout)
            return f"Motion {'completed' if done else 'timed out'} (mode={mode.value})"
        return f"Motion command sent (mode={mode.value}, not waiting)"

    def stop(self, emergency: bool = False) -> str:
        if not self._driver:
            return "Not connected"
        if emergency:
            self._driver.emergency_stop()
            return "EMERGENCY STOP executed"
        if self.enabled:
            retries = 0
            while not self._driver.disable():
                time.sleep(0.01)
                retries += 1
                if retries > 100:
                    return "Failed to disable arm"
        return "Arm disabled"

    def _wait_motion_done(self, timeout: float) -> bool:
        time.sleep(0.5)
        start = time.monotonic()
        while True:
            status = self._driver.get_motion_status()
            if status == 0:
                return True
            if time.monotonic() - start > timeout:
                return False
            time.sleep(MOTION_POLL_INTERVAL)
