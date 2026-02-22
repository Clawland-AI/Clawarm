"""Abstract base class for arm drivers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class ArmDriver(ABC):
    """Interface that both the real pyAgxArm driver and the mock driver implement."""

    @abstractmethod
    def connect(self, robot: str, channel: str, interface: str) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def set_normal_mode(self) -> None: ...

    @abstractmethod
    def set_master_mode(self) -> None: ...

    @abstractmethod
    def set_slave_mode(self) -> None: ...

    @abstractmethod
    def enable(self) -> bool: ...

    @abstractmethod
    def disable(self) -> bool: ...

    @abstractmethod
    def set_speed_percent(self, pct: int) -> None: ...

    @abstractmethod
    def set_motion_mode(self, mode: str) -> None: ...

    @abstractmethod
    def move_j(self, joints: list[float]) -> None: ...

    @abstractmethod
    def move_p(self, pose: list[float]) -> None: ...

    @abstractmethod
    def move_l(self, pose: list[float]) -> None: ...

    @abstractmethod
    def move_c(
        self, start: list[float], mid: list[float], end: list[float]
    ) -> None: ...

    @abstractmethod
    def get_joint_angles(self) -> Optional[list[float]]: ...

    @abstractmethod
    def get_flange_pose(self) -> Optional[list[float]]: ...

    @abstractmethod
    def get_motion_status(self) -> Optional[int]: ...

    @abstractmethod
    def emergency_stop(self) -> None: ...

    @abstractmethod
    def reset(self) -> None: ...
