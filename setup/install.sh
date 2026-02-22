#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== ClawArm Setup ==="
echo ""

# 1. Python dependencies
echo "[1/5] Installing Python dependencies..."
pip3 install -e "$PROJECT_DIR"
echo "  -> bridge server installed"

# 2. pyAgxArm (optional — skip if not needed)
echo ""
echo "[2/5] Installing pyAgxArm SDK..."
if pip3 show pyAgxArm &>/dev/null; then
    echo "  -> pyAgxArm already installed"
else
    echo "  Installing pyAgxArm from GitHub..."
    pip3 install git+https://github.com/agilexrobotics/pyAgxArm.git
    echo "  -> pyAgxArm installed"
fi

# 3. python-can
echo ""
echo "[3/5] Checking python-can..."
if python3 -c "import can" &>/dev/null; then
    echo "  -> python-can already installed"
else
    pip3 install python-can
    echo "  -> python-can installed"
fi

# 4. Copy OpenClaw skill
echo ""
echo "[4/5] Installing OpenClaw skill..."
SKILL_SRC="$PROJECT_DIR/skills/agx-arm-codegen"
SKILL_DST="$HOME/.openclaw/skills/agx-arm-codegen"

if [ -d "$HOME/.openclaw" ]; then
    mkdir -p "$SKILL_DST"
    cp -r "$SKILL_SRC/"* "$SKILL_DST/"
    echo "  -> Skill copied to $SKILL_DST"
else
    echo "  -> OpenClaw not found at ~/.openclaw — skip skill install"
    echo "     Install OpenClaw first: https://openclaw.ai/"
fi

# 5. Copy workspace templates
echo ""
echo "[5/5] Installing workspace templates..."
WORKSPACE_DIR="$HOME/.openclaw/workspace-clawarm"
if [ -d "$HOME/.openclaw" ]; then
    mkdir -p "$WORKSPACE_DIR"
    cp "$PROJECT_DIR/workspace/AGENTS.md" "$WORKSPACE_DIR/" 2>/dev/null || true
    cp "$PROJECT_DIR/workspace/SOUL.md" "$WORKSPACE_DIR/" 2>/dev/null || true
    mkdir -p "$WORKSPACE_DIR/memory"
    echo "  -> Workspace templates copied to $WORKSPACE_DIR"
else
    echo "  -> OpenClaw not found — skip workspace setup"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Activate CAN:    sudo bash setup/activate_can.sh"
echo "  2. Start bridge:    clawarm-bridge  (or: CLAWARM_MOCK=true clawarm-bridge)"
echo "  3. Check env:       python3 setup/check_env.py"
echo "  4. Configure OpenClaw: cp config/openclaw.example.json ~/.openclaw/openclaw.json"
