#!/usr/bin/env python3
"""Compatibility wrapper for the packaged disposition-store consistency checker."""

import runpy

try:
    from scripts.al_dev_tools.health.check_disposition_store_consistency import *  # noqa: F401,F403
    MODULE_NAME = "scripts.al_dev_tools.health.check_disposition_store_consistency"
except ModuleNotFoundError:
    from al_dev_tools.health.check_disposition_store_consistency import *  # noqa: F401,F403
    MODULE_NAME = "al_dev_tools.health.check_disposition_store_consistency"


if __name__ == "__main__":
    runpy.run_module(MODULE_NAME, run_name="__main__")
