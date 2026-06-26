#!/usr/bin/env python3
"""Compatibility wrapper for the packaged JSONL disposition migration CLI."""

import runpy

try:
    from scripts.al_dev_tools.health.migrate_health_disposition_jsonl import *  # noqa: F401,F403
    MODULE_NAME = "scripts.al_dev_tools.health.migrate_health_disposition_jsonl"
except ModuleNotFoundError:
    from al_dev_tools.health.migrate_health_disposition_jsonl import *  # noqa: F401,F403
    MODULE_NAME = "al_dev_tools.health.migrate_health_disposition_jsonl"


if __name__ == "__main__":
    runpy.run_module(MODULE_NAME, run_name="__main__")
