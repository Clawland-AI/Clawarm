"""Tests for the FastAPI bridge server endpoints using mock driver."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["CLAWARM_MOCK"] = "true"

import bridge.server as _srv
from bridge.server import app


@pytest.fixture(autouse=True)
def _reset_manager():
    """Reset global manager state between tests for isolation."""
    _srv._manager = None
    yield
    _srv._manager = None


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "ClawArm" in data["message"]


@pytest.mark.asyncio
async def test_status_not_connected(client: AsyncClient):
    resp = await client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False


@pytest.mark.asyncio
async def test_connect_and_status(client: AsyncClient):
    resp = await client.post("/connect", json={"robot": "nero", "channel": "can0"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    resp = await client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is True
    assert data["robot_type"] == "nero"
    assert data["dof"] == 7


@pytest.mark.asyncio
async def test_move_without_connect(client: AsyncClient):
    resp = await client.post("/move", json={"mode": "J", "target": [0.0] * 7})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_connect_move_disconnect(client: AsyncClient):
    await client.post("/connect", json={"robot": "nero"})

    resp = await client.post(
        "/move",
        json={"mode": "J", "target": [0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    resp = await client.post("/disconnect")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_move_cartesian(client: AsyncClient):
    await client.post("/connect", json={"robot": "nero"})

    resp = await client.post(
        "/move",
        json={"mode": "P", "target": [0.3, 0.0, 0.3, 0.0, 0.0, 0.0]},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_stop_disable(client: AsyncClient):
    await client.post("/connect", json={"robot": "nero"})
    resp = await client.post("/stop", json={"action": "disable"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_stop_emergency(client: AsyncClient):
    await client.post("/connect", json={"robot": "nero"})
    resp = await client.post("/stop", json={"action": "emergency_stop"})
    assert resp.status_code == 200
    assert "EMERGENCY" in resp.json()["message"]


@pytest.mark.asyncio
async def test_safety_rejects_out_of_range_joints(client: AsyncClient):
    await client.post("/connect", json={"robot": "nero"})
    resp = await client.post(
        "/move",
        json={"mode": "J", "target": [5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    )
    assert resp.status_code == 422
    assert "Safety" in resp.json()["detail"]
