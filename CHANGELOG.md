# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-22

### Added

- OpenClaw skill `agx-arm-codegen` for natural-language robotic arm code generation
- Python bridge server (FastAPI) wrapping pyAgxArm SDK with safety layer
- OpenClaw TypeScript plugin with `arm_connect`, `arm_status`, `arm_move`, `arm_stop` tools
- Mock driver for development and testing without physical hardware
- Safety layer with joint limits, workspace bounds, and velocity caps
- Support for NERO (7-DOF) and Piper (6-DOF) robotic arms
- Example scripts: hello_arm, pick_and_place, draw_circle
- Docker support for bridge server
- CI pipeline with lint and test stages
