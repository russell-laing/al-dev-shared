#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health artifact selector CLI."""

try:
    from scripts.al_dev_tools.health.select_health_artifacts import *  # noqa: F401,F403
    from scripts.al_dev_tools.health.select_health_artifacts import main
except ModuleNotFoundError:
    from al_dev_tools.health.select_health_artifacts import *  # noqa: F401,F403
    from al_dev_tools.health.select_health_artifacts import main


if __name__ == "__main__":
    raise SystemExit(main())
