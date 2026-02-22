# Security & Safety Policy

## Physical Safety

ClawArm controls **real robotic hardware** that can cause injury or property damage.

### Mandatory Safety Rules

1. **Clear the workspace** before any arm movement. Ensure no people or obstacles are within the arm's reach envelope.
2. **Start with low speed** (`set_speed_percent(30)`) when testing new motions. Increase only after verifying the trajectory.
3. **Keep the physical emergency stop within reach** at all times.
4. **Never disable the safety layer** (`safetyEnabled: true`) in production environments.
5. **Test in mock mode first** (`CLAWARM_MOCK=true`) before running against real hardware.

### Emergency Stop

- **Bridge API**: `POST /stop` with `{"action": "emergency_stop"}`
- **OpenClaw tool**: The agent can call `arm_stop` with action `emergency_stop`
- **Physical button**: Always preferred — use the hardware E-stop on the arm controller
- **Software kill**: `Ctrl+C` the bridge server process to cut all communication

## Software Security

### Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email [security@clawland.ai](mailto:security@clawland.ai) with details
3. Include steps to reproduce and potential impact
4. We will respond within 48 hours

### API Security

- The bridge server binds to `127.0.0.1` by default (localhost only)
- No authentication is required for local connections by design
- If exposing the bridge to a network, use a reverse proxy with authentication
- The OpenClaw plugin communicates with the bridge over HTTP — do not expose port 8420 to the internet

### Dependency Policy

- Pin all Python dependencies in `pyproject.toml`
- Run `pip audit` regularly to check for known vulnerabilities
- Keep pyAgxArm updated to the latest stable release
