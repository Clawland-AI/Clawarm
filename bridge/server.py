"""FastAPI bridge server — exposes pyAgxArm functionality as REST endpoints."""

from __future__ import annotations

import logging
import os

import uvicorn
from fastapi import FastAPI, HTTPException

from .arm_manager import ArmManager
from .models import (
    ConnectRequest,
    MoveRequest,
    ResultResponse,
    StatusResponse,
    StopAction,
    StopRequest,
)
from .safety import SafetyConfig, SafetyError

logger = logging.getLogger("clawarm.bridge")

app = FastAPI(
    title="ClawArm Bridge",
    description="REST API for AI-driven robotic arm control via pyAgxArm",
    version="0.1.0",
)

_manager: ArmManager | None = None


def _get_manager() -> ArmManager:
    global _manager
    if _manager is None:
        safety_val = os.environ.get("CLAWARM_SAFETY", "true").lower()
        safety_enabled = safety_val not in ("0", "false", "no")
        max_speed = int(os.environ.get("CLAWARM_MAX_SPEED", "80"))
        _manager = ArmManager(SafetyConfig(enabled=safety_enabled, max_speed_percent=max_speed))
    return _manager


@app.get("/", response_model=ResultResponse)
async def root():
    return ResultResponse(ok=True, message="ClawArm Bridge v0.1.0")


@app.post("/connect", response_model=ResultResponse)
async def connect(req: ConnectRequest):
    try:
        mgr = _get_manager()
        msg = mgr.connect(req.robot, req.channel, req.interface)
        return ResultResponse(ok=True, message=msg)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/disconnect", response_model=ResultResponse)
async def disconnect():
    mgr = _get_manager()
    msg = mgr.disconnect()
    return ResultResponse(ok=True, message=msg)


@app.get("/status", response_model=StatusResponse)
async def status():
    mgr = _get_manager()
    data = mgr.get_status()
    return StatusResponse(**data)


@app.post("/move", response_model=ResultResponse)
async def move(req: MoveRequest):
    mgr = _get_manager()
    if not mgr.connected:
        raise HTTPException(status_code=400, detail="Arm not connected. POST /connect first.")
    try:
        msg = mgr.move(
            mode=req.mode,
            target=req.target,
            mid_point=req.mid_point,
            end_point=req.end_point,
            speed_percent=req.speed_percent,
            wait=req.wait,
            timeout=req.timeout,
        )
        return ResultResponse(ok=True, message=msg)
    except SafetyError as exc:
        raise HTTPException(status_code=422, detail=f"Safety violation: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/enable", response_model=ResultResponse)
async def enable():
    mgr = _get_manager()
    if not mgr.connected:
        raise HTTPException(status_code=400, detail="Arm not connected")
    driver = mgr._driver
    retries = 0
    while not driver.enable():
        import time
        time.sleep(0.01)
        retries += 1
        if retries > 500:
            raise HTTPException(status_code=500, detail="Failed to enable arm")
    return ResultResponse(ok=True, message="Arm enabled")


@app.post("/disable", response_model=ResultResponse)
async def disable():
    mgr = _get_manager()
    if not mgr.connected:
        raise HTTPException(status_code=400, detail="Arm not connected")
    driver = mgr._driver
    retries = 0
    while not driver.disable():
        import time
        time.sleep(0.01)
        retries += 1
        if retries > 100:
            raise HTTPException(status_code=500, detail="Failed to disable arm")
    return ResultResponse(ok=True, message="Arm disabled")


@app.post("/stop", response_model=ResultResponse)
async def stop(req: StopRequest):
    mgr = _get_manager()
    msg = mgr.stop(emergency=(req.action == StopAction.EMERGENCY_STOP))
    return ResultResponse(ok=True, message=msg)


def main():
    host = os.environ.get("CLAWARM_HOST", "127.0.0.1")
    port = int(os.environ.get("CLAWARM_PORT", "8420"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    mock_mode = os.environ.get("CLAWARM_MOCK", "").lower() in ("1", "true", "yes")
    if mock_mode:
        logger.info("Starting in MOCK mode (no real hardware)")

    logger.info("ClawArm Bridge starting on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
