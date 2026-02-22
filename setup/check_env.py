#!/usr/bin/env python3
"""Verify that all dependencies and configurations are in place for ClawArm."""

import shutil
import subprocess
import sys
from pathlib import Path


def check(label: str, ok: bool, detail: str = "") -> bool:
    status = "OK" if ok else "FAIL"
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status:4s}] {label}{suffix}")
    return ok


def main() -> None:
    print("=== ClawArm Environment Check ===\n")
    all_ok = True

    # Python version
    v = sys.version_info
    all_ok &= check(
        "Python >= 3.10",
        v >= (3, 10),
        f"found {v.major}.{v.minor}.{v.micro}",
    )

    # python-can
    try:
        import can  # type: ignore
        all_ok &= check("python-can", True, f"v{can.__version__}")
    except ImportError:
        all_ok &= check("python-can", False, "pip install python-can")

    # pyAgxArm
    try:
        import pyAgxArm  # type: ignore
        all_ok &= check("pyAgxArm", True)
    except ImportError:
        all_ok &= check("pyAgxArm", False, "pip install pyAgxArm (optional for mock mode)")

    # FastAPI
    try:
        import fastapi  # type: ignore
        all_ok &= check("FastAPI", True, f"v{fastapi.__version__}")
    except ImportError:
        all_ok &= check("FastAPI", False, "pip install -e '.'")

    # uvicorn
    try:
        import uvicorn  # type: ignore
        all_ok &= check("uvicorn", True)
    except ImportError:
        all_ok &= check("uvicorn", False, "pip install -e '.'")

    # CAN interface (Linux only)
    print()
    if sys.platform == "linux":
        try:
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            has_can = "can0" in result.stdout
            all_ok &= check(
                "CAN interface (can0)",
                has_can,
                "UP" if has_can else "not found — run: sudo bash setup/activate_can.sh",
            )
        except Exception:
            all_ok &= check("CAN interface", False, "could not check")
    else:
        check("CAN interface", True, f"skipped on {sys.platform} (use mock mode)")

    # OpenClaw installation
    print()
    openclaw_bin = shutil.which("openclaw")
    all_ok &= check(
        "OpenClaw CLI",
        openclaw_bin is not None,
        openclaw_bin or "not found — https://openclaw.ai/",
    )

    # Skill installed
    skill_path = Path.home() / ".openclaw" / "skills" / "agx-arm-codegen" / "SKILL.md"
    check(
        "agx-arm-codegen skill",
        skill_path.exists(),
        str(skill_path) if skill_path.exists() else "run: bash setup/install.sh",
    )

    # Bridge server reachable
    print()
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8420/")
        with urllib.request.urlopen(req, timeout=2) as resp:
            all_ok &= check("Bridge server (:8420)", resp.status == 200)
    except Exception:
        check("Bridge server (:8420)", False, "not running — start with: clawarm-bridge")

    print()
    if all_ok:
        print("All checks passed. ClawArm is ready.")
    else:
        print("Some checks failed. See details above.")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
