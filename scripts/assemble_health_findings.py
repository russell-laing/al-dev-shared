#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health-findings assembler."""

import runpy

try:
    from scripts.al_dev_tools.health.assemble_health_findings import *  # noqa: F401,F403
    MODULE_NAME = "scripts.al_dev_tools.health.assemble_health_findings"
except ModuleNotFoundError:
    from al_dev_tools.health.assemble_health_findings import *  # noqa: F401,F403
    MODULE_NAME = "al_dev_tools.health.assemble_health_findings"


if __name__ == "__main__":
    runpy.run_module(MODULE_NAME, run_name="__main__")
