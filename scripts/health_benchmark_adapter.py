#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health benchmark adapter."""

try:
    from scripts.al_dev_tools.health.health_benchmark_adapter import *  # noqa: F401,F403
    from scripts.al_dev_tools.health.health_benchmark_adapter import main
except ModuleNotFoundError:
    from al_dev_tools.health.health_benchmark_adapter import *  # noqa: F401,F403
    from al_dev_tools.health.health_benchmark_adapter import main


if __name__ == "__main__":
    raise SystemExit(main())
