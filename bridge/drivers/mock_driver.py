"""Mock arm driver for development and testing without physical hardware."""

from __future__ import annotations

import logging
import time
from typing import Optional

from .base import ArmDriver

logger = logging.getLogger(__name__)

_DOF = {"nero": 7, "piper": 6, "piper_h": 6, "piper_l": 6, "piper_x": 6}


class MockArmDriver(ArmDriver):
    """Simulates a robotic arm in memory. All motions complete instantly."""

    def __init__(self) -> None:
        self._connected = False
        self._enabled = False
        self._robot: Optional[str] = None
        self._dof: int = 7
        self._speed_pct: int = 80
        self._motion_mode: str = "J"
        self._joint_angles: list[float] = []
        self._flange_pose: list[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._motion_status: int = 0  # 0 = idle
        self._move_start: float = 0.0

    def connect(self, robot: str, channel: str, interface: str) -> None:
        self._robot = robot
        self._dof = _DOF.get(robot, 7)
        self._joint_angles = [0.0] * self._dof
        self._connected = True
        logger.info("MockDriver: connected robot=%s channel=%s dof=%d", robot, channel, self._dof)

    def disconnect(self) -> None:
        self._connected = False
        self._enabled = False
        logger.info("MockDriver: disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected

    def set_normal_mode(self) -> None:
        logger.info("MockDriver: set_normal_mode")

    def set_master_mode(self) -> None:
        logger.info("MockDriver: set_master_mode")

    def set_slave_mode(self) -> None:
        logger.info("MockDriver: set_slave_mode")

    def enable(self) -> bool:
        self._enabled = True
        logger.info("MockDriver: enabled")
        return True

    def disable(self) -> bool:
        self._enabled = False
        logger.info("MockDriver: disabled")
        return True

    def set_speed_percent(self, pct: int) -> None:
        self._speed_pct = max(1, min(100, pct))
        logger.info("MockDriver: speed=%d%%", self._speed_pct)

    def set_motion_mode(self, mode: str) -> None:
        self._motion_mode = mode
        logger.info("MockDriver: motion_mode=%s", mode)

    def _simulate_move(self, target_joints: Optional[list[float]] = None) -> None:
        self._motion_status = 1  # moving
        self._move_start = time.monotonic()
        if target_joints is not None:
            self._joint_angles = list(target_joints)
        sim_duration = 0.1 * (100 / max(self._speed_pct, 1))
        time.sleep(min(sim_duration, 0.5))
        self._motion_status = 0  # done

    def move_j(self, joints: list[float]) -> None:
        logger.info("MockDriver: move_j(%s)", joints)
        self._simulate_move(joints)

    def move_p(self, pose: list[float]) -> None:
        logger.info("MockDriver: move_p(%s)", pose)
        self._flange_pose = list(pose)
        self._simulate_move()

    def move_l(self, pose: list[float]) -> None:
        logger.info("MockDriver: move_l(%s)", pose)
        self._flange_pose = list(pose)
        self._simulate_move()

    def move_c(
        self, start: list[float], mid: list[float], end: list[float]
    ) -> None:
        logger.info("MockDriver: move_c(start=%s, mid=%s, end=%s)", start, mid, end)
        self._flange_pose = list(end)
        self._simulate_move()

    def get_joint_angles(self) -> Optional[list[float]]:
        return list(self._joint_angles) if self._connected else None

    def get_flange_pose(self) -> Optional[list[float]]:
        return list(self._flange_pose) if self._connected else None

    def get_motion_status(self) -> Optional[int]:
        return self._motion_status if self._connected else None

    def emergency_stop(self) -> None:
        self._enabled = False
        self._motion_status = 0
        logger.warning("MockDriver: EMERGENCY STOP")

    def reset(self) -> None:
        self._motion_status = 0
        logger.info("MockDriver: reset after emergency stop")

    @property
    def robot_type(self) -> Optional[str]:
        return self._robot

    @property
    def dof(self) -> int:
        return self._dof

    @property
    def is_enabled(self) -> bool:
        return self._enabled
