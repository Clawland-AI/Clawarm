"""Real pyAgxArm driver wrapping the hardware SDK."""

from __future__ import annotations

import logging
from typing import Optional

from .base import ArmDriver

logger = logging.getLogger(__name__)

_DOF = {"nero": 7, "piper": 6, "piper_h": 6, "piper_l": 6, "piper_x": 6}

_MOTION_MODE_MAP: dict[str, str] = {
    "J": "J",
    "JS": "JS",
    "P": "P",
    "L": "L",
    "C": "C",
}


class AgxArmDriver(ArmDriver):
    """Wraps pyAgxArm SDK for real hardware control over CAN bus."""

    def __init__(self) -> None:
        self._robot_obj = None
        self._connected = False
        self._enabled = False
        self._robot_type: Optional[str] = None
        self._dof: int = 7

    def connect(self, robot: str, channel: str, interface: str) -> None:
        try:
            from pyAgxArm import AgxArmFactory, create_agx_arm_config
        except ImportError as exc:
            raise RuntimeError(
                "pyAgxArm is not installed. "
                "Install it with: pip install pyAgxArm  "
                "Or use mock mode: CLAWARM_MOCK=true clawarm-bridge"
            ) from exc

        cfg = create_agx_arm_config(
            robot=robot, comm="can", channel=channel, interface=interface
        )
        self._robot_obj = AgxArmFactory.create_arm(cfg)
        self._robot_obj.connect()
        self._robot_type = robot
        self._dof = _DOF.get(robot, 7)
        self._connected = True
        logger.info("AgxDriver: connected robot=%s channel=%s dof=%d", robot, channel, self._dof)

    def disconnect(self) -> None:
        if self._enabled:
            self.disable()
        self._connected = False
        self._robot_obj = None
        logger.info("AgxDriver: disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected and self._robot_obj is not None

    def set_normal_mode(self) -> None:
        self._robot_obj.set_normal_mode()

    def set_master_mode(self) -> None:
        self._robot_obj.set_master_mode()

    def set_slave_mode(self) -> None:
        self._robot_obj.set_slave_mode()

    def enable(self) -> bool:
        result = self._robot_obj.enable()
        if result:
            self._enabled = True
        return result

    def disable(self) -> bool:
        result = self._robot_obj.disable()
        if result:
            self._enabled = False
        return result

    def set_speed_percent(self, pct: int) -> None:
        self._robot_obj.set_speed_percent(pct)

    def set_motion_mode(self, mode: str) -> None:
        mode_attr = _MOTION_MODE_MAP.get(mode, mode)
        motion_mode = getattr(self._robot_obj.MOTION_MODE, mode_attr)
        self._robot_obj.set_motion_mode(motion_mode)

    def move_j(self, joints: list[float]) -> None:
        self._robot_obj.move_j(joints)

    def move_p(self, pose: list[float]) -> None:
        self._robot_obj.move_p(pose)

    def move_l(self, pose: list[float]) -> None:
        self._robot_obj.move_l(pose)

    def move_c(
        self, start: list[float], mid: list[float], end: list[float]
    ) -> None:
        self._robot_obj.move_c(start, mid, end)

    def get_joint_angles(self) -> Optional[list[float]]:
        ja = self._robot_obj.get_joint_angles()
        return list(ja.msg) if ja is not None else None

    def get_flange_pose(self) -> Optional[list[float]]:
        pose = self._robot_obj.get_flange_pose()
        if pose is None:
            return None
        return list(pose) if isinstance(pose, (list, tuple)) else list(pose.msg)

    def get_motion_status(self) -> Optional[int]:
        status = self._robot_obj.get_arm_status()
        if status is not None:
            return getattr(status.msg, "motion_status", None)
        return None

    def emergency_stop(self) -> None:
        self._robot_obj.electronic_emergency_stop()
        self._enabled = False
        logger.warning("AgxDriver: EMERGENCY STOP triggered")

    def reset(self) -> None:
        self._robot_obj.reset()
        logger.info("AgxDriver: reset after emergency stop")

    @property
    def robot_type(self) -> Optional[str]:
        return self._robot_type

    @property
    def dof(self) -> int:
        return self._dof

    @property
    def is_enabled(self) -> bool:
        return self._enabled
