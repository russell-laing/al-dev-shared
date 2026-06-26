#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health disposition store CLI."""

import runpy

try:
    from scripts.al_dev_tools.health.health_disposition_store import *  # noqa: F401,F403
    from scripts.al_dev_tools.health.health_disposition_store import _cli_match as _cli_match
    MODULE_NAME = "scripts.al_dev_tools.health.health_disposition_store"
except ModuleNotFoundError:
    from al_dev_tools.health.health_disposition_store import *  # noqa: F401,F403
    from al_dev_tools.health.health_disposition_store import _cli_match as _cli_match
    MODULE_NAME = "al_dev_tools.health.health_disposition_store"


if __name__ == "__main__":
    runpy.run_module(MODULE_NAME, run_name="__main__")
