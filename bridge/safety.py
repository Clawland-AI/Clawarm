"""Safety layer — validates motion commands before they reach the arm driver."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from .models import DOF_MAP, MotionMode, RobotType

logger = logging.getLogger(__name__)

PI = math.pi


@dataclass
class JointLimits:
    """Per-joint angle limits in radians [min, max]."""

    limits: list[tuple[float, float]]


@dataclass
class WorkspaceBounds:
    """Cartesian bounding box in meters."""

    x_min: float = -1.0
    x_max: float = 1.0
    y_min: float = -1.0
    y_max: float = 1.0
    z_min: float = -0.1
    z_max: float = 1.2


NERO_JOINT_LIMITS = JointLimits(
    limits=[
        (-2.618, 2.618),   # J1: ±150°
        (-2.094, 2.094),   # J2: ±120°
        (-2.618, 2.618),   # J3: ±150°
        (-2.094, 2.094),   # J4: ±120°
        (-2.618, 2.618),   # J5: ±150°
        (-2.094, 2.094),   # J6: ±120°
        (-2.618, 2.618),   # J7: ±150°
    ]
)

PIPER_JOINT_LIMITS = JointLimits(
    limits=[
        (-2.618, 2.618),   # J1: ±150°
        (-2.094, 2.094),   # J2: ±120°
        (-2.618, 2.618),   # J3: ±150°
        (-2.094, 2.094),   # J4: ±120°
        (-2.618, 2.618),   # J5: ±150°
        (-1.571, 1.571),   # J6: ±90°
    ]
)

JOINT_LIMITS_MAP: dict[RobotType, JointLimits] = {
    RobotType.NERO: NERO_JOINT_LIMITS,
    RobotType.PIPER: PIPER_JOINT_LIMITS,
    RobotType.PIPER_H: PIPER_JOINT_LIMITS,
    RobotType.PIPER_L: PIPER_JOINT_LIMITS,
    RobotType.PIPER_X: PIPER_JOINT_LIMITS,
}

DEFAULT_MAX_SPEED_PERCENT = 80


@dataclass
class SafetyConfig:
    enabled: bool = True
    max_speed_percent: int = DEFAULT_MAX_SPEED_PERCENT
    workspace_bounds: WorkspaceBounds = field(default_factory=WorkspaceBounds)


class SafetyError(Exception):
    """Raised when a command violates safety constraints."""


class SafetyValidator:
    """Validates motion commands against joint limits, workspace bounds, and speed caps."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self.config = config or SafetyConfig()

    def validate_speed(self, speed_percent: int) -> int:
        """Clamp speed to configured maximum. Returns the clamped value."""
        if not self.config.enabled:
            return speed_percent
        if speed_percent > self.config.max_speed_percent:
            logger.warning(
                "Safety: speed %d%% capped to %d%%",
                speed_percent,
                self.config.max_speed_percent,
            )
            return self.config.max_speed_percent
        return speed_percent

    def validate_joint_move(
        self, robot_type: RobotType, joints: list[float]
    ) -> None:
        """Check joint angles against per-robot limits."""
        if not self.config.enabled:
            return

        limits_def = JOINT_LIMITS_MAP.get(robot_type)
        if limits_def is None:
            return

        expected_dof = DOF_MAP.get(robot_type, len(joints))
        if len(joints) != expected_dof:
            raise SafetyError(
                f"Expected {expected_dof} joints for {robot_type.value}, got {len(joints)}"
            )

        for i, (angle, (lo, hi)) in enumerate(zip(joints, limits_def.limits)):
            if not (lo <= angle <= hi):
                raise SafetyError(
                    f"Joint {i + 1} angle {angle:.4f} rad out of range "
                    f"[{lo:.4f}, {hi:.4f}] for {robot_type.value}"
                )

    def validate_cartesian_move(self, pose: list[float]) -> None:
        """Check Cartesian position against workspace bounds."""
        if not self.config.enabled:
            return

        if len(pose) < 3:
            raise SafetyError(
                f"Cartesian pose must have at least 3 values (x,y,z), got {len(pose)}"
            )

        x, y, z = pose[0], pose[1], pose[2]
        wb = self.config.workspace_bounds

        if not (wb.x_min <= x <= wb.x_max):
            raise SafetyError(f"X={x:.4f}m outside workspace [{wb.x_min}, {wb.x_max}]")
        if not (wb.y_min <= y <= wb.y_max):
            raise SafetyError(f"Y={y:.4f}m outside workspace [{wb.y_min}, {wb.y_max}]")
        if not (wb.z_min <= z <= wb.z_max):
            raise SafetyError(f"Z={z:.4f}m outside workspace [{wb.z_min}, {wb.z_max}]")

    def validate_move(
        self,
        robot_type: RobotType,
        mode: MotionMode,
        target: list[float],
        mid_point: list[float] | None = None,
        end_point: list[float] | None = None,
    ) -> None:
        """Validate a move command based on its motion mode."""
        if not self.config.enabled:
            return

        if mode in (MotionMode.J, MotionMode.JS):
            self.validate_joint_move(robot_type, target)
        elif mode in (MotionMode.P, MotionMode.L):
            self.validate_cartesian_move(target)
        elif mode == MotionMode.C:
            self.validate_cartesian_move(target)
            if mid_point:
                self.validate_cartesian_move(mid_point)
            if end_point:
                self.validate_cartesian_move(end_point)
