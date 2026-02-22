#!/usr/bin/env bash
set -euo pipefail

# Activate SocketCAN interface for robotic arm communication.
# Usage: sudo bash activate_can.sh [interface] [bitrate]
#   interface: CAN interface name (default: can0)
#   bitrate:   CAN bus bitrate (default: 1000000)

INTERFACE="${1:-can0}"
BITRATE="${2:-1000000}"

echo "=== CAN Interface Activation ==="
echo "  Interface: $INTERFACE"
echo "  Bitrate:   $BITRATE"
echo ""

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root (sudo)."
    exit 1
fi

# Load CAN kernel modules
echo "Loading CAN kernel modules..."
modprobe can
modprobe can_raw
modprobe can_dev

# Check if interface exists
if ! ip link show "$INTERFACE" &>/dev/null; then
    echo "WARNING: Interface $INTERFACE does not exist."
    echo "  If using a USB-CAN adapter, check that it is connected."
    echo "  Available interfaces:"
    ip link show | grep -E "can[0-9]" || echo "    (none found)"
    exit 1
fi

# Bring down first (in case it's already up with wrong config)
ip link set "$INTERFACE" down 2>/dev/null || true

# Configure and bring up
ip link set "$INTERFACE" up type can bitrate "$BITRATE"

echo ""
echo "CAN interface $INTERFACE is UP (bitrate=$BITRATE)"
echo ""

# Verify
ip -details link show "$INTERFACE"

echo ""
echo "To test: candump $INTERFACE"
echo "To deactivate: sudo ip link set $INTERFACE down"
