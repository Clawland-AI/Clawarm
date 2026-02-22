"""Tests for the mock arm driver."""

import pytest

from bridge.drivers.mock_driver import MockArmDriver


@pytest.fixture
def driver():
    d = MockArmDriver()
    d.connect("nero", "can0", "socketcan")
    return d


def test_connect_sets_state(driver: MockArmDriver):
    assert driver.is_connected
    assert driver.robot_type == "nero"
    assert driver.dof == 7


def test_connect_piper():
    d = MockArmDriver()
    d.connect("piper", "can0", "socketcan")
    assert d.dof == 6
    assert d.robot_type == "piper"


def test_enable_disable(driver: MockArmDriver):
    assert not driver.is_enabled
    assert driver.enable()
    assert driver.is_enabled
    assert driver.disable()
    assert not driver.is_enabled


def test_move_j_updates_angles(driver: MockArmDriver):
    driver.enable()
    target = [0.1, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0]
    driver.move_j(target)
    angles = driver.get_joint_angles()
    assert angles is not None
    assert angles == pytest.approx(target)


def test_move_p_updates_pose(driver: MockArmDriver):
    driver.enable()
    pose = [0.3, 0.1, 0.2, 0.0, 3.14, 0.0]
    driver.move_p(pose)
    result = driver.get_flange_pose()
    assert result is not None
    assert result == pytest.approx(pose)


def test_motion_status_returns_idle_after_move(driver: MockArmDriver):
    driver.enable()
    driver.move_j([0.0] * 7)
    assert driver.get_motion_status() == 0


def test_emergency_stop_disables(driver: MockArmDriver):
    driver.enable()
    driver.emergency_stop()
    assert not driver.is_enabled
    assert driver.get_motion_status() == 0


def test_disconnect(driver: MockArmDriver):
    driver.disconnect()
    assert not driver.is_connected
    assert driver.get_joint_angles() is None


def test_initial_joint_angles_are_zero(driver: MockArmDriver):
    angles = driver.get_joint_angles()
    assert angles is not None
    assert all(a == 0.0 for a in angles)
    assert len(angles) == 7
