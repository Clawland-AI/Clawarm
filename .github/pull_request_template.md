## Summary

<!-- 1-3 bullet points describing the change -->

## Type

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] CI/DevOps

## Safety Checklist

- [ ] No changes to joint limits or workspace bounds without review
- [ ] Safety layer tests pass (`pytest tests/test_safety.py`)
- [ ] Mock driver tests pass (`pytest tests/test_mock_driver.py`)
- [ ] Bridge API tests pass (`pytest tests/test_bridge_api.py`)

## Test Plan

<!-- How was this tested? Mock mode? Real hardware? -->
