#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health loop-state validator."""

import runpy

try:
    from scripts.al_dev_tools.health.validate_health_loop_state import *  # noqa: F401,F403
    MODULE_NAME = "scripts.al_dev_tools.health.validate_health_loop_state"
except ModuleNotFoundError:
    from al_dev_tools.health.validate_health_loop_state import *  # noqa: F401,F403
    MODULE_NAME = "al_dev_tools.health.validate_health_loop_state"


if __name__ == "__main__":
    runpy.run_module(MODULE_NAME, run_name="__main__")
