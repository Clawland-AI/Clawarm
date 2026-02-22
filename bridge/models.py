"""Pydantic models for bridge API request/response schemas."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RobotType(str, Enum):
    NERO = "nero"
    PIPER = "piper"
    PIPER_H = "piper_h"
    PIPER_L = "piper_l"
    PIPER_X = "piper_x"


DOF_MAP: dict[RobotType, int] = {
    RobotType.NERO: 7,
    RobotType.PIPER: 6,
    RobotType.PIPER_H: 6,
    RobotType.PIPER_L: 6,
    RobotType.PIPER_X: 6,
}


class MotionMode(str, Enum):
    J = "J"
    JS = "JS"
    P = "P"
    L = "L"
    C = "C"


class StopAction(str, Enum):
    DISABLE = "disable"
    EMERGENCY_STOP = "emergency_stop"


# --- Requests ---


class ConnectRequest(BaseModel):
    robot: RobotType = RobotType.NERO
    channel: str = Field(default="can0", description="CAN interface name")
    interface: str = Field(default="socketcan", description="CAN interface type")


class MoveRequest(BaseModel):
    mode: MotionMode
    target: list[float] = Field(description="Target joint angles or Cartesian pose")
    mid_point: Optional[list[float]] = Field(
        default=None, description="Mid-point for arc motion (mode=C only)"
    )
    end_point: Optional[list[float]] = Field(
        default=None, description="End-point for arc motion (mode=C only)"
    )
    speed_percent: Optional[int] = Field(
        default=None, ge=1, le=100, description="Override speed percentage"
    )
    wait: bool = Field(default=True, description="Wait for motion to complete")
    timeout: float = Field(default=3.0, ge=0.1, le=30.0, description="Wait timeout in seconds")


class StopRequest(BaseModel):
    action: StopAction = StopAction.DISABLE


# --- Responses ---


class StatusResponse(BaseModel):
    connected: bool
    enabled: bool
    robot_type: Optional[str] = None
    dof: Optional[int] = None
    joint_angles: Optional[list[float]] = None
    flange_pose: Optional[list[float]] = None
    motion_status: Optional[int] = None


class ResultResponse(BaseModel):
    ok: bool
    message: str
    data: Optional[dict] = None
