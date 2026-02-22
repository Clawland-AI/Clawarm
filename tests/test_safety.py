"""Tests for the safety validation layer."""

import pytest

from bridge.models import MotionMode, RobotType
from bridge.safety import SafetyConfig, SafetyError, SafetyValidator, WorkspaceBounds


@pytest.fixture
def validator():
    return SafetyValidator(SafetyConfig(enabled=True, max_speed_percent=80))


@pytest.fixture
def disabled_validator():
    return SafetyValidator(SafetyConfig(enabled=False))


# --- Speed validation ---


def test_speed_capped(validator: SafetyValidator):
    assert validator.validate_speed(100) == 80
    assert validator.validate_speed(50) == 50
    assert validator.validate_speed(80) == 80


def test_speed_not_capped_when_disabled(disabled_validator: SafetyValidator):
    assert disabled_validator.validate_speed(100) == 100


# --- Joint validation ---


def test_valid_nero_joints(validator: SafetyValidator):
    validator.validate_joint_move(RobotType.NERO, [0.0] * 7)
    validator.validate_joint_move(RobotType.NERO, [0.5, -0.5, 1.0, -1.0, 0.5, -0.5, 0.0])


def test_invalid_nero_joint_count(validator: SafetyValidator):
    with pytest.raises(SafetyError, match="Expected 7 joints"):
        validator.validate_joint_move(RobotType.NERO, [0.0] * 6)


def test_nero_joint_out_of_range(validator: SafetyValidator):
    joints = [0.0] * 7
    joints[0] = 3.0  # exceeds ±2.618
    with pytest.raises(SafetyError, match="Joint 1"):
        validator.validate_joint_move(RobotType.NERO, joints)


def test_valid_piper_joints(validator: SafetyValidator):
    validator.validate_joint_move(RobotType.PIPER, [0.0] * 6)


def test_piper_joint_6_limit(validator: SafetyValidator):
    joints = [0.0] * 6
    joints[5] = 2.0  # exceeds ±1.571 for Piper J6
    with pytest.raises(SafetyError, match="Joint 6"):
        validator.validate_joint_move(RobotType.PIPER, joints)


def test_joint_validation_skipped_when_disabled(disabled_validator: SafetyValidator):
    disabled_validator.validate_joint_move(RobotType.NERO, [999.0] * 7)


# --- Cartesian validation ---


def test_valid_cartesian_pose(validator: SafetyValidator):
    validator.validate_cartesian_move([0.3, 0.1, 0.5, 0.0, 0.0, 0.0])


def test_cartesian_out_of_bounds_x(validator: SafetyValidator):
    with pytest.raises(SafetyError, match="X="):
        validator.validate_cartesian_move([2.0, 0.0, 0.5, 0.0, 0.0, 0.0])


def test_cartesian_out_of_bounds_z_negative(validator: SafetyValidator):
    with pytest.raises(SafetyError, match="Z="):
        validator.validate_cartesian_move([0.0, 0.0, -0.5, 0.0, 0.0, 0.0])


def test_cartesian_too_few_values(validator: SafetyValidator):
    with pytest.raises(SafetyError, match="at least 3"):
        validator.validate_cartesian_move([0.3, 0.1])


def test_custom_workspace_bounds():
    config = SafetyConfig(
        enabled=True,
        workspace_bounds=WorkspaceBounds(x_min=0, x_max=0.5, y_min=-0.3, y_max=0.3,
                                          z_min=0.0, z_max=0.6),
    )
    v = SafetyValidator(config)
    v.validate_cartesian_move([0.25, 0.0, 0.3, 0.0, 0.0, 0.0])
    with pytest.raises(SafetyError):
        v.validate_cartesian_move([-0.1, 0.0, 0.3, 0.0, 0.0, 0.0])


# --- Move validation (composite) ---


def test_validate_move_joint(validator: SafetyValidator):
    validator.validate_move(RobotType.NERO, MotionMode.J, [0.0] * 7)


def test_validate_move_cartesian(validator: SafetyValidator):
    validator.validate_move(
        RobotType.NERO, MotionMode.P, [0.3, 0.0, 0.3, 0.0, 0.0, 0.0]
    )


def test_validate_move_arc(validator: SafetyValidator):
    start = [0.3, 0.0, 0.3, 0.0, 0.0, 0.0]
    mid = [0.3, 0.05, 0.3, 0.0, 0.0, 0.0]
    end = [0.3, 0.0, 0.3, 0.0, 0.0, 0.0]
    validator.validate_move(RobotType.NERO, MotionMode.C, start, mid, end)
